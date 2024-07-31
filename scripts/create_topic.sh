#!/usr/bin/env bash

set -x
set -eo pipefail

until kafka-topics --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic $TEST_TOPIC_NAME; do
      >&2 echo "Broker is unavailable - sleeping"
      sleep 5
done
exit 0
