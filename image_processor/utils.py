# utils.py
def generate_css_goal_and_cards(template_url: str) -> str:
    return f"""
    .overlay {{
        position: relative;
        width: 1920px;
        height: 1920px;
        font-family: 'Proxima Nova', sans-serif;
        color: white;
        background-image: url('{template_url}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        text-transform: uppercase;
        overflow: hidden;
    }}

    .player-image {{
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 1750px;
        height: 1750px;
        object-fit: contain;
        object-position: bottom center;
    }}
    .player-name {{
        position: absolute;
        bottom: 150px;
        right: 30px;
        transform: rotate(-90deg) translateX(100%);
        transform-origin: bottom right;
        font-size: 40px;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }}
    """


def generate_css_fixture_and_game_status(template_url: str) -> str:
    return f"""
    body, html {{
        margin: 0;
        padding: 0;
    }}

    .overlay {{
        position: relative;
        width: 1920px;
        height: 1920px;
        font-family: 'Proxima Nova', sans-serif;
        color: white;
        background-image: url('{template_url}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        text-transform: uppercase;
    }}

    .hashtags {{
        position: absolute;
        top: 630px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 46px;
        font-weight: 700;
        color: white;
        white-space: nowrap;
        letter-spacing: 2px;
    }}

    .hashtag-symbol {{
        color: #0b52a7;
        letter-spacing: 10px;
    }}

    .hashtag {{
        display: inline-block;
    }}

    .hashtag + .hashtag {{
        margin-left: 20px;
    }}

    .team-container {{
        position: absolute;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 350px;
        height: 700px;
        top: 710px;
    }}

    .team-container.home {{
        left: 452px;
    }}

    .team-container.away {{
        right: 452px;
    }}

    .team-logo {{
        width: 350px;
        height: 350px;
    }}

    .team-name {{
        margin-top: 170px;
        font-size: 60px;
        font-weight: 700;
        white-space: nowrap;
        text-align: center;
        letter-spacing: 10px;
        word-break: normal;
        overflow-wrap: normal;
    }}

    .date {{
        position: absolute;
        bottom: 276px;
        right: 101px;
        font-size: 60px;
        text-align: right;
        font-weight: 700;
        color: #000;
    }}

    .time {{
        position: absolute;
        bottom: 186px;
        right: 101px;
        font-size: 60px;
        text-align: right;
        font-weight: 700;
        color: #000;
    }}

    .match-stadium {{
        position: absolute;
        bottom: 95px;
        right: 102px;
        font-size: 60px;
        text-align: right;
        font-weight: 700;
        color: #0b52a7;
    }}

    .team-result {{
        font-size: 350px;
        font-weight: 700;
        color: #ffd700;
    }}
    """


def sanitize_filename(name: str) -> str:
    import re

    return re.sub(r"[^\w\-]", "_", name)


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
    import os
    import tempfile
    from pathlib import Path

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


def render_html_to_image(
        html: str,
        output_filename: str = "rendered.png",
        width: int = 1920,
        height: int = 1920,
) -> str:
    """Render HTML using Playwright."""

    from playwright.sync_api import sync_playwright

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
    import subprocess

    """Render HTML using wkhtmltoimage."""
    print("🖼️ Rendering HTML to image with wkhtmltoimage...")
    html_path, output_image_path = prepare_html_output(html, output_filename)

    command = ["wkhtmltoimage", html_path, str(output_image_path)]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"wkhtmltoimage failed:\n{result.stderr}")

    print(f"✅ Screenshot saved to {output_image_path}")
    return str(output_image_path)
