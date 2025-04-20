import os
import time
from bs4 import BeautifulSoup
from pathlib import Path
from playwright.sync_api import sync_playwright


def update_lineup_html(html_path, output_path, numbers):
    with open(html_path, "r") as file:
        soup = BeautifulSoup(file, "html.parser")

    text_elements = soup.find_all("div", class_="xx")

    for i, el in enumerate(text_elements):
        if i < len(numbers):
            el.string = str(numbers[i])

    with open(output_path, "w") as file:
        file.write(str(soup))


def generate_lineup_from_html(output_filename="lineup.png"):
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_image_path = output_dir / output_filename
    update_lineup_html("original-html/field.html", "original-html/lineup_ready.html", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file:///mnt/Documents/Documents/Desarrollos/Clientes/FootballMad/images-html/original-html/lineup_ready.html")
        page.set_viewport_size({"width": 600, "height": 900})
        page.screenshot(path=str(output_image_path))
        browser.close()

    print(f"✅ Screenshot saved to {output_image_path}")

if __name__ == "__main__":
    start_time = time.time()
    generate_lineup_from_html()
    end_time = time.time()
    print(f"⏱️ Finished in {end_time - start_time:.2f} seconds")

    # Uncomment the following line to run the function with a custom filename
    # generate_lineup_from_html("custom_lineup.png")