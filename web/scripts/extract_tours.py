#!/usr/bin/env python3
"""
Extract tour data from Android ZIP bundles into static files for the web app.

Reads all ZIPs from android/app/src/main/assets/tours/ and produces:
  web/public/data/tours.json        — combined metadata for all 50 tours
  web/public/data/gpx/{slug}_dayN.gpx
  web/public/data/pdf/{slug}.pdf
"""

import json
import os
import re
import shutil
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = REPO_ROOT / "android" / "app" / "src" / "main" / "assets" / "tours"
OUT_DIR = REPO_ROOT / "web" / "public" / "data"
GPX_DIR = OUT_DIR / "gpx"
PDF_DIR = OUT_DIR / "pdf"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def infer_category(day_count: int) -> str:
    if day_count == 1:
        return "DAY"
    if day_count == 2:
        return "WEEKEND"
    if day_count == 3:
        return "THREE_DAY"
    return "SIX_DAY"


def category_label(cat: str) -> str:
    return {"DAY": "Day Tour", "WEEKEND": "Weekend", "THREE_DAY": "3-Day", "SIX_DAY": "6-Day"}.get(cat, cat)


def process_zip(zip_path: Path) -> dict | None:
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()

        # Parse tour.json
        if "tour.json" not in names:
            print(f"  SKIP {zip_path.name}: no tour.json")
            return None
        meta = json.loads(zf.read("tour.json"))

        slug = meta.get("slug") or slugify(meta.get("name", zip_path.stem))
        category = meta.get("category") or infer_category(meta.get("day_count", 1))

        # Extract PDF
        if "tour.pdf" in names:
            pdf_out = PDF_DIR / f"{slug}.pdf"
            pdf_out.write_bytes(zf.read("tour.pdf"))

        # Extract GPX files
        gpx_files = sorted(n for n in names if re.match(r"day\d+\.gpx", n))
        gpx_entries = []
        for gpx_name in gpx_files:
            m = re.match(r"day(\d+)\.gpx", gpx_name)
            day_num = int(m.group(1)) if m else 1
            out_name = f"{slug}_day{day_num}.gpx"
            (GPX_DIR / out_name).write_bytes(zf.read(gpx_name))
            gpx_entries.append({"dayNumber": day_num, "file": out_name})

        tour = {
            "slug": slug,
            "name": meta.get("name", ""),
            "category": category,
            "categoryLabel": category_label(category),
            "region": meta.get("region", ""),
            "totalDistanceKm": meta.get("total_distance_km", 0),
            "dayCount": meta.get("day_count", 1),
            "overview": meta.get("overview", ""),
            "highlights": meta.get("highlights", ""),
            "roadCharacter": meta.get("road_character", ""),
            "days": meta.get("days", []),
            "hasPdf": "tour.pdf" in names,
            "gpxFiles": gpx_entries,
        }
        return tour


def main():
    GPX_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    zip_files = sorted(ASSETS_DIR.glob("*.zip"))
    if not zip_files:
        print(f"No ZIP files found in {ASSETS_DIR}")
        return

    print(f"Processing {len(zip_files)} tour bundles…")
    tours = []
    for zp in zip_files:
        print(f"  {zp.name}")
        tour = process_zip(zp)
        if tour:
            tours.append(tour)

    # Sort: category order then name
    cat_order = {"DAY": 0, "WEEKEND": 1, "THREE_DAY": 2, "SIX_DAY": 3}
    tours.sort(key=lambda t: (cat_order.get(t["category"], 9), t["name"]))

    out_path = OUT_DIR / "tours.json"
    out_path.write_text(json.dumps(tours, ensure_ascii=False, indent=2))

    print(f"\nDone. {len(tours)} tours written to {out_path}")
    print(f"  GPX files: {len(list(GPX_DIR.glob('*.gpx')))}")
    print(f"  PDF files: {len(list(PDF_DIR.glob('*.pdf')))}")


if __name__ == "__main__":
    main()
