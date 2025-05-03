import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()
app = Celery("producer", broker=os.getenv("BROKER_URL_LOCALHOST"))


if __name__ == "__main__":
    # This is just for testing purposes
    event = {
        "fixture_id": "abc123",
        "timestamp": "2025-05-03T14:00:00Z",
        "score": {"home": 2, "away": 1},
    }
    app.send_task("process_match_event", args=[event])
    print("📨 Task sent!")
