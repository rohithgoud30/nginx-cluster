FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY log-forwarder.py .

CMD ["python", "-u", "log-forwarder.py"]

