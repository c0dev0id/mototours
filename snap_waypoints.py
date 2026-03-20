#!/usr/bin/env python3
"""Snap waypoint coordinates to nearest road using the Valhalla locate API.

For every waypoint across all generated GPX files, queries Valhalla for the
nearest road point.  Any waypoint that is more than SNAP_THRESHOLD_KM away
from the nearest road has its coordinates corrected in generate_tours.py and
generate_multiday_tours.py, then GPX files can be regenerated.

Usage:
    python snap_waypoints.py            # dry-run, prints corrections only
    python snap_waypoints.py --apply    # apply corrections to source files
"""

import argparse
import glob
import json
import math
import os
import re
import time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
from urllib.error import URLError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GPX_DIR = "output/gpx"
VALHALLA_LOCATE = "https://valhalla1.openstreetmap.de/locate"
SNAP_THRESHOLD_KM = 0.05   # 50 m — warn/fix if farther than this from nearest road
EARTH_RADIUS_KM = 6371.0
REQUEST_DELAY = 0.3         # seconds between Valhalla requests

SOURCE_FILES = [
    "generate_tours.py",
    "generate_multiday_tours.py",
]

GPX_NS = "{http://www.topografix.com/GPX/1/1}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    """Straight-line distance between two lat/lon points in km."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def valhalla_nearest(lat, lon, retries=4):
    """Return (snapped_lat, snapped_lon) from Valhalla locate, or None on failure."""
    body = json.dumps({
        "locations": [{"lat": lat, "lon": lon}],
        "costing": "auto",
    }).encode()
    delay = 2.0
    for attempt in range(retries):
        try:
            req = Request(
                VALHALLA_LOCATE,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "MotoTourSnapper/1.0",
                },
            )
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            # data is a list; first element is our location
            result = data[0] if isinstance(data, list) else data
            edges = result.get("edges", [])
            if edges:
                snap_lat = edges[0]["correlated_lat"]
                snap_lon = edges[0]["correlated_lon"]
                return snap_lat, snap_lon
        except (URLError, OSError, ValueError, KeyError, IndexError) as exc:
            if attempt < retries - 1:
                print(f"    Valhalla locate failed ({exc}), retry in {delay:.0f}s …")
                time.sleep(delay)
                delay *= 2
    return None


def collect_waypoints_from_gpx(gpx_dir):
    """Return sorted list of unique (name, lat, lon) tuples from all GPX wpt elements."""
    seen = {}
    for filepath in sorted(glob.glob(os.path.join(gpx_dir, "*.gpx"))):
        tree = ET.parse(filepath)
        root = tree.getroot()
        for wpt in root.findall(f"{GPX_NS}wpt"):
            lat = float(wpt.get("lat"))
            lon = float(wpt.get("lon"))
            name_el = wpt.find(f"{GPX_NS}name")
            name = name_el.text if name_el is not None else f"{lat},{lon}"
            key = (round(lat, 8), round(lon, 8))
            if key not in seen:
                seen[key] = name
    return [(name, lat, lon) for (lat, lon), name in sorted(seen.items())]


def make_coord_pattern(v):
    """Build a regex pattern that matches float v as stored in Python source.

    Handles trailing zeros: e.g. value 49.5 matches '49.5', '49.50', '49.500'.
    Handles integer-like decimals: 50.0 matches '50.0', '50.00', '50', etc.
    """
    # Minimal representation (strip trailing zeros)
    s = f"{v:.10f}".rstrip("0").rstrip(".")
    # Escape the decimal point
    escaped = s.replace(".", r"\.")
    if "." in s:
        # Already has decimal point — allow trailing zeros after last significant digit
        return escaped + r"0*"
    else:
        # Integer-like — allow optional .0+ suffix
        return escaped + r"(?:\.0+)?"


