from pathlib import Path
from confluent_kafka.schema_registry import SchemaRegistryClient, RegisteredSchema
from confluent_kafka import SerializingProducer

import json
from lib import  SerializationType, SCHEMA_REGISTRY_URL, TOPIC, cli

def delivery_report(err, msg):
    """message producer callback"""
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print(
        "User record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )

def main(schema_type: SerializationType, dump_path: Path):
    reg = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL, "basic.auth.user.info":"IVW44Y6DYGNXUSOY:FAAs4uKLZI4z6nuhZSvoCBzH2uN2pC+LecSna0zMtt563aab6OBYv+uI2hD/qc/k"})
    schema = reg.get_latest_version(TOPIC)
    
    message_serializer = schema_type.serializer(reg, schema)

    producer = SerializingProducer(
        {
            "bootstrap.servers": "localhost:9092",
            "security.protocol": "plaintext",
            "value.serializer": message_serializer,
            "delivery.timeout.ms": 120000,  # set it to 2 mins
            "enable.idempotence": "true",
        }
    )

    f = open(dump_path, "r", encoding="utf-8")
    l = None
    try:
        while l != "":
            l = f.readline()
            try:
                data = json.loads(l)
                print(f"{data!r}")
                producer.produce(
                    topic=TOPIC, value=data, on_delivery=delivery_report
                )
                producer.poll(1.0)
                producer.flush()

            except KeyboardInterrupt:
                break
    finally:
        f.close()



if __name__ == "__main__":
    schema_type, dummy_mode = cli()

    
    match (schema_type, dummy_mode):
        case (SerializationType.JSON, True):
            dummy_path = Path("dummy-dump.json")
        case (SerializationType.JSON, False):
            dummy_path = Path("ropax-dump.json")
        case (SerializationType.AVRO, False):
            dummy_path = Path("ropax-dump.json")
        case _:
            raise NotImplementedError
    print(f"Using {schema_type}")
    main(schema_type=schema_type, dump_path=dummy_path)
