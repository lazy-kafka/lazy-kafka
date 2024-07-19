from confluent_kafka.serialization import (
    StringSerializer,
)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka import SerializingProducer

import json

CONF = {
    "bootstrap.servers": "localhost:9092",
}
TOPIC = "foo"
SCHEMA_REGISTRY_URL = "http://localhost:8081"

def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

def data_to_dict(d: dict, ctx):
    return d

if __name__ == "__main__":
    reg = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})

    string_serializer = StringSerializer("utf_8")

    schema = reg.get_latest_version(TOPIC+'-value')

    string_serializer = StringSerializer("utf_8")

    avro_serializer = AvroSerializer(
        reg,
        schema.schema,
        data_to_dict,
        conf = {
          'auto.register.schemas': False
        },
    )

    producer = SerializingProducer({
        'bootstrap.servers': "localhost:9092",
        'security.protocol': 'plaintext',
        'value.serializer': avro_serializer,
        'delivery.timeout.ms': 120000, # set it to 2 mins
        'enable.idempotence': 'true'
    })

    f = open("dump.json", "r", encoding="utf-8")
    i = 0

    l = None
    try:
        while l != "":
            l = f.readline()
            try:
                data = json.loads(l)
                print(f"{data!r}")
                producer.produce(topic=TOPIC, value=data, on_delivery=delivery_report)
                producer.poll(1.0)
                producer.flush()

            except KeyboardInterrupt:
                break

    finally:
        f.close()
