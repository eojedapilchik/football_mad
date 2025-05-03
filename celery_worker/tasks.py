import os

from celery import Celery
from dotenv import load_dotenv

from directus.directus_service import DirectusService

load_dotenv()

broker_url = os.getenv("BROKER_URL")

if not broker_url:
    raise RuntimeError("Missing BROKER_URL in .env file")

app = Celery(
    "process_match_event",
    broker=broker_url,  # RabbitMQ broker
)

directus = DirectusService()


@app.task(name="process_match_event")
def process_match_event(event):
    print(f"✅ Received event: {event}")
    if not event or len(event) == 0:
        print("❌ No event data provided")
        return {"status": "error", "message": "No event data provided"}

    results = []
    print("🔍 Processing match event...")
    for e in event.get("matchDetails", {}).get("event", []):
        opta_id = e.get("id")
        if opta_id is None:
            continue

        qualifier = directus.get_event_qualifier_by_opta_id(opta_id)
        qualifier_name = qualifier.get("name") if qualifier else "Unknown"
        print(f"🔍 Qualifier for opta_id {opta_id}: {qualifier_name}")
        results.append({"opta_id": opta_id, "qualifier_name": qualifier_name})

    return {"status": "ok", "processed": len(results), "details": results}
