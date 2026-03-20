#!/usr/bin/env python3
"""Generate multi-day motorcycle tour GPX files and companion PDF."""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HOME = ("Hockenheim", 49.322, 8.548, "Gustav-Stresemann-Weg 1", False)
HOME_ADDRESS = "Gustav-Stresemann-Weg 1, 68766 Hockenheim"

OUTPUT_DIR = "output"
GPX_DIR = os.path.join(OUTPUT_DIR, "gpx")
PDF_FILE = os.path.join(OUTPUT_DIR, "motorcycle_multiday_tours_hockenheim.pdf")

FONT_DIR = "/usr/local/share/fonts/noto"

GREEN = HexColor("#2C5530")
DARK = HexColor("#333333")
ACCENT = HexColor("#C8611A")
LIGHT_GREY = HexColor("#E8E8E8")
MID_GREY = HexColor("#888888")
BLUE = HexColor("#2B547E")

# ---------------------------------------------------------------------------
# Tour data helpers
# ---------------------------------------------------------------------------
H_START = ("Hockenheim", 49.322, 8.548, "Start", False)
H_END = ("Hockenheim", 49.322, 8.548, "End \u2013 home", False)


def _total_km(tour):
    return sum(d["distance_km"] for d in tour["days"])


# ===================================================================
# WEEKEND TOURS  (10 tours, 2 days each)
# ===================================================================
WEEKEND_TOURS = [
    # W01 ---------------------------------------------------------------
    {
        "number": 1,
        "name": "Baiersbronn \u2013 Black Forest Gourmet",
        "slug": "baiersbronn",
        "region": "Schwarzwald",
        "difficulty": "Moderate",
        "overview": (
            "A weekend in Germany\u2019s gourmet capital, Baiersbronn\u2014home to "
            "three Michelin-starred restaurants set amid deep Black Forest "
            "valleys. The outbound ride weaves through the Nagold valley; the "
            "return takes the legendary Schwarzwaldhochstra\u00dfe."
        ),
        "highlights": [
            "Baiersbronn \u2013 Germany\u2019s Michelin-star capital",
            "Nagold valley curves through dense forest",
            "B500 Schwarzwaldhochstra\u00dfe on the return",
            "Mummelsee and Hornisgrinde summit",
        ],
        "days": [
            {
                "day": 1,
                "title": "Through the Nagold Valley to Baiersbronn",
                "distance_km": 210,
                "waypoints": [
                    H_START,
                    ("Bretten", 49.036, 8.707, "Melanchthon town", False),
                    ("Pforzheim", 48.891, 8.704, "Gold city", False),
                    ("Calw", 48.714, 8.741, "Hermann Hesse\u2019s birthplace", True),
                    ("Bad Teinach", 48.692, 8.688, "Spa in the valley", False),
                    ("Nagold", 48.551, 8.724, "Nagold river", False),
                    ("Altensteig", 48.586, 8.601, "Castle town", False),
                    ("Freudenstadt", 48.462, 8.411, "Largest Marktplatz", False),
                    ("Baiersbronn", 48.504, 8.378, "Overnight", False),
                ],
                "description": (
                    "Head south through Bretten and Pforzheim to Calw, Hermann "
                    "Hesse\u2019s birthplace on the Nagold river. Follow the winding "
                    "Nagold valley south through Bad Teinach and Nagold, with "
                    "continuous flowing curves through dense forest. At "
                    "Altensteig, enjoy the castle views before climbing to "
                    "Freudenstadt. A short ride east brings you to Baiersbronn."
                ),
                "midpoint_name": "Calw",
                "midpoint_description": (
                    "Hesse\u2019s birthplace straddles the Nagold with half-timbered "
                    "charm. Ratskeller Calw serves Swabian classics."
                ),
                "overnight": {
                    "name": "Baiersbronn",
                    "description": (
                        "Home to three Michelin-starred restaurants: Traube "
                        "Tonbach (Schwarzwaldstube, 3 stars), Bareiss, and "
                        "Sch\u00f6nbuch. Even budget-friendly Gasth\u00e4user here "
                        "serve excellent food. Stroll the village and enjoy "
                        "the forest air."
                    ),
                },
                "road_character": (
                    "The Nagold valley is pure motorcycle bliss\u2014flowing "
                    "curves following the river through forest. Well-surfaced "
                    "throughout."
                ),
            },
            {
                "day": 2,
                "title": "Murgtal & Schwarzwaldhochstra\u00dfe Home",
                "distance_km": 200,
                "waypoints": [
                    ("Baiersbronn", 48.504, 8.378, "Start day 2", False),
                    ("Schwarzenberg", 48.548, 8.364, "Into the Murg valley", False),
                    ("Forbach", 48.685, 8.347, "Covered wooden bridge", True),
                    ("Schwarzenbachtalsperre", 48.667, 8.322, "Reservoir", False),
                    ("Herrenwies", 48.658, 8.253, "Mountain village", False),
                    ("Sand", 48.654, 8.226, "Join B500", False),
                    ("Mummelsee", 48.596, 8.201, "Mountain lake", False),
                    ("B\u00fchlerh\u00f6he", 48.683, 8.223, "Viewpoint", False),
                    ("Baden-Baden", 48.761, 8.241, "Spa city", False),
                    H_END,
                ],
                "description": (
                    "Ride north along the Murg valley through Forbach with its "
                    "unique covered wooden bridge. Climb to the "
                    "Schwarzenbachtalsperre reservoir and Herrenwies, then join "
                    "the legendary B500 at Sand. Ride the "
                    "Schwarzwaldhochstra\u00dfe past the Mummelsee to B\u00fchlerh\u00f6he, "
                    "then descend to elegant Baden-Baden and home via the A5."
                ),
                "midpoint_name": "Forbach & B500",
                "midpoint_description": (
                    "Forbach\u2019s covered bridge is a landmark. The B500 ridge "
                    "road delivers sweeping curves and mountain views."
                ),
                "overnight": None,
                "road_character": (
                    "The Murgtal is technical with tight valley curves. The "
                    "B500 is sweeping and fast\u2014Germany\u2019s most iconic motorcycle "
                    "road. A fitting finale."
                ),
            },
        ],
    },
    # W02 ---------------------------------------------------------------
    {
        "number": 2,
        "name": "Bernkastel-Kues \u2013 Moselle Wine",
        "slug": "bernkastel_kues",
        "region": "Mosel",
        "difficulty": "Moderate",
        "overview": (
            "Ride through the Pf\u00e4lzerwald and Hunsr\u00fcck highlands to reach "
            "Bernkastel-Kues, one of the most romantic wine towns on the "
            "Moselle. Return along the Nahe valley for a completely "
            "different landscape."
        ),
        "highlights": [
            "Bernkastel-Kues \u2013 half-timbered Moselle gem",
            "Pf\u00e4lzerwald and Hunsr\u00fcck forest roads",
            "Moselle valley curves",
            "Nahe valley \u2013 Germany\u2019s hidden wine region",
        ],
        "days": [
            {
                "day": 1,
                "title": "Through Pf\u00e4lzerwald & Hunsr\u00fcck to the Moselle",
                "distance_km": 220,
                "waypoints": [
                    H_START,
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Wine route", False),
                    ("Johanniskreuz", 49.348, 7.850, "Forest crossroads", False),
                    ("Lauterecken", 49.650, 7.588, "Glan valley", False),
                    ("Kusel", 49.533, 7.400, "Burg Lichtenberg", True),
                    ("Idar-Oberstein", 49.714, 7.308, "Gemstone city", False),
                    ("Morbach", 49.810, 7.130, "Hunsr\u00fcck", False),
                    ("Bernkastel-Kues", 49.915, 7.068, "Overnight", False),
                ],
                "description": (
                    "Cross the Rhine at Speyer and ride through the "
                    "Pf\u00e4lzerwald to Johanniskreuz. Continue northwest through "
                    "Lauterecken to Kusel, overlooked by the largest castle "
                    "ruin in the Palatinate. Cross through Idar-Oberstein, "
                    "the gemstone capital carved into a gorge, and over the "
                    "Hunsr\u00fcck highlands to descend to the Moselle at "
                    "Bernkastel-Kues."
                ),
                "midpoint_name": "Kusel & Burg Lichtenberg",
                "midpoint_description": (
                    "Burg Lichtenberg above Kusel is the largest castle ruin "
                    "in the Pfalz. The Burgschänke serves Pfälzer Küche."
                ),
                "overnight": {
                    "name": "Bernkastel-Kues",
                    "description": (
                        "One of the most picturesque towns on the Moselle. "
                        "The leaning Spitzhäuschen and the Marktplatz are "
                        "unforgettable. Wine tasting along the riverfront is "
                        "a must. Hotel Zur Post or Weinromantikhotel Richtershof."
                    ),
                },
                "road_character": (
                    "Varied\u2014Pf\u00e4lzerwald forest curves, open Hunsr\u00fcck "
                    "highlands, and the dramatic descent to the Moselle."
                ),
            },
            {
                "day": 2,
                "title": "Nahe Valley & Pfalz Return",
                "distance_km": 270,
                "waypoints": [
                    ("Bernkastel-Kues", 49.915, 7.068, "Start day 2", False),
                    ("Neumagen-Dhron", 49.854, 6.895, "Oldest wine town", False),
                    ("Thalfang", 49.754, 7.010, "Hunsr\u00fcck", False),
                    ("Idar-Oberstein", 49.714, 7.308, "Gemstone gorge", False),
                    ("Kirn", 49.789, 7.455, "Nahe valley", True),
                    ("Bad Sobernheim", 49.783, 7.647, "Barefoot path", False),
                    ("Bad Kreuznach", 49.842, 7.867, "Spa town", False),
                    ("Bad D\u00fcrkheim", 49.462, 8.172, "Wine barrel", False),
                    ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Wine route", False),
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    H_END,
                ],
                "description": (
                    "Follow the Moselle south to Neumagen-Dhron (Germany\u2019s "
                    "oldest wine town), then climb back over the Hunsr\u00fcck to "
                    "Idar-Oberstein. Pick up the Nahe valley at Kirn and "
                    "follow this beautiful, underrated wine river east through "
                    "Bad Sobernheim and Bad Kreuznach. Cross into the Pfalz at "
                    "Bad D\u00fcrkheim and ride the Weinstra\u00dfe south to Speyer."
                ),
                "midpoint_name": "Nahe Valley",
                "midpoint_description": (
                    "The Nahe is one of Germany\u2019s most underrated wine "
                    "regions. The valley road winds through vineyards and "
                    "dramatic rock formations."
                ),
                "overnight": None,
                "road_character": (
                    "The Hunsr\u00fcck crossing is sweeping and open. The Nahe "
                    "valley is flowing and scenic. The Weinstra\u00dfe finale "
                    "is relaxed riding through wine country."
                ),
            },
        ],
    },
    # W03 ---------------------------------------------------------------
    {
        "number": 3,
        "name": "Kaysersberg \u2013 Alsatian Wine Village",
        "slug": "kaysersberg",
        "region": "Elsass / Alsace",
        "difficulty": "Moderate",
        "overview": (
            "Cross into France for a night in Kaysersberg\u2014Albert "
            "Schweitzer\u2019s birthplace and one of Alsace\u2019s most beautiful "
            "villages. The outbound ride goes through the Pf\u00e4lzerwald "
            "and northern Alsace; the return takes the Vosges heights."
        ),
        "highlights": [
            "Kaysersberg \u2013 voted France\u2019s favorite village",
            "Alsace Wine Route villages",
            "Vosges mountain passes on the return",
            "Cross-border riding through three landscapes",
        ],
        "days": [
            {
                "day": 1,
                "title": "Through Pf\u00e4lzerwald & Alsace to Kaysersberg",
                "distance_km": 270,
                "waypoints": [
                    H_START,
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    ("Landau in der Pfalz", 49.199, 8.117, "Pfalz", False),
                    ("Wissembourg", 49.037, 7.945, "Cross into France", False),
                    ("Niederbronn-les-Bains", 48.952, 7.643, "Thermal spa", False),
                    ("Saverne", 48.742, 7.362, "Rose City", True),
                    ("Marlenheim", 48.622, 7.492, "Wine route starts", False),
                    ("Obernai", 48.462, 7.483, "Alsatian gem", False),
                    ("Ribeauvill\u00e9", 48.194, 7.318, "Three castles", False),
                    ("Kaysersberg", 48.140, 7.264, "Overnight", False),
                ],
                "description": (
                    "Cross the Rhine at Speyer, ride through Landau and into "
                    "France at Wissembourg. Follow the northern Vosges through "
                    "Niederbronn to Saverne, then pick up the Alsace Wine Route "
                    "at Marlenheim. Ride south through Obernai, Ribeauvill\u00e9, "
                    "and a string of flower-draped villages to Kaysersberg."
                ),
                "midpoint_name": "Saverne",
                "midpoint_description": (
                    "The \u201cRose City\u201d with its enormous red sandstone "
                    "ch\u00e2teau. Taverne Katz serves Alsatian classics."
                ),
                "overnight": {
                    "name": "Kaysersberg",
                    "description": (
                        "Voted France\u2019s favorite village in 2017. The "
                        "fortified bridge, ruined castle, and half-timbered "
                        "houses are magical at dusk. Birthplace of Albert "
                        "Schweitzer. Restaurant Winstub Au Chasseur for a "
                        "Baeckeoffe dinner. Hotel Constantin or H\u00f4tel "
                        "Les Remparts."
                    ),
                },
                "road_character": (
                    "Pf\u00e4lzerwald forest curves, then open Alsatian wine "
                    "route through villages. Gentle and scenic."
                ),
            },
            {
                "day": 2,
                "title": "Vosges Passes & Rhine Return",
                "distance_km": 390,
                "waypoints": [
                    ("Kaysersberg", 48.140, 7.264, "Start day 2", False),
                    ("Munster", 48.042, 7.137, "Cheese valley", False),
                    ("Col de la Schlucht", 48.063, 7.023, "Mountain pass (1139 m)", True),
                    ("Route des Cr\u00eates", 47.977, 7.053, "Ridge road", False),
                    ("Grand Ballon (1424 m)", 47.902, 7.099, "Highest Vosges peak", False),
                    ("Guebwiller", 47.912, 7.210, "Rangen Grand Cru", False),
                    ("Rouffach", 47.956, 7.299, "Wine village", False),
                    ("Colmar", 48.079, 7.359, "Little Venice", False),
                    ("Rhinau", 48.318, 7.711, "Cross Rhine", False),
                    ("Offenburg", 48.473, 7.954, "Ortenau", False),
                    ("Baden-Baden", 48.761, 8.241, "Spa city", False),
                    H_END,
                ],
                "description": (
                    "Ride into the Munster valley (famous cheese!), then climb "
                    "to the Col de la Schlucht (1139 m). Join the Route des "
                    "Cr\u00eates\u2014the legendary Vosges ridge road\u2014south to the "
                    "Grand Ballon (1424 m), the highest peak in the Vosges. "
                    "Descend through Guebwiller and Rouffach to Colmar, cross "
                    "the Rhine at Rhinau, and return via Offenburg and "
                    "Baden-Baden."
                ),
                "midpoint_name": "Col de la Schlucht & Route des Cr\u00eates",
                "midpoint_description": (
                    "The Route des Cr\u00eates runs along the Vosges ridge at "
                    "1000\u20131400 m with views into both Alsace and Lorraine. "
                    "Built as a strategic WWI road. Ferme-Auberge du Grand "
                    "Ballon at the summit for Munster cheese and Flammekueche."
                ),
                "overnight": None,
                "road_character": (
                    "Mountain pass riding\u2014the Col de la Schlucht and Route "
                    "des Cr\u00eates are the highlight, with sweeping alpine-style "
                    "curves at altitude. The Grand Ballon descent is steep "
                    "with tight hairpins."
                ),
            },
        ],
    },
    # W04 ---------------------------------------------------------------
    {
        "number": 4,
        "name": "T\u00fcbingen \u2013 Schw\u00e4bische Alb",
        "slug": "tuebingen_alb",
        "region": "Schw\u00e4bische Alb",
        "difficulty": "Moderate",
        "overview": (
            "Ride to the charming university town of T\u00fcbingen on the Neckar, "
            "then return over the dramatic Schw\u00e4bische Alb escarpment\u2014with "
            "its fairy-tale Schloss Lichtenstein and the waterfall at Bad Urach."
        ),
        "highlights": [
            "T\u00fcbingen \u2013 romantic university town on the Neckar",
            "Schloss Lichtenstein \u2013 Swabia\u2019s fairy-tale castle",
            "Bad Urach waterfall",
            "Alb escarpment curves with panoramic views",
        ],
        "days": [
            {
                "day": 1,
                "title": "Through the Black Forest Edge to T\u00fcbingen",
                "distance_km": 200,
                "waypoints": [
                    H_START,
                    ("Bretten", 49.036, 8.707, "Melanchthon town", False),
                    ("Maulbronn", 49.002, 8.812, "UNESCO monastery", False),
                    ("Pforzheim", 48.891, 8.704, "Northern BF gate", False),
                    ("Calw", 48.714, 8.741, "Hermann Hesse", True),
                    ("Nagold", 48.551, 8.724, "Nagold valley", False),
                    ("Haiterbach", 48.521, 8.647, "Black Forest edge", False),
                    ("Horb am Neckar", 48.445, 8.692, "Neckar valley", False),
                    ("Rottenburg am Neckar", 48.476, 8.935, "Cathedral town", False),
                    ("T\u00fcbingen", 48.522, 9.057, "Overnight", False),
                ],
                "description": (
                    "Head south through Bretten and Maulbronn (UNESCO "
                    "monastery) to Pforzheim, then into the Black Forest edge "
                    "via Calw and the Nagold valley. Wind through Haiterbach "
                    "and Horb am Neckar, following the young Neckar river to "
                    "Rottenburg (bishop\u2019s town) and on to T\u00fcbingen."
                ),
                "midpoint_name": "Calw & Nagold Valley",
                "midpoint_description": (
                    "Hesse\u2019s birthplace. The Nagold valley south of Calw "
                    "is a flowing motorcycle road through forest."
                ),
                "overnight": {
                    "name": "T\u00fcbingen",
                    "description": (
                        "One of Germany\u2019s most romantic university towns. "
                        "Stocherkahn (punting) on the Neckar, the Altstadt "
                        "with H\u00f6lderlinturm, the castle terrace. Weinstube "
                        "Forelle for Swabian Maultaschen. Hotel Am Schloss "
                        "or Hotel Krone."
                    ),
                },
                "road_character": (
                    "The Nagold valley delivers flowing forest curves. The "
                    "approach to Horb and Rottenburg follows the young Neckar "
                    "through a gentle valley."
                ),
            },
            {
                "day": 2,
                "title": "Schw\u00e4bische Alb Escarpment Home",
                "distance_km": 260,
                "waypoints": [
                    ("T\u00fcbingen", 48.522, 9.057, "Start day 2", False),
                    ("Reutlingen", 48.492, 9.214, "Gateway to the Alb", False),
                    ("Bad Urach", 48.494, 9.397, "Waterfall", True),
                    ("Schloss Lichtenstein", 48.408, 9.260, "Fairy-tale castle", False),
                    ("M\u00fcnsingen", 48.412, 9.497, "Alb plateau", False),
                    ("R\u00f6merstein", 48.490, 9.541, "Alb edge", False),
                    ("Owen", 48.586, 9.453, "Teck castle views", False),
                    ("Kirchheim unter Teck", 48.647, 9.450, "Town at the Alb foot", False),
                    ("Esslingen am Neckar", 48.740, 9.310, "Medieval gem", False),
                    ("Vaihingen an der Enz", 48.933, 8.962, "Return north", False),
                    H_END,
                ],
                "description": (
                    "Head east to Reutlingen and climb to Bad Urach for the "
                    "famous waterfall. Continue to Schloss Lichtenstein, "
                    "perched on a cliff like a fairy-tale illustration. Cross "
                    "the Alb plateau through M\u00fcnsingen and R\u00f6merstein, then "
                    "descend the spectacular Alb escarpment to Owen and "
                    "Kirchheim. Pass through medieval Esslingen and return "
                    "north via Vaihingen."
                ),
                "midpoint_name": "Bad Urach & Schloss Lichtenstein",
                "midpoint_description": (
                    "The 37 m waterfall at Bad Urach is a short walk from "
                    "parking. Schloss Lichtenstein (1842) clings to a 250 m "
                    "cliff\u2014\u201cthe fairy-tale castle of W\u00fcrttemberg.\u201d"
                ),
                "overnight": None,
                "road_character": (
                    "The Alb escarpment delivers the best curves\u2014steep, "
                    "technical switchbacks with panoramic views. The plateau "
                    "roads are open and fast. A rewarding return ride."
                ),
            },
        ],
    },
    # W05 ---------------------------------------------------------------
    {
        "number": 5,
        "name": "Staufen \u2013 Faust & Southern Black Forest",
        "slug": "staufen_southern_bf",
        "region": "Schwarzwald",
        "difficulty": "Moderate to Challenging",
        "overview": (
            "Ride deep into the southern Black Forest to Staufen im "
            "Breisgau\u2014the town where Doctor Faust supposedly met the "
            "devil. The return takes you over the Belchen and through the "
            "dramatic H\u00f6llental gorge."
        ),
        "highlights": [
            "Staufen \u2013 Faust legend, charming wine town",
            "Belchen (1414 m) \u2013 finest panorama in the Black Forest",
            "H\u00f6llental \u2013 dramatic \u201cHell Valley\u201d gorge",
            "Titisee \u2013 iconic Black Forest lake",
        ],
        "days": [
            {
                "day": 1,
                "title": "Through Central Black Forest to Staufen",
                "distance_km": 280,
                "waypoints": [
                    H_START,
                    ("Pforzheim", 48.891, 8.704, "Gold City", False),
                    ("Calw", 48.714, 8.741, "Hermann Hesse\u2019s town", False),
                    ("Freudenstadt", 48.462, 8.411, "Marktplatz", False),
                    ("Schiltach", 48.290, 8.339, "Half-timbered gem", True),
                    ("Wolfach", 48.293, 8.219, "Glassblowing", False),
                    ("Elzach", 48.173, 8.071, "Elztal", False),
                    ("Waldkirch", 48.094, 7.959, "Kandel views", False),
                    ("Freiburg outskirts", 47.999, 7.842, "BF capital bypass", False),
                    ("Staufen im Breisgau", 47.883, 7.728, "Overnight", False),
                ],
                "description": (
                    "Head south through Pforzheim and Calw into the Black "
                    "Forest via the Nagoldtal to Freudenstadt. Continue to "
                    "the stunning half-timbered Schiltach, then through "
                    "Wolfach and the Elztal to Waldkirch. Pass Freiburg "
                    "to reach Staufen."
                ),
                "midpoint_name": "Schiltach",
                "midpoint_description": (
                    "One of Germany\u2019s best-preserved half-timbered towns, "
                    "where the Schiltach and Kinzig rivers meet. Weinstube "
                    "Zur Alten Br\u00fccke on the riverfront."
                ),
                "overnight": {
                    "name": "Staufen im Breisgau",
                    "description": (
                        "The town where Doctor Faust allegedly met the devil "
                        "in 1539 at the Gasthaus Zum L\u00f6wen (still operating!). "
                        "Charming Altstadt, vineyards on every slope. "
                        "Gasthaus Kreuz-Post for dinner. Hotel Sonne or "
                        "Gasthaus zum L\u00f6wen."
                    ),
                },
                "road_character": (
                    "Classic Black Forest valley riding\u2014Kinzigtal and Elztal "
                    "are flowing with river-following curves."
                ),
            },
            {
                "day": 2,
                "title": "Belchen, Titisee & H\u00f6llental Home",
                "distance_km": 310,
                "waypoints": [
                    ("Staufen im Breisgau", 47.883, 7.728, "Start day 2", False),
                    ("M\u00fcnstertal", 47.856, 7.770, "Valley south", False),
                    ("Belchen (1414 m)", 47.822, 7.831, "Panoramic summit", True),
                    ("Sch\u00f6nau", 47.787, 7.893, "Black Forest village", False),
                    ("Todtnau", 47.826, 7.946, "Waterfall town", False),
                    ("Feldberg area", 47.874, 8.005, "Highest BF peak views", False),
                    ("Titisee", 47.903, 8.157, "Iconic lake", False),
                    ("Hinterzarten", 47.906, 8.110, "Health resort", False),
                    ("H\u00f6llental", 47.897, 8.050, "Hell Valley gorge", False),
                    ("Freiburg", 47.999, 7.842, "BF capital", False),
                    ("Offenburg", 48.473, 7.954, "Ortenau", False),
                    ("Baden-Baden", 48.761, 8.241, "Spa city", False),
                    H_END,
                ],
                "description": (
                    "Ride through the M\u00fcnstertal and climb the spectacular "
                    "Belchen road to 1414 m\u2014the finest panorama in the Black "
                    "Forest. Descend to Sch\u00f6nau and Todtnau, then past the "
                    "Feldberg to Titisee for lunch. Return through Hinterzarten "
                    "and plunge into the H\u00f6llental\u2014a dramatic gorge with sheer "
                    "walls\u2014to Freiburg. Return north via Offenburg and "
                    "Baden-Baden."
                ),
                "midpoint_name": "Belchen (1414 m)",
                "midpoint_description": (
                    "Many consider the Belchen panorama finer than the "
                    "Feldberg\u2019s. On clear days you see the Alps. The Belchen "
                    "road is a motorcyclist\u2019s dream of tight hairpins."
                ),
                "overnight": None,
                "road_character": (
                    "Challenging and rewarding. The Belchen ascent is steep "
                    "with tight hairpins. The H\u00f6llental descent is dramatic "
                    "with tunnels and gorge walls."
                ),
            },
        ],
    },
    # W06 ---------------------------------------------------------------
    {
        "number": 6,
        "name": "Rothenburg ob der Tauber \u2013 Medieval Dream",
        "slug": "rothenburg",
        "region": "Franken / Hohenlohe",
        "difficulty": "Easy to Moderate",
        "overview": (
            "A weekend visiting Germany\u2019s most famous medieval town, "
            "riding through the Hohenlohe countryside on the way there "
            "and the romantic Tauber valley on the return."
        ),
        "highlights": [
            "Rothenburg ob der Tauber \u2013 medieval time capsule",
            "Hohenlohe countryside \u2013 castles at every village",
            "Tauber valley \u2013 romantic river road",
            "Michelstadt or Mosbach on the return",
        ],
        "days": [
            {
                "day": 1,
                "title": "Through Hohenlohe to Rothenburg",
                "distance_km": 210,
                "waypoints": [
                    H_START,
                    ("Sinsheim", 49.253, 8.879, "Head east", False),
                    ("Bad Wimpfen", 49.231, 9.165, "Kaiserpfalz", False),
                    ("Jagsthausen", 49.309, 9.469, "G\u00f6tzenburg", False),
                    ("Kloster Sch\u00f6ntal", 49.328, 9.500, "Baroque abbey", True),
                    ("K\u00fcnzelsau", 49.282, 9.685, "Hohenlohe capital", False),
                    ("Langenburg", 49.254, 9.858, "Castle & car museum", False),
                    ("Kirchberg a.d. Jagst", 49.201, 9.982, "Hilltop town", False),
                    ("Rothenburg o.d. Tauber", 49.377, 10.179, "Overnight", False),
                ],
                "description": (
                    "Ride east through Sinsheim to Bad Wimpfen (hilltop "
                    "Kaiserpfalz), then follow the Jagst valley through "
                    "Jagsthausen and Kloster Sch\u00f6ntal. Continue through the "
                    "Hohenlohe heartland via K\u00fcnzelsau and Langenburg to "
                    "Rothenburg ob der Tauber."
                ),
                "midpoint_name": "Kloster Sch\u00f6ntal",
                "midpoint_description": (
                    "Magnificent Baroque abbey in the Jagst valley. The "
                    "Klosterschenke serves regional dishes in the monastery."
                ),
                "overnight": {
                    "name": "Rothenburg ob der Tauber",
                    "description": (
                        "Walk the complete medieval town wall at sunset. The "
                        "Altstadt is a perfectly preserved medieval time "
                        "capsule. Night watchman tour at 20:00 is a must. "
                        "Hotel Herrnschl\u00f6sschen or Tilman Riemenschneider. "
                        "Dinner at Zur H\u00f6ll (in a 900-year-old building)."
                    ),
                },
                "road_character": (
                    "Gentle, rolling Hohenlohe countryside with moderate "
                    "curves through farmland and forest. Relaxed riding."
                ),
            },
            {
                "day": 2,
                "title": "Tauber Valley & Odenwald Return",
                "distance_km": 220,
                "waypoints": [
                    ("Rothenburg o.d. Tauber", 49.377, 10.179, "Start day 2", False),
                    ("Creglingen", 49.468, 10.031, "Riemenschneider altar", False),
                    ("Weikersheim", 49.479, 9.896, "Renaissance palace", True),
                    ("Bad Mergentheim", 49.493, 9.773, "Teutonic Order castle", False),
                    ("Tauberbischofsheim", 49.623, 9.663, "Tauber valley", False),
                    ("Wertheim", 49.759, 9.509, "Main confluence", False),
                    ("Miltenberg", 49.703, 9.265, "Half-timbered Main town", False),
                    ("Amorbach", 49.645, 9.221, "Baroque abbey", False),
                    ("Michelstadt", 49.676, 9.004, "Fairy-tale Rathaus", False),
                    ("Eberbach", 49.467, 8.988, "Neckar valley", False),
                    H_END,
                ],
                "description": (
                    "Follow the Tauber valley south through Creglingen "
                    "(Riemenschneider altar), Weikersheim (Renaissance palace), "
                    "Bad Mergentheim, and Tauberbischofsheim. At Wertheim, "
                    "join the Main briefly, then head into the Odenwald via "
                    "Miltenberg and Amorbach to Michelstadt. Return through "
                    "Eberbach and the Neckar valley."
                ),
                "midpoint_name": "Weikersheim",
                "midpoint_description": (
                    "The Renaissance palace and its Baroque garden are "
                    "magnificent. The Marktplatz is charming. Gasthaus Rose "
                    "for Tauber valley wines and regional cuisine."
                ),
                "overnight": None,
                "road_character": (
                    "The Tauber valley is gentle and scenic\u2014rolling wine "
                    "country. The Odenwald section adds forest curves."
                ),
            },
        ],
    },
    # W07 ---------------------------------------------------------------
    {
        "number": 7,
        "name": "W\u00fcrzburg \u2013 Baroque & Franconian Wine",
        "slug": "wuerzburg",
        "region": "Franken",
        "difficulty": "Moderate",
        "overview": (
            "Ride through the Odenwald and Main valley to W\u00fcrzburg\u2014home "
            "of the UNESCO Residenz and Franconia\u2019s best wines. Return "
            "through the Tauber valley and Hohenlohe."
        ),
        "highlights": [
            "W\u00fcrzburg Residenz \u2013 UNESCO Baroque palace",
            "Franconian wine country on the Main",
            "Main valley curves through forested hills",
            "Return via Tauber and Hohenlohe",
        ],
        "days": [
            {
                "day": 1,
                "title": "Odenwald & Main Valley to W\u00fcrzburg",
                "distance_km": 210,
                "waypoints": [
                    H_START,
                    ("Eberbach", 49.467, 8.988, "Neckar valley", False),
                    ("Beerfelden", 49.570, 8.977, "Deep Odenwald", False),
                    ("Amorbach", 49.645, 9.221, "Baroque abbey", True),
                    ("Miltenberg", 49.703, 9.265, "Main valley", False),
                    ("B\u00fcrgstadt", 49.719, 9.280, "Red wine village", False),
                    ("Wertheim", 49.759, 9.509, "Castle over the Main", False),
                    ("Marktheidenfeld", 49.844, 9.600, "Main valley", False),
                    ("W\u00fcrzburg", 49.792, 9.934, "Overnight", False),
                ],
                "description": (
                    "Ride east through the Neckar valley to Eberbach, then "
                    "climb into the deep Odenwald to Beerfelden and Amorbach. "
                    "Descend to the Main at Miltenberg and follow the river "
                    "north through Wertheim to W\u00fcrzburg."
                ),
                "midpoint_name": "Amorbach & Miltenberg",
                "midpoint_description": (
                    "Amorbach\u2019s Baroque abbey is stunning. Miltenberg\u2019s "
                    "half-timbered Main riverfront is postcard-perfect."
                ),
                "overnight": {
                    "name": "W\u00fcrzburg",
                    "description": (
                        "The UNESCO Residenz with Tiepolo\u2019s largest ceiling "
                        "fresco is unmissable. Walk across the Alte Mainbr\u00fccke "
                        "at sunset with a Schoppen (glass of Franconian wine). "
                        "Dinner at B\u00fcrgerspital Weinstuben. Hotel Rebstock "
                        "or Hotel W\u00fcrzburger Hof."
                    ),
                },
                "road_character": (
                    "Odenwald forest curves, then the Main valley\u2014flowing "
                    "river road with castle views. Moderate throughout."
                ),
            },
            {
                "day": 2,
                "title": "Tauber Valley & Hohenlohe Return",
                "distance_km": 290,
                "waypoints": [
                    ("W\u00fcrzburg", 49.792, 9.934, "Start day 2", False),
                    ("Ochsenfurt", 49.664, 10.063, "Main valley south", False),
                    ("Tauberbischofsheim", 49.623, 9.663, "Tauber valley", False),
                    ("Lauda-K\u00f6nigshofen", 49.565, 9.710, "Wine town", False),
                    ("Bad Mergentheim", 49.493, 9.773, "Teutonic Knights", True),
                    ("Weikersheim", 49.479, 9.896, "Palace", False),
                    ("Schwäbisch Hall", 49.112, 9.738, "Marktplatz", False),
                    ("\u00d6hringen", 49.201, 9.501, "Hohenlohe", False),
                    ("Neckarsulm", 49.192, 9.225, "Motorcycle museum!", False),
                    ("Sinsheim", 49.253, 8.879, "Return west", False),
                    H_END,
                ],
                "description": (
                    "Head south from W\u00fcrzburg through Ochsenfurt and into "
                    "the Tauber valley. Visit Bad Mergentheim (Teutonic "
                    "Knights castle) and Weikersheim, then ride through "
                    "Hohenlohe to Schwäbisch Hall. Return via \u00d6hringen and "
                    "Neckarsulm\u2014stop at the Deutsches Zweirad-Museum!"
                ),
                "midpoint_name": "Bad Mergentheim",
                "midpoint_description": (
                    "The Teutonic Knights made this their capital. The "
                    "Deutschordensschloss and Wildpark are excellent."
                ),
                "overnight": None,
                "road_character": (
                    "Tauber valley is gentle and scenic. Hohenlohe adds "
                    "rolling hills. The motorcycle museum in Neckarsulm is "
                    "a perfect final stop."
                ),
            },
        ],
    },
    # W08 ---------------------------------------------------------------
    {
        "number": 8,
        "name": "Triberg \u2013 Black Forest Waterfalls",
        "slug": "triberg_waterfalls",
        "region": "Schwarzwald",
        "difficulty": "Moderate",
        "overview": (
            "Ride into the heart of the Black Forest to Triberg\u2014home of "
            "Germany\u2019s highest waterfalls and the cuckoo clock tradition. "
            "Outbound through the Renchtal, return via the "
            "Schwarzwaldhochstra\u00dfe."
        ),
        "highlights": [
            "Triberg waterfalls \u2013 Germany\u2019s highest (163 m)",
            "Cuckoo clock tradition \u2013 world\u2019s largest cuckoo clock",
            "Allerheiligen ruins & waterfalls on the approach",
            "B500 Schwarzwaldhochstra\u00dfe on the return",
        ],
        "days": [
            {
                "day": 1,
                "title": "Renchtal & Allerheiligen to Triberg",
                "distance_km": 220,
                "waypoints": [
                    H_START,
                    ("Rastatt", 48.858, 8.204, "Via Rhine valley", False),
                    ("Achern", 48.628, 8.075, "Enter hills", False),
                    ("Kappelrodeck", 48.592, 8.113, "Red wine village", False),
                    ("Ottenh\u00f6fen", 48.570, 8.152, "Valley end", False),
                    ("Kloster Allerheiligen", 48.538, 8.132, "Ruined monastery", True),
                    ("Oppenau", 48.474, 8.161, "Renchtal", False),
                    ("Bad Peterstal", 48.427, 8.202, "Spa village", False),
                    ("Freudenstadt", 48.462, 8.411, "Marktplatz", False),
                    ("Schiltach", 48.290, 8.339, "Half-timbered", False),
                    ("Triberg", 48.133, 8.237, "Overnight", False),
                ],
                "description": (
                    "Take the A5 to Achern and climb through Kappelrodeck to "
                    "Allerheiligen\u2014the atmospheric ruined monastery with its "
                    "83 m cascading waterfalls. Cross to the Renchtal, ride "
                    "south through Oppenau, then east to Freudenstadt. "
                    "Continue through Schiltach to Triberg."
                ),
                "midpoint_name": "Kloster Allerheiligen",
                "midpoint_description": (
                    "Gothic ruins draped in ivy with 83 m waterfalls below. "
                    "The climb is steep with tight switchbacks."
                ),
                "overnight": {
                    "name": "Triberg",
                    "description": (
                        "Germany\u2019s highest waterfalls cascade 163 m through "
                        "forest. The town is the center of cuckoo clock "
                        "culture. Visit the Schwarzwaldmuseum. Restaurant "
                        "Zum B\u00e4ren for Schwarzw\u00e4lder Kirschtorte. Parkhotel "
                        "Wehrle or Romantik Hotel Spielweg (nearby)."
                    ),
                },
                "road_character": (
                    "The Allerheiligen climb is the most technical in this "
                    "collection\u2014steep switchbacks. Valley riding after is "
                    "flowing and scenic."
                ),
            },
            {
                "day": 2,
                "title": "Gutachtal & Schwarzwaldhochstra\u00dfe Home",
                "distance_km": 250,
                "waypoints": [
                    ("Triberg", 48.133, 8.237, "Start day 2", False),
                    ("Hornberg", 48.212, 8.228, "Valley town", False),
                    ("Gutach (Vogtsbauernhof)", 48.256, 8.180, "Open-air museum", False),
                    ("Hausach", 48.282, 8.175, "Kinzigtal", False),
                    ("Gengenbach", 48.407, 8.015, "Nice of the BF", True),
                    ("Sasbachwalden", 48.619, 8.120, "Flower village", False),
                    ("B500 Sand", 48.654, 8.226, "Join Hochstra\u00dfe", False),
                    ("Mummelsee", 48.596, 8.201, "Mountain lake", False),
                    ("Baden-Baden", 48.761, 8.241, "Spa city", False),
                    H_END,
                ],
                "description": (
                    "Ride north through the Gutachtal past the "
                    "Vogtsbauernhof, then through the Kinzigtal to beautiful "
                    "Gengenbach. Climb to Sasbachwalden and join the B500 at "
                    "Sand. Ride the Schwarzwaldhochstra\u00dfe past the Mummelsee "
                    "and descend through Baden-Baden. A5 north home."
                ),
                "midpoint_name": "Gengenbach",
                "midpoint_description": (
                    "Called \u201cthe Nice of the Black Forest\u201d for its "
                    "Mediterranean flair. Stunning Altstadt and Rathaus."
                ),
                "overnight": None,
                "road_character": (
                    "Valley riding through Gutachtal and Kinzigtal, then "
                    "the sweeping B500 ridge\u2014a perfect day 2."
                ),
            },
        ],
    },
    # W09 ---------------------------------------------------------------
    {
        "number": 9,
        "name": "Munster \u2013 Vosges Mountain Passes",
        "slug": "munster_vosges",
        "region": "Elsass / Vosges",
        "difficulty": "Moderate to Challenging",
        "overview": (
            "Cross into France for a night in the Munster valley\u2014famous "
            "for its pungent cheese\u2014surrounded by the highest peaks of "
            "the Vosges mountains. Two days of mountain pass riding."
        ),
        "highlights": [
            "Munster valley \u2013 cheese and mountain meadows",
            "Col de la Schlucht \u2013 classic Vosges pass",
            "Route des Cr\u00eates \u2013 WWI ridge road",
            "Grand Ballon (1424 m) \u2013 highest Vosges summit",
        ],
        "days": [
            {
                "day": 1,
                "title": "Alsace Wine Route to Munster",
                "distance_km": 270,
                "waypoints": [
                    H_START,
                    ("Karlsruhe", 49.006, 8.404, "A5 south", False),
                    ("Kehl", 48.572, 7.818, "Cross Rhine", False),
                    ("Strasbourg", 48.573, 7.752, "Alsatian capital", False),
                    ("Obernai", 48.462, 7.483, "Alsatian gem", True),
                    ("Barr", 48.407, 7.449, "Wine capital", False),
                    ("Andlau", 48.387, 7.417, "Romanesque abbey", False),
                    ("Ribeauvill\u00e9", 48.194, 7.318, "Three castles", False),
                    ("Kaysersberg", 48.140, 7.264, "Albert Schweitzer", False),
                    ("Munster", 48.042, 7.137, "Overnight", False),
                ],
                "description": (
                    "Head south on the A5 to Kehl, cross the Rhine into "
                    "Strasbourg, then join the Alsace Wine Route. Head south "
                    "through a parade of half-timbered villages\u2014Obernai, "
                    "Barr, Andlau, Ribeauvill\u00e9, Kaysersberg\u2014to the Munster "
                    "valley."
                ),
                "midpoint_name": "Obernai",
                "midpoint_description": (
                    "Quintessential Alsatian town. Winstub Le Caveau de "
                    "Gail for choucroute garnie and Gew\u00fcrztraminer."
                ),
                "overnight": {
                    "name": "Munster",
                    "description": (
                        "The valley that gave Munster cheese its name. "
                        "Try the cheese at the march\u00e9 or a ferme-auberge. "
                        "The town is a quiet base for the mountain passes. "
                        "H\u00f4tel Deybach or Verte Vall\u00e9e."
                    ),
                },
                "road_character": (
                    "Gentle Alsace wine route riding\u2014scenic and relaxed. "
                    "The focus today is food, wine, and scenery."
                ),
            },
            {
                "day": 2,
                "title": "Vosges Passes & Grand Ballon Return",
                "distance_km": 320,
                "waypoints": [
                    ("Munster", 48.042, 7.137, "Start day 2", False),
                    ("Col de la Schlucht (1139 m)", 48.063, 7.023, "Mountain pass", False),
                    ("Hohneck (1363 m)", 48.040, 7.007, "Vosges peak views", False),
                    ("Route des Cr\u00eates", 47.977, 7.053, "Ridge road", True),
                    ("Le Markstein", 47.929, 7.032, "Ski station", False),
                    ("Grand Ballon (1424 m)", 47.902, 7.099, "Highest Vosges peak", False),
                    ("Guebwiller", 47.912, 7.210, "Rangen vineyard", False),
                    ("Colmar", 48.079, 7.359, "Little Venice", False),
                    ("Rhinau", 48.318, 7.711, "Cross Rhine", False),
                    ("Offenburg", 48.473, 7.954, "Ortenau", False),
                    ("Baden-Baden", 48.761, 8.241, "Spa city", False),
                    H_END,
                ],
                "description": (
                    "Climb to the Col de la Schlucht, then ride the Route "
                    "des Cr\u00eates\u2014the dramatic ridge road with views into both "
                    "valleys. Summit the Grand Ballon (1424 m), descend to "
                    "Guebwiller, detour through Colmar\u2019s \u201cLittle Venice,\u201d "
                    "cross the Rhine at Rhinau, and return via Offenburg and "
                    "Baden-Baden."
                ),
                "midpoint_name": "Route des Cr\u00eates & Grand Ballon",
                "midpoint_description": (
                    "The ridge road at 1200\u20131400 m with alpine meadows and "
                    "views to the Alps on clear days. Ferme-Auberge du "
                    "Grand Ballon for a summit lunch."
                ),
                "overnight": None,
                "road_character": (
                    "Mountain pass riding at its best. The Col de la "
                    "Schlucht and Route des Cr\u00eates are sweeping; the Grand "
                    "Ballon descent is steep with hairpins."
                ),
            },
        ],
    },
    # W10 ---------------------------------------------------------------
    {
        "number": 10,
        "name": "Idar-Oberstein \u2013 Hunsr\u00fcck Gemstone Country",
        "slug": "idar_oberstein",
        "region": "Hunsr\u00fcck / Nahe",
        "difficulty": "Moderate",
        "overview": (
            "Discover the wild Hunsr\u00fcck highlands and the gemstone city "
            "of Idar-Oberstein\u2014where a church is built into a cliff face "
            "and precious stones have been cut for centuries."
        ),
        "highlights": [
            "Idar-Oberstein \u2013 Felsenkirche built into a cliff",
            "Hunsr\u00fcck Hochwald \u2013 wild highland landscape",
            "Nahe valley wine region",
            "Pf\u00e4lzerwald forest roads",
        ],
        "days": [
            {
                "day": 1,
                "title": "Pf\u00e4lzerwald & Hunsr\u00fcck to Idar-Oberstein",
                "distance_km": 200,
                "waypoints": [
                    H_START,
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Wine route", False),
                    ("Johanniskreuz", 49.348, 7.850, "Biker crossroads", False),
                    ("Lauterecken", 49.650, 7.588, "Glan valley", True),
                    ("Meisenheim", 49.708, 7.669, "Medieval gem", False),
                    ("Kirn", 49.789, 7.455, "Nahe valley", False),
                    ("Idar-Oberstein", 49.714, 7.308, "Overnight", False),
                ],
                "description": (
                    "Cross the Rhine at Speyer and ride through the "
                    "Pf\u00e4lzerwald to Johanniskreuz. Continue northwest "
                    "through Lauterecken and the medieval town of Meisenheim, "
                    "then up the Nahe to Kirn and Idar-Oberstein."
                ),
                "midpoint_name": "Lauterecken & Meisenheim",
                "midpoint_description": (
                    "Lauterecken sits at the Glan-Lauter confluence. "
                    "Meisenheim is one of the few towns in the Pfalz never "
                    "destroyed by war\u2014its medieval fabric is intact."
                ),
                "overnight": {
                    "name": "Idar-Oberstein",
                    "description": (
                        "The Felsenkirche (cliff church) is carved into a "
                        "rock face 60 m above the valley\u2014extraordinary. "
                        "Visit the Edelsteinmuseum (gemstone museum) and the "
                        "Edelsteinminen (gem mines). Restaurant Bl\u00e4ttch\u2019s "
                        "for regional dishes. Hotel Handelshof."
                    ),
                },
                "road_character": (
                    "Pf\u00e4lzerwald forest curves followed by open Glan and "
                    "Nahe valley riding. Varied and interesting."
                ),
            },
            {
                "day": 2,
                "title": "Hunsr\u00fcck Heights & Nahe Valley Home",
                "distance_km": 280,
                "waypoints": [
                    ("Idar-Oberstein", 49.714, 7.308, "Start day 2", False),
                    ("Birkenfeld", 49.649, 7.163, "Hunsr\u00fcck", False),
                    ("Thalfang", 49.754, 7.010, "Erbeskopf nearby", False),
                    ("Hunsr\u00fcck Hochwald", 49.720, 7.060, "Wild highlands", True),
                    ("Morbach", 49.810, 7.130, "Forest town", False),
                    ("Bad Sobernheim", 49.783, 7.647, "Barefoot trail", False),
                    ("Bad Kreuznach", 49.842, 7.867, "Nahe wines", False),
                    ("Alsenz valley", 49.750, 7.850, "Through to Pfalz", False),
                    ("Bad D\u00fcrkheim", 49.462, 8.172, "Wine barrel", False),
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    H_END,
                ],
                "description": (
                    "Ride through Birkenfeld and climb to the Hunsr\u00fcck "
                    "Hochwald near Thalfang (the Erbeskopf at 816 m is the "
                    "highest point in Rhineland-Palatinate). Cross the "
                    "highlands to Morbach, then descend to the Nahe valley "
                    "at Bad Sobernheim. Follow the Nahe east to Bad "
                    "Kreuznach, cross through the Alsenz valley to the Pfalz, "
                    "and return via Bad D\u00fcrkheim and Speyer."
                ),
                "midpoint_name": "Hunsr\u00fcck Hochwald",
                "midpoint_description": (
                    "Wild highland plateau with open heathland and dense "
                    "forest. The national park here is one of Germany\u2019s "
                    "newest. Remote and atmospheric."
                ),
                "overnight": None,
                "road_character": (
                    "The Hunsr\u00fcck is open and sweeping\u2014long curves through "
                    "heath and forest. The Nahe valley is flowing wine "
                    "country. Relaxed return through the Pfalz."
                ),
            },
        ],
    },
]

