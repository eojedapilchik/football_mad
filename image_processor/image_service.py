import os
import re
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from image_processor.utils import (
    generate_css_fixture_and_game_status,
    generate_css_goal_and_cards,
)

load_dotenv()


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


def generate_goal_html(data):
    css = generate_css_goal_and_cards(data["team_goal_template_url"])
    html = f"""
        <div class="overlay">
            <img class="player-image" src="{data["player_image_url"]}" alt="{data["player_name"]}">
            <div class="player-name">{data["player_name"]}</div>
        </div>
    """
    return {"html": html, "css": css}


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name)


def save_html_to_disk(html: str, filename: str) -> str:
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ HTML saved to {output_path}")
    return str(output_path)


def generate_cards_html(data: dict[str, Any]) -> str:
    save_to_disk = os.getenv("SAVE_HTML_TO_DISK", "false").lower() == "true"
    red_url = os.getenv("RED_CARD_TEMPLATE_URL", "")
    yellow_url = os.getenv("YELLOW_CARD_TEMPLATE_URL", "")
    player_image_template = os.getenv("PLAYER_IMAGE_URL", "")

    if not red_url or not yellow_url:
        raise ValueError(
            "Card template URLs (RED_CARD_TEMPLATE_URL, YELLOW_CARD_TEMPLATE_URL) must be set."
        )
    if not player_image_template:
        raise ValueError("PLAYER_IMAGE_URL must be set.")

    card_color = data.get("card_color")
    if card_color not in ("red", "yellow"):
        raise ValueError("Invalid card_color. Expected 'red' or 'yellow'.")

    template_url = red_url if card_color == "red" else yellow_url
    css = generate_css_goal_and_cards(template_url)

    player_photo_url = data.get("player_photo_url", "")
    player_name = data.get("player_name", "Unknown")

    player_image_url = player_image_template.replace("{{22.photo}}",
                                                     player_photo_url)

    html_body = f"""
        <div class="overlay">
            <img class="player-image" src="{player_image_url}" alt="{player_name}">
            <div class="player-name">{player_name}</div>
        </div>
    """

    full_html = f"""
        <html>
        <head>
            <style>{css}</style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
    """
    print(f"✅ HTML generated for {card_color} card and player: {player_name}")
    if save_to_disk:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        safe_name = sanitize_filename(player_name)
        filename = f"{safe_name}_{card_color}_card_{timestamp}.html"
        html_path, _ = prepare_html_output(full_html, filename,
                                           use_temp_html=False)
        print(f"✅ HTML saved to {html_path}")

    return full_html


def generate_game_status_html(data):
    home_team = data["home_team"]
    away_team = data["away_team"]
    status = data["status"]
    score = data["score"].strip("[]").split("-")
    home_score, away_score = score[0], score[1]
    goal_scorers = process_goal_events(data["events"])

    html = f"""
    <div class="container">
        <p>Home Team: {home_team["name"]}</p>
        <p>Home Team Logo: {home_team["logo"][:20]}...</p>
        <p>Away Team: {away_team["name"]}</p>
        <p>Away Team Logo: {away_team["logo"][:20]}...</p>
        <p>Status: {status}</p>
        <p>Home Team Score: {home_score}</p>
        <p>Away Team Score: {away_score}</p>
        <div>
            <h3>Home team scorers:</h3>
            {''.join([f"<p>{scorer['player_name']}: {scorer['minute']}'</p>" for scorer in goal_scorers['home_team_scorers']])}
        </div>
        <div>
            <h3>Away team scorers:</h3>
            {''.join([f"<p>{scorer['player_name']}: {scorer['minute']}'</p>" for scorer in goal_scorers['away_team_scorers']])}
        </div>
    </div>
    """
    return {"html": html, "css": ""}


def format_date_and_time(date_str: str, time_str: str):
    day, month, year = date_str.split(".")
    date_iso = f"{year}-{month.zfill(2)}-{day.zfill(2)}T{time_str}Z"
    utc_dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
    london_dt = utc_dt.astimezone(ZoneInfo("Europe/London"))

    formatted_date = london_dt.strftime("%a %d %b").upper()
    formatted_time = (
        london_dt.strftime("%H:%M %Z").replace("BST", "BST").replace("GMT",
                                                                     "GMT")
    )

    return formatted_date, formatted_time


