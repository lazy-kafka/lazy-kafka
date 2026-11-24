"""Produce schema-conformant messages to a topic.

The latest schema for the `<topic>-value` subject is fetched from the
Schema Registry, so messages always follow whatever is currently registered
(e.g. `test-topic` follows the `test-topic-value` subject). Values are
generated randomly from the schema itself -- nothing about the payload is
duplicated in this file. Both JSON and AVRO registered schemas are supported;
AVRO types are normalized to the internal (JSON-schema-like) representation
before generating values.

Usage:

    uv run python src/lazy_kafka/scripts/produce_from_schema.py [TOPIC]
    uv run python src/lazy_kafka/scripts/produce_from_schema.py test-topic --interval 0.5

Ctrl+C to stop.
"""

from __future__ import annotations

import json
import random
import time
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)

from lazy_kafka.config import Configuration

DEFAULT_TOPIC = "test-topic"
DEFAULT_INTERVAL = 1.0


def instance_for_schema(
    schema: dict[str, Any], rng: random.Random | None = None
) -> Any:
    """Generate a random instance conforming to the given (JSON) schema.

    Supports the subset of JSON Schema Draft-07 that data-producing schemas
    realistically use: `const`, `enum`, primitives, `arrays`, and nested
    `objects`. Unknown or unsupported constructs raise `ValueError` with a
    clear message rather than producing invalid data.
    """
    rng = rng or random.Random()

    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return rng.choice(schema["enum"])

    schema_type: str | list[str] | None = schema.get("type")
    if isinstance(schema_type, list):
        # Pick the first supported type from a list constraint.
        supported = [t for t in schema_type if t != "null"] or schema_type
        schema_type = supported[0]

    match schema_type:
        case "string":
            fmt = schema.get("format")
            if fmt == "date-time":
                stamp = datetime.now(UTC) - timedelta(seconds=rng.randint(0, 3600))
                # Emit UTC in canonical ISO form (trailing Z instead of +00:00).
                return stamp.isoformat().replace("+00:00", "Z")
            return f"test-{uuid4().hex[:10]}"
        case "integer":
            lower = schema.get("minimum", 0)
            exclusive = schema.get("exclusiveMinimum")
            if exclusive is not None:
                # Value must satisfy lower > exclusiveMinimum as well.
                lower = max(lower, int(exclusive) + 1)
            upper = schema.get("maximum", max(100, int(lower) + 100))
            return rng.randint(int(lower), int(upper))
        case "number":
            lower = schema.get("minimum", 0.0)
            exclusive = schema.get("exclusiveMinimum")
            if exclusive is not None:
                lower = max(lower, float(exclusive) + 0.01)
            upper = schema.get("maximum", max(100.0, float(lower) + 100.0))
            return round(rng.uniform(float(lower), float(upper)), 4)
        case "boolean":
            return rng.random() < 0.5
        case "array":
            return [instance_for_schema(schema["items"], rng)]
        case "object":
            properties: dict[str, Any] = schema.get("properties", {})
            required: list[str] = schema.get("required", list(properties))
            return {
                k: instance_for_schema(properties[k], rng)
                for k in required
                if k in properties
            }
        case None:
            raise ValueError(
                f"Schema node has no usable type or constraint: {schema!r}"
            )
        case other:
            raise ValueError(f"Unsupported schema type {other!r} in: {schema!r}")


def latest_schema(client: SchemaRegistryClient, subject: str) -> dict[str, Any]:
    """Fetch and parse the latest registered schema for `subject`."""


