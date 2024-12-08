#!/bin/bash

# Run the batch processor once
python batch_processor.py

# Keep container running
tail -f /dev/null
