"""Tests for lazy_kafka.serializers (Avro details decoding)."""

from __future__ import annotations

import json
import struct
from unittest.mock import MagicMock, patch

from confluent_kafka.schema_registry._sync.mock_schema_registry_client import (
    MockSchemaRegistryClient,
)

from lazy_kafka.serializers import AvroMessageDecoder, looks_like_wire_format

REGISTRY_CONF = {"url": "http://localhost:8081"}

AVRO_SCHEMA = {
    "type": "record",
    "name": "Event",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "id2", "type": ["long", "null"]},
    ],
}

MAGIC = b"\x00"
SCHEMA_ID = 1


def _wire(payload: bytes) -> bytes:
    return MAGIC + struct.pack(">I", SCHEMA_ID) + payload


def _mock_registry_conf() -> MagicMock:
    conf = MagicMock()
    conf.host = "http://localhost:8081"
    return conf


def _register_and_encode():
    """Register AVRO_SCHEMA on a mock registry and encode one sample."""
    from confluent_kafka.schema_registry.avro import AvroSerializer

    registry = MockSchemaRegistryClient(dict(REGISTRY_CONF))
    serializer = AvroSerializer(registry, json.dumps(AVRO_SCHEMA), lambda v, _: v)
    from confluent_kafka.serialization import MessageField, SerializationContext

    # AvroSerializer output IS the full Confluent wire message
    # (magic + schema id + encoded payload) — no extra wrapping.
    encoded = serializer(
        {"id": "abc", "id2": 3},
        SerializationContext("test-topic", MessageField.VALUE),
    )
    return registry, encoded


def test_plain_json_is_not_wire_format():
    assert not looks_like_wire_format(b'{"a": 1}')


def test_wire_format_detection():
    assert looks_like_wire_format(_wire(b"\x08"))


def test_wire_format_none_and_short_payloads():
    assert not looks_like_wire_format(None)
    assert not looks_like_wire_format(b"\x00\x01")
    assert not looks_like_wire_format(b"")


def test_decode_roundtrip():
    registry, payload = _register_and_encode()

    with patch(
        "lazy_kafka.serializers._get_schema_registry_client",
        return_value=registry,
    ):
        decoder = AvroMessageDecoder(topic="test-topic", registry=_mock_registry_conf())
        decoded = decoder.decode(payload)

    assert decoded == {"id": "abc", "id2": 3}


def test_decode_plain_json_returns_none():
    decoder = AvroMessageDecoder(topic="t", registry=MagicMock())
    assert decoder.decode(b'{"plain": "json"}') is None


def test_decode_none_payload_returns_none():
    decoder = AvroMessageDecoder(topic="t", registry=MagicMock())
    assert decoder.decode(None) is None


def test_decode_no_schema_returns_none():
    registry = MockSchemaRegistryClient(dict(REGISTRY_CONF))

    with patch(
        "lazy_kafka.serializers._get_schema_registry_client",
        return_value=registry,
    ):
        decoder = AvroMessageDecoder(
            topic="no-such-topic", registry=_mock_registry_conf()
        )
        # 5-byte header claiming a schema id that does not exist on the mock.
        assert decoder.decode(_wire(b"\x08")) is None


def test_decode_error_returns_none():
    decoder = AvroMessageDecoder(topic="t", registry=MagicMock())
    decoder._deserializer = MagicMock(side_effect=RuntimeError("bad avro"))
    assert decoder.decode(_wire(b"\x08")) is None


def test_decode_scalar_result_is_returned():
    # Primitive Avro schemas ("string", "long", …) decode to scalars.
    decoder = AvroMessageDecoder(topic="t", registry=MagicMock())
    decoder._deserializer = MagicMock(return_value="a plain string")
    assert decoder.decode(_wire(b"\x08")) == "a plain string"


def test_decode_none_result_returns_none():
    decoder = AvroMessageDecoder(topic="t", registry=MagicMock())
    decoder._deserializer = MagicMock(return_value=None)
    assert decoder.decode(_wire(b"\x08")) is None


def test_lazy_deserializer_built_once():
    registry, payload = _register_and_encode()

    with patch(
        "lazy_kafka.serializers._get_schema_registry_client",
        return_value=registry,
    ) as factory:
        decoder = AvroMessageDecoder(topic="test-topic", registry=_mock_registry_conf())
        decoder.decode(payload)
        decoder.decode(payload)

    # Schema lookup happens once, not once per message.
    assert factory.call_count == 1


def test_decoder_without_registry_never_decodes():
    decoder = AvroMessageDecoder(topic="t", registry=None)
    assert decoder.decode(_wire(b"\x08")) is None
