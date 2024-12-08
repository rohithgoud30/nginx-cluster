import time
import json
import os
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'RAWLOG')
LOG_PATH = '/app/logs/access.log'

def get_producer():
    retries = 5
    for _ in range(retries):
        try:
            return KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            print(f"Retrying Kafka connection: {e}")
            time.sleep(5)

def main():
    producer = get_producer()
    while not os.path.exists(LOG_PATH):
        print(f"Waiting for log file at {LOG_PATH}")
        time.sleep(5)

    with open(LOG_PATH, 'r') as file:
        file.seek(0, 2)
        while True:
            line = file.readline()
            if line:
                producer.send(KAFKA_TOPIC, value=json.loads(line))
                print(f"Forwarded: {line.strip()}")
            time.sleep(0.1)

if __name__ == "__main__":
    main()

