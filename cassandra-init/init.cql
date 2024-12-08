-- Create the keyspace
CREATE KEYSPACE IF NOT EXISTS nginx_logs
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

-- Create the `results` table for real-time log processing
CREATE TABLE IF NOT EXISTS nginx_logs.results (
    window_start timestamp,
    page_path text,
    visit_count int,
    unique_visitors int,
    PRIMARY KEY (window_start, page_path)
);

-- Create the `daily_results` table for batch processing
CREATE TABLE IF NOT EXISTS nginx_logs.daily_results (
    date date,
    page_path text,
    total_visits int,
    unique_visitors int,
    PRIMARY KEY (date, page_path)
);

