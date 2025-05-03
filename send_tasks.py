from dotenv import load_dotenv

from celery_worker.tasks import process_match_event

load_dotenv()

if __name__ == "__main__":
    # This is just for testing purposes
    event = {
        "fixture_id": "abc123",
        "timestamp": "2025-05-03T14:00:00Z",
        "score": {"home": 2, "away": 1},
    }
    process_match_event.delay(event)
    print("📨 Task sent!")
