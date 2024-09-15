#!/bin/sh

# Create schema, associate with topic
#
# Generic request form [reference](https://docs.confluent.io/platform/current/schema-registry/develop/using.html)
#   curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
#     --data '{"schema": "{\"type\": \"string\"}"}' \
#     http://localhost:8081/subjects/Kafka-value/versions

set -x

until curl --output /dev/null --silent $SCHEMA_REGISTRY_URL/; do
      >&2 echo "Server unavailable - sleeping"
      sleep 10
done

response=$(curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    --write-out '%{http_code}' --output /dev/null \
    --data '{"type":"object", "properties":{"id":{"type":"string"},"amount":{"type":"number"} }}' \
    $SCHEMA_REGISTRY_URL/subjects/test-value/versions
)

response=$(curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    --write-out '%{http_code}' --output /dev/null \
    --data '{"schema": "{\"type\": \"string\"}"}' \
    $SCHEMA_REGISTRY_URL/subjects/$SUBJECT/versions
)

if [ "$response" -eq 200 ]; then
    >&2 echo "Schema created successfully."
    exit 0
else
    >&2 echo "Schema creation failed."
    exit 1
fi
