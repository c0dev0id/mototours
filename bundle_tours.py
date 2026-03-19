#!/usr/bin/env python3
"""
Package existing tours into ZIP bundles for the MotoTour Android app.

Each bundle contains:
  tour.json  — metadata manifest
  tour.pdf   — per-tour companion PDF
  day1.gpx   — one GPX per day

Bundles are written to android/app/src/main/assets/tours/
"""

import json
import os
import sys
import zipfile

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle

# Import tour data from generators
sys.path.insert(0, os.path.dirname(__file__))
from generate_tours import TOURS
from generate_multiday_tours import WEEKEND_TOURS, THREE_DAY_TOURS, SIX_DAY_TOURS, _total_km

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ASSETS_DIR = os.path.join("android", "app", "src", "main", "assets", "tours")
GPX_DIR = os.path.join("output", "gpx")

FONT_DIR = "/usr/local/share/fonts/noto"
GREEN = HexColor("#2C5530")
DARK = HexColor("#333333")
ACCENT = HexColor("#C8611A")
BLUE = HexColor("#2B547E")
LIGHT_GREY = HexColor("#E8E8E8")

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
def setup_fonts():
    pdfmetrics.registerFont(TTFont("NotoSans", os.path.join(FONT_DIR, "NotoSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("NotoSans-Bold", os.path.join(FONT_DIR, "NotoSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("NotoSans-Italic", os.path.join(FONT_DIR, "NotoSans-Italic.ttf")))
    pdfmetrics.registerFont(TTFont("NotoSans-BoldItalic", os.path.join(FONT_DIR, "NotoSans-BoldItalic.ttf")))
    registerFontFamily("NotoSans", normal="NotoSans", bold="NotoSans-Bold",
                        italic="NotoSans-Italic", boldItalic="NotoSans-BoldItalic")

# ---------------------------------------------------------------------------
# Per-tour PDF generation
# ---------------------------------------------------------------------------
STYLES = {}

def init_styles():
    STYLES["title"] = ParagraphStyle("title", fontName="NotoSans-Bold", fontSize=16,
                                      textColor=GREEN, spaceAfter=6, alignment=TA_CENTER)
    STYLES["subtitle"] = ParagraphStyle("subtitle", fontName="NotoSans", fontSize=10,
                                         textColor=ACCENT, spaceAfter=12, alignment=TA_CENTER)
    STYLES["heading"] = ParagraphStyle("heading", fontName="NotoSans-Bold", fontSize=12,
                                        textColor=GREEN, spaceBefore=10, spaceAfter=4)
    STYLES["day_heading"] = ParagraphStyle("day_heading", fontName="NotoSans-Bold", fontSize=11,
                                            textColor=BLUE, spaceBefore=8, spaceAfter=4)
    STYLES["body"] = ParagraphStyle("body", fontName="NotoSans", fontSize=9,
                                     textColor=DARK, leading=13, spaceAfter=4,
                                     alignment=TA_JUSTIFY)
    STYLES["small"] = ParagraphStyle("small", fontName="NotoSans", fontSize=8,
                                      textColor=DARK, leading=11, spaceAfter=2)
    STYLES["label"] = ParagraphStyle("label", fontName="NotoSans-Bold", fontSize=8,
                                      textColor=ACCENT, spaceAfter=1)


def generate_day_tour_pdf(tour, pdf_path):
    """Generate a single-page PDF for a day tour."""
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    story = []
    s = STYLES

    story.append(Paragraph(tour["name"], s["title"]))
    story.append(Paragraph(f'{tour["region"]}  •  {tour["distance_km"]} km  •  {tour["difficulty"]}',
                           s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY, spaceAfter=8))

    story.append(Paragraph("Overview", s["heading"]))
    story.append(Paragraph(tour["overview"], s["body"]))

    story.append(Paragraph("Route", s["heading"]))
    story.append(Paragraph(tour["route_description"], s["body"]))

    story.append(Paragraph(f'Midpoint: {tour["midpoint_name"]}', s["label"]))
    story.append(Paragraph(tour["midpoint_description"], s["small"]))

    if tour.get("highlights"):
        story.append(Paragraph("Highlights", s["heading"]))
        for h in tour["highlights"]:
            story.append(Paragraph(f"• {h}", s["small"]))

    if tour.get("road_character"):
        story.append(Paragraph("Road Character", s["heading"]))
        story.append(Paragraph(tour["road_character"], s["small"]))

    # Waypoint list
    story.append(Paragraph("Waypoints", s["heading"]))
    for name, lat, lon, desc, is_mid in tour["waypoints"]:
        prefix = "★ " if is_mid else "• "
        story.append(Paragraph(f"{prefix}<b>{name}</b> — {desc}", s["small"]))

    doc.build(story)


def generate_multiday_tour_pdf(tour, pdf_path):
    """Generate a PDF for a multi-day tour."""
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    story = []
    s = STYLES

    total_km = _total_km(tour)
    story.append(Paragraph(tour["name"], s["title"]))
    story.append(Paragraph(f'{tour["region"]}  •  {total_km} km total  •  {len(tour["days"])} days',
                           s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY, spaceAfter=8))

    if tour.get("overview"):
        story.append(Paragraph("Overview", s["heading"]))
        story.append(Paragraph(tour["overview"], s["body"]))

    if tour.get("highlights"):
        story.append(Paragraph("Highlights", s["heading"]))
        for h in tour["highlights"]:
            story.append(Paragraph(f"• {h}", s["small"]))

    if tour.get("road_character"):
        story.append(Paragraph("Road Character", s["heading"]))
        story.append(Paragraph(tour["road_character"], s["small"]))

    for day in tour["days"]:
        day_num = day.get("day") or day.get("day_number", "?")
        day_title = day.get("title") or day.get("name", "")
        story.append(Spacer(1, 6*mm))
        story.append(HRFlowable(width="100%", thickness=0.3, color=LIGHT_GREY, spaceAfter=4))
        story.append(Paragraph(
            f'Day {day_num}: {day_title} ({day["distance_km"]} km)', s["day_heading"]))
        story.append(Paragraph(day["description"], s["body"]))

        if day.get("midpoint_name"):
            story.append(Paragraph(f'Midpoint: {day["midpoint_name"]}', s["label"]))
            story.append(Paragraph(day.get("midpoint_description", ""), s["small"]))

        if day.get("overnight_name"):
            story.append(Paragraph(f'Overnight: {day["overnight_name"]}', s["label"]))
            story.append(Paragraph(day.get("overnight_description", ""), s["small"]))

        story.append(Paragraph("Waypoints", s["label"]))
        for name, lat, lon, desc, is_mid in day["waypoints"]:
            prefix = "★ " if is_mid else "• "
            story.append(Paragraph(f"{prefix}<b>{name}</b> — {desc}", s["small"]))

    doc.build(story)


# ---------------------------------------------------------------------------
# Bundle creation
# ---------------------------------------------------------------------------
def make_manifest_day(tour):
    return {
        "name": tour["name"],
        "slug": tour["slug"],
        "category": "DAY",
        "region": tour["region"],
        "total_distance_km": tour["distance_km"],
        "day_count": 1,
        "overview": tour["overview"],
        "highlights": ", ".join(tour.get("highlights", [])),
        "road_character": tour.get("road_character", ""),
        "days": [{
            "name": tour["name"],
            "distance_km": tour["distance_km"],
            "description": tour["route_description"],
        }],
    }


def make_manifest_multiday(tour, category):
    return {
        "name": tour["name"],
        "slug": tour["slug"],
        "category": category,
        "region": tour["region"],
        "total_distance_km": _total_km(tour),
        "day_count": len(tour["days"]),
        "overview": tour.get("overview", ""),
        "highlights": ", ".join(tour.get("highlights", [])),
        "road_character": tour.get("road_character", ""),
        "days": [{
            "name": d.get("title") or d.get("name", ""),
            "distance_km": d["distance_km"],
            "description": d["description"],
        } for d in tour["days"]],
    }


def bundle_day_tour(tour, outdir):
    """Create ZIP bundle for a single day tour."""
    slug = tour["slug"]
    num = tour["number"]
    gpx_name = f"tour_{num:02d}_{slug}.gpx"
    gpx_path = os.path.join(GPX_DIR, gpx_name)

    if not os.path.exists(gpx_path):
        print(f"  WARNING: {gpx_path} not found, skipping")
        return None

    # Generate per-tour PDF
    pdf_path = os.path.join(outdir, f"_tmp_{slug}.pdf")
    generate_day_tour_pdf(tour, pdf_path)

    # Create ZIP
    zip_name = f"day_{num:02d}_{slug}.zip"
    zip_path = os.path.join(outdir, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("tour.json", json.dumps(make_manifest_day(tour), indent=2, ensure_ascii=False))
        zf.write(pdf_path, "tour.pdf")
        zf.write(gpx_path, "day1.gpx")

    os.unlink(pdf_path)
    return zip_name


def bundle_multiday_tour(tour, prefix, category, outdir):
    """Create ZIP bundle for a multi-day tour."""
    slug = tour["slug"]
    num = tour["number"]
    n_days = len(tour["days"])

    # Collect GPX files
    gpx_files = []
    for d in range(1, n_days + 1):
        gpx_name = f"{prefix}_{num:02d}_{slug}_day{d}.gpx"
        gpx_path = os.path.join(GPX_DIR, gpx_name)
        if not os.path.exists(gpx_path):
            print(f"  WARNING: {gpx_path} not found, skipping tour")
            return None
        gpx_files.append(gpx_path)

    # Generate per-tour PDF
    pdf_path = os.path.join(outdir, f"_tmp_{slug}.pdf")
    generate_multiday_tour_pdf(tour, pdf_path)

    # Create ZIP
    zip_name = f"{prefix}_{num:02d}_{slug}.zip"
    zip_path = os.path.join(outdir, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("tour.json",
                     json.dumps(make_manifest_multiday(tour, category), indent=2, ensure_ascii=False))
        zf.write(pdf_path, "tour.pdf")
        for i, gpath in enumerate(gpx_files):
            zf.write(gpath, f"day{i + 1}.gpx")

    os.unlink(pdf_path)
    return zip_name


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    setup_fonts()
    init_styles()

    count = 0

    print("Bundling day tours ...")
    for tour in TOURS:
        name = bundle_day_tour(tour, ASSETS_DIR)
        if name:
            print(f"  {name}")
            count += 1

    print("Bundling weekend tours ...")
    for tour in WEEKEND_TOURS:
        name = bundle_multiday_tour(tour, "weekend", "WEEKEND", ASSETS_DIR)
        if name:
            print(f"  {name}")
            count += 1

    print("Bundling 3-day tours ...")
    for tour in THREE_DAY_TOURS:
        name = bundle_multiday_tour(tour, "tour3d", "THREE_DAY", ASSETS_DIR)
        if name:
            print(f"  {name}")
            count += 1

    print("Bundling 6-day tours ...")
    for tour in SIX_DAY_TOURS:
        name = bundle_multiday_tour(tour, "tour6d", "SIX_DAY", ASSETS_DIR)
        if name:
            print(f"  {name}")
            count += 1

    print(f"\n{count} bundles created in {ASSETS_DIR}/")


if __name__ == "__main__":
    main()
