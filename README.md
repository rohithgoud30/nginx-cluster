# NGINX Cluster Project

This project implements a scalable NGINX cluster with Kafka, Cassandra, and real-time and batch log processing capabilities. It supports containerized deployment using Docker Compose.

---

## Features
- **NGINX Load Balancer**: Distributes traffic across multiple web servers.
- **Kafka Integration**: Facilitates log forwarding and real-time processing.
- **Cassandra**: Stores results for real-time and batch processing.
- **Batch and Real-Time Processing**: Process logs and aggregate results.

---

## Quick Start

### 1. Clone the Repository
Clone the project to your local machine:
```bash
git clone https://github.com/rohithgoud30/nginx-cluster.git
cd nginx-cluster
```

---

### 2. Run the Project with Docker Compose
Start all services using Docker Compose:
```bash
docker-compose up -d --build
```

Verify that all services are running:
```bash
docker ps
```

---

### 3. Initialize Cassandra Schema
Set up the required schema in Cassandra for real-time and batch log processing.

1. **Schema Definition:**

   The schema includes:
   - A `results` table for real-time log aggregation.
   - A `daily_results` table for batch log processing.

   ```sql
   -- Create the keyspace
   CREATE KEYSPACE IF NOT EXISTS nginx_logs
   WITH replication = {
     'class': 'SimpleStrategy',
     'replication_factor': 1
   };

   -- Table for real-time log processing
   CREATE TABLE IF NOT EXISTS nginx_logs.results (
       window_start timestamp,
       page_path text,
       visit_count int,
       unique_visitors int,
       PRIMARY KEY (window_start, page_path)
   );

   -- Table for batch processing
   CREATE TABLE IF NOT EXISTS nginx_logs.daily_results (
       date date,
       page_path text,
       total_visits int,
       unique_visitors int,
       PRIMARY KEY (date, page_path)
   );
   ```

2. **Copy the Schema File into the Cassandra Container:**
   ```bash
   docker cp cassandra-init/init.cql cassandra:/tmp/init.cql
   ```

3. **Access the Cassandra Container:**
   ```bash
   docker exec -it cassandra bash
   ```

4. **Run the Schema Script Using `cqlsh`:**
   ```bash
   cqlsh
   SOURCE '/tmp/init.cql';
   ```

5. **Verify the Schema:**
   ```bash
   DESCRIBE KEYSPACE nginx_logs;
   ```

---

## Monitoring and Logs

1. **Monitor Webserver Logs:**
   ```bash
   docker logs -f webserver1
   docker logs -f webserver2
   docker logs -f webserver3
   ```

2. **Check Real-Time Processing Results:**
   ```bash
   docker exec -it kafka kafka-console-consumer \
     --bootstrap-server kafka:9092 \
     --topic PRODUCTS \
     --from-beginning
   ```

3. **Verify Cassandra Tables:**
   Query the `results` and `daily_results` tables:
   ```bash
   docker exec -it cassandra bash
   cqlsh
   SELECT * FROM nginx_logs.results;
   SELECT * FROM nginx_logs.daily_results;
   ```

---

## Stopping and Cleaning Up

1. **Stop All Services:**
   ```bash
   docker-compose down
   ```

2. **Remove Unused Docker Resources:**
   ```bash
   docker system prune -a
   ```

---

## Directory Structure
```plaintext
nginx-cluster/
├── batch-processor/       # Handles batch processing jobs
├── cassandra-init/        # Cassandra initialization scripts
├── configs/               # Configurations for NGINX servers
├── display-consumer/      # Consumer service for Kafka topics
├── kafka/                 # Kafka log forwarding
├── kafka-init/            # Kafka setup scripts
├── kafka-streaming/       # Real-time Kafka stream processing
├── log-forwarder/         # Log forwarding service
├── logs/                  # Log files (access, error, and results)
├── static/                # HTML static files
├── stream-processor/      # Real-time log stream processor
```

---

## Additional Notes
- Ensure Docker and Docker Compose are installed before starting the project.
- Use `docker logs <container_name>` to troubleshoot individual services.

This README includes all the necessary steps for running and setting up the project, ensuring a smooth start for any user. Save it as `README.md` in your project root directory. Let me know if you need further refinements!
