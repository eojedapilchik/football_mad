import json
import os
import time

from celery import Celery
from dotenv import load_dotenv

from directus.directus_service import DirectusService
from google.sheet_service import GoogleSheetService

load_dotenv()

broker_url = os.getenv("BROKER_URL")
sheet_id = os.getenv("GOOGLE_SHEET_ID")

if not broker_url:
    raise RuntimeError("Missing BROKER_URL in .env file")

app = Celery(
    "process_match_event",
    broker=broker_url,  # RabbitMQ broker
)

directus = DirectusService()
gsheet_service = GoogleSheetService(sheet_id)


@app.task(name="process_match_event")
def process_match_event(event):
    print(f"✅ Received event: {json.dumps(event, indent=2)}")
    if not event or len(event) == 0:
        print("❌ No event data provided")
        return {"status": "error", "message": "No event data provided"}

    results = []
    match_details = event.get("matchDetails")
    if match_details is None:
        print("❌ No match details found in event")
        return {"status": "error",
                "message": "No match details found in event"}
    fixture_id = match_details.get("id")
    for e in match_details.get("event", []):
        print(f"🔍 Processing matchDetails: {json.dumps(e, indent=2)}")
        opta_id = e.get("id")
        type_id = e.get("typeId")
        contestant_id = e.get("contestantId")
        player_id = e.get("playerId")
        current_time = e.get("timeStamp")
        x = e.get("x")
        y = e.get("y")
        period = e.get("periodId")
        time_min = e.get("timeMin")
        time_sec = e.get("timeSec")
        qualifiers = []
        for qualifier in e.get("qualifier", []):
            if qualifier.get("qualifierId") is not None:
                print(
                    f"🔍 Processing qualifier: {json.dumps(qualifier, indent=2)}")
                qualifier_id = qualifier.get("qualifierId")
                value = qualifier.get("value")
                qualifier = directus.get_event_qualifier_by_opta_id(
                    qualifier_id)
                qualifier_name = qualifier.get(
                    "name") if qualifier else "Unknown"
                qualifiers.append(f"{qualifier_name} ({value})")

        event_type = directus.get_event_type_by_opta_id(type_id)
        if event_type is None:
            print(f"❌ Event type not found for ID: {type_id}")
        team = directus.get_team_by_opta_id(contestant_id)
        if team is None:
            print(f"❌ Team not found for ID: {contestant_id}")
        player = directus.get_player_by_opta_id(player_id)
        print(f"🔍 Player: {json.dumps(player, indent=2)}")

        results.append(
            {
                "opta_id": opta_id,
                "type_id": type_id,
                "contestant_id": contestant_id,
                "qualifiers": ", ".join(qualifiers),
                "team": team,
                "player": player,
            }
        )

        # Append row to Google Sheet
        row = [
            current_time,
            player.get("name") if player else "Unknown",
            team.get("name") if team else "Unknown",
            event_type.get("name") if event_type else "Unknown",
            ", ".join(qualifiers),
            opta_id,
            fixture_id,
            period,
            time_min,
            time_sec,
            x,
            y,
        ]
        gsheet_service.append_row(row, tab_name="game events")
        print(f"✅ Row appended: {row}")
        time.sleep(3)  # Sleep to avoid hitting Google Sheets API rate limits

    return {"status": "ok", "processed": len(results), "details": results}
