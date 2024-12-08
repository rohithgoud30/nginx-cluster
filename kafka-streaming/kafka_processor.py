from kafka import KafkaConsumer, KafkaProducer
from cassandra.cluster import Cluster
from datetime import datetime, timedelta
import json
import logging

# Configuration
KAFKA_BROKER = "kafka:9092"
RAWLOG_TOPIC = "RAWLOG"
PRODUCTS_TOPIC = "PRODUCTS"
CASSANDRA_HOST = "cassandra"
CASSANDRA_KEYSPACE = "nginx_logs"
WINDOW_SIZE_SECONDS = 300  # 5 minutes

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cassandra setup
cluster = Cluster([CASSANDRA_HOST])
session = cluster.connect()
session.set_keyspace(CASSANDRA_KEYSPACE)

# Kafka setup
consumer = KafkaConsumer(
    RAWLOG_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="latest"
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

def update_counters(window_start, page, user_id, unique_visitors_set):
    """Update visit_count and unique_visitors counters in Cassandra."""
    is_unique = user_id not in unique_visitors_set
    unique_visitors_set.add(user_id)

    session.execute("""
        UPDATE results
        SET visit_count = visit_count + 1,
            unique_visitors = unique_visitors + ?
        WHERE window_start = ? AND page_path = ?
    """, (1 if is_unique else 0, window_start, page))

def process_logs():
    """Process logs in real-time."""
    unique_visitors_set = set()
    start_time = datetime.now()
    window_start = start_time.replace(second=0, microsecond=0)

    for message in consumer:
        log = message.value
        timestamp = datetime.strptime(log["timestamp"], "%Y-%m-%dT%H:%M:%S")
        page = log["page"]
        user_id = log["user_id"]

        # Ensure log falls into the current window
        if timestamp >= window_start + timedelta(seconds=WINDOW_SIZE_SECONDS):
            # Publish results to Kafka
            producer.send(PRODUCTS_TOPIC, value={"window_start": window_start.isoformat()})
            logger.info(f"Published results for window {window_start}")

            # Reset for the next window
            unique_visitors_set.clear()
            window_start += timedelta(seconds=WINDOW_SIZE_SECONDS)

        # Update counters in Cassandra
        update_counters(window_start, page, user_id, unique_visitors_set)

if __name__ == "__main__":
    try:
        process_logs()
    except KeyboardInterrupt:
        logger.info("Shutting down processor.")
    finally:
        consumer.close()
        producer.close()
        cluster.shutdown()
