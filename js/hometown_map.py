"""
hometown_map.py
Reads a CSV of hometown locations, geocodes each address with the
Mapbox Geocoding API v6, and builds an interactive Folium map with:
  • a custom Mapbox basemap
  • category-specific marker colors + icons
  • popups containing name, description, and an image (WEB URL)
  • a title + legend overlay

Requirements:
    pip install pandas requests folium
"""

import os
import sys
import time
import folium
import pandas as pd
import requests

# ============================================================
# CONFIGURATION — edit these three values before running
# ============================================================
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoicmVlc2VicmF1biIsImEiOiJjbWx0cHBnZTYwMnBlM2ZwdjQxNmQwZzltIn0.Nr9nHuokI7a96ch9D26mdg"
MAPBOX_USERNAME = "reesebraun"
MAPBOX_STYLE_ID = "cmm2t33un003q01rwa56h79q9"  # from mapbox://styles/reesebraun/cmm2t33un003q01rwa56h79q9

CSV_PATH = "Lab6_HometownMap.csv"
OUTPUT_HTML = "pearland_hometown_map.html"

TILES_URL = (
    f"https://api.mapbox.com/styles/v1/{MAPBOX_USERNAME}/{MAPBOX_STYLE_ID}/tiles/256/"
    "{z}/{x}/{y}@2x"
    f"?access_token={MAPBOX_ACCESS_TOKEN}"
)

# ============================================================
# ICON + COLOUR MAPPING (type → marker style)
# Font Awesome icons via folium.Icon(..., prefix="fa")
# ============================================================
TYPE_STYLE = {
    "restaurant": {"color": "red", "icon": "utensils"},

    "coffee shop": {"color": "cadetblue", "icon": "coffee"},

    "park": {"color": "darkgreen", "icon": "tree"},

    "shop": {"color": "purple", "icon": "shopping-bag"},

    "shopping center": {"color": "darkpurple", "icon": "shopping-bag"},

    "school": {"color": "blue", "icon": "graduation-cap"},

    "golfcourse": {"color": "lightgreen", "icon": "flag"},

    "activities": {"color": "orange", "icon": "star"},
    
    "church": {"color": "lightblue", "icon": "place-of-worship"},
    "bar": {"color": "darkred", "icon": "glass-martini"},

    "recreational center": {"color": "beige", "icon": "futbol"},
    "fitness studio": {"color": "pink", "icon": "dumbbell"},
    "salon": {"color": "lightred", "icon": "cut"},
}

DEFAULT_STYLE = {"color": "gray", "icon": "map-marker-alt"}


def style_for_type(place_type):
    key = (place_type or "").strip().lower()
    return TYPE_STYLE.get(key, DEFAULT_STYLE)


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def geocode_address(address):
    """Mapbox Geocoding API v6 forward geocode. Returns (lat, lon) or (None, None)."""
    url = "https://api.mapbox.com/search/geocode/v6/forward"
    params = {"q": address, "access_token": MAPBOX_ACCESS_TOKEN, "limit": 1}

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        features = data.get("features", [])
        if not features:
            print(f"  ⚠  No geocode results for: {address}")
            return None, None

        lon, lat = features[0]["geometry"]["coordinates"]
        return lat, lon

    except Exception as e:
        print(f"  ⚠  Geocoding error for '{address}': {e}")
        return None, None


def build_popup_html(name, description, image_url=""):
    """Popup HTML with name, description, and an image loaded from a WEB URL."""
    img_block = ""
    if isinstance(image_url, str) and image_url.strip():
        img_block = f"""
        <div style="margin-top:10px;">
            <img src="{image_url}" style="width:240px; max-width:100%; border-radius:10px;">
        </div>
        """

    return f"""
    <div style="width:260px; font-family: Arial, sans-serif;">
        <h4 style="margin:0 0 6px 0;">{name}</h4>
        <div style="font-size:13px; line-height:1.35;">{description}</div>
        {img_block}
    </div>
    """


