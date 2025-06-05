FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir pika psycopg2-binary
CMD ["python", "consumer_bd1.py"]