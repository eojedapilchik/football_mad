import json
import random
import time

from directus.directus_service import DirectusService
from google.sheet_service import GoogleSheetService
from image_processor.image_service import (
    generate_cards_html,
    render_html_to_image,
    render_html_to_image_wkhtml,
)

YELLOW_CARD_QUALIFIER_ID = 31
RED_CARD_QUALIFIER_ID = 33
GOAL_EVENT_TYPE_ID = 16


class MatchEventService:
    def __init__(self, sheet_id):
        self.directus = DirectusService()
        self.gsheet_service = GoogleSheetService(sheet_id)
        self.handler_map = {
            YELLOW_CARD_QUALIFIER_ID: self._handle_cards,
            RED_CARD_QUALIFIER_ID: self._handle_cards,
        }

    @staticmethod
    def _handle_cards(qualifier_id, value, event_data):
        player = event_data.get("player")
        if not player:
            print("❌ No player data found in event data for card event")
            return
        if qualifier_id == YELLOW_CARD_QUALIFIER_ID:
            color = "yellow"
        elif qualifier_id == RED_CARD_QUALIFIER_ID:
            color = "red"
        else:
            print(
                f"⚠️ Unknown card qualifierId: {qualifier_id} value: {value}")
            return
        print(
            f" -> Handling {color} card: {json.dumps(qualifier_id, indent=2)}")
        html = generate_cards_html(
            {
                "card_color": color,
                "player_photo_url": player.get("photo"),
                "player_name": player.get("name"),
            }
        )
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"card_{color}_{player.get('name')}_{timestamp}_wkhtml.png"
        filename2 = f"card_{color}_{player.get('name')}_{timestamp}_playwright.png"
        image = render_html_to_image_wkhtml(html, filename)
        image2 = render_html_to_image(html, filename2)
        # print(f"HTML for red card generated: {html['html']}")
        return html

    def process_event(self, event):
        if not event or not event.get("matchDetails"):
            print("❌ No valid event data provided")
            return {"status": "error",
                    "message": "Invalid or empty event data"}

        match_details = event["matchDetails"]
        fixture_id = match_details.get("id")
        results = []

        for e in match_details.get("event", []):
            result = self._process_single_event(e, fixture_id)
            if result:
                results.append(result)

        return {"status": "ok", "processed": len(results), "details": results}

    def _process_single_event(self, e, fixture_id):
        print(f"🔍 Processing event: {json.dumps(e, indent=2)}")

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

        event_type = self.directus.get_event_type_by_opta_id(type_id)
        team = self.directus.get_team_by_opta_id(contestant_id)
        player = self.directus.get_player_by_opta_id(player_id)
        event_data = {
            "team": team,
            "player": player,
            "opta_id": opta_id,
            "type_id": type_id,
            "contestant_id": contestant_id,
            "current_time": current_time,
            "x": x,
            "y": y,
            "period": period,
            "time_min": time_min,
            "time_sec": time_sec,
        }
        qualifiers_str = self._process_qualifiers(e.get("qualifier", []),
                                                  event_data)

        row = [
            current_time,
            player.get("name") if player else "Unknown",
            team.get("name") if team else "Unknown",
            event_type.get("name") if event_type else "Unknown",
            qualifiers_str,
            opta_id,
            fixture_id,
            "matchEvent",
            period,
            time_min,
            time_sec,
            x,
            y,
        ]

        self.gsheet_service.append_row(row, tab_name="game events")
        print(f"✅ Row appended: {row}")
        time.sleep(
            random.uniform(4.5, 7.5))  # To respect Google Sheets rate limits

        return event_data

    def _process_qualifiers(self, qualifiers: list, event_data: dict):
        parts = []
        for qualifier in qualifiers:
            qualifier_id = qualifier.get("qualifierId")
            value = qualifier.get("value")
            if qualifier_id is not None:
                print(
                    f"🔍 Processing qualifier: {json.dumps(qualifier, indent=2)}")
                handler = self.handler_map.get(qualifier_id)
                if handler:
                    result = handler(qualifier_id, value, event_data)
                resolved = self.directus.get_event_qualifier_by_opta_id(
                    qualifier_id)
                name = resolved.get("name") if resolved else "Unknown"
                parts.append(f"{name} ({value})")
        return ", ".join(parts)
