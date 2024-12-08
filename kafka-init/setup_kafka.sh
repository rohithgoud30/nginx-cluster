# kafka-init/setup_kafka.sh
#!/bin/bash

until kafka-topics --list --bootstrap-server kafka:9092 >/dev/null 2>&1; do
  echo "Waiting for Kafka..."
  sleep 5
done

# Create RAWLOG topic if not exists
if ! kafka-topics --list --bootstrap-server kafka:9092 | grep -q "^RAWLOG$"; then
  kafka-topics --create --topic RAWLOG \
    --bootstrap-server kafka:9092 \
    --partitions 3 \
    --replication-factor 1
  echo "RAWLOG topic created."
fi

# Create PRODUCTS topic if not exists
if ! kafka-topics --list --bootstrap-server kafka:9092 | grep -q "^PRODUCTS$"; then
  kafka-topics --create --topic PRODUCTS \
    --bootstrap-server kafka:9092 \
    --partitions 3 \
    --replication-factor 1
  echo "PRODUCTS topic created."
fi
