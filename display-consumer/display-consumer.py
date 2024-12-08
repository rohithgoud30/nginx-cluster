import time
import json
import logging
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CASSANDRA_HOSTS = ['cassandra']
KAFKA_TOPIC = 'RAWLOG'
KAFKA_BOOTSTRAP_SERVER = 'kafka:9092'
GROUP_ID = 'display-consumer'

def connect_cassandra():
    """Connect to Cassandra and return the session and cluster."""
    try:
        cluster = Cluster(CASSANDRA_HOSTS)
        session = cluster.connect()
        session.set_keyspace('nginx_logs')
        logger.info("Connected to Cassandra.")
        return session, cluster
    except Exception as e:
        logger.error(f"Error connecting to Cassandra: {e}")
        raise

def update_results_table(session, window_start, page_path, is_unique):
    """Update the results table in Cassandra."""
    try:
        # Update the counters
        session.execute("""
            UPDATE results
            SET visit_count = visit_count + 1,
                unique_visitors = unique_visitors + %s
            WHERE window_start = %s AND page_path = %s
        """, (1 if is_unique else 0, window_start, page_path))
        logger.info(f"Updated results for page_path={page_path}, unique={is_unique}")
    except Exception as e:
        logger.error(f"Error updating results table: {e}")

def consume_kafka_messages():
    """Consume messages from Kafka and process them."""
    session, cluster = connect_cassandra()
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
        group_id=GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest'
    )

    logger.info("Kafka consumer started.")

    unique_visitors = set()
    window_start = datetime.now().replace(second=0, microsecond=0)
    window_duration = timedelta(minutes=1)

    for message in consumer:
        log_entry = message.value
        logger.debug(f"Log entry: {log_entry}")

        try:
            page_path = log_entry.get('request', '').split(' ')[1]
            client_ip = log_entry.get('remote_addr', '')

            # Check if client IP is unique for the current window
            is_unique = client_ip not in unique_visitors
            if is_unique:
                unique_visitors.add(client_ip)

            # Update the results table
            update_results_table(session, window_start, page_path, is_unique)

            # Check if the current window has ended
            if datetime.now() >= window_start + window_duration:
                logger.info(f"Window ended: {window_start} to {window_start + window_duration}")
                window_start += window_duration
                unique_visitors.clear()

        except Exception as e:
            logger.error(f"Error processing log entry: {e}")

    consumer.close()
    cluster.shutdown()

if __name__ == "__main__":
    try:
        consume_kafka_messages()
    except Exception as e:
        logger.error(f"Fatal error: {e}")

