"""Deserialization helpers for message details.

Kept intentionally free of any TUI imports so it can be unit-tested
without a running app.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lazy_kafka.config import RegistryConfiguration

_LOGGER = logging.getLogger(__name__)

# Confluent wire format: b"\x00" + 4-byte schema id + payload. Messages
# produced with an Avro/JSON/Protobuf serializer carry this prefix.
AVRO_MAGIC_BYTE = 0


def looks_like_wire_format(payload: bytes | None) -> bool:
    """Return True if `payload` starts with the Confluent wire-format byte."""
    return payload is not None and len(payload) > 5 and payload[0] == AVRO_MAGIC_BYTE


def _get_schema_registry_client(config: RegistryConfiguration):
    """Build a confluent-kafka SchemaRegistryClient from lazy-kafka config."""
    from confluent_kafka.schema_registry import SchemaRegistryClient

    return SchemaRegistryClient(config.to_config(flavor="confluent"))


@dataclass
class AvroMessageDecoder:
    """Decode Confluent Avro wire-format payloads for a single topic.

    Looks up the latest `<topic>-value` schema in the Schema Registry and
    lazily builds an `AvroDeserializer` from it. Everything is lazy: no
    network requests happen until the first decode, and every failure
    (no schema, unreachable registry, missing magic byte, decode error)
    logs at INFO and yields `None`, never raising.
    """

    topic: str
    registry: RegistryConfiguration | None
    _deserializer: Callable | None = field(default=None, init=False, repr=False)

    def _build_deserializer(self) -> Callable | None:
        """Fetch the latest value schema and build a decoder; None on failure."""
        from confluent_kafka.schema_registry.avro import AvroDeserializer

        subject = f"{self.topic}-value"
        if self.registry is None:
            return None
        try:
            client = _get_schema_registry_client(self.registry)
            latest = client.get_latest_version(subject)
        except Exception as e:  # noqa: BLE001 - best-effort lookup by design
            _LOGGER.info(
                "No usable Avro schema for subject %r: %s",
                subject,
                e,
            )
            return None

        if (getattr(latest, "schema_type", None) or getattr(
            getattr(latest, "schema", None), "schema_type", "AVRO"
        )) != "AVRO":
            # JSON/Protobuf messages keep using the existing JSON handling.
            _LOGGER.debug("Subject %r is not AVRO; skipping Avro decode", subject)
            return None

        return AvroDeserializer(client, latest.schema.schema_str)

    def decode(self, payload: bytes | None) -> object | None:
        """Decode a wire-format payload, or return None on any failure."""
        if not looks_like_wire_format(payload):
            return None
        if self._deserializer is None:
            self._deserializer = self._build_deserializer()  # lazy, cached
        if self._deserializer is None:
            return None
        try:
            value = self._deserializer(payload, None)
        except Exception as e:  # noqa: BLE001 - details must never raise
            _LOGGER.info("Avro decode failed for topic %r: %s", self.topic, e)
            return None
        # Primitive schemas ("string", "long", …) decode to scalars, records
        # to dicts — both are displayable; None is returned on failure only.
        return value
