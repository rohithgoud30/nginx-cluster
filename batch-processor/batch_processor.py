import os
import logging
from datetime import datetime, timedelta
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self):
        load_balancing_policy = DCAwareRoundRobinPolicy(local_dc='datacenter1')
        self.cluster = Cluster(
            contact_points=['cassandra'],
            load_balancing_policy=load_balancing_policy,
            protocol_version=5
        )
        self.session = self.cluster.connect('nginx_logs')
        logger.info("Connected to Cassandra cluster")

    def process_daily_stats(self):
        try:
            today = datetime.now().date()
            start_ts = datetime.combine(today, datetime.min.time())
            end_ts = datetime.now()
            
            logger.info(f"Processing logs from {start_ts} to {end_ts}")

            query = """
                SELECT window_start, page_path, visit_count, unique_visitors
                FROM results
                WHERE window_start >= %s AND window_start <= %s
                ALLOW FILTERING
            """
            
            rows = self.session.execute(query, [start_ts, end_ts])
            
            daily_stats = {}
            total_rows = 0
            
            for row in rows:
                total_rows += 1
                if row.page_path not in daily_stats:
                    daily_stats[row.page_path] = {
                        'visits': 0,
                        'unique_visitors': row.unique_visitors
                    }
                daily_stats[row.page_path]['visits'] += row.visit_count

            logger.info(f"Processed {total_rows} rows from results table")
            
            if not daily_stats:
                logger.warning("No data found for processing")
                return

            logger.info("=== Aggregated Statistics ===")
            for page_path, stats in daily_stats.items():
                logger.info(
                    f"Page: {page_path}, "
                    f"Total Visits: {stats['visits']}, "
                    f"Unique Visitors: {stats['unique_visitors']}"
                )

            # Fix: Changed ? to %s in insert query
            insert_query = """
                INSERT INTO daily_results 
                (date, page_path, total_visits, unique_visitors)
                VALUES (%s, %s, %s, %s)
            """
            
            for page_path, stats in daily_stats.items():
                params = [today, page_path, stats['visits'], stats['unique_visitors']]
                logger.info(f"Inserting data with params: {params}")
                self.session.execute(insert_query, params)
                logger.info(f"Stored daily stats for {page_path}")

            # Fix: Changed ? to %s in verify query
            verify_query = "SELECT * FROM daily_results WHERE date = %s"
            results = self.session.execute(verify_query, [today])
            
            logger.info("=== Stored Daily Results ===")
            for row in results:
                logger.info(
                    f"Page: {row.page_path}, "
                    f"Total Visits: {row.total_visits}, "
                    f"Unique Visitors: {row.unique_visitors}"
                )

        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            raise
        finally:
            logger.info("Batch processing cycle completed")

    def cleanup(self):
        if self.cluster:
            self.cluster.shutdown()
            logger.info("Cassandra connection closed")

def main():
    processor = None
    try:
        processor = BatchProcessor()
        processor.process_daily_stats()
    except Exception as e:
        logger.error(f"Fatal error in batch processor: {str(e)}")
    finally:
        if processor:
            processor.cleanup()

if __name__ == "__main__":
    main()
