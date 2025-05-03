import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

broker_url = os.getenv("BROKER_CREDENTIALS")

if not broker_url:
    raise RuntimeError("Missing BROKER_CREDENTIALS in .env file")

app = Celery(
    "process_match_event",
    broker=broker_url,  # RabbitMQ broker
)


@app.task(name="process_match_event")
def process_match_event(event):
    print(f"✅ Received event: {event}")
    # Here you could insert into MongoDB or process the data
