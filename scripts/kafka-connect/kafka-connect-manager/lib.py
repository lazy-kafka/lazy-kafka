
import argparse
from enum import StrEnum, auto
from typing import Union, Self, Tuple
from confluent_kafka.schema_registry import SchemaRegistryClient, RegisteredSchema
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka import SerializingProducer

import json

#SCHEMA_REGISTRY_URL = "http://localhost:8081"
#TOPIC = "foo"


# NOTE: PROD OVERRIDES
SCHEMA_REGISTRY_URL = "https://psrc-do01d.eu-central-1.aws.confluent.cloud"
TOPIC = "pub.rma-ropax-pqnek.monitoring-new-recommendation"

def data_to_dict(d: dict, ctx):
    return d

class SerializationType(StrEnum):
    AVRO = "AVRO"
    JSON = "JSON"

    @staticmethod
    def from_str(v: str):
        try:
            return SerializationType[v]
        except KeyError:
            raise NotImplementedError(f"{v}") 

    def serializer(self: Self, registry: SchemaRegistryClient, schema: RegisteredSchema) -> Union[AvroSerializer, JSONSerializer]:
        match self:
            case SerializationType.AVRO:
                 message_serializer = AvroSerializer(
                    registry,
                    schema.schema,
                    data_to_dict,
                    conf = {
                      'auto.register.schemas': False
                    },
                 )
                 
            case SerializationType.JSON:
                #Note that the authors of the lib swapped the first two pos args
                # hence we cannot use factory 
                message_serializer = JSONSerializer(
                    schema.schema,
                    registry,
                    data_to_dict,
                    conf={
                        "auto.register.schemas": False,
                    },
                )
            case _:
                raise NotImplementedError
        return message_serializer



def cli(default_value = SerializationType.AVRO.value) -> Tuple[SerializationType, bool]:
    """Side-effect parser - parse arguments"""
    parser = argparse.ArgumentParser(
        description="Write schema compatible messages to topic."
    )
    parser.add_argument('--dummy', action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "-t",
        "--schema-type",
        dest="schema_type",
        choices=["AVRO", "JSON"],
        type=str,
        default=default_value.upper(),
        help="Log to topic foo with schema look-up (default: AVRO schema)",
    )

    args = parser.parse_args()
    dummy_mode = True if args.dummy else False
    return SerializationType.from_str(args.schema_type), dummy_mode
