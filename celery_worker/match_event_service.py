import json
import os
import random
import time
from datetime import datetime

from directus.directus_service import DirectusService
from google.sheet_service import GoogleSheetService
from image_processor.image_service import generate_cards_image, generate_goal_image
from opta.opta_service import PerformFeedsService
from utils.feature_flags import flags
from utils.logger import setup_logger

logger = setup_logger("match_event_service")

YELLOW_CARD_QUALIFIER_ID = 31
RED_CARD_QUALIFIER_ID = 33
CARD_EVENT_TYPE_ID = 17
GOAL_EVENT_TYPE_ID = 16
LIVESCORE_FEED_NAME = "liveScore"


def save_livescore_event(event, fixture_id):
    os.makedirs("logs/livescore", exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"logs/livescore/{fixture_id}_{date_str}.json"

    # Load existing data if file exists
    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as f:
            try:
                events = json.load(f)
                if not isinstance(events, list):
                    events = []
            except json.JSONDecodeError:
                events = []
    else:
        events = []

    # Append the new event
    events.append(event)

    # Write the updated list back to the file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    logger.info(f"📁 Appended LiveScore event to {filename}")


class MatchEventService:
    def __init__(self, sheet_id):
        self.directus = DirectusService()
        self.gsheet_service = GoogleSheetService(sheet_id)
        self.opta_service = PerformFeedsService()
        self.handler_map = {
            YELLOW_CARD_QUALIFIER_ID: self._handle_cards,
            RED_CARD_QUALIFIER_ID: self._handle_cards,
        }

    @staticmethod
    def _handle_cards(qualifier_id, value, event_data) -> None:
        player = event_data.get("player")
        if not player:
            logger.error("❌ No player data found in event data for card event")
            return
        if qualifier_id == YELLOW_CARD_QUALIFIER_ID:
            color = "yellow"
        elif qualifier_id == RED_CARD_QUALIFIER_ID:
            color = "red"
        else:
            logger.warning(f"⚠️ Unknown card qualifierId: {qualifier_id} value: {value}")
            return
        logger.info(f" -> Handling {color} card: {json.dumps(qualifier_id, indent=2)}")
        generate_cards_image(
            {
                "card_color": color,
                "player_photo_url": player.get("photo"),
                "player_name": player.get("name"),
            }
        )

    def _handle_goal(self, event_data) -> None:
        logger.info("⚽️ Processing goal event")
        player = event_data.get("player")
        team = event_data.get("team")
        if not player:
            logger.error("❌ No player data found in event data for goal event")
            return
        fixture_id = event_data.get("fixture_id")
        if not fixture_id:
            logger.error("❌ No fixture ID found in event data for goal event")
            return
        current_data = self.opta_service.get_match_stats(fixture_id)
        if not current_data:
            logger.error("❌ No current data found for fixture ID")
            return
        scores = (
            current_data.get("liveData", {}).get("matchDetails", {}).get("scores", {})
        )
        logger.info(
            f"🟩 Current data for fixture ID {fixture_id}: "
            f"{json.dumps(scores, indent=2)}"
        )
        generate_goal_image(
            {
                "player_name": player.get("name"),
                "player_photo_url": player.get("photo"),
                "team_goal_template_url": team.get("goal_template"),
            }
        )

    def process_event(self, event):
        if not event or not event.get("matchDetails"):
            logger.warning("❌ No valid event data provided")
            return {"status": "error", "message": "Invalid or empty event data"}
        if flags.debug_mode:
            logger.info(f"✅ Received event: {json.dumps(event, indent=2)}")
        match_details = event["matchDetails"]
        fixture_id = match_details.get("id")
        raw_events = match_details.get("event")
        feed_name = match_details.get("feedName")

        if not raw_events:
            logger.warning("⚠️ No events found in matchDetails")
            return {"status": "ok", "processed": 0, "details": []}

        if flags.save_livescore_events and feed_name == LIVESCORE_FEED_NAME:
            logger.info("📁 Saving LiveScore event data")
            save_livescore_event(event, fixture_id)

        # Ensure we have a list to iterate
        if isinstance(raw_events, dict):
            raw_events = [raw_events]

        results = [
            self._process_single_event(e, fixture_id, feed_name)
            for e in raw_events
            if e
        ]

        return {
            "status": "ok",
            "processed": len([r for r in results if r]),
            "details": [r for r in results if r],
        }

    @staticmethod
    def _extract_event_metadata(e: dict) -> dict:
        return {
            "current_time": e.get("timeStamp"),
            "x": e.get("x"),
            "y": e.get("y"),
            "period": e.get("periodId"),
            "time_min": e.get("timeMin"),
            "time_sec": e.get("timeSec"),
            "time_stamp": e.get("timeStamp"),
        }

    def _process_single_event(self, e, fixture_id, feed_name):
        if not isinstance(e, dict):
            logger.error(f"❌ Invalid event data format {e}")
            return None

        opta_id = e.get("id")
        logger.info(f"⚙️ Processing event: {opta_id} feed: {feed_name}")

        type_id = e.get("typeId")
        contestant_id = e.get("contestantId")
        player_id = e.get("playerId")

        event_type = self.directus.get_event_type_by_opta_id(type_id)
        team = self.directus.get_team_by_opta_id(contestant_id)
        player = self.directus.get_player_by_opta_id(player_id)

        event_metadata = self._extract_event_metadata(e)
        event_data = {
            "team": team,
            "player": player,
            "opta_id": opta_id,
            "type_id": type_id,
            "contestant_id": contestant_id,
            "fixture_id": fixture_id,
            "feed_name": feed_name,
            **event_metadata,
        }

        if type_id == GOAL_EVENT_TYPE_ID and feed_name != LIVESCORE_FEED_NAME:
            self._handle_goal(event_data)

        qualifiers_str = self._process_qualifiers(e.get("qualifier", []), event_data)

        row = [
            event_metadata["time_stamp"],
            player.get("name") if player else "Unknown",
            team.get("name") if team else "Unknown",
            event_type.get("name") if event_type else "Unknown",
            qualifiers_str,
            opta_id,
            fixture_id,
            feed_name,
            event_metadata["period"],
            event_metadata["time_min"],
            event_metadata["time_sec"],
            event_metadata["x"],
            event_metadata["y"],
        ]

        if flags.save_to_gsheet:
            self.gsheet_service.append_row(row, tab_name="game events")
            print(f"✅ Row appended: {row}")
        time.sleep(random.uniform(4.5, 7.5))  # To respect Google Sheets rate limits

        return event_data

    def _process_qualifiers(self, qualifiers: list, event_data: dict):
        type_id = event_data.get("type_id")
        feed_name = event_data.get("feed_name")
        parts = []
        for qualifier in qualifiers:
            qualifier_id = qualifier.get("qualifierId")
            value = qualifier.get("value")
            if qualifier_id is None:
                continue

            logger.info(f"🔍 Processing qualifier: {qualifier_id}")
            handler = self.handler_map.get(qualifier_id)
            if (
                handler
                and type_id == CARD_EVENT_TYPE_ID
                and feed_name != LIVESCORE_FEED_NAME
            ):
                handler(qualifier_id, value, event_data)

            qualifier_info = self.directus.get_event_qualifier_by_opta_id(qualifier_id)
            name = qualifier_info.get("name") if qualifier_info else "Unknown"
            parts.append(f"{name} ({value})")
        return ", ".join(parts)
