import time
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from image_processor.html_generator_service import HtmlGeneratorService
from image_processor.utils import render_html_to_image, render_html_to_image_wkhtml
from utils.feature_flags import flags
from utils.logger import setup_logger

load_dotenv()

logger = setup_logger("image_service")


def process_goal_events(events):
    result = {"home_team_scorers": [], "away_team_scorers": []}
    for event in events:
        if event.get("@type") == "goal":
            scorer = {
                "player_name": event.get("@player"),
                "minute": event.get("@minute"),
            }
            if event.get("@team") == "localteam":
                result["home_team_scorers"].append(scorer)
            elif event.get("@team") == "visitorteam":
                result["away_team_scorers"].append(scorer)
    return result


def generate_goal_image(data: dict[str, Any]) -> None:
    player = data.get("player_name")
    logger.info(f"Generating goal image for {player}")
    save_to_disk = flags.save_html_to_disk
    html_generator = HtmlGeneratorService()
    html = html_generator.generate_goal_html(data, save_to_disk)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename_1 = f"goal_{player}_{timestamp}_wkhtml.png"
    filename_2 = f"goal_{player}_{timestamp}_playwright.jpg"
    render_html_to_image_wkhtml(html, filename_1)
    render_html_to_image(html, filename_2)


def generate_cards_image(data: dict[str, Any]) -> None:
    player = data.get("player_name")
    logger.info(f"Generating cards image for {player}")
    save_to_disk = flags.save_html_to_disk
    html_generator = HtmlGeneratorService()
    html = html_generator.generate_cards_html(data, save_to_disk)
    color = data.get("card_color")
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename_1 = f"card_{color}_{player}_{timestamp}_wkhtml.png"
    filename_2 = f"card_{color}_{player}_{timestamp}_playwright.png"
    render_html_to_image_wkhtml(html, filename_1)
    render_html_to_image(html, filename_2)


# def generate_game_status_html(data):
#     home_team = data["home_team"]
#     away_team = data["away_team"]
#     status = data["status"]
#     score = data["score"].strip("[]").split("-")
#     home_score, away_score = score[0], score[1]
#     goal_scorers = process_goal_events(data["events"])
#
#     html = f"""
#     <div class="container">
#         <p>Home Team: {home_team["name"]}</p>
#         <p>Home Team Logo: {home_team["logo"][:20]}...</p>
#         <p>Away Team: {away_team["name"]}</p>
#         <p>Away Team Logo: {away_team["logo"][:20]}...</p>
#         <p>Status: {status}</p>
#         <p>Home Team Score: {home_score}</p>
#         <p>Away Team Score: {away_score}</p>
#         <div>
#             <h3>Home team scorers:</h3>
#             {''.join([f"<p>{scorer['player_name']}: {scorer['minute']}'</p>"
#             for scorer in goal_scorers['home_team_scorers']])}
#         </div>
#         <div>
#             <h3>Away team scorers:</h3>
#             {''.join([f"<p>{scorer['player_name']}: {scorer['minute']}'</p>"
#             for scorer in goal_scorers['away_team_scorers']])}
#         </div>
#     </div>
#     """
#     return {"html": html, "css": ""}


def format_date_and_time(date_str: str, time_str: str):
    day, month, year = date_str.split(".")
    date_iso = f"{year}-{month.zfill(2)}-{day.zfill(2)}T{time_str}Z"
    utc_dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
    london_dt = utc_dt.astimezone(ZoneInfo("Europe/London"))

    formatted_date = london_dt.strftime("%a %d %b").upper()
    formatted_time = (
        london_dt.strftime("%H:%M %Z").replace("BST", "BST").replace("GMT", "GMT")
    )

    return formatted_date, formatted_time


# def generate_half_and_full_time_html(data):
#     home_team = data["home_team"]
#     away_team = data["away_team"]
#     formatted_date, formatted_time = format_date_and_time(data["date"],
#                                                           data["time"])
#     css = generate_css_fixture_and_game_status(data["template_url"])
#
#     html = f"""
#         <div class="overlay">
#             <div class="hashtags">
#                 <span class="hashtag"><span class="hashtag-symbol">#</span>
#                 {home_team["hashtag"]}{away_team["hashtag"]}</span>
#                 <span class="hashtag"><span class="hashtag-symbol">#</span>
#                 {data["league_hashtag"]}</span>
#             </div>
#             <div class="team-container home">
#                 <div class="team-result">{home_team["goals"]}</div>
#                 <div class="team-name">{home_team["name"]}</div>
#             </div>
#             <div class="team-container away">
#                 <div class="team-result">{away_team["goals"]}</div>
#                 <div class="team-name">{away_team["name"]}</div>
#             </div>
#             <div class="date">{formatted_date}</div>
#             <div class="time">{formatted_time}</div>
#             <div class="match-stadium">{data["stadium_name"]}</div>
#         </div>
#     """
#     return {"html": html, "css": css, "formattedTime": formatted_time}
#
#
#
#
# def generate_fixture_html(data):
#     home_team = data["home_team"]
#     away_team = data["away_team"]
#     formatted_date, formatted_time = format_date_and_time(data["date"],
#                                                           data["time"])
#     css = generate_css_fixture_and_game_status(data["template_url"])
#
#     html = f"""
#         <div class="overlay">
#             <div class="hashtags">
#                 <span class="hashtag"><span class="hashtag-symbol">#</span>
#                 {home_team["hashtag"]}{away_team["hashtag"]}</span>
#                 <span class="hashtag"><span class="hashtag-symbol">#</span>
#                 {data["league_hashtag"]}</span>
#             </div>
#             <div class="team-container home">
#                 <img class="team-logo" src="{home_team["logo"]}"
#                 alt="{home_team["name"]} logo">
#                 <div class="team-name">{home_team["name"]}</div>
#             </div>
#             <div class="team-container away">
#                 <img class="team-logo" src="{away_team["logo"]}"
#                 alt="{away_team["name"]} logo">
#                 <div class="team-name">{away_team["name"]}</div>
#             </div>
#             <div class="date">{formatted_date}</div>
#             <div class="time">{formatted_time}</div>
#             <div class="match-stadium">{data["stadium_name"]}</div>
#         </div>
#     """
#     return {"html": html, "css": css, "formattedTime": formatted_time}
