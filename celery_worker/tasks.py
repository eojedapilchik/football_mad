import json
import os

from celery import Celery
from dotenv import load_dotenv

from celery_worker.match_event_service import MatchEventService
from utils.logger import setup_logger

logger = setup_logger("match_event_service")

load_dotenv()

broker_url = os.getenv("BROKER_URL")
sheet_id = os.getenv("GOOGLE_SHEET_ID")

if not broker_url:
    raise RuntimeError("Missing BROKER_URL in .env file")

app = Celery(
    "process_match_event",
    broker=broker_url,  # RabbitMQ broker
)

match_service = MatchEventService(sheet_id)


@app.task(name="process_match_event")
def process_match_event(event):
    logger.info(f"✅ Received event: {json.dumps(event, indent=2)}")
    return match_service.process_event(event)
