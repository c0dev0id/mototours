#!/usr/bin/env python3
"""Validate GPX motorcycle tour routes using the Valhalla routing API.

Parses each GPX file, sends waypoints to Valhalla, and reports issues like
routing failures, distance mismatches, and excessive detours.
"""

import argparse
import glob
import json
import math
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
from urllib.error import URLError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VALHALLA_URL = "https://valhalla1.openstreetmap.de/route"
GPX_NS = "{http://www.topografix.com/GPX/1/1}"
EARTH_RADIUS_KM = 6371.0

# Thresholds
DISTANCE_WARN_PCT = 20   # warn if OSRM differs >20% from stated
DISTANCE_ERR_PCT = 40    # error if OSRM differs >40% from stated
DETOUR_RATIO_WARN = 3.0  # warn if leg is >3x straight-line distance
LONG_LEG_WARN_KM = 100   # warn if a single leg exceeds this


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


def parse_gpx(filepath):
    """Parse a GPX file and return tour info."""
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Tour name from metadata
    meta_name = root.find(f"{GPX_NS}metadata/{GPX_NS}name")
    tour_name = meta_name.text if meta_name is not None else os.path.basename(filepath)

    # Route points and stated distance
    rte = root.find(f"{GPX_NS}rte")
    route_points = []
    stated_km = None

    if rte is not None:
        desc_el = rte.find(f"{GPX_NS}desc")
        if desc_el is not None and desc_el.text:
            m = re.search(r"~(\d+)\s*km", desc_el.text)
            if m:
                stated_km = int(m.group(1))

        for rtept in rte.findall(f"{GPX_NS}rtept"):
            lat = float(rtept.get("lat"))
            lon = float(rtept.get("lon"))
            name_el = rtept.find(f"{GPX_NS}name")
            name = name_el.text if name_el is not None else f"{lat},{lon}"
            route_points.append((lat, lon, name))

    return {
        "filename": os.path.basename(filepath),
        "filepath": filepath,
        "tour_name": tour_name,
        "stated_km": stated_km,
        "route_points": route_points,
    }


def query_valhalla(route_points, timeout=15):
    """Query Valhalla for a route through the given points.

    Returns a normalized dict with keys:
      total_km, total_min, legs: [{km, minutes}]
    or None on failure.
    """
    if len(route_points) < 2:
        return None

    body = json.dumps({
        "locations": [{"lat": lat, "lon": lon} for lat, lon, _name in route_points],
        "costing": "auto",
        "units": "km",
    }).encode()

    for attempt in range(2):
        try:
            req = Request(
                VALHALLA_URL,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "MotoTourValidator/1.0",
                },
            )
            with urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            trip = data.get("trip")
            if not trip:
                return None
            summary = trip["summary"]
            legs = []
            for leg in trip.get("legs", []):
                ls = leg["summary"]
                legs.append({"km": ls["length"], "minutes": ls["time"] / 60.0})
            return {
                "total_km": summary["length"],
                "total_min": summary["time"] / 60.0,
                "legs": legs,
            }
        except (URLError, OSError, ValueError, KeyError):
            if attempt == 0:
                time.sleep(2)
    return None


def validate_route(tour, route_data):
    """Check a route for issues. Returns list of (level, message) tuples."""
    issues = []

    if not tour["route_points"]:
        issues.append(("ERROR", "No route points found in GPX file"))
        return issues

    if route_data is None:
        issues.append(("ERROR", "Routing failed — could not calculate route"))
        return issues

    routed_km = route_data["total_km"]
    legs = route_data["legs"]
    points = tour["route_points"]

    # Check total distance vs stated
    stated_km = tour["stated_km"]
    if stated_km:
        pct_diff = ((routed_km - stated_km) / stated_km) * 100
        if abs(pct_diff) > DISTANCE_ERR_PCT:
            issues.append(("ERROR",
                f"Distance mismatch: stated ~{stated_km} km, routed {routed_km:.1f} km "
                f"({pct_diff:+.1f}%)"))
        elif abs(pct_diff) > DISTANCE_WARN_PCT:
            issues.append(("WARNING",
                f"Distance mismatch: stated ~{stated_km} km, routed {routed_km:.1f} km "
                f"({pct_diff:+.1f}%)"))

    # Check individual legs
    for i, leg in enumerate(legs):
        if i >= len(points) - 1:
            break
        lat1, lon1, name1 = points[i]
        lat2, lon2, name2 = points[i + 1]
        leg_km = leg["km"]
        straight_km = haversine_km(lat1, lon1, lat2, lon2)

        # Detour ratio
        if straight_km > 0.5:  # skip very short legs
            ratio = leg_km / straight_km
            if ratio > DETOUR_RATIO_WARN:
                issues.append(("WARNING",
                    f"High detour ratio on leg {i+1}: {name1} -> {name2}: "
                    f"ratio {ratio:.1f}x (straight {straight_km:.1f} km, "
                    f"routed {leg_km:.1f} km)"))

        # Long leg
        if leg_km > LONG_LEG_WARN_KM:
            issues.append(("WARNING",
                f"Long leg {i+1}: {name1} -> {name2}: {leg_km:.1f} km"))

    return issues


