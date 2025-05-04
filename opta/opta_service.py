import hashlib
import os
import time
from datetime import datetime

import requests
from dateutil.parser import parse as parse_date
from dotenv import load_dotenv

load_dotenv()

OUTLET = os.getenv("OUTLET")
SECRET = os.getenv("SECRET")
TOURNAMENT_ID = os.getenv("TOURNAMENT_ID", "2kwbbcootiqqgmrzs6o5inle5")


class PerformFeedsService:
    BASE_API = "https://api.performfeeds.com/soccerdata"
    OAUTH_API = "https://oauth.performgroup.com/oauth/token"

    def __init__(self, outlet: str = None, secret: str = None):
        self.outlet = outlet or OUTLET
        self.secret = secret or SECRET
        self.access_token = self._authenticate()

    def _generate_unique_hash(self, timestamp: int) -> str:
        key = str.encode(self.outlet + str(timestamp) + self.secret)
        return hashlib.sha512(key).hexdigest()

    def _authenticate(self) -> str:
        timestamp = int(round(time.time() * 1000))
        unique_hash = self._generate_unique_hash(timestamp)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {unique_hash}",
            "Timestamp": str(timestamp),
        }

        body = {
            "grant_type": "client_credentials",
            "scope": "b2b-feeds-auth",
        }

        response = requests.post(
            f"{self.OAUTH_API}/{self.outlet}?_fmt=json&_rt=b",
            data=body,
            headers=headers,
            timeout=90,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_tournament_calendar_id(self, comp_id: str = None) -> str:
        if not comp_id:
            comp_id = TOURNAMENT_ID
        url = (
            f"{self.BASE_API}/tournamentcalendar/{self.outlet}/active"
            f"?_rt=b&_fmt=json&comp={comp_id}"
        )
        response = requests.get(url, headers=self._get_headers(), timeout=90)
        response.raise_for_status()
        data = response.json()

        try:
            return data["competition"][0]["tournamentCalendar"][0]["id"]
        except (KeyError, IndexError):
            raise ValueError("Could not extract tournamentCalendar ID")

    def get_today_fixture_uuids(self, tournament_id: str) -> list:
        url = (
            f"{self.BASE_API}/tournamentschedule/{self.outlet}"
            f"?tmcl={tournament_id}&_fmt=json&_rt=b"
        )
        response = requests.get(url, headers=self._get_headers(), timeout=90)
        response.raise_for_status()
        data = response.json()

        fixture_uuids = []
        for match_date in data.get("matchDate", []):
            date_str = match_date["date"]
            if date_str.endswith("Z"):
                date_str = date_str[:-1]
            if parse_date(date_str).date() == datetime.today().date():
                for match in match_date.get("match", []):
                    fixture_uuids.append(match["id"])

        return fixture_uuids

    def get_match_stats(self, fixture_uuid: str) -> dict:
        url = (
            f"{self.BASE_API}/matchstats/{self.outlet}/{fixture_uuid}"
            "?_rt=b&_fmt=json"
        )
        response = requests.get(url, headers=self._get_headers(), timeout=90)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    service = PerformFeedsService()
    _tournament_id = service.get_tournament_calendar_id()
    print(f"Tournament Calendar ID: {_tournament_id}")

    fixtures = service.get_today_fixture_uuids(_tournament_id)
    print("Today's Fixtures:", fixtures)

    for _fixture_uuid in fixtures:
        stats = service.get_match_stats(_fixture_uuid)
        print(f"Stats for {_fixture_uuid}:", stats)