# ===================================================================
# THREE-DAY TOURS  (5 tours)
# ===================================================================
THREE_DAY_TOURS = [
    # T01 ---------------------------------------------------------------
    {
        "number": 1,
        "name": "Black Forest Grand Circuit",
        "slug": "bf_grand_circuit",
        "region": "Schwarzwald",
        "difficulty": "Moderate to Challenging",
        "overview": (
            "Three days through the full length of the Black Forest\u2014from "
            "the B500 ridge in the north to the Belchen and H\u00f6llental in "
            "the south. The definitive Black Forest motorcycle tour."
        ),
        "highlights": [
            "B500 Schwarzwaldhochstra\u00dfe \u2013 complete ridge ride",
            "Triberg waterfalls and Kinzigtal",
            "Titisee, Feldberg & Belchen summits",
            "H\u00f6llental gorge and Freiburg",
        ],
        "days": [
            {
                "day": 1,
                "title": "Schwarzwaldhochstra\u00dfe to Triberg",
                "distance_km": 210,
                "waypoints": [
                    H_START,
                    ("Baden-Baden", 48.761, 8.241, "Spa city (via A5)", False),
                    ("B\u00fchlerh\u00f6he", 48.683, 8.223, "Join B500", False),
                    ("Mummelsee", 48.596, 8.201, "Mountain lake", True),
                    ("Ruhestein", 48.561, 8.221, "National Park", False),
                    ("Freudenstadt", 48.462, 8.411, "Largest Marktplatz", False),
                    ("Alpirsbach", 48.346, 8.403, "Brewery", False),
                    ("Schiltach", 48.290, 8.339, "Half-timbered", False),
                    ("Triberg", 48.133, 8.237, "Overnight", False),
                ],
                "description": (
                    "Ride the full B500 from Baden-Baden to Freudenstadt, "
                    "then south through Alpirsbach and Schiltach to Triberg."
                ),
                "midpoint_name": "Mummelsee",
                "midpoint_description": "Mystical lake at 1036 m. Berghotel for lunch.",
                "overnight": {
                    "name": "Triberg",
                    "description": "Germany\u2019s highest waterfalls (163 m). Cuckoo clock capital. Parkhotel Wehrle.",
                },
                "road_character": "B500 ridge curves followed by valley riding. A classic first day.",
            },
            {
                "day": 2,
                "title": "Titisee, Belchen & Staufen",
                "distance_km": 170,
                "waypoints": [
                    ("Triberg", 48.133, 8.237, "Start day 2", False),
                    ("Furtwangen", 48.055, 8.208, "Clock museum", False),
                    ("Titisee", 47.903, 8.157, "Iconic lake", True),
                    ("Hinterzarten", 47.906, 8.110, "Health resort", False),
                    ("Feldberg area", 47.874, 8.005, "Highest BF peak", False),
                    ("Todtnau", 47.826, 7.946, "Waterfall town", False),
                    ("Belchen (1414 m)", 47.822, 7.831, "Finest panorama", False),
                    ("M\u00fcnstertal", 47.856, 7.770, "Southern valley", False),
                    ("Staufen im Breisgau", 47.883, 7.728, "Overnight", False),
                ],
                "description": (
                    "Ride to Furtwangen (clock museum), then to the Titisee. "
                    "Continue through Hinterzarten past the Feldberg to "
                    "Todtnau, climb the Belchen, and descend through the "
                    "M\u00fcnstertal to Staufen."
                ),
                "midpoint_name": "Titisee",
                "midpoint_description": "Iconic Black Forest lake at 858 m. Lakeside lunch.",
                "overnight": {
                    "name": "Staufen im Breisgau",
                    "description": "Faust legend town. Gasthaus Zum L\u00f6wen. Vineyards everywhere.",
                },
                "road_character": "Mixed\u2014flowing valley roads and steep Belchen hairpins.",
            },
            {
                "day": 3,
                "title": "H\u00f6llental & Kinzigtal Home",
                "distance_km": 350,
                "waypoints": [
                    ("Staufen im Breisgau", 47.883, 7.728, "Start day 3", False),
                    ("Freiburg", 47.999, 7.842, "BF capital", False),
                    ("Kirchzarten", 47.963, 7.952, "H\u00f6llental entrance", False),
                    ("H\u00f6llental", 47.897, 8.050, "Hell Valley gorge", True),
                    ("Hinterzarten", 47.906, 8.110, "Health resort", False),
                    ("Elzach", 48.173, 8.071, "Elztal", False),
                    ("Wolfach", 48.293, 8.219, "Kinzigtal", False),
                    ("Gengenbach", 48.407, 8.015, "Gengenbach", False),
                    ("Oberkirch", 48.528, 8.078, "Renchtal", False),
                    ("Baden-Baden", 48.761, 8.241, "Spa city", False),
                    H_END,
                ],
                "description": (
                    "From Staufen, ride through Freiburg and up the dramatic "
                    "H\u00f6llental gorge. Continue through Hinterzarten and the "
                    "Elztal north to Wolfach and Gengenbach. Return via "
                    "Oberkirch and Baden-Baden."
                ),
                "midpoint_name": "H\u00f6llental",
                "midpoint_description": "Dramatic gorge with sheer walls and the famous Hirschsprung narrows.",
                "overnight": None,
                "road_character": "H\u00f6llental is dramatic, Elztal and Kinzigtal are flowing valley curves.",
            },
        ],
    },
    # T02 ---------------------------------------------------------------
    {
        "number": 2,
        "name": "Alsace & Vosges Explorer",
        "slug": "alsace_vosges",
        "region": "Elsass / Vosges",
        "difficulty": "Moderate",
        "overview": (
            "Three days exploring Alsace from north to south\u2014the wine "
            "route, the Vosges mountain passes, and the southern "
            "vineyard villages. An immersion in France\u2019s most Germanic "
            "and gastronomic region."
        ),
        "highlights": [
            "Full Alsace Wine Route from north to south",
            "Vosges passes \u2013 Col du Donon, Col de la Schlucht",
            "Route des Cr\u00eates ridge road",
            "Colmar, Riquewihr, Kaysersberg \u2013 Alsatian jewels",
        ],
        "days": [
            {
                "day": 1,
                "title": "Pf\u00e4lzerwald to Northern Alsace",
                "distance_km": 270,
                "waypoints": [
                    H_START,
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    ("Wissembourg", 49.037, 7.945, "Cross into France", False),
                    ("Lembach", 49.003, 7.788, "Ch\u00e2teau Fleckenstein", False),
                    ("Niederbronn-les-Bains", 48.952, 7.643, "Thermal spa", False),
                    ("Bitche", 49.052, 7.430, "Vauban citadel", True),
                    ("Col du Donon (727 m)", 48.519, 7.131, "Vosges pass", False),
                    ("Schirmeck", 48.479, 7.220, "Vosges valley", False),
                    ("Obernai", 48.462, 7.483, "Overnight", False),
                ],
                "description": (
                    "Cross into France at Wissembourg, visit Ch\u00e2teau "
                    "Fleckenstein, then ride to Bitche\u2019s Vauban citadel. "
                    "Cross the Col du Donon and descend to Obernai."
                ),
                "midpoint_name": "Bitche Citadel",
                "midpoint_description": "Vauban\u2019s masterpiece fortress on sandstone cliffs.",
                "overnight": {
                    "name": "Obernai",
                    "description": "Half-timbered Marktplatz, Kappelturm tower. Winstub cuisine. H\u00f4tel Le Colombier.",
                },
                "road_character": "Northern Vosges forest roads, then the Col du Donon climb.",
            },
            {
                "day": 2,
                "title": "Wine Route & Vosges Passes",
                "distance_km": 130,
                "waypoints": [
                    ("Obernai", 48.462, 7.483, "Start day 2", False),
                    ("Mont Sainte-Odile", 48.437, 7.404, "Pilgrimage site", False),
                    ("Barr", 48.407, 7.449, "Wine capital", False),
                    ("Ribeauvill\u00e9", 48.194, 7.318, "Three castles", True),
                    ("Riquewihr", 48.167, 7.298, "Walled wine village", False),
                    ("Kaysersberg", 48.140, 7.264, "Schweitzer\u2019s birthplace", False),
                    ("Munster", 48.042, 7.137, "Cheese valley", False),
                    ("Col de la Schlucht", 48.063, 7.023, "Mountain pass (1139 m)", False),
                    ("G\u00e9rardmer", 48.073, 6.879, "Overnight", False),
                ],
                "description": (
                    "Visit Mont Sainte-Odile, then ride the wine route south "
                    "through Barr, Ribeauvill\u00e9, Riquewihr, and Kaysersberg. "
                    "Climb through the Munster valley to the Col de la Schlucht "
                    "and descend to G\u00e9rardmer."
                ),
                "midpoint_name": "Ribeauvill\u00e9 & Riquewihr",
                "midpoint_description": "The two most photogenic wine villages in Alsace.",
                "overnight": {
                    "name": "G\u00e9rardmer",
                    "description": "Lake resort in the Vosges. Famous for Munster cheese. H\u00f4tel Le Grand H\u00f4tel.",
                },
                "road_character": "Wine route villages, then mountain pass climbing.",
            },
            {
                "day": 3,
                "title": "Route des Cr\u00eates & Colmar Return",
                "distance_km": 340,
                "waypoints": [
                    ("G\u00e9rardmer", 48.073, 6.879, "Start day 3", False),
                    ("La Bresse", 48.001, 6.869, "Ski resort", False),
                    ("Route des Cr\u00eates", 47.977, 7.053, "Ridge road", True),
                    ("Grand Ballon (1424 m)", 47.902, 7.099, "Highest Vosges", False),
                    ("Guebwiller", 47.912, 7.210, "Rangen Grand Cru", False),
                    ("Eguisheim", 48.042, 7.306, "Circular wine village", False),
                    ("Colmar", 48.079, 7.359, "Little Venice", False),
                    ("Rhinau", 48.318, 7.711, "Cross Rhine", False),
                    ("Offenburg", 48.473, 7.954, "Ortenau", False),
                    ("Baden-Baden", 48.761, 8.241, "Spa city", False),
                    H_END,
                ],
                "description": (
                    "Ride through La Bresse and join the Route des Cr\u00eates "
                    "south to the Grand Ballon. Descend to Guebwiller, visit "
                    "circular Eguisheim and Colmar\u2019s \u201cLittle Venice,\u201d then "
                    "cross the Rhine at Rhinau and return via Offenburg and "
                    "Baden-Baden."
                ),
                "midpoint_name": "Route des Cr\u00eates",
                "midpoint_description": "The Vosges ridge road at 1200\u20131400 m. Alpine views on clear days.",
                "overnight": None,
                "road_character": "Mountain ridge riding, then gentle descent through wine country.",
            },
        ],
    },
    # T03 ---------------------------------------------------------------
    {
        "number": 3,
        "name": "Franconia & Tauber Valley",
        "slug": "franconia_tauber",
        "region": "Franken / Tauber",
        "difficulty": "Moderate",
        "overview": (
            "Three days through Franconia\u2014Germany\u2019s wine and culture "
            "heartland. W\u00fcrzburg\u2019s Baroque splendor, Rothenburg\u2019s "
            "medieval walls, and the romantic Tauber valley."
        ),
        "highlights": [
            "W\u00fcrzburg Residenz (UNESCO) and Franconian wine",
            "Rothenburg ob der Tauber",
            "Romantic Tauber valley",
            "Odenwald forest roads",
        ],
        "days": [
            {
                "day": 1, "title": "Odenwald & Main to W\u00fcrzburg",
                "distance_km": 210,
                "waypoints": [
                    H_START,
                    ("Eberbach", 49.467, 8.988, "Neckar valley", False),
                    ("Beerfelden", 49.570, 8.977, "Deep Odenwald", False),
                    ("Amorbach", 49.645, 9.221, "Baroque abbey", True),
                    ("Miltenberg", 49.703, 9.265, "Main valley", False),
                    ("Wertheim", 49.759, 9.509, "Main confluence", False),
                    ("W\u00fcrzburg", 49.792, 9.934, "Overnight", False),
                ],
                "description": "Through the Odenwald to Amorbach and the Main valley to W\u00fcrzburg.",
                "midpoint_name": "Amorbach", "midpoint_description": "Stunning Baroque abbey.",
                "overnight": {"name": "W\u00fcrzburg", "description": "UNESCO Residenz, Alte Mainbr\u00fccke at sunset. B\u00fcrgerspital Weinstuben."},
                "road_character": "Odenwald forest curves, then flowing Main valley.",
            },
            {
                "day": 2, "title": "Franconian Wine to Rothenburg",
                "distance_km": 130,
                "waypoints": [
                    ("W\u00fcrzburg", 49.792, 9.934, "Start day 2", False),
                    ("Ochsenfurt", 49.664, 10.063, "Medieval town", False),
                    ("Tauberbischofsheim", 49.623, 9.663, "Tauber valley", False),
                    ("Bad Mergentheim", 49.493, 9.773, "Teutonic Knights", True),
                    ("Weikersheim", 49.479, 9.896, "Palace gardens", False),
                    ("Creglingen", 49.468, 10.031, "Riemenschneider altar", False),
                    ("Rothenburg o.d. Tauber", 49.377, 10.179, "Overnight", False),
                ],
                "description": "South from W\u00fcrzburg through the Tauber valley to Rothenburg.",
                "midpoint_name": "Bad Mergentheim", "midpoint_description": "Teutonic Order castle and gardens.",
                "overnight": {"name": "Rothenburg o.d. Tauber", "description": "Walk the town wall at sunset. Night watchman tour. Zur H\u00f6ll restaurant."},
                "road_character": "Gentle Tauber valley. Scenic wine country.",
            },
            {
                "day": 3, "title": "Hohenlohe & Neckar Return",
                "distance_km": 210,
                "waypoints": [
                    ("Rothenburg o.d. Tauber", 49.377, 10.179, "Start day 3", False),
                    ("Feuchtwangen", 49.167, 10.328, "Market town", False),
                    ("Crailsheim", 49.134, 10.072, "Eastern Hohenlohe", False),
                    ("Schw\u00e4bisch Hall", 49.112, 9.738, "Theatrical Marktplatz", True),
                    ("\u00d6hringen", 49.201, 9.501, "Hohenlohe", False),
                    ("Neckarsulm", 49.192, 9.225, "Motorcycle museum", False),
                    ("Bad Wimpfen", 49.231, 9.165, "Kaiserpfalz", False),
                    ("Sinsheim", 49.253, 8.879, "Return west", False),
                    H_END,
                ],
                "description": "Through Hohenlohe via Schw\u00e4bisch Hall, the motorcycle museum, and Bad Wimpfen home.",
                "midpoint_name": "Schw\u00e4bisch Hall", "midpoint_description": "Dramatic Marktplatz staircase. Brauereigasthof Zum L\u00f6wen.",
                "overnight": None,
                "road_character": "Rolling Hohenlohe countryside. Gentle, scenic return.",
            },
        ],
    },
    # T04 ---------------------------------------------------------------
    {
        "number": 4,
        "name": "Moselle, Eifel & Rhine",
        "slug": "moselle_eifel_rhine",
        "region": "Mosel / Eifel / Rhein",
        "difficulty": "Moderate",
        "overview": (
            "Three days through western Germany\u2019s most dramatic river "
            "valleys\u2014the Moselle, the Ahr, and the Rhine\u2014with a detour "
            "to the N\u00fcrburgring and the volcanic Eifel."
        ),
        "highlights": [
            "Bernkastel-Kues and Cochem \u2013 Moselle wine towns",
            "N\u00fcrburgring \u2013 legendary circuit",
            "Ahr valley \u2013 red wine gorge",
            "Loreley and Rhine gorge castles",
        ],
        "days": [
            {
                "day": 1, "title": "Pf\u00e4lzerwald to the Moselle",
                "distance_km": 280,
                "waypoints": [
                    H_START,
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    ("Johanniskreuz", 49.348, 7.850, "Forest crossroads", False),
                    ("Kusel", 49.533, 7.400, "Burg Lichtenberg", False),
                    ("Idar-Oberstein", 49.714, 7.308, "Gemstone city", True),
                    ("Morbach", 49.810, 7.130, "Hunsr\u00fcck", False),
                    ("Bernkastel-Kues", 49.915, 7.068, "Moselle wine", False),
                    ("Traben-Trarbach", 49.947, 7.118, "Art Nouveau town", False),
                    ("Cochem", 50.146, 7.167, "Overnight", False),
                ],
                "description": "Through the Pf\u00e4lzerwald and Hunsr\u00fcck to Bernkastel, then along the Moselle to Cochem.",
                "midpoint_name": "Idar-Oberstein", "midpoint_description": "Felsenkirche in the cliff, gemstone museum.",
                "overnight": {"name": "Cochem", "description": "Reichsburg castle above the Moselle, wine taverns along the river. Hotel Am Hafen."},
                "road_character": "Forest roads, highland crossing, then Moselle valley curves.",
            },
            {
                "day": 2, "title": "Eifel, N\u00fcrburgring & Ahr Valley",
                "distance_km": 130,
                "waypoints": [
                    ("Cochem", 50.146, 7.167, "Start day 2", False),
                    ("Burg Eltz", 50.205, 7.337, "Fairy-tale castle", False),
                    ("Mayen", 50.328, 7.223, "Eifel town", False),
                    ("N\u00fcrburgring", 50.336, 6.943, "Legendary circuit", True),
                    ("Adenau", 50.383, 6.931, "Eifel village", False),
                    ("Altenahr", 50.518, 6.985, "Ahr gorge", False),
                    ("Bad Neuenahr-Ahrweiler", 50.543, 7.112, "Overnight", False),
                ],
                "description": "Visit Burg Eltz, ride through the Eifel to the N\u00fcrburgring, then through the Ahr valley.",
                "midpoint_name": "N\u00fcrburgring", "midpoint_description": "The legendary \u201cGreen Hell.\u201d Visitor center and Nordschleife.",
                "overnight": {"name": "Bad Neuenahr-Ahrweiler", "description": "Wine town recovering from the 2021 flood. Excellent Ahr valley reds. Steinheuers Restaurant."},
                "road_character": "Eifel highlands, then the tight Ahr gorge\u2014excellent motorcycle country.",
            },
            {
                "day": 3, "title": "Rhine Gorge & Nahe Valley Home",
                "distance_km": 270,
                "waypoints": [
                    ("Bad Neuenahr-Ahrweiler", 50.543, 7.112, "Start day 3", False),
                    ("Remagen", 50.578, 7.233, "Bridge at Remagen", False),
                    ("Koblenz", 50.354, 7.599, "Deutsches Eck", False),
                    ("Boppard", 50.230, 7.593, "Rhine bend", False),
                    ("St. Goar / Loreley", 50.153, 7.711, "Legendary rock", True),
                    ("Bacharach", 50.059, 7.770, "Rhine wine town", False),
                    ("Bingen", 49.966, 7.895, "Nahe confluence", False),
                    ("Bad Kreuznach", 49.842, 7.867, "Nahe wines", False),
                    ("Bad D\u00fcrkheim", 49.462, 8.172, "Wine barrel", False),
                    H_END,
                ],
                "description": "Rhine south from Koblenz through the Loreley gorge, then Nahe valley and Pfalz home.",
                "midpoint_name": "Loreley & Rhine Gorge", "midpoint_description": "UNESCO Rhine gorge with castle ruins on every hilltop.",
                "overnight": None,
                "road_character": "Rhine valley is scenic and moderate. Nahe valley is flowing wine country.",
            },
        ],
    },
    # T05 ---------------------------------------------------------------
    {
        "number": 5,
        "name": "Schw\u00e4bische Alb & Danube Sources",
        "slug": "schwaebische_alb",
        "region": "Schw\u00e4bische Alb",
        "difficulty": "Moderate",
        "overview": (
            "Three days exploring the Schw\u00e4bische Alb\u2014the limestone "
            "escarpment south of Stuttgart with spectacular castle ruins, "
            "caves, and the young Danube."
        ),
        "highlights": [
            "Schw\u00e4bisch Hall \u2013 theatrical medieval town",
            "Blaubeuren Blautopf \u2013 magical blue spring",
            "Schloss Lichtenstein \u2013 fairy-tale castle",
            "Alb escarpment switchbacks",
        ],
        "days": [
            {
                "day": 1, "title": "Through Hohenlohe to Heidenheim",
                "distance_km": 210,
                "waypoints": [
                    H_START,
                    ("Sinsheim", 49.253, 8.879, "Head east", False),
                    ("Heilbronn", 49.142, 9.220, "Bypass", False),
                    ("Weinsberg", 49.151, 9.286, "Weibertreu castle", False),
                    ("Schw\u00e4bisch Hall", 49.112, 9.738, "Marktplatz", True),
                    ("Gaildorf", 48.995, 9.770, "Kocher valley", False),
                    ("Aalen", 48.837, 10.093, "Limes museum", False),
                    ("Heidenheim a.d. Brenz", 48.676, 10.152, "Overnight", False),
                ],
                "description": "East through Heilbronn to Schwäbisch Hall, then south through the Kocher valley to Heidenheim.",
                "midpoint_name": "Schw\u00e4bisch Hall", "midpoint_description": "Germany\u2019s most dramatic Marktplatz. Brauereigasthof Zum L\u00f6wen.",
                "overnight": {"name": "Heidenheim a.d. Brenz", "description": "Gateway to the eastern Alb. Schloss Hellenstein above the town. Hotel Linde."},
                "road_character": "Hohenlohe hills, then Kocher valley curves.",
            },
            {
                "day": 2, "title": "Eastern Alb to T\u00fcbingen",
                "distance_km": 200,
                "waypoints": [
                    ("Heidenheim a.d. Brenz", 48.676, 10.152, "Start day 2", False),
                    ("Blaubeuren", 48.412, 9.783, "Blautopf spring", True),
                    ("M\u00fcnsingen", 48.412, 9.497, "Alb plateau", False),
                    ("Schloss Lichtenstein", 48.408, 9.260, "Fairy-tale castle", False),
                    ("Bad Urach", 48.494, 9.397, "Waterfall", False),
                    ("Reutlingen", 48.492, 9.214, "Alb foot", False),
                    ("T\u00fcbingen", 48.522, 9.057, "Overnight", False),
                ],
                "description": "Cross the Alb to Blaubeuren\u2019s blue spring, visit Lichtenstein and Bad Urach, descend to T\u00fcbingen.",
                "midpoint_name": "Blaubeuren Blautopf", "midpoint_description": "An impossibly blue karst spring. The monastery is beautiful.",
                "overnight": {"name": "T\u00fcbingen", "description": "Romantic university town. Punting on the Neckar. Weinstube Forelle."},
                "road_character": "Alb plateau roads, dramatic escarpment descents, switchbacks.",
            },
            {
                "day": 3, "title": "Nagoldtal & Black Forest Edge Home",
                "distance_km": 200,
                "waypoints": [
                    ("T\u00fcbingen", 48.522, 9.057, "Start day 3", False),
                    ("Rottenburg", 48.476, 8.935, "Cathedral town", False),
                    ("Horb am Neckar", 48.445, 8.692, "Neckar valley", False),
                    ("Nagold", 48.551, 8.724, "Nagold river", True),
                    ("Calw", 48.714, 8.741, "Hesse\u2019s birthplace", False),
                    ("Bad Liebenzell", 48.775, 8.732, "Thermal springs", False),
                    ("Pforzheim", 48.891, 8.704, "Gold city", False),
                    ("Bretten", 49.036, 8.707, "Melanchthon", False),
                    H_END,
                ],
                "description": "Follow the young Neckar to Horb, then the Nagold valley north through Calw and Pforzheim home.",
                "midpoint_name": "Nagold valley", "midpoint_description": "Flowing forest river road\u2014classic motorcycle curves.",
                "overnight": None,
                "road_character": "Neckar and Nagold valley curves. A flowing, scenic finale.",
            },
        ],
    },
]

