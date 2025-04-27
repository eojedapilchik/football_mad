from __future__ import annotations

import json
import os
import time

from PIL import Image, ImageDraw, ImageFont

from formations import formations

SCALE = 2  # You can change to 3 for even smoother rendering


FONT_PATH = "fonts/ARIALBD.ttf"


def hex_to_rgb(hex_color):
    hex_color = hex_color.strip()
    if not hex_color.startswith("#") or len(hex_color) not in [4, 7]:
        raise ValueError(f"Invalid hex color: {hex_color}")
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def create_field_with_layers(field_color_hex, stripes_path, lines_path):
    # Load both layers at original size
    stripes = Image.open(stripes_path).convert("RGBA")
    lines = Image.open(lines_path).convert("RGBA")

    # Create high-res canvas based on field lines size (do NOT resize overlays)
    canvas_size = (stripes.width * SCALE, stripes.height * SCALE)
    canvas = Image.new("RGBA", canvas_size, hex_to_rgb(field_color_hex) + (255,))
    print(f"✅ Created canvas with size {canvas_size} and color {field_color_hex}")

    # Center original-sized stripes onto canvas
    stripes_scaled = stripes.resize(
        (stripes.width * SCALE, stripes.height * SCALE), Image.LANCZOS
    )
    stripes_offset = (
        (canvas_size[0] - stripes_scaled.width) // 2,
        (canvas_size[1] - stripes_scaled.height) // 2,
    )
    canvas.alpha_composite(stripes_scaled, dest=stripes_offset)
    print(f"✅ Centered striped base at offset {stripes_offset}")

    # Center original-sized field lines onto canvas
    lines_scaled = lines.resize(
        (lines.width * SCALE, lines.height * SCALE), Image.LANCZOS
    )
    lines_offset = (
        (canvas_size[0] - lines_scaled.width) // 2,
        (canvas_size[1] - lines_scaled.height) // 2,
    )
    canvas.alpha_composite(lines_scaled, dest=lines_offset)
    print(f"✅ Centered field lines at offset {lines_offset}")

    return (
        canvas,
        lines_offset,
        lines_scaled.size,
    )  # Return offset and field area for placing players


def get_formation_positions(config):

    positions = config.get("positions", [])
    flip_vertical = config.get("flip_vertical", False)
    if not positions and "formation" in config:
        formation_code = config["formation"]
        if formation_code not in formations:
            raise ValueError(f"Formation '{formation_code}' is not defined.")

        coords = formations[formation_code]
        positions = [
            {"number": i + 1, "x": x, "y": y} for i, (x, y) in enumerate(coords)
        ]
        print(f"✅ Loaded formation '{formation_code}' with {len(coords)} players.")

    if len(positions) < 11:
        raise ValueError(
            "Not enough players defined. A full lineup requires 11 players."
        )

    if flip_vertical:
        for pos in positions:
            pos["y"] = 1.0 - pos["y"]
    return positions


def draw_players(image, config, offset=(0, 0), field_area_size=None):
    draw = ImageDraw.Draw(image)
    font_size = config.get("number_font_size", 32) * SCALE
    font_path = config.get("font_path", FONT_PATH)

    # Try font from config, then Arial Bold, then fallback
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)  # Windows Arial Bold
            print("⚠️ Using Arial Bold fallback font.")
        except OSError:
            print("⚠️ Could not load any font, using default.")
            font = ImageFont.load_default()

    ox, oy = offset
    fw, fh = field_area_size or image.size
    radius = config.get("circle_radius", 40) * SCALE

    positions = get_formation_positions(config)
    for player in positions:
        x = int(player["x"] * fw) + ox
        y = int(player["y"] * fh) + oy
        number = str(player["number"])

        # Draw player circle
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=config["circle_color"],
        )

        # Center the number in the circle using textbbox
        bbox = draw.textbbox((0, 0), number, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x - text_width // 2
        text_y = y - text_height // 2

        draw.text((text_x, text_y), number, fill=config["text_color"], font=font)

    print("✅ Players drawn on field.")
    return image


def paste_centered(base_img, overlay_img):
    """Paste overlay_img centered on base_img"""
    base_w, base_h = base_img.size
    overlay_w, overlay_h = overlay_img.size
    offset = ((base_w - overlay_w) // 2, (base_h - overlay_h) // 2)
    base_img.alpha_composite(overlay_img, dest=offset)
    print("✅ Pasted field lines centered on base image.")
    return offset  # Used to shift player coordinates


def generate_lineup_from_config(config):
    field_img, offset, field_area_size = create_field_with_layers(
        config["field_color"],
        "field_base.png",
        "FieldLines.png",
    )

    # Step 2: Draw players on high-res image
    final = draw_players(
        field_img, config, offset=offset, field_area_size=field_area_size
    )

    # Step 3: Downscale for smoothness
    final = final.resize((final.width // SCALE, final.height // SCALE), Image.LANCZOS)

    return final  # Return PIL image


def main():
    with open("config.json") as f:
        config = json.load(f)

    final = generate_lineup_from_config(config)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_filename = f"lineup_img_based_{timestamp}.png"
    output_path = os.path.join(output_dir, output_filename)
    final.save(output_path)
    print(f"✅ Saved: {output_path}")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"⏱️ Finished in {end_time - start_time:.2f} seconds")
