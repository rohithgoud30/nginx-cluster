FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV TOP_N=3
ENV CASSANDRA_HOST=cassandra

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Start command
CMD ["./entrypoint.sh"]
