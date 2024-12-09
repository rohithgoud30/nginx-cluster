# NGINX Cluster Project

This project implements a scalable NGINX cluster with Kafka, Cassandra, and real-time and batch processing capabilities. It includes tools for log forwarding, Kafka streaming, and batch processing.

---

**SENG 691 Data Intensive Application Final Project**

---

## Table of Contents

- [NGINX Cluster Project](#nginx-cluster-project)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Folder Structure](#folder-structure)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [How to Run](#how-to-run)
  - [Usage](#usage)
    - [Access NGINX Load Balancer](#access-nginx-load-balancer)
    - [Generate Traffic](#generate-traffic)
    - [Monitor Real-Time Logs](#monitor-real-time-logs)
    - [Trigger Batch Processing](#trigger-batch-processing)
    - [View Logs](#view-logs)
  - [Stopping and Cleaning Up](#stopping-and-cleaning-up)
  - [Configuration](#configuration)
  - [Contributing](#contributing)

---

## Features

- NGINX load balancer with multiple web servers.
- Log forwarding to Kafka for streaming and processing.
- Real-time log aggregation using Kafka streaming.
- Batch processing of logs.
- Integration with Cassandra for data storage.

---

## Folder Structure

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

## Prerequisites

Ensure the following are installed on your system:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)
- Git

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/rohithgoud30/nginx-cluster.git
   cd nginx-cluster
   ```

2. **Build and Start Services:**
   Use Docker Compose to build and start the containers:

   ```bash
   docker-compose up -d --build
   ```

3. **Verify Services:**
   Ensure all services are running:

   ```bash
   docker ps
   ```

---

## How to Run

Follow these steps to run the project:

1. **Start Docker Compose:**
   If not already running, use:

   ```bash
   docker-compose up -d --build
   ```

2. **Verify Running Services:**
   Check that all required containers are running:

   ```bash
   docker ps
   ```

3. **Access the NGINX Load Balancer:**
   Open your browser and navigate to:

   ```plaintext
   http://localhost:8080/
   ```

   You should see one of the following messages:

   - Welcome to Webserver3
   - Welcome to Webserver2
   - Welcome to Webserver1

4. **Simulate Traffic:**
   Run the traffic generator to simulate HTTP requests:

   ```bash
   cd simulation
   python traffic-generator.py
   ```

5. **Monitor Kafka Logs:**
   Check real-time processing logs from the Kafka stream:

   ```bash
   docker exec -it kafka_container_id kafka-console-consumer --bootstrap-server localhost:9092 --topic PRODUCTS
   ```

6. **Trigger Batch Processing Manually (Optional):**

   ```bash
   docker exec -it batch_processor_container_id python batch_processor.py
   ```

7. **Access Logs:**
   Logs are located in the `logs/` directory of the project.

---

## Usage

### Access NGINX Load Balancer

Once the services are running, access the NGINX load balancer in your browser:

```plaintext
http://localhost:8080/
```

You should see one of the following messages:

- Welcome to Webserver3
- Welcome to Webserver2
- Welcome to Webserver1

### Generate Traffic

Simulate HTTP traffic using the traffic generator:

```bash
cd simulation
python traffic-generator.py
```

### Monitor Real-Time Logs

Monitor processing results from the Kafka stream:

```bash
docker exec -it kafka_container_id kafka-console-consumer --bootstrap-server localhost:9092 --topic PRODUCTS
```

### Trigger Batch Processing

The batch processor runs periodically using cron, but you can trigger it manually:

```bash
docker exec -it batch_processor_container_id python batch_processor.py
```

### View Logs

Logs are stored in the `logs/` directory:

```plaintext
logs/
├── access.log
├── batch_processor.log
├── error.log
└── results.jtl
```

---

## Stopping and Cleaning Up

1. **Stop and Remove Services:**
   Stop all running containers and clean up associated resources:

   ```bash
   docker-compose down
   ```

2. **Clean Up Docker Resources:**
   Remove unused images, containers, and networks:

   ```bash
   docker system prune -a
   ```

---

## Configuration

- Modify Kafka and Cassandra settings in their respective directories.
- Update `configs/loadbalancer.conf` for custom NGINX load balancer rules.
- Change cron job schedules in `batch-processor/crontab` as needed.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
