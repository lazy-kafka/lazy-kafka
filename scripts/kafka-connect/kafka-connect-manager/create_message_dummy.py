"""create avro schema messages"""
from confluent_kafka.serialization import (
    StringSerializer,
)
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


CONF = {
    "bootstrap.servers": "localhost:9092",
}

TOPIC = "foo"

# schema also in avro_schema.avsc file

SCHEMA_REGISTRY_URL = "http://localhost:8081"


def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

class User(object):
    def __init__(self, name,  favorite_number, favorite_color,address):
        self.name = name
        self.favorite_number = favorite_number
        self.favorite_color = favorite_color
        # address should not be serialized, see user_to_dict()
        self._address = address


def data_to_dict(user, ctx):
    return dict(name=user.name,
                favorite_number=user.favorite_number,
                favorite_color=user.favorite_color,
                address={"street": user._address}
                )

USERS = [User("john",int(3),"blue", "blabla"), User("jan", int(1), "red","blabla")]

if __name__ == "__main__":
    reg = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})

    string_serializer = StringSerializer("utf_8")
    schema = reg.get_latest_version(TOPIC+'-value')
    print(f"{schema.schema.schema_str!r}")

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

    try:
        for user in USERS:
            try:
                print(f"{user!r}")
                producer.produce(topic=TOPIC, value=user, on_delivery=delivery_report)
                producer.poll(1.0)
                producer.flush()

            except KeyboardInterrupt:
                break

    finally:
        print("done")
