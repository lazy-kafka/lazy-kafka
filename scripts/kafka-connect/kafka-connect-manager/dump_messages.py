from confluent_kafka import Consumer, KafkaException
import sys
import json

import logging

_LOGGER = logging.getLogger(__name__)

CONF = {
    "bootstrap.servers":"pkc-e8wrm.eu-central-1.aws.confluent.cloud:9092",
    "security.protocol":"SASL_SSL",
    "sasl.mechanism":"PLAIN",
    "sasl.username":"RLD3HSGNNBA5MGVO",
    "sasl.password":"WsjjieibNjDWxeh8FvLJRh80nioiiB5mxaxC+M7xFdxSrA0ArJV1O/vpyyyZl9Jj",
    "group.id":"rma-ropax-pqnek.local.test",
    "auto.offset.reset": "earliest",
}

LOGGER = logging.getLogger('consumer')
LOGGER.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
LOGGER.addHandler(handler)

TOPIC = ["pub.rma-ropax-pqnek.ropax-capacity-recommendations"]


if __name__ == "__main__":
    c = Consumer(CONF,logger=LOGGER)

    def print_assignment(consumer, partitions):
        print('Assignment:', partitions)

    c.subscribe(TOPIC, on_assign=print_assignment)

    # Read messages from Kafka, print to stdout
    f = open("dump.json", "w+", encoding='utf-8')
    i = 0
    try:
        while True:
            if i > 10:
                break
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                json.dump(json.loads(msg.value().decode("utf-8").replace("'",'"')), f, ensure_ascii=True)
                f.write("\n")
                f.flush()
                # Store the offset associated with msg to a local cache.
                # Stored offsets are committed to Kafka by a background thread every 'auto.commit.interval.ms'.
                # Explicitly storing offsets after processing gives at-least once semantics.
                #c.store_offsets(msg)
            i += 1

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        c.close()
        f.close()


