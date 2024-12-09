# NGINX Cluster Project

This project implements a scalable NGINX cluster with Kafka, Cassandra, real-time log processing, and batch processing. It is designed for distributed traffic management, real-time analytics, and daily aggregation.

---

## Features
- **NGINX Load Balancer**: Routes traffic to web servers.
- **Kafka Integration**: Manages log forwarding and real-time processing.
- **Cassandra**: Stores real-time results and daily aggregated data.
- **Batch Processing**: Automates daily statistics aggregation.
- **Dockerized Setup**: Easily deployable using Docker Compose.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Cassandra Schema Initialization](#cassandra-schema-initialization)
3. [Verification Steps](#verification-steps)
    - [Phase 1: Environment Setup](#phase-1-environment-setup)
    - [Phase 2: Log Forwarder and Kafka Integration](#phase-2-log-forwarder-and-kafka-integration)
    - [Phase 3: Real-Time Processing](#phase-3-real-time-processing)
    - [Phase 4: Batch Processing](#phase-4-batch-processing)
4. [Stopping and Cleaning Up](#stopping-and-cleaning-up)

---

## Quick Start

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rohithgoud30/nginx-cluster.git
   cd nginx-cluster
   ```

2. **Start the Project**:
   ```bash
   docker-compose up -d --build
   ```

3. **Verify Running Services**:
   ```bash
   docker ps
   ```

4. **Access Load Balancer**:
   Visit the load balancer in your browser:
   ```plaintext
   http://localhost
   ```

---

## Cassandra Schema Initialization

1. **Copy Schema File into Cassandra Container**:
   ```bash
   docker cp cassandra-init/init.cql cassandra:/tmp/init.cql
   ```

2. **Access Cassandra Container**:
   ```bash
   docker exec -it cassandra bash
   ```

3. **Run Schema Script**:
   ```bash
   cqlsh
   SOURCE '/tmp/init.cql';
   ```

4. **Verify Schema**:
   ```bash
   DESCRIBE KEYSPACE nginx_logs;
   ```

The schema defines:
- **`results` Table**: Stores real-time log processing results.
- **`daily_results` Table**: Aggregates daily statistics.

---

## Verification Steps

### Phase 1: Environment Setup

1. **Verify Containers**:
   ```bash
   docker-compose ps
   ```

2. **Check NGINX Logs**:
   ```bash
   docker logs webserver1
   docker logs webserver2
   docker logs webserver3
   ```

3. **Simulate Traffic**:
   ```bash
   curl http://localhost:8080/products1.html
   curl http://localhost:8080/products2.html
   ```

4. **Validate Logs**:
   Inside the webserver container:
   ```bash
   docker exec -it webserver1 sh
   tail -f /var/log/nginx/access.log
   ```

---

### Phase 2: Log Forwarder and Kafka Integration

1. **Verify Kafka Topics**:
   ```bash
   docker exec -it kafka kafka-topics --list --bootstrap-server kafka:9092
   ```

2. **Check Log Forwarder**:
   ```bash
   docker logs -f log-forwarder
   ```

3. **Inspect Kafka Messages**:
   ```bash
   docker exec -it kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic RAWLOG --from-beginning
   ```

4. **Validate Cassandra Updates**:
   Query the `results` table:
   ```bash
   docker exec -it cassandra cqlsh -e "SELECT * FROM nginx_logs.results LIMIT 5;"
   ```

---

### Phase 3: Real-Time Processing

1. **Verify Stream Processor Logs**:
   ```bash
   docker logs -f stream-processor
   ```

2. **Simulate Traffic**:
   Use the traffic script:
   ```bash
   chmod +x test_traffic.sh
   ./test_traffic.sh
   ```

3. **Monitor Kafka Topics**:
   ```bash
   docker exec -it kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic PRODUCTS --from-beginning
   ```

4. **Validate Cassandra Aggregation**:
   ```bash
   docker exec -it cassandra cqlsh -e "SELECT * FROM nginx_logs.results ORDER BY window_start DESC LIMIT 5;"
   ```

---

### Phase 4: Batch Processing

1. **Run Batch Processor**:
   ```bash
   docker exec batch-processor python /app/batch_processor.py
   ```

2. **Verify Daily Results**:
   Query the `daily_results` table:
   ```bash
   docker exec -it cassandra cqlsh -e "SELECT * FROM nginx_logs.daily_results ORDER BY date DESC LIMIT 5;"
   ```

3. **Set Up Cron Job**:
   Add the cron job:
   ```bash
   crontab batch-processor/crontab
   ```

4. **Validate Cron Job**:
   ```bash
   crontab -l
   ```

---

## Stopping and Cleaning Up

1. **Stop All Services**:
   ```bash
   docker-compose down
   ```

2. **Remove Unused Resources**:
   ```bash
   docker system prune -a
   ```
