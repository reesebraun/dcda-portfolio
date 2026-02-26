
import base64
import os
import time
import requests
import pandas as pd
import folium
from folium.map import Popup

# -----------------------------
# 1) CONFIG: Fill these in
# -----------------------------
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoicmVlc2VicmF1biIsImEiOiJjbWx0cHBnZTYwMnBlM2ZwdjQxNmQwZzltIn0.Nr9nHuokI7a96ch9D26mdgE"
MAPBOX_USERNAME = "YOUR_USERNAME"
MAPBOX_STYLE_ID = "YOUR_STYLE_ID"  # the part after /styles/username/
CSV_PATH = "Lab6_Hometown_Locations.csv"
OUTPUT_HTML = "pearland_hometown_map.html"

# Mapbox tiles URL (Raster tiles)
TILES_URL = (
    f"mapbox://styles/reesebraun/cmm2t33un003q01rwa56h79q9"
    "{z}/{x}/{y}@2x?access_token=" + MAPBOX_ACCESS_TOKEN
)

# -----------------------------
# 2) Helpers
# -----------------------------
def geocode_address(address: str, access_token: str):
    """
    Forward geocode an address using Mapbox Geocoding API (v6).
    Returns (lat, lon) or (None, None) if not found.
    """
    url = "https://api.mapbox.com/search/geocode/v6/forward"
    params = {
        "q": address,
        "access_token": access_token,
        "limit": 1,
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    features = data.get("features", [])
    if not features:
        return None, None

    # v6 returns geometry with coordinates [lon, lat]
    coords = features[0]["geometry"]["coordinates"]
    lon, lat = coords[0], coords[1]
    return lat, lon


def image_to_data_uri(image_path: str):
    """
    Converts a local image file into a data URI string so it can display in a Folium popup.
    If file doesn't exist, returns None.
    """
    if not image_path or not os.path.exists(image_path):
        return None

    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        return None

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    mime = "jpeg" if ext in ["jpg", "jpeg"] else ext
    return f"data:image/{mime};base64,{encoded}"


def icon_color_for_type(place_type: str) -> str:
    """
    Maps your location 'type' to Folium marker colors.
    Edit these categories however you want.
    """
    t = (place_type or "").strip().lower()

    mapping = {
        "park": "darkgreen",
        "nature": "green",
        "restaurant": "red",
        "food": "red",
        "coffee": "cadetblue",
        "cafe": "cadetblue",
        "shopping": "purple",
        "school": "blue",
        "cultural": "orange",
        "museum": "orange",
        "memory": "pink",
    }
    return mapping.get(t, "gray")


def build_popup_html(name: str, description: str, image_data_uri: str | None):
    """
    Creates clean popup HTML with optional image.
    """
    safe_name = name or "Location"
    safe_desc = description or ""

    img_html = ""
    if image_data_uri:
        img_html = f"""
        <div style="margin-top:8px;">
          <img src="{image_data_uri}" style="width:220px; max-width:100%; border-radius:10px;">
        </div>
        """

    html = f"""
    <div style="width:250px; font-family: Arial, sans-serif;">
      <h4 style="margin:0 0 6px 0;">{safe_name}</h4>
      <div style="font-size: 13px; line-height: 1.35;">{safe_desc}</div>
      {img_html}
    </div>
    """
    return html


# -----------------------------
# 3) Main Script
# -----------------------------
def main():
    df = pd.read_csv(CSV_PATH)

    # Check required columns
    required_cols = {"name", "address", "type", "description", "image"}
    missing = required_cols - set(df.columns.str.lower())
    # If user's CSV columns have exact names, normalize for safety:
    df.columns = [c.lower().strip() for c in df.columns]

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    # Geocode (test with first 2–3 rows if you want)
    lats, lons = [], []
    for i, row in df.iterrows():
        address = str(row["address"])
        lat, lon = geocode_address(address, MAPBOX_ACCESS_TOKEN)
        lats.append(lat)
        lons.append(lon)

        # gentle rate limit so Mapbox doesn't get annoyed
        time.sleep(0.15)

    df["lat"] = lats
    df["lon"] = lons

    # Drop rows that failed geocoding
    df_ok = df.dropna(subset=["lat", "lon"]).copy()
    if df_ok.empty:
        raise RuntimeError("No locations were successfully geocoded. Check addresses / token.")

    # Center map on average coords (Pearland-ish)
    center_lat = df_ok["lat"].mean()
    center_lon = df_ok["lon"].mean()

    # Create Folium map with custom Mapbox tiles
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles=None
    )

    folium.TileLayer(
        tiles=TILES_URL,
        attr="Mapbox",
        name="Custom Basemap",
        overlay=False,
        control=False,
        max_zoom=18
    ).add_to(m)

    # Add markers
    for _, row in df_ok.iterrows():
        name = row["name"]
        description = row["description"]
        place_type = row["type"]
        image_path = row["image"]

        img_uri = image_to_data_uri(image_path)
        popup_html = build_popup_html(name, description, img_uri)

        popup = Popup(popup_html, max_width=300)

        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=popup,
            tooltip=name,
            icon=folium.Icon(color=icon_color_for_type(place_type), icon="info-sign"),
        ).add_to(m)

    # Save HTML
    m.save(OUTPUT_HTML)
    print(f"✅ Map saved to {OUTPUT_HTML}")


if __name__ == "__main__":
    main()