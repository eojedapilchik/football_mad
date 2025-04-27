from __future__ import annotations

import json
from io import BytesIO

import streamlit as st

from formations import formations
from from_base_images import generate_lineup_from_config

st.set_page_config(layout="wide", page_title="Formation Visualizer", page_icon="⚽")
st.title("⚽ Formation Visualizer")

# Prepare default formation
default_formation = list(formations.keys())[0]
formation_name = st.session_state.get("formation_name", default_formation)

# Layout: dropdown left, downloads right
col_dropdown, col_dl = st.columns([1, 1])

with col_dropdown:
    st.markdown("### 🧩 Formation")
    formation_name = st.selectbox(
        "Choose Formation",
        list(formations.keys()),
        index=list(formations.keys()).index(formation_name),
        label_visibility="collapsed",
    )
    st.session_state["formation_name"] = formation_name

# Load default coords
default_coords = formations[formation_name]

# Layout: table left, image right
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📊 Formation Coordinates")
    coords = st.data_editor(
        [
            {"number": i + 1, "x": round(x, 2), "y": round(y, 2)}
            for i, (x, y) in enumerate(default_coords)
        ],
        column_order=["number", "x", "y"],
        column_config={
            "number": st.column_config.NumberColumn(
                "No.", width="small", disabled=True
            ),
            "x": st.column_config.NumberColumn("X"),
            "y": st.column_config.NumberColumn("Y"),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
    )

    st.markdown("### ⚙️ Customize Colors")
    circle_color = st.color_picker("Circle Color", "#d00000")
    text_color = st.color_picker("Text Color", "#ffffff")
    field_color = st.color_picker("Field Color", "#3B7A57")

    st.markdown("### 🔁 Orientation")
    flip_vertical = st.checkbox("Flip vertically (attack bottom to top)", value=False)

# Generate positions from editor
positions = [
    {
        "number": row["number"],
        "x": row["x"],
        "y": (1.0 - row["y"]) if flip_vertical else row["y"],
    }
    for row in coords
]

# Build config
config = {
    "circle_color": circle_color,
    "text_color": text_color,
    "field_color": field_color,
    "circle_radius": 20,
    "number_font_size": 18,
    "positions": positions,
}

# Generate image
img = generate_lineup_from_config(config)

with col2:
    st.subheader("📸 Preview")
    st.image(img, caption="Formation Preview", width=350)

# Downloads - buttons on the right
with col_dl:
    st.markdown("### 📥 Export")

    formation_slug = formation_name.lower().replace(" ", "_")

    # Prepare image for download
    buf = BytesIO()
    img.save(buf, format="PNG")

    # Use smaller styled buttons
    st.markdown(
        """
        <style>
        .small-button button {
            padding: 0.3rem 0.8rem;
            font-size: 0.85rem;
            border-radius: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="small-button">', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download PNG",
            buf.getvalue(),
            file_name=f"{formation_slug}.png",
            mime="image/png",
            key="png_download",
        )
        st.download_button(
            "⬇️ Download JSON",
            json.dumps(config, indent=2),
            file_name=f"{formation_slug}.json",
            mime="application/json",
            key="json_download",
        )
        st.markdown("</div>", unsafe_allow_html=True)
