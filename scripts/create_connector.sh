#!/bin/sh
# Create kafka connector
set -x
set -eo pipefail

until curl --output /dev/null --silent $KAFKA_CONNECT_URL/connectors; do
      >&2 echo "Kafka Connect server unavailable - sleeping"
      sleep 10
done

response=$(curl -X PUT -H "Content-Type: application/json" --write-out '%{http_code}' --output /dev/null $KAFKA_CONNECT_URL/connectors/s3-sink/config\
    -d '{
    "store.url": "http://localstack:4566",
    "aws.access.key.id": "",
    "aws.secret.access.key": "",
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "flush.size": 1,
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "locale": "en-US",
    "name": "s3-sink",
    "parquet.codec": "snappy",
    "partition.duration.ms": 3600000,
    "partitioner.class": "io.confluent.connect.storage.partitioner.DefaultPartitioner",
    "rotate.interval.ms": 600000,
    "s3.bucket.name": "my-bucket",
    "s3.region": "eu-central-1",
    "s3.schema.compatibility": "NONE",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "tasks.max": 1,
    "timestamp.extractor": "Record",
    "timestamp.field": "time",
    "timezone": "UTC",
    "topics": "test-topic",
    "topics.dir": "topics",
    "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter.schema.registry.url": "http://schema-registry:8081"
}')

if [ "$response" -eq 200 ]; then
    >&2 echo "Connector created successfully."
    exit 0
else
    >&2 echo "Connector creation failed."
    exit 1
fi
