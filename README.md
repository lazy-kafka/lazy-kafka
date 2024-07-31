# lazy-kafka

[![PyPI - Version](https://img.shields.io/pypi/v/lazy-kafka.svg)](https://pypi.org/project/lazy-kafka)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lazy-kafka.svg)](https://pypi.org/project/lazy-kafka)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install lazy-kafka
```

## License

`lazy-kafka` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

# dev

check topics:
docker exec 1793ae26d162 /bin/kafka-topics --bootstrap-server=localhost:9092

## Docker compose
The docker compose will:
- Start a Kafka cluster: 1 broker and 1 zookeeper
  - create a test-topic
- Start ConfluentSchemaRegistry
  - register a 'test-schema' for the 'test-topic'
- Start LocalStack S3 bucket 'test-bucket'
- Start Kafka Connect
  - create a connector to read from test-topic, dump to S3 test-bucket
