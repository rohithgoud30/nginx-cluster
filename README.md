````markdown
# NGINX Cluster Project

This project implements a scalable NGINX cluster with Kafka, Cassandra, and real-time and batch log processing capabilities. The project supports containerized deployment using Docker Compose.

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
````

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

1. **Copy the Schema File into the Cassandra Container:**

   ```bash
   docker cp cassandra-init/init.cql cassandra:/tmp/init.cql
   ```

2. **Access the Cassandra Container:**

   ```bash
   docker exec -it cassandra bash
   ```

3. **Run the Schema Script Using `cqlsh`:**

   ```bash
   cqlsh
   SOURCE '/tmp/init.cql';
   ```

4. **Verify the Schema:**
   ```bash
   DESCRIBE KEYSPACE nginx_logs;
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
   Access Cassandra to query the results:
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

2. **Remove Unused Resources:**
   ```bash
   docker system prune -a
   ```

---

## Additional Notes

- Ensure Docker and Docker Compose are installed and running before starting the project.
- For troubleshooting Kafka, Cassandra, or NGINX issues, check the respective container logs using `docker logs <container_name>`.
  markdown```
