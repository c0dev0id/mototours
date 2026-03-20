"""
fetch_optional_pois.py
Query the Overpass API for notable POIs near each motorcycle tour, then write
optional_pois.py containing OPTIONAL_POIS dict keyed by tour slug (single-day)
or {slug}_day{n} (multiday).

Run:  python fetch_optional_pois.py
Output: optional_pois.py  (imported by generate_tours.py / generate_multiday_tours.py)
"""

import json
import math
import time
import urllib.request
import urllib.parse
import sys

# ---------------------------------------------------------------------------
# Import tour data
# ---------------------------------------------------------------------------
sys.path.insert(0, ".")
from generate_tours import TOURS as SINGLE_DAY_TOURS
from generate_multiday_tours import WEEKEND_TOURS, THREE_DAY_TOURS, SIX_DAY_TOURS

MULTIDAY_ALL = [
    ("tour2d", WEEKEND_TOURS),
    ("tour3d", THREE_DAY_TOURS),
    ("tour6d", SIX_DAY_TOURS),
]

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
BBOX_PAD = 0.06        # degrees to expand bbox around route waypoints
MAX_BBOX_DEG = 1.0     # clamp bbox to this size in each dimension to avoid timeouts
MAX_POIS = 7           # max optional POIs per tour/day
RATE_LIMIT_S = 2.0     # seconds between Overpass requests

# OSM category → GPX sym priority order (higher index = lower priority)
CATEGORY_PRIORITY = ["Castle", "Monastery", "Museum", "Waterfall", "Lake",
                     "Scenic Area", "Summit", "Spa", "Winery", "Attraction"]

OSM_TO_SYM = {
    "castle":        "Castle",
    "fort":          "Castle",
    "monastery":     "Monastery",
    "ruins":         "Castle",
    "museum":        "Museum",
    "waterfall":     "Waterfall",
    "viewpoint":     "Scenic Area",
    "peak":          "Summit",
    "spa_complex":   "Spa",
    "winery":        "Winery",
    "brewery":       "Winery",
    "attraction":    "Attraction",
    "artwork":       "Attraction",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bbox_of(waypoints):
    lats = [w[1] for w in waypoints]
    lons = [w[2] for w in waypoints]
    c_lat = (min(lats) + max(lats)) / 2
    c_lon = (min(lons) + max(lons)) / 2
    half = MAX_BBOX_DEG / 2
    return (
        max(min(lats) - BBOX_PAD, c_lat - half),
        max(min(lons) - BBOX_PAD, c_lon - half),
        min(max(lats) + BBOX_PAD, c_lat + half),
        min(max(lons) + BBOX_PAD, c_lon + half),
    )


def overpass_query(bbox):
    s, w, n, e = bbox
    bb = f"{s:.6f},{w:.6f},{n:.6f},{e:.6f}"
    query = f"""
[out:json][timeout:15];
(
  node["tourism"~"^(castle|viewpoint|museum|attraction|artwork|winery)$"]["name"]({bb});
  node["historic"~"^(castle|monastery|ruins|fort)$"]["name"]({bb});
  node["natural"="waterfall"]["name"]({bb});
  node["natural"="peak"]["name"]({bb});
  node["amenity"~"^(spa_complex|brewery)$"]["name"]({bb});
  way["tourism"~"^(castle|viewpoint|museum|winery)$"]["name"]({bb});
  way["historic"~"^(castle|monastery|ruins)$"]["name"]({bb});
  relation["tourism"~"^(castle|museum)$"]["name"]({bb});
  relation["historic"~"^(castle|monastery)$"]["name"]({bb});
);
out center qt 30;
"""
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(OVERPASS_URL, data=data,
                                 headers={"User-Agent": "mototours-poi-fetcher/1.0"})
    # Retry up to 3 times on 429 / 5xx with backoff
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 2:
                time.sleep(4 * (attempt + 1))
                continue
            raise


def osm_to_sym(tags):
    for key in ("tourism", "historic", "natural", "amenity", "leisure"):
        val = tags.get(key, "")
        if val in OSM_TO_SYM:
            return OSM_TO_SYM[val]
    return "Attraction"


def sym_priority(sym):
    try:
        return CATEGORY_PRIORITY.index(sym)
    except ValueError:
        return len(CATEGORY_PRIORITY)


def fetch_pois_for(waypoints):
    """Return list of (name, lat, lon, sym) for notable POIs near *waypoints*."""
    bbox = bbox_of(waypoints)
    try:
        result = overpass_query(bbox)
    except Exception as exc:
        print(f"    WARNING: Overpass query failed: {exc}", file=sys.stderr)
        return []

    candidates = []
    for el in result.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name", "").strip()
        if not name:
            continue
        # lat/lon: node has direct coords; way/relation has "center"
        if el["type"] == "node":
            lat, lon = el["lat"], el["lon"]
        elif "center" in el:
            lat, lon = el["center"]["lat"], el["center"]["lon"]
        else:
            continue
        sym = osm_to_sym(tags)
        candidates.append((name, lat, lon, sym))

    # Sort by category priority, then deduplicate by name
    candidates.sort(key=lambda c: sym_priority(c[3]))
    seen_names = set()
    unique = []
    for c in candidates:
        if c[0] not in seen_names:
            seen_names.add(c[0])
            unique.append(c)

    return unique[:MAX_POIS]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    result = {}

    print(f"Fetching optional POIs for {len(SINGLE_DAY_TOURS)} single-day tours...")
    for tour in SINGLE_DAY_TOURS:
        slug = tour["slug"]
        print(f"  {slug} ...", end=" ", flush=True)
        pois = fetch_pois_for(tour["waypoints"])
        if pois:
            result[slug] = pois
            print(f"{len(pois)} POIs found")
        else:
            print("none")
        time.sleep(RATE_LIMIT_S)

    total_multiday = sum(len(tours) for _, tours in MULTIDAY_ALL)
    print(f"\nFetching optional POIs for {total_multiday} multiday tours ({sum(len(t['days']) for _, tours in MULTIDAY_ALL for t in tours)} days)...")
    for prefix, tours in MULTIDAY_ALL:
        for tour in tours:
            for day in tour["days"]:
                key = f"{tour['slug']}_day{day['day']}"
                print(f"  {key} ...", end=" ", flush=True)
                pois = fetch_pois_for(day["waypoints"])
                if pois:
                    result[key] = pois
                    print(f"{len(pois)} POIs found")
                else:
                    print("none")
                time.sleep(RATE_LIMIT_S)

    # Write output file
    lines = [
        "# Auto-generated by fetch_optional_pois.py — do not edit by hand",
        "# Re-run: python fetch_optional_pois.py",
        "",
        "OPTIONAL_POIS = {",
    ]
    for key, pois in sorted(result.items()):
        lines.append(f"    {key!r}: [")
        for name, lat, lon, sym in pois:
            lines.append(f"        ({name!r}, {lat:.6f}, {lon:.6f}, {sym!r}),")
        lines.append("    ],")
    lines.append("}")
    lines.append("")

    out_path = "optional_pois.py"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nWrote {out_path} with {len(result)} entries.")


if __name__ == "__main__":
    main()