def generate_half_and_full_time_html(data):
    home_team = data["home_team"]
    away_team = data["away_team"]
    formatted_date, formatted_time = format_date_and_time(data["date"],
                                                          data["time"])
    css = generate_css_fixture_and_game_status(data["template_url"])

    html = f"""
        <div class="overlay">
            <div class="hashtags">
                <span class="hashtag"><span class="hashtag-symbol">#</span>{home_team["hashtag"]}{away_team["hashtag"]}</span>
                <span class="hashtag"><span class="hashtag-symbol">#</span>{data["league_hashtag"]}</span>
            </div>
            <div class="team-container home">
                <div class="team-result">{home_team["goals"]}</div>
                <div class="team-name">{home_team["name"]}</div>
            </div>
            <div class="team-container away">
                <div class="team-result">{away_team["goals"]}</div>
                <div class="team-name">{away_team["name"]}</div>
            </div>
            <div class="date">{formatted_date}</div>
            <div class="time">{formatted_time}</div>
            <div class="match-stadium">{data["stadium_name"]}</div>
        </div>
    """
    return {"html": html, "css": css, "formattedTime": formatted_time}


def prepare_html_output(
        html: str, filename: str, use_temp_html: bool = True
) -> tuple[str, str]:
    """
    Prepares HTML and image output paths.

    :param html: HTML content to write
    :param filename: Desired output image filename (e.g., "rendered.png")
    :param use_temp_html: If True, saves HTML to a temporary file; otherwise, saves it under IMAGE_OUTPUT_DIR
    :return: Tuple (html_path, image_output_path)
    """
    output_dir = os.getenv("IMAGE_OUTPUT_DIR")
    if not output_dir:
        raise ValueError(
            "❌ IMAGE_OUTPUT_DIR not set in environment variables.")

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    if use_temp_html:
        # Save to a temporary HTML file (for tools like Playwright)
        with tempfile.NamedTemporaryFile(
                suffix=".html", delete=False, mode="w", encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(html)
            html_path = tmp_file.name
    else:
        # Save HTML to a named file in the output directory
        html_path = output_dir_path / filename.replace(".png", ".html")
        html_path.write_text(html, encoding="utf-8")

    image_path = output_dir_path / filename
    return str(html_path), str(image_path)


def generate_fixture_html(data):
    home_team = data["home_team"]
    away_team = data["away_team"]
    formatted_date, formatted_time = format_date_and_time(data["date"],
                                                          data["time"])
    css = generate_css_fixture_and_game_status(data["template_url"])

    html = f"""
        <div class="overlay">
            <div class="hashtags">
                <span class="hashtag"><span class="hashtag-symbol">#</span>{home_team["hashtag"]}{away_team["hashtag"]}</span>
                <span class="hashtag"><span class="hashtag-symbol">#</span>{data["league_hashtag"]}</span>
            </div>
            <div class="team-container home">
                <img class="team-logo" src="{home_team["logo"]}" alt="{home_team["name"]} logo">
                <div class="team-name">{home_team["name"]}</div>
            </div>
            <div class="team-container away">
                <img class="team-logo" src="{away_team["logo"]}" alt="{away_team["name"]} logo">
                <div class="team-name">{away_team["name"]}</div>
            </div>
            <div class="date">{formatted_date}</div>
            <div class="time">{formatted_time}</div>
            <div class="match-stadium">{data["stadium_name"]}</div>
        </div>
    """
    return {"html": html, "css": css, "formattedTime": formatted_time}


def render_html_to_image(
        html: str,
        output_filename: str = "rendered.png",
        width: int = 1920,
        height: int = 1920,
) -> str:
    """Render HTML using Playwright."""
    print("🖼️ Rendering HTML to image using Playwright...")
    html_path, output_image_path = prepare_html_output(html, output_filename)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{html_path}")
        page.set_viewport_size({"width": width, "height": height})
        page.screenshot(path=str(output_image_path))
        browser.close()

    print(f"✅ Screenshot saved to {output_image_path}")
    return str(output_image_path)


def render_html_to_image_wkhtml(
        html: str, output_filename: str = "rendered.png"
) -> str:
    """Render HTML using wkhtmltoimage."""
    print("🖼️ Rendering HTML to image with wkhtmltoimage...")
    html_path, output_image_path = prepare_html_output(html, output_filename)

    command = ["wkhtmltoimage", html_path, str(output_image_path)]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"wkhtmltoimage failed:\n{result.stderr}")

    print(f"✅ Screenshot saved to {output_image_path}")
    return str(output_image_path)