def add_title(map_obj, title_text):
    """Fixed title banner at top center."""
    title_html = f"""
    <div style="
        position: fixed;
        top: 18px; left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        background: rgba(255,255,255,0.92);
        padding: 10px 18px;
        border-radius: 14px;
        font-size: 22px;
        font-weight: 700;
        box-shadow: 0 2px 10px rgba(0,0,0,0.18);
        border: 2px solid rgba(111,143,134,0.35);
        font-family: Arial, sans-serif;
    ">
      {title_text}
    </div>
    """
    map_obj.get_root().html.add_child(folium.Element(title_html))


def add_legend(map_obj, legend_title, legend_items):
    """Legend box in bottom-left (no duplicates)."""
    rows = ""
    for label, color, icon in legend_items:
        rows += f"""
        <div style="display:flex; align-items:center; margin:6px 0;">
          <div style="
              width:14px; height:14px; border-radius:50%;
              background:{color};
              border:1px solid rgba(0,0,0,0.25);
              margin-right:10px;"></div>
          <span style="font-size:14px;">{label}</span>
          <span style="margin-left:auto; font-size:12px; opacity:0.7;">{icon}</span>
        </div>
        """

    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 24px; left: 24px;
        z-index: 9999;
        background: rgba(255,255,255,0.92);
        padding: 14px 16px;
        border-radius: 12px;
        width: 270px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.18);
        border: 2px solid rgba(111,143,134,0.35);
        font-family: Arial, sans-serif;
    ">
      <div style="font-weight:700; font-size:16px; margin-bottom:8px;">
        {legend_title}
      </div>
      <div style="max-height:220px; overflow:auto;">
        {rows}
      </div>
    </div>
    """
    map_obj.get_root().html.add_child(folium.Element(legend_html))


# ============================================================
# MAIN
# ============================================================
def main():
    if not os.path.isfile(CSV_PATH):
        sys.exit(f"❌  CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower() for c in df.columns]

    required_cols = {"name", "address", "type", "description", "image_url"}
    missing = required_cols - set(df.columns)
    if missing:
        sys.exit(f"❌  CSV is missing required columns: {missing}")

    print(f"📄  Loaded {len(df)} locations from {CSV_PATH}\n")

    # Geocode
    latitudes, longitudes = [], []
    for idx, row in df.iterrows():
        address = str(row["address"]).strip()
        print(f"  Geocoding ({idx + 1}/{len(df)}): {address}")
        lat, lon = geocode_address(address)
        latitudes.append(lat)
        longitudes.append(lon)
        time.sleep(0.15)

    df["lat"] = latitudes
    df["lon"] = longitudes

    df_valid = df.dropna(subset=["lat", "lon"]).copy()
    print(f"\n✅  Successfully geocoded {len(df_valid)} / {len(df)} locations\n")

    if df_valid.empty:
        sys.exit("❌  No addresses could be geocoded. Check your addresses and token.")

    # Create map
    centre_lat = df_valid["lat"].mean()
    centre_lon = df_valid["lon"].mean()

    m = folium.Map(location=[centre_lat, centre_lon], zoom_start=12, tiles=None)

    # Custom basemap
    folium.TileLayer(
        tiles=TILES_URL,
        attr="© Mapbox © OpenStreetMap",
        name="Custom Mapbox Basemap",
        overlay=False,
        control=False,
        max_zoom=19,
    ).add_to(m)

    # Title + legend overlays
    add_title(m, "📍 Pearland Favorites Map")
    add_legend(m, "Legend", TYPE_STYLE)

    # Markers
    for _, row in df_valid.iterrows():
        name = row["name"]
        description = row["description"]
        place_type = row["type"]
        image_url = row.get("image_url", "")

        popup_html = build_popup_html(name, description, image_url)
        popup = folium.Popup(popup_html, max_width=320)

        st = style_for_type(place_type)

        folium.Marker(
            location=[row["lat"], row["lon"]],
            tooltip=name,
            popup=popup,
            icon=folium.Icon(color=st["color"], icon=st["icon"], prefix="fa"),
        ).add_to(m)

    # Save
    m.save(OUTPUT_HTML)
    print(f"🗺️  Map saved to {OUTPUT_HTML}")


if __name__ == "__main__":
    main()