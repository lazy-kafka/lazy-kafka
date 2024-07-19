############
kafkaconnect
############

|Build| |Docker|

A Python client for managing connectors using the `Kafka Connect API <https://docs.confluent.io/current/connect/references/restapi.html>`_.

See `the docs <https://kafka-connect-manager.lsst.io>`_ for more information.


.. |Build| image:: https://github.com/lsst-sqre/kafka-connect-manager/workflows/CI/badge.svg
  :alt: GitHub Actions
  :scale: 100%
  :target: https://github.com/lsst-sqre/kafka-connect-manager/actions

.. |Docker| image:: https://img.shields.io/docker/v/lsstsqre/kafkaconnect?sort=date
  :alt: Docker Hub repository
  :scale: 100%
  :target: https://hub.docker.com/repository/docker/lsstsqre/kafkaconnect

kafka connect: https://docs.confluent.io/platform/current/installation/configuration/connect/index.html
https://docs.confluent.io/kafka-connectors/s3-sink/current/configuration_options.html

## list all messages from topic
docker exec -it broker kafka-console-consumer --bootstrap-server localhost:9092 --topic foo --from-beginning
docker exec -it broker kafka-console-consumer --bootstrap-server localhost:9092 --topic foo --from-beginning

### AVRO consumer
docker exec -it schema-registry kafka-avro-console-consumer --bootstrap-server broker:29092 --topic foo --from-beginning
docker exec -it schema-registry kafka-avro-console-producer --bootstrap-server broker:29092 --topic foo --property value.schema='{"type":"record","name":"myrecord","fields":[{"name":"f1","type":"string"}]}'

docker exec -it broker kafka-console-producer --bootstrap-server localhost:9092 --topic foo

## set up kafka connect to sink to s3
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

1. docker compose up -d (aws --endpoint-url http://localhost:4566 s3 ls should print "my-bucket" the bucket is created automatically)

1. docker-compose exec broker kafka-topics --bootstrap-server broker:9092 --create --topic foo --partitions 1 --replication-factor 1  

1. kafkaconnect create s3-sink ./tests/mycfg.json

1. docker-compose exec schema-registry kafka-avro-console-producer --bootstrap-server broker:29092 --topic foo --property value.schema='{"type":"record", "name":"foo", "fields":[{"name":"bar","type":"string"}, {"name":"baz","type":"float"}]}'

{"bar":"bar", "baz":1}
{"bar":"bor", "baz":2}
C-d

1. aws --endpoint-url http://localhost:4566 s3 ls my-bucket/ should show 'PRE topics/'
1. python ropax.py

       bar  baz  year month day hour
    0  bar  1.0  2024    04  16   08
    1  bor  2.0  2024    04  16   08

## Delete messages from topic   
when a topic get's an exotic message - e.g.: 'bad-message' (a raw str) the kafka-connect goes down with unrecoverable error.

Remove all messages:

0. docker cp ./delete_kafka_logs.json broker:/
1. docker compose exec broker kafka-delete-records --bootstrap-server broker:9092 --offset-json-file /delete_kafka_logs.json
1. kafkaconnect create s3-sink ./tests/mycfg.json
 


## Schema registry
source: https://docs.confluent.io/platform/current/schema-registry/schema-deletion-guidelines.html

list schemas:        curl --silent -X GET http://localhost:8081/subjects/ | jq .
details of schema:   curl --silent -X GET http://localhost:8081/subjects/foo-value/versions/latest | jq .
delete all schemas associated: curl -X DELETE http://localhost:8081/subjects/foo-value



THIS WORKS:
  AVRO:  kafkaconnect create s3-sink ./connectors/s3_sink/s3-sink-avro-connector.json