def avro_type_to_value_schema(avro_type: Any) -> dict[str, Any]:
    """Normalize an AVRO type node into a generator-compatible schema node.

    The generator speaks a JSON-Schema-ish subset (see `instance_for_schema`);
    AVRO schemas express roughly the same information differently. Nullable
    unions (`["null", "string"]`) are flattened to their single non-null side.
    """
    if isinstance(avro_type, list):  # union
        alternatives = [t for t in avro_type if t != "null"]
        if len(alternatives) != 1:
            raise ValueError(
                f"Unsupported union with multiple non-null branches: {avro_type!r}"
            )
        return avro_type_to_value_schema(alternatives[0])

    if not isinstance(avro_type, dict):  # primitive name
        mapping = {
            "string": "string",
            "int": "integer",
            "long": "integer",
            "float": "number",
            "double": "number",
            "boolean": "boolean",
        }
        try:
            return {"type": mapping[avro_type]}
        except KeyError:
            raise ValueError(f"Unsupported AVRO type {avro_type!r}.") from None

    match avro_type.get("type"):
        case "record":
            fields = avro_type.get("fields", [])
            properties = {
                f["name"]: avro_type_to_value_schema(f["type"]) for f in fields
            }
            return {
                "type": "object",
                "properties": properties,
                # AVRO requires every field to be present (or defaulted).
                "required": list(properties),
            }
        case "enum":
            return {"type": "string", "enum": avro_type["symbols"]}
        case "array":
            return {
                "type": "array",
                "items": avro_type_to_value_schema(avro_type["items"]),
            }
        case _ if avro_type.get("logicalType") in (
            "timestamp-millis",
            "timestamp-micros",
        ):
            # AVRO serializes logical timestamps as epoch integers (not ISO
            # strings); generate a value within the last hour.
            now = int(
                time.time()
                * (
                    1_000
                    if avro_type["logicalType"] == "timestamp-millis"
                    else 1_000_000
                )
            )
            window = 3_600 * (
                1_000 if avro_type["logicalType"] == "timestamp-millis" else 1_000_000
            )
            return {"type": "integer", "minimum": now - window, "maximum": now}
        case _ if avro_type.get("logicalType") == "date":
            # Days since epoch; generate a day within the last month.
            today = int(time.time() // 86_400)
            return {"type": "integer", "minimum": today - 30, "maximum": today}
        case primitive if primitive in (
            "string",
            "int",
            "long",
            "float",
            "double",
            "boolean",
        ):
            return avro_type_to_value_schema(primitive)
        case wrapped if isinstance(wrapped, str):
            return avro_type_to_value_schema(wrapped)
        case other:
            raise ValueError(f"Unsupported AVRO type node {other!r}.")


def latest_value_schema(
    client: SchemaRegistryClient, subject: str
) -> tuple[str, dict[str, Any]]:
    """Fetch the latest registered schema for `subject`.

    Returns `(schema_type, raw_schema)` plus, for AVRO, a normalized
    schema usable by `instance_for_schema`.
    """
    registered = client.get_latest_version(subject)
    raw_schema = json.loads(registered.schema.schema_str)
    return registered.schema.schema_type, raw_schema


def delivery_report(err: Any, msg: Any) -> None:
    if err is not None:
        print(f"Delivery failed: {err}")
        return
    print(f"OK {msg.topic()}[{msg.partition()}] offset {msg.offset()}")


def main(topic: str = DEFAULT_TOPIC, interval: float = DEFAULT_INTERVAL) -> None:
    cfg = Configuration()
    registry = SchemaRegistryClient(cfg.registry.to_config())

    subject = f"{topic}-value"
    schema_type, raw_schema = latest_value_schema(registry, subject)
    print(f"Following {subject} ({schema_type}, fetched from Schema Registry):")
    print(json.dumps(raw_schema, indent=2))

    match schema_type:
        case "JSON":
            value_schema = raw_schema
            serializer = JSONSerializer(
                json.dumps(raw_schema),
                registry,
                lambda value, ctx: value,
                conf={"auto.register.schemas": False},
            )
        case "AVRO":
            value_schema = avro_type_to_value_schema(raw_schema)
            serializer = AvroSerializer(
                registry,
                json.dumps(raw_schema),
                lambda value, ctx: value,
                conf={"auto.register.schemas": False},
            )
        case other:
            raise ValueError(
                f"{subject} is registered as {other}; this producer supports JSON and AVRO."
            )

    key_serializer = StringSerializer("utf_8")
    producer = Producer(cfg.kafka.to_config())

    print(f"Emitting messages to {topic} (ctrl+C to stop)...")
    try:
        while True:
            producer.poll(0.0)
            value = instance_for_schema(value_schema)
            producer.produce(
                topic=topic,
                key=key_serializer(str(uuid4())),
                value=serializer(
                    value, SerializationContext(topic, MessageField.VALUE)
                ),
                on_delivery=delivery_report,
            )
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "topic", nargs="?", default=DEFAULT_TOPIC, help="topic to produce to"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help="seconds between messages",
    )
    args = parser.parse_args()
    main(args.topic, args.interval)
