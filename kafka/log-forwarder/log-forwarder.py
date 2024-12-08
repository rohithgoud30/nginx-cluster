from kafka import KafkaProducer
import time
import json
import os

KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'RAWLOG'
LOG_FILE = '../logs/access.log'  # Relative path to the log file

def main():
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("Starting to stream logs to Kafka...")
    log_path = os.path.join(os.path.dirname(__file__), LOG_FILE)
    with open(log_path, 'r') as log_file:
        log_file.seek(0, 2)  # Move to the end of the file
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(1)
                continue
            try:
                log_data = json.loads(line.strip())
                producer.send(KAFKA_TOPIC, log_data)
                print(f"Sent to Kafka: {log_data}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse log line: {line}. Error: {e}")

if __name__ == "__main__":
    main()