def print_report(results, verbose=False):
    """Print a human-readable validation report."""
    errors = [(t, r, i) for t, r, i in results if any(lv == "ERROR" for lv, _ in i)]
    warnings = [(t, r, i) for t, r, i in results
                if any(lv == "WARNING" for lv, _ in i) and not any(lv == "ERROR" for lv, _ in i)]
    passed = [(t, r, i) for t, r, i in results if not i]

    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"ROUTE VALIDATION REPORT")
    print(f"{'=' * 60}")
    print(f"Validated: {total} | Passed: {len(passed)} | "
          f"Warnings: {len(warnings)} | Errors: {len(errors)}")
    print()

    if errors:
        print(f"{'─' * 60}")
        print("ERRORS")
        print(f"{'─' * 60}")
        for tour, rd, issues in errors:
            _print_tour_issues(tour, rd, issues)
        print()

    if warnings:
        print(f"{'─' * 60}")
        print("WARNINGS")
        print(f"{'─' * 60}")
        for tour, rd, issues in warnings:
            _print_tour_issues(tour, rd, issues)
        print()

    if verbose and passed:
        print(f"{'─' * 60}")
        print("PASSED")
        print(f"{'─' * 60}")
        for tour, rd, issues in passed:
            routed_km = rd["total_km"] if rd else 0
            stated = tour["stated_km"]
            if stated:
                pct = ((routed_km - stated) / stated) * 100
                print(f"  {tour['filename']}: stated ~{stated} km, "
                      f"routed {routed_km:.1f} km ({pct:+.1f}%)")
            else:
                print(f"  {tour['filename']}: routed {routed_km:.1f} km")


def _print_tour_issues(tour, rd, issues):
    """Print issues for a single tour."""
    print(f"\n  {tour['filename']}")
    print(f"    {tour['tour_name']}")
    if rd:
        routed_km = rd["total_km"]
        stated = tour["stated_km"]
        if stated:
            print(f"    Stated: ~{stated} km | Routed: {routed_km:.1f} km")
        else:
            print(f"    Routed: {routed_km:.1f} km")
    for level, msg in issues:
        print(f"    [{level}] {msg}")


def print_json_report(results):
    """Print machine-readable JSON report."""
    output = []
    for tour, rd, issues in results:
        entry = {
            "filename": tour["filename"],
            "tour_name": tour["tour_name"],
            "stated_km": tour["stated_km"],
            "routed_km": round(rd["total_km"], 1) if rd else None,
            "issues": [{"level": lv, "message": msg} for lv, msg in issues],
        }
        if rd:
            points = tour["route_points"]
            entry["legs"] = []
            for i, leg in enumerate(rd["legs"]):
                if i < len(points) - 1:
                    entry["legs"].append({
                        "from": points[i][2],
                        "to": points[i + 1][2],
                        "routed_km": round(leg["km"], 1),
                        "straight_km": round(haversine_km(
                            points[i][0], points[i][1],
                            points[i + 1][0], points[i + 1][1]), 1),
                    })
        output.append(entry)
    print(json.dumps(output, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Validate GPX routes via OSRM")
    parser.add_argument("--gpx-dir", default="output/gpx",
                        help="Directory containing GPX files (default: output/gpx)")
    parser.add_argument("--file", help="Validate a single GPX file")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output JSON instead of text report")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Seconds between API calls (default: 1.0)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show passed routes in report")
    args = parser.parse_args()

    if args.file:
        gpx_files = [args.file]
    else:
        gpx_files = sorted(glob.glob(os.path.join(args.gpx_dir, "*.gpx")))

    if not gpx_files:
        print("No GPX files found.", file=sys.stderr)
        sys.exit(1)

    results = []
    for i, filepath in enumerate(gpx_files):
        tour = parse_gpx(filepath)
        n_pts = len(tour["route_points"])
        if not args.json_output:
            print(f"[{i+1}/{len(gpx_files)}] {tour['filename']} "
                  f"({n_pts} pts)...", file=sys.stderr, flush=True)

        rd = query_valhalla(tour["route_points"])
        issues = validate_route(tour, rd)
        results.append((tour, rd, issues))

        if i < len(gpx_files) - 1:
            time.sleep(args.delay)

    if args.json_output:
        print_json_report(results)
    else:
        print_report(results, verbose=args.verbose)


if __name__ == "__main__":
    main()