# ===================================================================
# SIX-DAY TOURS  (5 tours)
# ===================================================================
SIX_DAY_TOURS = [
    # S01 ---------------------------------------------------------------
    {
        "number": 1,
        "name": "Black Forest to the Alps",
        "slug": "bf_to_alps",
        "region": "Schwarzwald / Bodensee / Allg\u00e4u",
        "difficulty": "Moderate to Challenging",
        "overview": (
            "The ultimate southwest Germany tour\u2014ride the full Black "
            "Forest from ridge to lake, cross to Lake Constance, reach "
            "the Allg\u00e4u Alps, and return over the Schw\u00e4bische Alb. Six "
            "days, six different landscapes."
        ),
        "highlights": [
            "B500 Schwarzwaldhochstra\u00dfe",
            "Titisee, Belchen & southern Black Forest",
            "Rhine Falls at Schaffhausen",
            "Lake Constance (Meersburg)",
            "Allg\u00e4u Alps (Oberstdorf)",
            "Schw\u00e4bische Alb return",
        ],
        "days": [
            {
                "day": 1, "title": "Schwarzwaldhochstra\u00dfe to Baiersbronn",
                "distance_km": 160,
                "waypoints": [
                    H_START,
                    ("Baden-Baden", 48.761, 8.241, "Via A5", False),
                    ("B\u00fchlerh\u00f6he", 48.683, 8.223, "Join B500", False),
                    ("Mummelsee", 48.596, 8.201, "Mountain lake", True),
                    ("Ruhestein", 48.561, 8.221, "Nationalpark", False),
                    ("Freudenstadt", 48.462, 8.411, "Marktplatz", False),
                    ("Baiersbronn", 48.504, 8.378, "Overnight", False),
                ],
                "description": "B500 from Baden-Baden to Freudenstadt, overnight in Baiersbronn.",
                "midpoint_name": "Mummelsee", "midpoint_description": "Mystical lake at 1036 m.",
                "overnight": {"name": "Baiersbronn", "description": "Michelin-star dining in the forest."},
                "road_character": "B500 ridge curves. The classic opening day.",
            },
            {
                "day": 2, "title": "Central Black Forest to Schluchsee",
                "distance_km": 140,
                "waypoints": [
                    ("Baiersbronn", 48.504, 8.378, "Start", False),
                    ("Schiltach", 48.290, 8.339, "Half-timbered", False),
                    ("Triberg", 48.133, 8.237, "Waterfalls", True),
                    ("Furtwangen", 48.055, 8.208, "Clock museum", False),
                    ("Titisee", 47.903, 8.157, "Iconic lake", False),
                    ("Schluchsee", 47.819, 8.179, "Overnight", False),
                ],
                "description": "Through Schiltach and Triberg to Titisee and Schluchsee.",
                "midpoint_name": "Triberg", "midpoint_description": "Germany\u2019s highest waterfalls (163 m).",
                "overnight": {"name": "Schluchsee", "description": "Quiet lake at 930 m. Parkhotel Flora."},
                "road_character": "Valley curves, then high Black Forest plateau roads.",
            },
            {
                "day": 3, "title": "Rhine Falls & Lake Constance",
                "distance_km": 200,
                "waypoints": [
                    ("Schluchsee", 47.819, 8.179, "Start", False),
                    ("Bonndorf", 47.818, 8.340, "Wutach gorge area", False),
                    ("Waldshut-Tiengen", 47.623, 8.215, "High Rhine", False),
                    ("Schaffhausen (Rhine Falls)", 47.697, 8.635, "Europe\u2019s largest waterfall", True),
                    ("Stein am Rhein", 47.660, 8.860, "Medieval painted houses", False),
                    ("Konstanz", 47.658, 9.175, "Lake Constance", False),
                    ("Meersburg", 47.694, 9.271, "Overnight", False),
                ],
                "description": "South to the Rhine Falls at Schaffhausen, then along Lake Constance to Meersburg.",
                "midpoint_name": "Rhine Falls", "midpoint_description": "Europe\u2019s largest waterfall by volume. Stunning.",
                "overnight": {"name": "Meersburg", "description": "Medieval castle town on Lake Constance. Winzerstube zum Becher."},
                "road_character": "Rolling terrain to the Rhine, then lakeside riding.",
            },
            {
                "day": 4, "title": "Lake Constance to the Alps",
                "distance_km": 170,
                "waypoints": [
                    ("Meersburg", 47.694, 9.271, "Start", False),
                    ("Friedrichshafen", 47.655, 9.479, "Zeppelin town", False),
                    ("Lindau", 47.545, 9.682, "Island town", False),
                    ("Bregenz", 47.503, 9.741, "Austria (briefly)", True),
                    ("Egg", 47.430, 9.897, "Bregenzerwald village", False),
                    ("Bezau", 47.386, 9.902, "Valley village", False),
                    ("Hittisau", 47.460, 9.957, "Bregenzerwald", False),
                    ("Balderschwang", 47.457, 10.106, "Remote mountain village", False),
                    ("Oberstdorf", 47.408, 10.279, "Overnight", False),
                ],
                "description": "Along Lake Constance to Lindau and Bregenz, then through the scenic Bregenzerwald via Egg and Bezau to Oberstdorf.",
                "midpoint_name": "Bregenz & Bregenzerwald", "midpoint_description": "Austrian lakefront, then dramatic mountain roads.",
                "overnight": {"name": "Oberstdorf", "description": "Alpine resort at the southern tip of Germany. Nebelhornbahn for panoramic views. Das Fetzwerk restaurant."},
                "road_character": "Lakeside, then mountain switchbacks through the Bregenzerwald. The most alpine day.",
            },
            {
                "day": 5, "title": "Allg\u00e4u to Ulm",
                "distance_km": 150,
                "waypoints": [
                    ("Oberstdorf", 47.408, 10.279, "Start", False),
                    ("Sonthofen", 47.515, 10.281, "Allg\u00e4u town", False),
                    ("Immenstadt", 47.560, 10.219, "Alpsee", False),
                    ("Kempten", 47.726, 10.316, "Roman town", True),
                    ("Ottobeuren", 47.941, 10.300, "Baroque basilica", False),
                    ("Memmingen", 47.987, 10.181, "Medieval old town", False),
                    ("Ulm", 48.401, 9.987, "Overnight", False),
                ],
                "description": "Through the Allg\u00e4u foothills via Kempten and Ottobeuren to Ulm.",
                "midpoint_name": "Kempten", "midpoint_description": "One of Germany\u2019s oldest cities. Roman finds and Allg\u00e4u culture.",
                "overnight": {"name": "Ulm", "description": "World\u2019s tallest church spire (161.5 m). The Fischerviertel is charming. Zur Forelle restaurant."},
                "road_character": "Allg\u00e4u foothills with mountain backdrop. Gentle rolling terrain.",
            },
            {
                "day": 6, "title": "Schw\u00e4bische Alb Return Home",
                "distance_km": 260,
                "waypoints": [
                    ("Ulm", 48.401, 9.987, "Start", False),
                    ("Blaubeuren", 48.412, 9.783, "Blautopf spring", True),
                    ("M\u00fcnsingen", 48.412, 9.497, "Alb plateau", False),
                    ("Bad Urach", 48.494, 9.397, "Waterfall", False),
                    ("Schloss Lichtenstein", 48.408, 9.260, "Fairy-tale castle", False),
                    ("T\u00fcbingen", 48.522, 9.057, "University town", False),
                    ("Calw", 48.714, 8.741, "Hesse\u2019s town", False),
                    ("Pforzheim", 48.891, 8.704, "Gold city", False),
                    H_END,
                ],
                "description": "Cross the Alb via Blaubeuren and Lichtenstein, then through T\u00fcbingen and Calw home.",
                "midpoint_name": "Blaubeuren", "midpoint_description": "The Blautopf\u2014an impossibly blue karst spring.",
                "overnight": None,
                "road_character": "Alb escarpment switchbacks, then Nagold valley curves. A grand finale.",
            },
        ],
    },
    # S02 ---------------------------------------------------------------
    {
        "number": 2,
        "name": "Alsace, Black Forest & Lake Constance",
        "slug": "alsace_bf_constance",
        "region": "Elsass / Schwarzwald / Bodensee",
        "difficulty": "Moderate",
        "overview": (
            "A six-day grand loop through three countries: France (Alsace "
            "& Vosges), Germany (Black Forest), and briefly Switzerland "
            "(Rhine Falls). Wine, mountains, lakes, and valleys."
        ),
        "highlights": [
            "Northern Vosges \u2013 UNESCO Biosphere",
            "Alsace Wine Route in full",
            "Vosges mountain passes (Grand Ballon)",
            "Freiburg and H\u00f6llental gorge",
            "Rhine Falls & Lake Constance",
            "Central Black Forest valleys",
        ],
        "days": [
            {
                "day": 1, "title": "Into the Northern Vosges",
                "distance_km": 210,
                "waypoints": [
                    H_START,
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    ("Wissembourg", 49.037, 7.945, "Cross into France", False),
                    ("Lembach", 49.003, 7.788, "Fleckenstein", True),
                    ("Niederbronn-les-Bains", 48.952, 7.643, "Spa", False),
                    ("Saverne", 48.742, 7.362, "Rose City", False),
                    ("Obernai", 48.462, 7.483, "Overnight", False),
                ],
                "description": "Through Pf\u00e4lzerwald to Wissembourg, Ch\u00e2teau Fleckenstein, northern Vosges to Obernai.",
                "midpoint_name": "Ch\u00e2teau du Fleckenstein", "midpoint_description": "Castle carved from sandstone.",
                "overnight": {"name": "Obernai", "description": "Alsatian gem. H\u00f4tel Le Colombier."},
                "road_character": "Forest roads through the northern Vosges.",
            },
            {
                "day": 2, "title": "Wine Route & Vosges Passes",
                "distance_km": 200,
                "waypoints": [
                    ("Obernai", 48.462, 7.483, "Start", False),
                    ("Ribeauvill\u00e9", 48.194, 7.318, "Three castles", True),
                    ("Kaysersberg", 48.140, 7.264, "Schweitzer", False),
                    ("Munster", 48.042, 7.137, "Cheese valley", False),
                    ("Col de la Schlucht", 48.063, 7.023, "Pass (1139 m)", False),
                    ("Route des Cr\u00eates", 47.977, 7.053, "Ridge road", False),
                    ("Grand Ballon", 47.902, 7.099, "Highest Vosges", False),
                    ("Colmar", 48.079, 7.359, "Overnight", False),
                ],
                "description": "Wine route, Vosges passes, Grand Ballon, down to Colmar.",
                "midpoint_name": "Ribeauvill\u00e9 to Grand Ballon", "midpoint_description": "The best of Alsace in one day.",
                "overnight": {"name": "Colmar", "description": "Little Venice, Unterlinden Museum. H\u00f4tel Le Mar\u00e9chal."},
                "road_character": "Wine villages, then mountain pass climbing and ridge riding.",
            },
            {
                "day": 3, "title": "Across to Freiburg",
                "distance_km": 120,
                "waypoints": [
                    ("Colmar", 48.079, 7.359, "Start", False),
                    ("Eguisheim", 48.042, 7.306, "Circular village", False),
                    ("Rouffach", 47.956, 7.299, "Wine village", False),
                    ("Breisach am Rhein", 48.028, 7.583, "Cross Rhine", True),
                    ("Kaiserstuhl", 48.092, 7.655, "Volcanic hills", False),
                    ("Staufen im Breisgau", 47.883, 7.728, "Faust town", False),
                    ("Freiburg", 47.999, 7.842, "Overnight", False),
                ],
                "description": "Southern Alsace villages, cross Rhine at Breisach, Kaiserstuhl, Staufen to Freiburg.",
                "midpoint_name": "Kaiserstuhl", "midpoint_description": "Volcanic wine hills with Mediterranean microclimate.",
                "overnight": {"name": "Freiburg", "description": "Black Forest capital. M\u00fcnster and B\u00e4chle. Gasthaus Zum Roten B\u00e4ren."},
                "road_character": "Wine villages and Kaiserstuhl panoramic roads. Relaxed day.",
            },
            {
                "day": 4, "title": "Southern Black Forest & Rhine Falls",
                "distance_km": 210,
                "waypoints": [
                    ("Freiburg", 47.999, 7.842, "Start", False),
                    ("H\u00f6llental", 47.897, 8.050, "Hell Valley", True),
                    ("Titisee", 47.903, 8.157, "Black Forest lake", False),
                    ("Schluchsee", 47.819, 8.179, "High lake", False),
                    ("Waldshut", 47.623, 8.215, "High Rhine", False),
                    ("Schaffhausen (Rhine Falls)", 47.697, 8.635, "Waterfall", False),
                    ("Meersburg", 47.694, 9.271, "Overnight", False),
                ],
                "description": "H\u00f6llental, Titisee, south to Rhine Falls, then Lake Constance.",
                "midpoint_name": "H\u00f6llental & Titisee", "midpoint_description": "Gorge and iconic lake.",
                "overnight": {"name": "Meersburg", "description": "Medieval castle on the lake."},
                "road_character": "Dramatic gorge, Black Forest heights, lakeside finale.",
            },
            {
                "day": 5, "title": "Lake Constance to Triberg",
                "distance_km": 150,
                "waypoints": [
                    ("Meersburg", 47.694, 9.271, "Start", False),
                    ("\u00dcberlingen", 47.769, 9.160, "Lake town", False),
                    ("Singen", 47.763, 8.836, "Hegau volcanoes", False),
                    ("Donaueschingen", 47.951, 8.503, "Danube source", True),
                    ("Villingen", 48.062, 8.461, "Twin town", False),
                    ("Triberg", 48.133, 8.237, "Overnight", False),
                ],
                "description": "Along Lake Constance, then north through Donaueschingen (Danube source) to Triberg.",
                "midpoint_name": "Donaueschingen", "midpoint_description": "Where the Danube begins its 2850 km journey to the Black Sea.",
                "overnight": {"name": "Triberg", "description": "Waterfalls and cuckoo clocks."},
                "road_character": "Lakeside, then rolling Baar plateau and forest roads.",
            },
            {
                "day": 6, "title": "Kinzigtal & B500 Home",
                "distance_km": 210,
                "waypoints": [
                    ("Triberg", 48.133, 8.237, "Start", False),
                    ("Schiltach", 48.290, 8.339, "Half-timbered", False),
                    ("Wolfach", 48.293, 8.219, "Kinzigtal", False),
                    ("Gengenbach", 48.407, 8.015, "Nice of the BF", True),
                    ("Sasbachwalden", 48.619, 8.120, "Flower village", False),
                    ("B500", 48.654, 8.226, "Hochstra\u00dfe", False),
                    ("Baden-Baden", 48.761, 8.241, "Spa city", False),
                    H_END,
                ],
                "description": "Through Kinzigtal, flower village Sasbachwalden, B500 and Baden-Baden home.",
                "midpoint_name": "Gengenbach", "midpoint_description": "\u201cNice of the Black Forest.\u201d",
                "overnight": None,
                "road_character": "Valley curves and B500 ridge\u2014a fitting end to a grand tour.",
            },
        ],
    },
    # S03 ---------------------------------------------------------------
    {
        "number": 3,
        "name": "Franconia & Romantic Road",
        "slug": "franconia_romantic_road",
        "region": "Franken / Romantische Stra\u00dfe",
        "difficulty": "Moderate",
        "overview": (
            "Six days through Franconia\u2014from the Main valley and "
            "W\u00fcrzburg through the Franconian Switzerland karst "
            "landscape to N\u00fcrnberg, the Altm\u00fchltal, and the Romantic "
            "Road. Return through Hohenlohe."
        ),
        "highlights": [
            "W\u00fcrzburg Residenz (UNESCO)",
            "Bamberg \u2013 UNESCO old town",
            "Fr\u00e4nkische Schweiz \u2013 castles and caves",
            "Altm\u00fchltal nature park",
            "Dinkelsb\u00fchl & Rothenburg \u2013 Romantic Road",
            "Schw\u00e4bisch Hall & Hohenlohe return",
        ],
        "days": [
            {
                "day": 1, "title": "Odenwald to W\u00fcrzburg", "distance_km": 210,
                "waypoints": [
                    H_START, ("Eberbach", 49.467, 8.988, "Neckar", False),
                    ("Amorbach", 49.645, 9.221, "Baroque abbey", True),
                    ("Miltenberg", 49.703, 9.265, "Main valley", False),
                    ("Wertheim", 49.759, 9.509, "Castle", False),
                    ("W\u00fcrzburg", 49.792, 9.934, "Overnight", False),
                ],
                "description": "Through the Odenwald and Main valley to W\u00fcrzburg.",
                "midpoint_name": "Amorbach", "midpoint_description": "Baroque abbey in the forest.",
                "overnight": {"name": "W\u00fcrzburg", "description": "Residenz, Alte Mainbr\u00fccke, Franconian wine."},
                "road_character": "Forest curves and flowing river valley.",
            },
            {
                "day": 2, "title": "Franconian Wine to Bamberg", "distance_km": 130,
                "waypoints": [
                    ("W\u00fcrzburg", 49.792, 9.934, "Start", False),
                    ("Volkach", 49.866, 10.227, "Mainschleife", True),
                    ("Dettelbach", 49.800, 10.168, "Pilgrim town", False),
                    ("Iphofen", 49.701, 10.258, "Wine town", False),
                    ("Bamberg", 49.891, 10.886, "Overnight", False),
                ],
                "description": "Through Franconian wine country along the Main to UNESCO Bamberg.",
                "midpoint_name": "Volkach & Mainschleife", "midpoint_description": "The iconic Main river loop through vineyards.",
                "overnight": {"name": "Bamberg", "description": "UNESCO old town, Rauchbier (smoked beer), Little Venice."},
                "road_character": "Gentle wine country roads along the Main.",
            },
            {
                "day": 3, "title": "Fr\u00e4nkische Schweiz", "distance_km": 130,
                "waypoints": [
                    ("Bamberg", 49.891, 10.886, "Start", False),
                    ("Pottenstein", 49.771, 11.408, "Castle on the cliff", True),
                    ("G\u00f6\u00dfweinstein", 49.770, 11.337, "Pilgrimage basilica", False),
                    ("Ebermannstadt", 49.782, 11.185, "Wiesent valley", False),
                    ("Forchheim", 49.720, 11.058, "Half-timbered", False),
                    ("N\u00fcrnberg", 49.452, 11.077, "Overnight", False),
                ],
                "description": "Through the Fr\u00e4nkische Schweiz\u2014dramatic karst landscape with castle-topped cliffs and caves\u2014to N\u00fcrnberg.",
                "midpoint_name": "Pottenstein & G\u00f6\u00dfweinstein", "midpoint_description": "Castle cliffs and the Basilica of the Trinity.",
                "overnight": {"name": "N\u00fcrnberg", "description": "Kaiserburg, Altstadt, Bratwurst. Hotel Drei Raben."},
                "road_character": "Tight curves through karst valleys. Excellent motorcycle country.",
            },
            {
                "day": 4, "title": "Altm\u00fchltal to Dinkelsb\u00fchl", "distance_km": 200,
                "waypoints": [
                    ("N\u00fcrnberg", 49.452, 11.077, "Start", False),
                    ("Neumarkt i.d. Oberpfalz", 49.280, 11.460, "Eastern Franconia", False),
                    ("Berching", 49.106, 11.440, "Medieval town", False),
                    ("Eichst\u00e4tt", 48.892, 11.184, "Baroque bishop\u2019s town", True),
                    ("Solnhofen", 48.897, 10.966, "Fossil limestone", False),
                    ("N\u00f6rdlingen", 48.851, 10.489, "Ries crater", False),
                    ("Dinkelsb\u00fchl", 49.067, 10.319, "Overnight", False),
                ],
                "description": "Through the Altm\u00fchltal to Eichst\u00e4tt, N\u00f6rdlingen\u2019s meteor crater, and medieval Dinkelsb\u00fchl.",
                "midpoint_name": "Eichst\u00e4tt", "midpoint_description": "Baroque jewel on the Altm\u00fchl. Completely intact old town.",
                "overnight": {"name": "Dinkelsb\u00fchl", "description": "Arguably even prettier than Rothenburg. Haus Appelberg. Deutsches Haus restaurant."},
                "road_character": "Altm\u00fchl valley\u2014gentle curves through limestone landscape.",
            },
            {
                "day": 5, "title": "Romantic Road to Schw\u00e4bisch Hall", "distance_km": 150,
                "waypoints": [
                    ("Dinkelsb\u00fchl", 49.067, 10.319, "Start", False),
                    ("Feuchtwangen", 49.167, 10.328, "Romantic Road", False),
                    ("Rothenburg o.d. Tauber", 49.377, 10.179, "Medieval dream", True),
                    ("Crailsheim", 49.134, 10.072, "Eastern Hohenlohe", False),
                    ("Langenburg", 49.254, 9.858, "Castle", False),
                    ("Schw\u00e4bisch Hall", 49.112, 9.738, "Overnight", False),
                ],
                "description": "Romantic Road through Rothenburg, then Hohenlohe to Schw\u00e4bisch Hall.",
                "midpoint_name": "Rothenburg o.d. Tauber", "midpoint_description": "Germany\u2019s most famous medieval town.",
                "overnight": {"name": "Schw\u00e4bisch Hall", "description": "Theatrical Marktplatz, Comburg monastery. Hotel Goldener Adler."},
                "road_character": "Rolling Romantic Road, then Hohenlohe hills.",
            },
            {
                "day": 6, "title": "Hohenlohe & Neckar Home", "distance_km": 200,
                "waypoints": [
                    ("Schw\u00e4bisch Hall", 49.112, 9.738, "Start", False),
                    ("\u00d6hringen", 49.201, 9.501, "Hohenlohe", False),
                    ("Neckarsulm", 49.192, 9.225, "Motorcycle museum!", True),
                    ("Bad Wimpfen", 49.231, 9.165, "Kaiserpfalz", False),
                    ("Mosbach", 49.353, 9.146, "Fachwerk", False),
                    ("Eberbach", 49.467, 8.988, "Neckar valley", False),
                    H_END,
                ],
                "description": "Through Hohenlohe, motorcycle museum, Bad Wimpfen, Neckar valley home.",
                "midpoint_name": "Deutsches Zweirad-Museum", "midpoint_description": "Germany\u2019s motorcycle museum. The perfect last stop.",
                "overnight": None,
                "road_character": "Hohenlohe hills, then Neckar valley curves. A satisfying finale.",
            },
        ],
    },
    # S04 ---------------------------------------------------------------
    {
        "number": 4,
        "name": "Moselle, Eifel & Rhine Grand Loop",
        "slug": "moselle_eifel_rhine_grand",
        "region": "Mosel / Eifel / Rhein / Lahn / Taunus",
        "difficulty": "Moderate",
        "overview": (
            "A grand clockwise loop through western Germany\u2019s finest "
            "river valleys and mountain ranges\u2014Taunus, Lahn, Rhine, "
            "Eifel, Moselle, Hunsr\u00fcck, and Nahe."
        ),
        "highlights": [
            "Taunus mountain roads",
            "Koblenz Deutsches Eck",
            "Eifel & N\u00fcrburgring",
            "Moselle wine towns (Cochem, Bernkastel)",
            "Rhine gorge & Loreley",
            "Nahe valley return",
        ],
        "days": [
            {
                "day": 1, "title": "Bergstra\u00dfe & Taunus", "distance_km": 210,
                "waypoints": [
                    H_START, ("Weinheim", 49.550, 8.667, "Bergstra\u00dfe", False),
                    ("Bensheim", 49.681, 8.618, "Bergstra\u00dfe", False),
                    ("Darmstadt", 49.874, 8.650, "Architecture", False),
                    ("Idstein", 50.222, 8.268, "Taunus", True),
                    ("Limburg an der Lahn", 50.387, 8.063, "Cathedral", False),
                    ("Weilburg", 50.486, 8.262, "Overnight", False),
                ],
                "description": "North along the Bergstra\u00dfe, through the Taunus to Limburg and Weilburg.",
                "midpoint_name": "Idstein & Taunus", "midpoint_description": "Half-timbered Idstein and Taunus mountain curves.",
                "overnight": {"name": "Weilburg", "description": "Baroque palace above the Lahn. Schlosshotel Weilburg."},
                "road_character": "Bergstra\u00dfe, then Taunus forest curves. Good start.",
            },
            {
                "day": 2, "title": "Lahn Valley to Koblenz", "distance_km": 140,
                "waypoints": [
                    ("Weilburg", 50.486, 8.262, "Start", False),
                    ("Nassau", 50.315, 7.795, "Lahn valley", False),
                    ("Bad Ems", 50.334, 7.722, "Spa (UNESCO)", True),
                    ("Koblenz", 50.354, 7.599, "Deutsches Eck", False),
                    ("Boppard", 50.230, 7.593, "Rhine bend", False),
                    ("St. Goar", 50.153, 7.711, "Loreley views", False),
                    ("Bacharach", 50.059, 7.770, "Overnight", False),
                ],
                "description": "Lahn valley to Koblenz, then Rhine south through the Loreley gorge.",
                "midpoint_name": "Bad Ems", "midpoint_description": "UNESCO Great Spa town on the Lahn.",
                "overnight": {"name": "Bacharach", "description": "Most romantic Rhine wine town. Postenturm views. Altes Haus restaurant."},
                "road_character": "Lahn valley curves, then Rhine gorge\u2014castle at every bend.",
            },
            {
                "day": 3, "title": "Rhine to Eifel", "distance_km": 210,
                "waypoints": [
                    ("Bacharach", 50.059, 7.770, "Start", False),
                    ("Bingen", 49.966, 7.895, "Rhine-Nahe", False),
                    ("Koblenz", 50.354, 7.599, "Rhine north", False),
                    ("Andernach", 50.440, 7.404, "Eifel approach", False),
                    ("Mayen", 50.328, 7.223, "Eifel", True),
                    ("Burg Eltz", 50.205, 7.337, "Fairy-tale castle", False),
                    ("Cochem", 50.146, 7.167, "Overnight", False),
                ],
                "description": "Rhine north to Koblenz, into the Eifel via Mayen, Burg Eltz to Cochem.",
                "midpoint_name": "Burg Eltz", "midpoint_description": "Germany\u2019s fairy-tale castle, never destroyed.",
                "overnight": {"name": "Cochem", "description": "Reichsburg and Moselle wine taverns."},
                "road_character": "Rhine valley, then Eifel highland curves to Moselle.",
            },
            {
                "day": 4, "title": "N\u00fcrburgring & Ahr Valley", "distance_km": 150,
                "waypoints": [
                    ("Cochem", 50.146, 7.167, "Start", False),
                    ("Ulmen", 50.210, 6.975, "Maar lake", False),
                    ("Daun", 50.196, 6.831, "Volcanic Eifel", True),
                    ("Manderscheid", 50.091, 6.808, "Twin castles", False),
                    ("Kelberg", 50.281, 6.909, "Eifel ridge", False),
                    ("N\u00fcrburgring", 50.336, 6.943, "Green Hell", False),
                    ("Adenau", 50.383, 6.931, "Eifel village", False),
                    ("Altenahr", 50.518, 6.985, "Ahr gorge", False),
                    ("Bad Neuenahr", 50.543, 7.112, "Overnight", False),
                ],
                "description": "Through volcanic Eifel via Daun and Manderscheid, N\u00fcrburgring, then the scenic Ahr valley.",
                "midpoint_name": "Daun & Vulkaneifel", "midpoint_description": "Volcanic maar lakes\u2014round, deep, mysterious.",
                "overnight": {"name": "Bad Neuenahr", "description": "Ahr valley wine, rebuilt after the 2021 flood."},
                "road_character": "Eifel highland sweepers, then tight Ahr gorge curves.",
            },
            {
                "day": 5, "title": "Moselle Wine Towns", "distance_km": 210,
                "waypoints": [
                    ("Bad Neuenahr", 50.543, 7.112, "Start", False),
                    ("Remagen", 50.578, 7.233, "Bridge", False),
                    ("Koblenz", 50.354, 7.599, "Moselle start", False),
                    ("Traben-Trarbach", 49.947, 7.118, "Art Nouveau", True),
                    ("Bernkastel-Kues", 49.915, 7.068, "Wine gem", False),
                    ("Morbach", 49.810, 7.130, "Hunsr\u00fcck", False),
                    ("Idar-Oberstein", 49.714, 7.308, "Overnight", False),
                ],
                "description": "Rhine to Koblenz, Moselle south through wine towns, up to Hunsr\u00fcck.",
                "midpoint_name": "Traben-Trarbach & Bernkastel", "midpoint_description": "The Moselle\u2019s finest wine towns.",
                "overnight": {"name": "Idar-Oberstein", "description": "Cliff church, gemstone museum."},
                "road_character": "Moselle valley\u2014endless curves following the river.",
            },
            {
                "day": 6, "title": "Nahe & Pf\u00e4lzerwald Home", "distance_km": 200,
                "waypoints": [
                    ("Idar-Oberstein", 49.714, 7.308, "Start", False),
                    ("Kirn", 49.789, 7.455, "Nahe valley", False),
                    ("Bad Kreuznach", 49.842, 7.867, "Spa & wine", True),
                    ("Bad D\u00fcrkheim", 49.462, 8.172, "World\u2019s largest wine barrel", False),
                    ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Wine route", False),
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    H_END,
                ],
                "description": "Nahe valley east, then Pfalz wine country home.",
                "midpoint_name": "Bad Kreuznach", "midpoint_description": "Nahe wines, Br\u00fcckenh\u00e4user (houses on a bridge).",
                "overnight": None,
                "road_character": "Nahe valley, then Weinstra\u00dfe. A relaxed wine-country finale.",
            },
        ],
    },
    # S05 ---------------------------------------------------------------
    {
        "number": 5,
        "name": "Thuringia & Central Germany",
        "slug": "thuringia_central",
        "region": "Franken / Th\u00fcringen / Hessen",
        "difficulty": "Moderate",
        "overview": (
            "The most adventurous tour heads northeast into Thuringia\u2014"
            "the green heart of Germany. Six days through the Main "
            "valley, Th\u00fcringer Wald, Rh\u00f6n mountains, and back through "
            "Hesse and the Taunus. Completely different from the other tours."
        ),
        "highlights": [
            "Bamberg \u2013 UNESCO old town",
            "Th\u00fcringer Wald \u2013 Germany\u2019s green heart",
            "Rh\u00f6n \u2013 Wasserkuppe (highest Hesse peak)",
            "Marburg \u2013 fairy-tale university town",
            "Lahn valley & Taunus",
            "Rheingau wine on the return",
        ],
        "days": [
            {
                "day": 1, "title": "Main Valley to Bamberg", "distance_km": 270,
                "waypoints": [
                    H_START, ("Michelstadt", 49.676, 9.004, "Odenwald", False),
                    ("Miltenberg", 49.703, 9.265, "Main valley", False),
                    ("Wertheim", 49.759, 9.509, "Castle", True),
                    ("W\u00fcrzburg", 49.792, 9.934, "Brief stop", False),
                    ("Bamberg", 49.891, 10.886, "Overnight", False),
                ],
                "description": "Through Odenwald and Main valley, past W\u00fcrzburg to Bamberg.",
                "midpoint_name": "Wertheim", "midpoint_description": "Castle above the Main-Tauber confluence.",
                "overnight": {"name": "Bamberg", "description": "UNESCO Altstadt, Rauchbier, Little Venice. Messerschmitt hotel."},
                "road_character": "Odenwald curves, then Main valley.",
            },
            {
                "day": 2, "title": "Into the Th\u00fcringer Wald", "distance_km": 210,
                "waypoints": [
                    ("Bamberg", 49.891, 10.886, "Start", False),
                    ("Coburg", 50.259, 10.964, "Veste Coburg", True),
                    ("Kronach", 50.241, 11.328, "Festung Rosenberg", False),
                    ("Saalfeld", 50.648, 11.364, "Fairy grottoes", False),
                    ("Schwarzatal", 50.622, 11.200, "Deep valley", False),
                    ("Ilmenau", 50.685, 10.919, "Overnight", False),
                ],
                "description": "North to Coburg (Luther\u2019s fortress), through the Frankenwald to the Th\u00fcringer Wald.",
                "midpoint_name": "Coburg", "midpoint_description": "Veste Coburg\u2014Luther stayed here. Magnificent fortress.",
                "overnight": {"name": "Ilmenau", "description": "Goethe\u2019s favorite retreat. Kickelhahn viewpoint. Hotel Tanne."},
                "road_character": "Frankenwald and Th\u00fcringer Wald\u2014dense forest and winding roads.",
            },
            {
                "day": 3, "title": "Th\u00fcringer Wald to Meiningen", "distance_km": 140,
                "waypoints": [
                    ("Ilmenau", 50.685, 10.919, "Start", False),
                    ("Oberhof", 50.721, 10.732, "Winter sports", True),
                    ("Tabarz", 50.875, 10.524, "Near Inselsberg", False),
                    ("Friedrichroda", 50.859, 10.558, "Crystal cave", False),
                    ("Brotterode", 50.817, 10.437, "Inselsberg area", False),
                    ("Schmalkalden", 50.724, 10.449, "Half-timbered", False),
                    ("Meiningen", 50.556, 10.417, "Overnight", False),
                ],
                "description": "Along the Rennsteig ridge via Oberhof, loop north to the Inselsberg area through Tabarz and Friedrichroda, then south to Schmalkalden and Meiningen.",
                "midpoint_name": "Oberhof & Rennsteig", "midpoint_description": "The Rennsteig is Germany\u2019s oldest and most famous long-distance trail.",
                "overnight": {"name": "Meiningen", "description": "Theater town. Impressive Schloss Elisabethenburg. Henneberger Haus."},
                "road_character": "Mountain ridge roads through dense forest. Excellent curves.",
            },
            {
                "day": 4, "title": "Rh\u00f6n Mountains", "distance_km": 140,
                "waypoints": [
                    ("Meiningen", 50.556, 10.417, "Start", False),
                    ("Rh\u00f6n", 50.500, 10.100, "Open highlands", False),
                    ("Wasserkuppe (950 m)", 50.498, 9.937, "Highest Hesse peak", True),
                    ("Gersfeld", 50.453, 9.920, "Rh\u00f6n village", False),
                    ("Fulda", 50.550, 9.676, "Baroque town", False),
                    ("Alsfeld", 50.749, 9.271, "Overnight", False),
                ],
                "description": "Cross the Rh\u00f6n\u2014the \u201cland of open spaces\u201d\u2014over the Wasserkuppe to Fulda and Alsfeld.",
                "midpoint_name": "Wasserkuppe (950 m)", "midpoint_description": "Highest peak in Hesse. Birthplace of gliding. Panoramic views.",
                "overnight": {"name": "Alsfeld", "description": "Fairy-tale half-timbered Altstadt. Weinhaus am Markt."},
                "road_character": "Open Rh\u00f6n highlands\u2014sweeping roads with endless views.",
            },
            {
                "day": 5, "title": "Hesse to the Lahn", "distance_km": 170,
                "waypoints": [
                    ("Alsfeld", 50.749, 9.271, "Start", False),
                    ("Marburg", 50.810, 8.770, "University town", True),
                    ("Gladenbach", 50.769, 8.583, "Hinterland", False),
                    ("Herborn", 50.680, 8.302, "Lahn valley", False),
                    ("Weilburg", 50.486, 8.262, "Lahn palace", False),
                    ("Limburg an der Lahn", 50.387, 8.063, "Overnight", False),
                ],
                "description": "To fairy-tale Marburg, then through the Hessisches Hinterland to the Lahn valley.",
                "midpoint_name": "Marburg", "midpoint_description": "Fairy-tale castle above the old town. Grimm Brothers studied here.",
                "overnight": {"name": "Limburg an der Lahn", "description": "Dramatic cathedral. Half-timbered Altstadt. Dom Hotel."},
                "road_character": "Hessian hills and Lahn valley\u2014flowing curves through varied terrain.",
            },
            {
                "day": 6, "title": "Taunus, Rheingau & Pfalz Home", "distance_km": 210,
                "waypoints": [
                    ("Limburg an der Lahn", 50.387, 8.063, "Start", False),
                    ("Idstein", 50.222, 8.268, "Taunus", False),
                    ("R\u00fcdesheim", 49.978, 7.920, "Rheingau wine", True),
                    ("Bingen", 49.966, 7.895, "Rhine-Nahe", False),
                    ("Alzey", 49.747, 8.116, "Rheinhessen", False),
                    ("Bad D\u00fcrkheim", 49.462, 8.172, "Pfalz wine", False),
                    ("Speyer", 49.317, 8.431, "Cross Rhine", False),
                    H_END,
                ],
                "description": "Through Taunus to Rheingau (R\u00fcdesheim wine), then south through the Pfalz home.",
                "midpoint_name": "R\u00fcdesheim & Rheingau", "midpoint_description": "Rhine wine at its finest. Drosselgasse and cable car to Niederwalddenkmal.",
                "overnight": None,
                "road_character": "Taunus curves, Rhine views, then wine country home.",
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# GPX generation (one file per day leg)
# ---------------------------------------------------------------------------
GPX_NS = "http://www.topografix.com/GPX/1/1"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMA_LOC = "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"


def _gpx_pretty(root):
    rough = ET.tostring(root, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ", encoding="UTF-8")


def generate_gpx_day(tour, day, prefix, outdir):
    """Write one GPX file for a single day leg. Return the filename."""
    gpx = ET.Element("gpx")
    gpx.set("xmlns", GPX_NS)
    gpx.set("xmlns:xsi", XSI_NS)
    gpx.set("xsi:schemaLocation", SCHEMA_LOC)
    gpx.set("version", "1.1")
    gpx.set("creator", "Hockenheim Motorcycle Tours")

    meta = ET.SubElement(gpx, "metadata")
    ET.SubElement(meta, "name").text = (
        f"{prefix.capitalize()} {tour['number']:02d}, Day {day['day']}: "
        f"{day['title']}"
    )
    ET.SubElement(meta, "desc").text = day["description"]

    day_waypoints = day["waypoints"]
    for i, (name, lat, lon, desc, is_mid) in enumerate(day_waypoints):
        wpt = ET.SubElement(gpx, "wpt")
        wpt.set("lat", f"{lat:.6f}")
        wpt.set("lon", f"{lon:.6f}")
        ET.SubElement(wpt, "name").text = name
        if desc:
            ET.SubElement(wpt, "desc").text = desc
        if is_mid:
            ET.SubElement(wpt, "sym").text = "Restaurant"
            ET.SubElement(wpt, "type").text = "Midpoint"
        elif name == "Hockenheim":
            ET.SubElement(wpt, "sym").text = "Flag, Blue"
            ET.SubElement(wpt, "type").text = "Start" if i == 0 else "End"
        elif day.get("overnight") and name == day["overnight"]["name"]:
            ET.SubElement(wpt, "sym").text = "Hotel"
            ET.SubElement(wpt, "type").text = "Overnight"
        else:
            ET.SubElement(wpt, "type").text = "Via"

    rte = ET.SubElement(gpx, "rte")
    ET.SubElement(rte, "name").text = day["title"]
    ET.SubElement(rte, "desc").text = f"~{day['distance_km']} km"
    for name, lat, lon, _, _ in day["waypoints"]:
        rtept = ET.SubElement(rte, "rtept")
        rtept.set("lat", f"{lat:.6f}")
        rtept.set("lon", f"{lon:.6f}")
        ET.SubElement(rtept, "name").text = name

    fname = f"{prefix}_{tour['number']:02d}_{tour['slug']}_day{day['day']}.gpx"
    path = os.path.join(outdir, fname)
    with open(path, "wb") as f:
        f.write(_gpx_pretty(gpx))
    return fname


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------
def _register_fonts():
    for name, fn in {
        "NotoSans": "NotoSans-Regular.ttf",
        "NotoSans-Bold": "NotoSans-Bold.ttf",
        "NotoSans-Italic": "NotoSans-Italic.ttf",
        "NotoSans-BoldItalic": "NotoSans-BoldItalic.ttf",
        "NotoSerif-Bold": "NotoSerif-Bold.ttf",
    }.items():
        p = os.path.join(FONT_DIR, fn)
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p))
    registerFontFamily(
        "NotoSans", normal="NotoSans", bold="NotoSans-Bold",
        italic="NotoSans-Italic", boldItalic="NotoSans-BoldItalic",
    )


def _styles():
    return {
        "title": ParagraphStyle("T", fontName="NotoSerif-Bold", fontSize=26, alignment=TA_CENTER, textColor=GREEN, leading=32),
        "subtitle": ParagraphStyle("ST", fontName="NotoSans", fontSize=12, alignment=TA_CENTER, textColor=MID_GREY, leading=16),
        "h1": ParagraphStyle("H1", fontName="NotoSerif-Bold", fontSize=16, textColor=GREEN, spaceBefore=6, spaceAfter=4, leading=20),
        "h2": ParagraphStyle("H2", fontName="NotoSans-Bold", fontSize=11, textColor=ACCENT, spaceBefore=10, spaceAfter=3, leading=14),
        "h3": ParagraphStyle("H3", fontName="NotoSans-Bold", fontSize=10, textColor=BLUE, spaceBefore=8, spaceAfter=2, leading=13),
        "body": ParagraphStyle("B", fontName="NotoSans", fontSize=9.5, alignment=TA_JUSTIFY, leading=13.5, textColor=DARK),
        "bullet": ParagraphStyle("BL", fontName="NotoSans", fontSize=9.5, leftIndent=16, bulletIndent=4, leading=13, textColor=DARK),
        "meta": ParagraphStyle("M", fontName="NotoSans", fontSize=9, textColor=MID_GREY, leading=12),
        "gpx": ParagraphStyle("G", fontName="NotoSans-Italic", fontSize=8.5, textColor=MID_GREY, spaceBefore=4),
        "toc_cat": ParagraphStyle("TC", fontName="NotoSerif-Bold", fontSize=13, textColor=GREEN, spaceBefore=14, spaceAfter=2),
        "toc": ParagraphStyle("TE", fontName="NotoSans", fontSize=9.5, textColor=DARK, leftIndent=10, leading=14),
    }


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("NotoSans", 8)
    canvas.setFillColor(MID_GREY)
    canvas.drawCentredString(
        A4[0] / 2, 1.2 * cm,
        f"Motorcycle Multi-Day Tours from Hockenheim  \u2022  Page {doc.page}",
    )
    canvas.restoreState()


def _add_tour(story, tour, prefix, S):
    """Append flowables for one multi-day tour."""
    story.append(HRFlowable(width="100%", thickness=1.5, color=GREEN, spaceBefore=0, spaceAfter=6))
    cat_label = {"weekend": "Weekend", "tour3d": "3-Day", "tour6d": "6-Day"}[prefix]
    total = _total_km(tour)
    ndays = len(tour["days"])
    story.append(Paragraph(
        f"{cat_label} Tour {tour['number']:02d} &nbsp;&nbsp; "
        f"<font color='#888888'>{tour['region']}</font>", S["meta"],
    ))
    story.append(Paragraph(tour["name"], S["h1"]))
    story.append(Paragraph(
        f"Total: ~{total} km &nbsp;|&nbsp; {ndays} Days &nbsp;|&nbsp; "
        f"Difficulty: {tour['difficulty']}", S["meta"],
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(tour["overview"], S["body"]))
    story.append(Spacer(1, 2 * mm))

    # Highlights
    story.append(Paragraph("Highlights", S["h2"]))
    for h in tour["highlights"]:
        story.append(Paragraph(f"\u2022 &nbsp; {h}", S["bullet"]))

    # Days
    for day in tour["days"]:
        story.append(Paragraph(
            f"Day {day['day']}: {day['title']} (~{day['distance_km']} km)",
            S["h2"],
        ))
        story.append(Paragraph(day["description"], S["body"]))

        if day.get("midpoint_name"):
            story.append(Paragraph(
                f"<b>Midpoint:</b> {day['midpoint_name']} \u2013 "
                f"{day.get('midpoint_description', '')}", S["body"],
            ))

        ov = day.get("overnight")
        if ov:
            story.append(Paragraph(
                f"<b>Overnight: {ov['name']}</b> \u2013 {ov['description']}",
                S["body"],
            ))

        if day.get("road_character"):
            story.append(Paragraph(
                f"<i>Road character: {day['road_character']}</i>", S["body"],
            ))

        gpx_name = f"{prefix}_{tour['number']:02d}_{tour['slug']}_day{day['day']}.gpx"
        story.append(Paragraph(f"GPX: {gpx_name}", S["gpx"]))

    story.append(PageBreak())


def generate_pdf(weekend, three_day, six_day, outpath):
    _register_fonts()
    S = _styles()
    doc = SimpleDocTemplate(
        outpath, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    story = []

    # Title page
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph("Motorcycle Multi-Day Tours<br/>from Hockenheim", S["title"]))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(
        "10 Weekend Tours \u2022 5 Three-Day Tours \u2022 5 Six-Day Tours", S["subtitle"],
    ))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"Start &amp; End: {HOME_ADDRESS}", S["subtitle"]))
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(
        "This guide presents 20 multi-day motorcycle tours ranging from "
        "weekend getaways to six-day grand tours, all starting and ending "
        "at your front door in Hockenheim. Each day covers 180\u2013240 km of "
        "curves. Overnight stops include hotel suggestions and dinner "
        "recommendations. A matching GPX file is provided for every day.",
        S["body"],
    ))
    story.append(PageBreak())

    # TOC
    story.append(Paragraph("Contents", S["title"]))
    story.append(Spacer(1, 0.5 * cm))

    for label, tours in [
        ("Weekend Tours (2 Days)", weekend),
        ("Three-Day Tours", three_day),
        ("Six-Day Tours", six_day),
    ]:
        story.append(Paragraph(label, S["toc_cat"]))
        for t in tours:
            total = _total_km(t)
            nd = len(t["days"])
            story.append(Paragraph(
                f"<b>{t['number']:02d}</b> &nbsp; {t['name']} "
                f"<font color='#888888'>({t['region']}, ~{total} km, "
                f"{nd} days, {t['difficulty']})</font>",
                S["toc"],
            ))
    story.append(PageBreak())

    # Tours
    for prefix, tours in [
        ("weekend", weekend),
        ("tour3d", three_day),
        ("tour6d", six_day),
    ]:
        for t in tours:
            _add_tour(story, t, prefix, S)

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(GPX_DIR, exist_ok=True)

    all_tours = [
        ("weekend", WEEKEND_TOURS),
        ("tour3d", THREE_DAY_TOURS),
        ("tour6d", SIX_DAY_TOURS),
    ]

    total_gpx = 0
    for prefix, tours in all_tours:
        for t in tours:
            for day in t["days"]:
                fname = generate_gpx_day(t, day, prefix, GPX_DIR)
                print(f"  {fname}")
                total_gpx += 1

    print(f"\n{total_gpx} GPX files generated.")
    print(f"\nGenerating PDF: {PDF_FILE} ...")
    generate_pdf(WEEKEND_TOURS, THREE_DAY_TOURS, SIX_DAY_TOURS, PDF_FILE)
    print("Done.")


if __name__ == "__main__":
    main()
