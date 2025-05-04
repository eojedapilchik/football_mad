import os
import time
from typing import Any

from image_processor.utils import (
    generate_css_goal_and_cards,
    prepare_html_output,
    sanitize_filename,
)


class HtmlGeneratorService:
    def __init__(self):
        self.player_image_template = os.getenv("PLAYER_IMAGE_URL", "")
        if not self.player_image_template:
            raise ValueError("PLAYER_IMAGE_URL must be set.")

        self.red_card_url = os.getenv("RED_CARD_TEMPLATE_URL", "")
        self.yellow_card_url = os.getenv("YELLOW_CARD_TEMPLATE_URL", "")

    def _get_player_image_url(self, photo_url: str) -> str:
        return self.player_image_template.replace("{{22.photo}}", photo_url)

    @staticmethod
    def _build_html(css: str, image_url: str, player_name: str) -> str:
        html_body = f"""
            <div class="overlay">
                <img class="player-image" src="{image_url}" alt="{player_name}">
                <div class="player-name">{player_name}</div>
            </div>
        """
        return f"""
            <html>
            <head><style>{css}</style></head>
            <body>{html_body}</body>
            </html>
        """

    @staticmethod
    def _save_to_disk(html: str, player_name: str, label: str) -> None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        safe_name = sanitize_filename(player_name)
        filename = f"{safe_name}_{label}_{timestamp}.html"
        html_path, _ = prepare_html_output(html, filename, use_temp_html=False)
        print(f"✅ HTML saved to {html_path}")

    def generate_goal_html(self, data: dict[str, Any],
                           save_to_disk=False) -> str:
        player_name = data.get("player_name", "Unknown")
        player_photo_url = data.get("player_photo_url", "")
        team_goal_template_url = data.get("team_goal_template_url", "")
        goal_template_url = os.getenv("GOAL_TEMPLATE_URL", "")
        if not team_goal_template_url:
            raise ValueError("team_goal_template_url must be set.")
        if not goal_template_url:
            raise ValueError("goal_template_url must be set.")
        if not player_photo_url:
            raise ValueError("player_photo_url must be set.")
        template_url = goal_template_url.replace(
            "{{9.goal_template}}", team_goal_template_url
        )
        css = generate_css_goal_and_cards(template_url)
        player_image_url = self._get_player_image_url(player_photo_url)

        html = self._build_html(css, player_image_url, player_name)
        if save_to_disk:
            self._save_to_disk(html, player_name, "goal")

        return html

    def generate_cards_html(self, data: dict[str, Any],
                            save_to_disk=False) -> str:
        card_color = data.get("card_color")
        if card_color not in ("red", "yellow"):
            raise ValueError("Invalid card_color. Expected 'red' or 'yellow'.")

        if not self.red_card_url or not self.yellow_card_url:
            raise ValueError("Card template URLs must be set.")

        template_url = (
            self.red_card_url if card_color == "red" else self.yellow_card_url
        )
        css = generate_css_goal_and_cards(template_url)

        player_name = data.get("player_name", "Unknown")
        player_photo_url = data.get("player_photo_url", "")
        player_image_url = self._get_player_image_url(player_photo_url)

        html = self._build_html(css, player_image_url, player_name)
        print(
            f"✅ HTML generated for {card_color} card and player: {player_name}")
        if save_to_disk:
            self._save_to_disk(html, player_name, f"{card_color}_card")

        return html
