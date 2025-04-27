import os
import time
import hashlib
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from dateutil.parser import parse as parse_date

load_dotenv()

OUTLET = os.getenv("OUTLET")
SECRET = os.getenv("SECRET")


def generate_unique_hash(outlet: str, secret: str, timestamp: int) -> str:
    key = str.encode(outlet + str(timestamp) + secret)
    return hashlib.sha512(key).hexdigest()


def get_access_token(outlet: str, secret: str) -> str:
    timestamp = int(round(time.time() * 1000))
    unique_hash = generate_unique_hash(outlet, secret, timestamp)

    post_url = f"https://oauth.performgroup.com/oauth/token/{outlet}?_fmt=json&_rt=b"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {unique_hash}',
        'Timestamp': str(timestamp)
    }

    body = {
        'grant_type': 'client_credentials',
        'scope': 'b2b-feeds-auth'
    }

    response = requests.post(post_url, data=body, headers=headers)
    response.raise_for_status()
    return response.json()['access_token']


def get_tournament_calendar(access_token: str, outlet: str) -> str:
    headers = {'Authorization': f'Bearer {access_token}'}
    url = (
        f"https://api.performfeeds.com/soccerdata/tournamentcalendar/{outlet}/active"
        "?_rt=b&_fmt=json&comp=2kwbbcootiqqgmrzs6o5inle5"
    )

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(data)
    try:
        tournament_id = data["competition"][0]["tournamentCalendar"][0]["id"]
        return tournament_id
    except (KeyError, IndexError):
        raise ValueError("Could not extract tournamentCalendar ID")


def get_fixture_uuids(access_token: str, outlet: str, tournament_id: str) -> list[str]:
    headers = {'Authorization': f'Bearer {access_token}'}
    url = (
        f"https://api.performfeeds.com/soccerdata/tournamentschedule/{outlet}"
        f"?tmcl={tournament_id}&_fmt=json&_rt=b"
    )

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(data)
    fixture_uuids = []
    for match_date in data.get("matchDate", []):
        date_str = match_date["date"]
        if date_str.endswith("Z"):
            date_str = date_str[:-1]

        if parse_date(date_str).date() == datetime.today().date():
            for match in match_date.get("match", []):
                fixture_uuids.append(match["id"])

    return fixture_uuids



def main():
    if not OUTLET or not SECRET:
        raise ValueError("OUTLET and SECRET must be set in environment variables.")

    access_token = get_access_token(OUTLET, SECRET)
    tournament_id = get_tournament_calendar(access_token, OUTLET)
    print(f"Tournament Calendar ID: {tournament_id}")

    fixture_uuids = get_fixture_uuids(access_token, OUTLET, tournament_id)
    print("Today's Fixture UUIDs:", fixture_uuids)


if __name__ == "__main__":
    main()
