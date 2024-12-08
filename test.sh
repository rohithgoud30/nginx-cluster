#!/bin/bash

echo "1. Rebuilding consumer..."
docker-compose build display-consumer
docker-compose up -d display-consumer

echo "2. Waiting for services to start..."
sleep 5

echo "3. Checking Cassandra keyspace..."
docker exec -it cassandra cqlsh -e "DESCRIBE KEYSPACES;"

echo "4. Testing direct write to Cassandra..."
docker exec -it cassandra cqlsh -e "
CREATE KEYSPACE IF NOT EXISTS test WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
USE test;
CREATE TABLE IF NOT EXISTS test_counter (id text PRIMARY KEY, value counter);
UPDATE test_counter SET value = value + 1 WHERE id = 'test1';
SELECT * FROM test_counter;"

echo "5. Generating test traffic..."
for i in {1..5}; do
    curl http://localhost:8080/product1.html
    sleep 1
done

echo "6. Waiting for processing..."
sleep 10

echo "7. Checking results..."
docker exec -it cassandra cqlsh -e "SELECT * FROM nginx_logs.results;"

echo "8. Checking consumer logs..."
docker logs display-consumer
