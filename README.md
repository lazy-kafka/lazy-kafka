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
run:
- 🐳 docker environment `$ scripts/start-up`
- 📃 `$ hatch run dev:console`
- 💾 `$ hatch run dev:app`

If you are using pip:
- `pip install -e .`
- `lazy-kafka`

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



# useful

curl -s -XGET http://localhost:8083/connector-plugins | jq '.[].class'

curl -XGET http://localhost:8083/connectors

# Roadmap

## v0.1.0
- settings management
- k-connect continuous update (like watch)
  - [x] Color the State column based on the value
  - [x] Fix currently highlighted connector selection on update
  - [x] Load from config file
    - [-] Add file watcher - get inspiration from watchdog or [toolong](https://github.com/Textualize/toolong/blob/main/src/toolong/watcher.py)
  - [x] Expose more configuration (kafka auth related)

## v0.2.0
- [ ] see messages in a stream
  - [ ] extend kafka page support: AIOKafka/confluent-kafka library facade
    - [ ] implementation only with confluent-kafka, but with a facade
- [ ] produce messages into a stream
  - [ ] concrete producer
  - [ ] dummy producer (agent pool pattern?)



## 

## v1.0
Generate client code from openapi
- deprecate confluent-kafka in favor of [kafka-rest api](https://github.com/confluentinc/kafka-rest/blob/master/api/v3/openapi.yaml)
    - [docker](https://hub.docker.com/r/confluentinc/cp-kafka-rest)
- kakfa-connect
-schema-registy


## 09-15
- schema listing and browsing
  x multiple versions of stuff (-> always show the latest)
  x ** it is cumbersome to go from subject to schema (human exploration) **
    ** it is easy to look up `id` -> schema (how the messages are serialized) **
    0. request to list subjects
    1. request to `subjects/<subject>/versions` to list versions
    2. request to `subjects/<subjects>/versions/-1` to get the latest schema info
    3. request to `schemas/ids/{id}/schema`
  -> can delete schema with a dialog popping up
  -> The design philosophy is to handle events as close to the source as possible. 


- create modal screens to create schema, connector, topic (?)
- create settings management from config file
- create a screen for settings
- add delete action
- 



# NOTES
- confluent kafka docs: https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#confluent_kafka.TopicPartition
- detailed example of confluent kafka lib api: https://github.com/confluentinc/confluent-kafka-python/issues/1443


