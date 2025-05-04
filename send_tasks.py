import json
import os
import re

from celery import Celery
from dotenv import load_dotenv

load_dotenv()
app = Celery("producer", broker=os.getenv("BROKER_URL_LOCALHOST"))

# Path to your test data log file
TEST_DATA_FILE = "test_data"

# Regex to extract the JSON from each line
JSON_PATTERN = re.compile(r"Parsed message: (?P<json>{.*})")


def produce_tasks_from_file(filepath: str):
    with open(filepath, encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            match = JSON_PATTERN.search(line)
            if not match:
                print(f"❌ Skipping line {line_number}: {line}")
                continue

            try:
                parsed = json.loads(match.group("json"))
                match_details = (
                    parsed.get("content", {}).get("liveData", {}).get("matchDetails")
                )
                if not match_details:
                    print(f"⚠️ No 'matchDetails' found in line {line_number}")
                    continue

                # Send task to Celery
                app.send_task(
                    "process_match_event", args=[{"matchDetails": match_details}]
                )
                print(
                    f"📨 Sent task for match ID {match_details.get('id')} (line {line_number})"
                )

            except json.JSONDecodeError as e:
                print(f"❌ JSON error on line {line_number}: {e}")


if __name__ == "__main__":
    # This is just for testing purposes
    event = {
        "fixture_id": "abc123",
        "timestamp": "2025-05-03T14:00:00Z",
        "score": {"home": 2, "away": 1},
    }
    # app.send_task("process_match_event", args=[event])
    # print("📨 Task sent!")
    produce_tasks_from_file(TEST_DATA_FILE)
