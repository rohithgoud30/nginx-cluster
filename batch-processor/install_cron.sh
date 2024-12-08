#!/bin/bash
echo "0 20 * * * docker exec batch-processor python /app/batch_processor.py >> /var/log/batch-processor.log 2>&1" | crontab -
echo "Installed cron job for batch processor"
