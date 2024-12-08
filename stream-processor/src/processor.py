import os
import json
from datetime import datetime, timedelta
from kafka import KafkaConsumer, KafkaProducer
from cassandra.cluster import Cluster
from collections import Counter
import logging

# Configuration
WINDOW_MINUTES = int(os.getenv('WINDOW_MINUTES', '5'))
TOP_N = int(os.getenv('TOP_N', '3'))
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
KAFKA_INPUT_TOPIC = os.getenv('KAFKA_INPUT_TOPIC', 'RAWLOG')
KAFKA_OUTPUT_TOPIC = os.getenv('KAFKA_OUTPUT_TOPIC', 'PRODUCTS')
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'cassandra')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PageViewProcessor:
    def __init__(self):
        logger.info(f"Initializing processor with: Window(P)={WINDOW_MINUTES}min, TOP_N={TOP_N}")
        
        try:
            self.consumer = KafkaConsumer(
                KAFKA_INPUT_TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='stream-processor',
                auto_offset_reset='earliest'
            )
            logger.info("KafkaConsumer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize KafkaConsumer. Error: {e}")
            raise

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda m: json.dumps(m).encode('utf-8')
            )
            logger.info("KafkaProducer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize KafkaProducer. Error: {e}")
            raise

        try:
            self.cassandra = Cluster([CASSANDRA_HOST]).connect('nginx_logs')
            logger.info("Cassandra connection established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Cassandra. Error: {e}")
            raise

        self.window_start = self._get_window_start()
        self.page_counts = Counter()

    def _get_window_start(self):
        now = datetime.now()
        return now.replace(
            minute=(now.minute // WINDOW_MINUTES) * WINDOW_MINUTES,
            second=0,
            microsecond=0
        )

    def process_window(self):
        """Process current window and produce results"""
        if not self.page_counts:
            self.window_start += timedelta(minutes=WINDOW_MINUTES)
            logger.info(f"No data to process. Moving to new window: {self.window_start}")
            return

        window_end = self.window_start + timedelta(minutes=WINDOW_MINUTES)
        top_pages = self.page_counts.most_common(TOP_N)

        # Prepare results
        results = {
            'timestamp': self.window_start.isoformat(),
            'window_minutes': WINDOW_MINUTES,
            'top_pages': [
                {'page': page, 'count': count}
                for page, count in top_pages
            ]
        }

        # Send to Kafka
        try:
            logger.debug(f"Publishing to PRODUCTS: {results}")
            self.producer.send(KAFKA_OUTPUT_TOPIC, results)
            logger.info(f"Window results published to Kafka: {results}")
        except Exception as e:
            logger.error(f"Failed to send results to Kafka. Error: {e}")

        # Write to Cassandra
        for page, count in top_pages:
            try:
                logger.debug(f"Updating Cassandra: page={page}, count={count}")
                self.cassandra.execute("""
                    UPDATE results
                    SET visit_count = visit_count + %s,
                        window_size = %s
                    WHERE window_start = %s AND page_path = %s
                """, (count, WINDOW_MINUTES, self.window_start, page))
                logger.info(f"Updated Cassandra for {page} with count {count}")
            except Exception as e:
                logger.error(f"Cassandra update failed for {page}. Error: {e}")

        # Reset for next window
        self.page_counts.clear()
        self.window_start += timedelta(minutes=WINDOW_MINUTES)
        logger.info(f"Starting new window from {self.window_start}")

    def run(self):
        """Main processing loop"""
        logger.info(f"Starting page view processing...")
        
        try:
            for message in self.consumer:
                current_time = datetime.now()
                
                # Check if window ended
                if current_time >= self.window_start + timedelta(minutes=WINDOW_MINUTES):
                    self.process_window()
                
                # Process message
                try:
                    request = message.value.get('request', '')
                    page = request.split()[1] if request else ''
                    if page.startswith('/product'):
                        self.page_counts[page] += 1
                        logger.debug(f"Processed page view: {page}")
                        logger.debug(f"Page counts updated: {self.page_counts}")
                    else:
                        logger.debug(f"Ignored page view: {request}")
                except Exception as e:
                    logger.error(f"Error processing message: {message.value}. Error: {e}")

        except KeyboardInterrupt:
            logger.info("Shutting down processor...")
        finally:
            self.consumer.close()
            self.producer.close()

if __name__ == "__main__":
    processor = PageViewProcessor()
    processor.run()
