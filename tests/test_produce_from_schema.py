"""Tests for the random schema-instance generator in produce_from_schema."""

from __future__ import annotations

import random
import time

import pytest

from lazy_kafka.scripts.produce_from_schema import (
    avro_type_to_value_schema,
    instance_for_schema,
)


def seeded():
    return random.Random(42)


def test_const_and_enum():
    assert instance_for_schema({"const": "fixed"}) == "fixed"
    value = instance_for_schema({"enum": ["a", "b", "c"]}, seeded())
    assert value in ("a", "b", "c")


def test_string_types():
    value = instance_for_schema({"type": "string"}, seeded())
    assert isinstance(value, str)
    assert value

    stamp = instance_for_schema({"type": "string", "format": "date-time"}, seeded())
    assert stamp.endswith("Z")
    assert "T" in stamp


def test_numeric_respects_bounds():
    value = instance_for_schema(
        {"type": "integer", "minimum": 5, "maximum": 6}, seeded()
    )
    assert value in (5, 6)

    number = instance_for_schema(
        {"type": "number", "minimum": 1.5, "maximum": 1.6}, seeded()
    )
    assert 1.5 <= number <= 1.6

    # exclusiveMinimum must be avoided
    exclusive = instance_for_schema(
        {"type": "integer", "exclusiveMinimum": 0, "minimum": 0}, seeded()
    )
    assert exclusive > 0


def test_exclusive_minimum_without_minimum():
    # exclusiveMinimum must win even when `minimum` is absent
    value = instance_for_schema({"type": "integer", "exclusiveMinimum": 5}, seeded())
    assert value > 5

    number = instance_for_schema({"type": "number", "exclusiveMinimum": 5.0}, seeded())
    assert number > 5.0


def test_boolean():
    assert isinstance(instance_for_schema({"type": "boolean"}, seeded()), bool)


def test_object_uses_required_fields():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "secret": {"type": "string"},
            "count": {"type": "integer"},
        },
        "required": ["name", "count"],
    }
    value = instance_for_schema(schema, seeded())
    assert set(value) == {"name", "count"}  # secrets out, required in
    assert value["count"] == int(value["count"])


def test_object_without_required_uses_all_properties():
    schema = {
        "type": "object",
        "properties": {"a": {"type": "integer"}},
    }
    value = instance_for_schema(schema, seeded())
    assert set(value) == {"a"}


def test_nested_and_arrays():
    schema = {
        "type": "object",
        "properties": {
            "tags": {"type": "array", "items": {"type": "string", "const": "x"}},
            "meta": {
                "type": "object",
                "properties": {"uid": {"type": "string"}},
                "required": ["uid"],
            },
        },
        "required": ["tags", "meta"],
    }
    value = instance_for_schema(schema, seeded())
    assert value["tags"] == ["x"]
    assert set(value["meta"]) == {"uid"}
    assert isinstance(value["meta"]["uid"], str)


def test_type_list_picks_supported():
    value = instance_for_schema({"type": ["null", "string"]}, seeded())
    assert isinstance(value, str)


def test_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported schema type"):
        instance_for_schema({"type": "unknown"}, seeded())


def test_no_type_raises():
    with pytest.raises(ValueError, match="no usable type"):
        instance_for_schema({}, seeded())


## AVRO normalization


def test_avro_primitives_map():
    assert avro_type_to_value_schema("string")["type"] == "string"
    assert avro_type_to_value_schema("long")["type"] == "integer"
    assert avro_type_to_value_schema("double")["type"] == "number"
    assert avro_type_to_value_schema("boolean")["type"] == "boolean"


def test_avro_nullable_union_flattens():
    assert avro_type_to_value_schema(["null", "string"])["type"] == "string"


def test_avro_multi_branch_union_raises():
    with pytest.raises(ValueError, match="multiple non-null branches"):
        avro_type_to_value_schema(["null", "int", "double"])


def test_avro_record_to_object():
    avro = {
        "type": "record",
        "name": "Measurement",
        "fields": [
            {"name": "sensor", "type": "string"},
            {"name": "value", "type": "double"},
            {"name": "note", "type": ["null", "string"]},
        ],
    }
    node = avro_type_to_value_schema(avro)
    assert node["type"] == "object"
    assert set(node["required"]) == {"sensor", "value", "note"}
    value = instance_for_schema(node, seeded())
    assert isinstance(value["value"], float)
    assert isinstance(value["note"], str)


def test_avro_enum_array_and_nested_record():
    avro = {
        "type": "record",
        "name": "Outer",
        "fields": [
            {
                "name": "shape",
                "type": {"type": "enum", "name": "Shape", "symbols": ["good", "flat"]},
            },
            {"name": "tags", "type": {"type": "array", "items": "string"}},
            {
                "name": "inner",
                "type": {
                    "type": "record",
                    "name": "Inner",
                    "fields": [{"name": "uid", "type": "string"}],
                },
            },
        ],
    }
    node = avro_type_to_value_schema(avro)
    value = instance_for_schema(node, seeded())
    assert value["shape"] in ("good", "flat")
    assert len(value["tags"]) == 1
    assert isinstance(value["tags"][0], str)
    assert isinstance(value["inner"]["uid"], str)


def test_avro_logical_timestamp():
    node = avro_type_to_value_schema(
        {"type": "long", "logicalType": "timestamp-millis"}
    )
    assert node["type"] == "integer"  # AVRO puts epoch ints on the wire
    value = instance_for_schema(node, seeded())
    now_ms = time.time() * 1000
    assert 0 < value <= now_ms


def test_avro_logical_date():
    node = avro_type_to_value_schema({"type": "int", "logicalType": "date"})
    assert node["type"] == "integer"  # days since epoch


def test_avro_unknown_type_raises():
    with pytest.raises(ValueError, match="Unsupported AVRO type"):
        avro_type_to_value_schema("bytes")


def test_avro_unknown_node_raises():
    with pytest.raises(ValueError, match="Unsupported AVRO type"):
        avro_type_to_value_schema({"type": "fixed"})