def apply_corrections_to_file(filepath, corrections):
    """Replace old coordinate pairs with new ones in a Python source file.

    corrections: list of (old_lat, old_lon, new_lat, new_lon, name)

    Strategy: find the pattern  <old_lat>, <old_lon>  within a waypoint tuple
    and replace with <new_lat>, <new_lon>.  We match a trailing comma to avoid
    replacing coordinates that appear in other numeric contexts.  Trailing zeros
    are handled so that e.g. 49.500 and 9.040 are matched by patterns for 49.5
    and 9.04 respectively.
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        content = fh.read()

    changed = 0
    for old_lat, old_lon, new_lat, new_lon, _name in corrections:
        new_lat_s = f"{new_lat:.6f}"
        new_lon_s = f"{new_lon:.6f}"

        # Match the two coordinate values appearing consecutively in a tuple:
        # e.g.  49.322, 8.548,  or  49.500, 9.040,
        # The look-ahead (?=\s*,) ensures a third field follows (desc, is_midpoint).
        pattern = (
            r"(" + make_coord_pattern(old_lat) + r",\s*)"
            + make_coord_pattern(old_lon)
            + r"(?=\s*,)"
        )
        replacement = f"{new_lat_s}, {new_lon_s}"
        new_content, n = re.subn(pattern, replacement, content)
        if n:
            content = new_content
            changed += n

    if changed:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(content)
    return changed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Snap waypoint coordinates to nearest road via Valhalla locate"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply coordinate corrections to source files (default: dry-run only)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=SNAP_THRESHOLD_KM,
        metavar="KM",
        help=f"Snap threshold in km (default: {SNAP_THRESHOLD_KM})",
    )
    args = parser.parse_args()

    print(f"Collecting waypoints from {GPX_DIR} …")
    waypoints = collect_waypoints_from_gpx(GPX_DIR)
    print(f"Found {len(waypoints)} unique waypoints.\n")

    corrections = []   # (old_lat, old_lon, new_lat, new_lon, name)
    errors = []

    for i, (name, lat, lon) in enumerate(waypoints):
        snapped = valhalla_nearest(lat, lon)
        if snapped is None:
            errors.append((name, lat, lon))
            print(f"  [{i+1}/{len(waypoints)}] FAILED  {name!r} ({lat}, {lon})")
            time.sleep(REQUEST_DELAY)
            continue

        snap_lat, snap_lon = snapped
        dist_m = haversine_km(lat, lon, snap_lat, snap_lon) * 1000

        if dist_m > args.threshold * 1000:
            corrections.append((lat, lon, snap_lat, snap_lon, name))
            print(
                f"  [{i+1}/{len(waypoints)}] OFF-ROAD  {name!r:40s} "
                f"({lat:.6f}, {lon:.6f})  →  ({snap_lat:.6f}, {snap_lon:.6f})  "
                f"snap={dist_m:.0f} m"
            )
        else:
            print(
                f"  [{i+1}/{len(waypoints)}] ok        {name!r:40s} "
                f"({lat:.6f}, {lon:.6f})  snap={dist_m:.0f} m"
            )

        time.sleep(REQUEST_DELAY)

    print(f"\n{'=' * 70}")
    print(f"Summary: {len(corrections)} corrections needed, {len(errors)} lookup failures")

    if not corrections:
        print("Nothing to fix.")
        return

    print("\nCorrections:")
    for old_lat, old_lon, new_lat, new_lon, name in corrections:
        dist_m = haversine_km(old_lat, old_lon, new_lat, new_lon) * 1000
        print(f"  {name!r}: ({old_lat}, {old_lon}) → ({new_lat:.6f}, {new_lon:.6f})  [{dist_m:.0f} m]")

    if not args.apply:
        print("\nDry-run mode — pass --apply to patch source files.")
        return

    print("\nApplying corrections …")
    total_changes = 0
    for filepath in SOURCE_FILES:
        if not os.path.exists(filepath):
            continue
        n = apply_corrections_to_file(filepath, corrections)
        print(f"  {filepath}: {n} replacement(s)")
        total_changes += n

    if total_changes:
        print(f"\nDone — {total_changes} coordinate(s) updated.")
        print("Re-run generate_tours.py and generate_multiday_tours.py to regenerate GPX files.")
    else:
        print("\nNo replacements made — check that coordinates in source files match exactly.")


if __name__ == "__main__":
    main()
