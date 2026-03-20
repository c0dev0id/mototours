#!/usr/bin/env python3
"""Generate motorcycle day tour GPX files and companion PDF from Hockenheim."""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HOME_LAT = 49.322
HOME_LON = 8.548
HOME_NAME = "Hockenheim"
HOME_ADDRESS = "Gustav-Stresemann-Weg 1, 68766 Hockenheim"

OUTPUT_DIR = "output"
GPX_DIR = os.path.join(OUTPUT_DIR, "gpx")
PDF_FILE = os.path.join(OUTPUT_DIR, "motorcycle_tours_hockenheim.pdf")

FONT_DIR = "/usr/local/share/fonts/noto"

# Colors
GREEN = HexColor("#2C5530")
DARK = HexColor("#333333")
ACCENT = HexColor("#C8611A")
LIGHT_GREY = HexColor("#E8E8E8")
MID_GREY = HexColor("#888888")

# ---------------------------------------------------------------------------
# Tour data
# ---------------------------------------------------------------------------
# Each tour: dict with number, name, slug, region, distance_km, difficulty,
# waypoints (list of (name, lat, lon, desc, is_midpoint) tuples),
# overview, route_description, midpoint_name, midpoint_description,
# highlights (list of str), road_character.

TOURS = [
    # ------------------------------------------------------------------
    # PFAELZERWALD / PALATINATE  (Tours 1-5)
    # ------------------------------------------------------------------
    {
        "number": 1,
        "name": "Deutsche Weinstra\u00dfe & Trifels",
        "slug": "weinstrasse_trifels",
        "region": "Pf\u00e4lzerwald",
        "distance_km": 200,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Speyer", 49.317, 8.431, "Cross the Rhine", False),
            ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Gateway to the wine route", False),
            ("Maikammer", 49.306, 8.132, "Wine village", False),
            ("Edenkoben", 49.284, 8.120, "Villa Ludwigsh\u00f6he", False),
            ("Rhodt unter Rietburg", 49.269, 8.110, "Charming wine village", False),
            ("Landau in der Pfalz", 49.199, 8.117, "Turn west", False),
            ("Annweiler am Trifels", 49.204, 7.969, "Approach Trifels", False),
            ("Burg Trifels", 49.207, 7.982, "Imperial castle \u2013 midpoint stop", True),
            ("Ramberg", 49.244, 7.974, "Into the forest", False),
            ("Johanniskreuz", 49.348, 7.850, "Legendary forest crossroads", False),
            ("Lambrecht", 49.373, 8.080, "Exit forest", False),
            ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Return to wine country", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine back", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Wind your way through Germany\u2019s oldest wine route, sampling the charm of "
            "sun-drenched Palatinate villages before climbing to the legendary Trifels "
            "Castle\u2014where Richard the Lionheart was once held captive\u2014then plunging "
            "into the green heart of the Pf\u00e4lzerwald on winding forest roads."
        ),
        "route_description": (
            "From Hockenheim, cross the Rhine at Speyer and head west to Neustadt an der "
            "Weinstra\u00dfe, the gateway to the Deutsche Weinstra\u00dfe. Follow the wine route "
            "south through a string of picturesque villages\u2014Maikammer, Edenkoben, and "
            "Rhodt unter Rietburg\u2014where vineyards climb gentle hills and half-timbered "
            "houses line narrow streets. At Landau, turn west toward Annweiler and climb "
            "to Burg Trifels, perched dramatically on a sandstone pinnacle. After your "
            "stop, head north through the Pf\u00e4lzerwald via Ramberg to Johanniskreuz, the "
            "legendary crossroads in the heart of the forest, then descend through "
            "Lambrecht back to Neustadt. Return to Hockenheim via Speyer."
        ),
        "midpoint_name": "Burg Trifels",
        "midpoint_description": (
            "This imperial castle sits atop a 494 m sandstone crag with sweeping views "
            "over the Pf\u00e4lzerwald. It held the crown jewels of the Holy Roman Empire "
            "and famously imprisoned Richard the Lionheart in 1193\u20131194. The "
            "Burgsch\u00e4nke restaurant at the foot of the castle serves excellent regional "
            "cuisine."
        ),
        "highlights": [
            "Deutsche Weinstra\u00dfe villages with vineyards and half-timbered houses",
            "Burg Trifels \u2013 imperial castle with stunning views and deep history",
            "Winding forest roads through the heart of the Pf\u00e4lzerwald",
            "Johanniskreuz \u2013 the legendary biker crossroads in the forest",
        ],
        "road_character": (
            "The wine route is smooth and scenic with gentle curves. The road up to "
            "Trifels has steeper switchbacks. The forest roads between Ramberg and "
            "Johanniskreuz are the highlight: flowing, well-surfaced curves through "
            "dense forest with virtually no traffic."
        ),
    },
    {
        "number": 2,
        "name": "Dahner Felsenland \u2013 Sandstone Wonders",
        "slug": "dahner_felsenland",
        "region": "Pf\u00e4lzerwald",
        "distance_km": 250,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Landau in der Pfalz", 49.199, 8.117, "Head south", False),
            ("Annweiler am Trifels", 49.204, 7.969, "Enter the forest", False),
            ("Hauenstein", 49.192, 7.855, "Forest village", False),
            ("Dahn", 49.151, 7.790, "Sandstone rock landscape \u2013 midpoint", True),
            ("Fischbach bei Dahn", 49.104, 7.658, "Deep in the rocks", False),
            ("Pirmasens", 49.201, 7.605, "Turn north", False),
            ("Waldfischbach-Burgalben", 49.281, 7.656, "Forest road", False),
            ("Hochspeyer", 49.431, 7.894, "Northern Pf\u00e4lzerwald", False),
            ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Back to wine country", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Ride into the dramatic Dahner Felsenland, where massive sandstone towers "
            "and bizarre rock formations rise from dense forest. This is the wildest "
            "landscape in the Pf\u00e4lzerwald, with twisting roads carved through a "
            "geological wonderland."
        ),
        "route_description": (
            "Cross the Rhine at Speyer and cut through Landau to Annweiler, then "
            "continue south through the forest to Hauenstein, where the road begins "
            "winding between towering sandstone formations. Dahn is the heart of the "
            "Felsenland\u2014a small town surrounded by castle-topped rock pinnacles "
            "and bizarre natural sandstone sculptures. Continue south to Fischbach bei "
            "Dahn, deep in the rock landscape, then swing east to Pirmasens and north "
            "through Waldfischbach-Burgalben. Follow forest roads past Hochspeyer, "
            "then descend to Neustadt and return via Speyer."
        ),
        "midpoint_name": "Dahn & Dahner Felsenland",
        "midpoint_description": (
            "The town of Dahn sits amid the most spectacular part of the Felsenland, "
            "where sandstone towers up to 50 meters tall erupt from the forest floor. "
            "The Jungfernsprung rock is the iconic formation. Visit the ruined Altdahn "
            "castle perched on three rock pinnacles. Restaurant Felsenland Badstube "
            "serves excellent Palatinate cuisine with views of the rocks."
        ),
        "highlights": [
            "Bizarre sandstone rock formations rising from the forest",
            "Altdahn castle complex on three rock pinnacles",
            "Tight, twisting forest roads with minimal traffic",
            "One of the most unusual landscapes in Germany",
        ],
        "road_character": (
            "Flowing forest roads with medium-radius curves south of Annweiler. Around "
            "Dahn, the roads become tighter and more technical as they weave between "
            "rock formations. The northern return through Waldfischbach has faster, "
            "sweeping curves through open forest."
        ),
    },
    {
        "number": 3,
        "name": "Kalmit Summit & Wine Villages",
        "slug": "kalmit_wine_villages",
        "region": "Pf\u00e4lzerwald",
        "distance_km": 165,
        "difficulty": "Easy to Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Wine route", False),
            ("Sankt Martin", 49.302, 8.106, "Charming wine village", False),
            ("Kalmit (672 m)", 49.326, 8.075, "Highest peak of the Pf\u00e4lzerwald \u2013 midpoint", True),
            ("Hohe Loog", 49.337, 8.084, "Viewpoint", False),
            ("Maikammer", 49.306, 8.132, "Wine village", False),
            ("Edenkoben", 49.284, 8.120, "Villa Ludwigsh\u00f6he", False),
            ("Gleiszellen-Gleishorbach", 49.117, 8.052, "Southern wine route", False),
            ("Bad Bergzabern", 49.100, 8.001, "Spa town", False),
            ("Landau in der Pfalz", 49.199, 8.117, "Return north", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "A shorter tour perfect for a relaxed afternoon, climbing to the highest "
            "peak of the Pf\u00e4lzerwald and weaving through the sun-blessed wine "
            "villages of the southern Deutsche Weinstra\u00dfe."
        ),
        "route_description": (
            "From Hockenheim, cross at Speyer and head to Neustadt. Turn south to the "
            "picturesque village of Sankt Martin, nestled against the Haardt mountains. "
            "Follow the narrow road climbing steeply to the Kalmit, at 672 meters the "
            "highest summit in the Pf\u00e4lzerwald. After enjoying the panorama, descend "
            "via Hohe Loog and Maikammer, then follow the wine route south through "
            "Edenkoben\u2014stop briefly at the Italianate Villa Ludwigsh\u00f6he\u2014continuing "
            "through Gleiszellen and Bad Bergzabern. Return north through Landau and "
            "Speyer."
        ),
        "midpoint_name": "Kalmit (672 m)",
        "midpoint_description": (
            "The highest peak in the Pf\u00e4lzerwald offers a 360\u00b0 panorama from the "
            "Rhine plain to the Vosges mountains. The Kalmith\u00fctte, a rustic mountain "
            "hut run by the Pf\u00e4lzerwald-Verein, serves hearty regional "
            "dishes\u2014Saumagen, Flammkuchen, and local wines. The terrace view is "
            "spectacular."
        ),
        "highlights": [
            "Kalmit summit \u2013 highest point of the Pf\u00e4lzerwald with sweeping panorama",
            "Sankt Martin \u2013 one of the prettiest wine villages in Germany",
            "The steep, winding Kalmith\u00f6henstra\u00dfe",
            "Southern Weinstra\u00dfe villages with their relaxed Mediterranean atmosphere",
        ],
        "road_character": (
            "The approach through wine villages is gentle and scenic. The climb to the "
            "Kalmit is the thrill\u2014a narrow, steep road with tight hairpins through "
            "forest. The southern Weinstra\u00dfe is relaxed riding through vineyard-lined "
            "roads."
        ),
    },
    {
        "number": 4,
        "name": "Johanniskreuz \u2013 Heart of the Pf\u00e4lzerwald",
        "slug": "johanniskreuz_elmstein",
        "region": "Pf\u00e4lzerwald",
        "distance_km": 185,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Enter wine country", False),
            ("Lambrecht", 49.373, 8.080, "Enter Elmstein Valley", False),
            ("Elmstein", 49.360, 7.940, "Valley village", False),
            ("Iggelbach", 49.347, 7.890, "Deeper into forest", False),
            ("Johanniskreuz", 49.348, 7.850, "Legendary crossroads \u2013 midpoint", True),
            ("Hochspeyer", 49.431, 7.894, "North exit", False),
            ("Frankenstein", 49.394, 7.971, "Castle ruin", False),
            ("Weidenthal", 49.383, 7.923, "Forest village", False),
            ("Neidenfels", 49.378, 8.042, "Back to the valley", False),
            ("Lambrecht", 49.373, 8.080, "Exit valley", False),
            ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Return", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Ride through the enchanting Elmstein Valley, the scenic gorge slicing "
            "through the Pf\u00e4lzerwald, to reach Johanniskreuz\u2014the legendary forest "
            "crossroads that has been a favorite biker meeting point for decades."
        ),
        "route_description": (
            "From Speyer, ride west to Neustadt and turn into the Elmstein Valley at "
            "Lambrecht. This narrow valley road is a motorcyclist\u2019s dream\u2014flowing "
            "curves following the Speyerbach stream through dense forest. Pass through "
            "tiny Elmstein and Iggelbach to reach Johanniskreuz, the crossroads in the "
            "heart of the Pf\u00e4lzerwald where four forest roads meet. This has been a "
            "gathering point for motorcyclists for generations. After lunch, head north "
            "to Hochspeyer, then loop back south through Frankenstein (with its ruined "
            "castle) and Weidenthal, returning through the valley to Lambrecht and "
            "back via Speyer."
        ),
        "midpoint_name": "Johanniskreuz",
        "midpoint_description": (
            "This legendary forest crossroads has been THE biker meeting point of the "
            "Pf\u00e4lzerwald since the 1960s. The Haus Johanniskreuz restaurant serves "
            "classic Pf\u00e4lzer dishes\u2014Leberkn\u00f6del, Saumagen, and wild game in season. "
            "On weekends, you\u2019ll find dozens of motorcycles parked here. The "
            "atmosphere is relaxed and the forest setting is magnificent."
        ),
        "highlights": [
            "Elmstein Valley \u2013 one of the best motorcycle roads in the Pfalz",
            "Johanniskreuz \u2013 legendary biker crossroads with great food",
            "Burg Frankenstein ruins (the Pfalz version!)",
            "Continuous flowing curves through pristine forest",
        ],
        "road_character": (
            "Pure motorcycling bliss. The Elmstein Valley road is a flowing sequence "
            "of medium-radius curves following the stream, perfectly surfaced and "
            "rarely congested. The forest roads around Johanniskreuz are wider and "
            "faster. The Frankenstein loop adds some tighter technical sections."
        ),
    },
    {
        "number": 5,
        "name": "Wasgau & the German Wine Gate",
        "slug": "wasgau_wine_gate",
        "region": "Pf\u00e4lzerwald",
        "distance_km": 240,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Landau in der Pfalz", 49.199, 8.117, "Head south", False),
            ("Annweiler am Trifels", 49.204, 7.969, "Into the forest", False),
            ("Bad Bergzabern", 49.100, 8.001, "Spa town", False),
            ("D\u00f6rrenbach", 49.082, 8.006, "Prettiest village in the Pfalz", False),
            ("Schweigen-Rechtenbach", 49.049, 8.054, "Deutsches Weintor \u2013 midpoint", True),
            ("Wissembourg", 49.037, 7.945, "Brief French detour", False),
            ("Schweighofen", 49.052, 8.096, "Border villages", False),
            ("Steinfeld", 49.067, 8.051, "Quiet border region", False),
            ("Klingenm\u00fcnster", 49.135, 8.015, "Wine village", False),
            ("Rhodt unter Rietburg", 49.269, 8.110, "Northern wine route", False),
            ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Return north", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Ride to the southern tip of the Deutsche Weinstra\u00dfe, where Germany "
            "meets France. The Wasgau region offers romantic castle ruins, a brief "
            "French border crossing, and the iconic Deutsches Weintor\u2014the monumental "
            "gate marking the start of the German wine route."
        ),
        "route_description": (
            "From Speyer, head southwest through Landau and Annweiler to Bad "
            "Bergzabern, then continue south to D\u00f6rrenbach\u2014officially voted the "
            "prettiest village in the Pfalz with its half-timbered houses and central "
            "linden tree. Ride to Schweigen-Rechtenbach where the Deutsche Weinstra\u00dfe "
            "begins (or ends) at the monumental Deutsches Weintor. Cross briefly into "
            "Wissembourg in France for coffee, then return through quiet border-region "
            "villages\u2014Schweighofen, Steinfeld\u2014heading north through Klingenm\u00fcnster "
            "and Rhodt unter Rietburg. Follow the Weinstra\u00dfe back to Neustadt and "
            "return via Speyer."
        ),
        "midpoint_name": "Schweigen-Rechtenbach & Deutsches Weintor",
        "midpoint_description": (
            "The imposing stone Wine Gate marks the southern start of the Deutsche "
            "Weinstra\u00dfe. The terrace restaurant atop the gate offers spectacular "
            "views into Alsace and over the vineyards. Wissembourg, just 500 meters "
            "across the French border, adds a charming Alsatian detour with its "
            "canals and half-timbered houses."
        ),
        "highlights": [
            "Deutsches Weintor \u2013 the iconic start of the German Wine Route",
            "D\u00f6rrenbach \u2013 \u201cprettiest village in the Pfalz\u201d",
            "Brief border crossing into Alsace (Wissembourg)",
            "Full length of the southern Deutsche Weinstra\u00dfe",
        ],
        "road_character": (
            "Mostly gentle curves through wine country with some tighter sections "
            "through villages. The roads south of Bad Bergzabern become more winding "
            "as you enter the hilly border region. Quiet and unhurried\u2014perfect for "
            "enjoying the scenery."
        ),
    },
    # ------------------------------------------------------------------
    # ODENWALD  (Tours 6-10)
    # ------------------------------------------------------------------
    {
        "number": 6,
        "name": "Romantic Neckartal",
        "slug": "romantic_neckartal",
        "region": "Odenwald",
        "distance_km": 190,
        "difficulty": "Easy to Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Heidelberg", 49.409, 8.693, "Ride east", False),
            ("Neckargem\u00fcnd", 49.393, 8.797, "Valley narrows", False),
            ("Neckarsteinach", 49.403, 8.838, "Four Castle Town", False),
            ("Hirschhorn", 49.448, 8.893, "Pearl of the Neckar", False),
            ("Eberbach", 49.467, 8.988, "Medieval town \u2013 midpoint", True),
            ("Zwingenberg am Neckar", 49.352, 9.039, "Castle on the cliff", False),
            ("Mosbach", 49.353, 9.146, "Half-timbered town", False),
            ("Neckarzimmern", 49.319, 9.138, "Burg Hornberg", False),
            ("Gundelsheim", 49.285, 9.159, "Neckar valley", False),
            ("Bad Rappenau", 49.239, 8.993, "Return west", False),
            ("Sinsheim", 49.253, 8.879, "Kraichgau", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Follow the winding Neckar river through its most romantic stretch\u2014a "
            "narrow valley lined with castle ruins, medieval towns, and forested "
            "slopes. The road hugs the river through countless curves as you pass "
            "through four-castle Neckarsteinach, Hirschhorn, and Eberbach."
        ),
        "route_description": (
            "Head east to Heidelberg and pick up the Neckar valley road (B37). The "
            "valley narrows dramatically east of Neckargem\u00fcnd, and the road begins "
            "its dance with the river. Pass Neckarsteinach\u2014known as the \u201cFour "
            "Castle Town\u201d for its quartet of hilltop ruins\u2014and continue to "
            "Hirschhorn, where a massive castle towers over a river bend. Follow the "
            "Neckar to Eberbach, a well-preserved medieval town perfect for lunch. "
            "Continue south along the river to Zwingenberg, where a castle perches "
            "impossibly on a cliff face, and on to Mosbach with its beautiful "
            "half-timbered old town. Return westward through Bad Rappenau and "
            "Sinsheim to Hockenheim."
        ),
        "midpoint_name": "Eberbach am Neckar",
        "midpoint_description": (
            "This charming medieval town sits in a wide bend of the Neckar. The "
            "well-preserved Altstadt features a castle, half-timbered houses, and the "
            "historic Kettenbr\u00fccke. Gasthaus Zum Karpfen on the market square is a "
            "local institution serving seasonal fish from the Neckar and traditional "
            "Baden cuisine."
        ),
        "highlights": [
            "Neckarsteinach \u2013 four medieval castles on one hillside",
            "Hirschhorn \u2013 \u201cPearl of the Neckar Valley\u201d",
            "Zwingenberg Castle \u2013 dramatic clifftop position",
            "Continuous river-following curves with castle views",
        ],
        "road_character": (
            "The B37 along the Neckar is a flowing river road\u2014sweeping curves that "
            "follow every bend of the water. Well-surfaced but watch for cyclists and "
            "tourist traffic on sunny weekends. The return via Sinsheim is faster "
            "and more open."
        ),
    },
    {
        "number": 7,
        "name": "Nibelungenstra\u00dfe",
        "slug": "nibelungenstrasse",
        "region": "Odenwald",
        "distance_km": 210,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Heidelberg", 49.409, 8.693, "Head east", False),
            ("Wilhelmsfeld", 49.474, 8.750, "Into the hills", False),
            ("Sch\u00f6nau", 49.438, 8.811, "Climbing", False),
            ("Eberbach", 49.467, 8.988, "Neckar crossing", False),
            ("Oberzent", 49.530, 8.960, "Deep forest", False),
            ("Lindenfels", 49.568, 8.780, "Pearl of the Odenwald \u2013 midpoint", True),
            ("F\u00fcrth im Odenwald", 49.650, 8.773, "Continue north", False),
            ("Rimbach", 49.621, 8.761, "Forest edge", False),
            ("M\u00f6rlenbach", 49.597, 8.735, "Descending", False),
            ("Weinheim", 49.550, 8.667, "Bergstra\u00dfe", False),
            ("Hockenheim", 49.322, 8.548, "End (via A5)", False),
        ],
        "overview": (
            "Trace the route of the Nibelungen through the deep Odenwald on the "
            "legendary B47\u2014a road steeped in mythology and motorcycle legend alike. "
            "Dense forest, tight curves, and the charming hilltop town of Lindenfels."
        ),
        "route_description": (
            "From Heidelberg, climb into the hills via Wilhelmsfeld and Sch\u00f6nau, "
            "gaining altitude as the forest thickens. Join the Neckar briefly at "
            "Eberbach, then turn north into the deep Odenwald. The B47\u2014the "
            "Nibelungenstra\u00dfe\u2014cuts through dense forest on a winding path "
            "supposedly traced by the Nibelungen on their journey to the Huns. Climb "
            "to Lindenfels, the \u201cPearl of the Odenwald,\u201d a hilltop town with a "
            "ruined castle offering sweeping views. Continue north through F\u00fcrth "
            "and Rimbach, descending through M\u00f6rlenbach to Weinheim at the foot of "
            "the Bergstra\u00dfe, then return south to Hockenheim."
        ),
        "midpoint_name": "Lindenfels",
        "midpoint_description": (
            "Known as the \u201cPerle des Odenwaldes,\u201d this hilltop town at 400 m is "
            "crowned by a 12th-century castle ruin with panoramic views over the "
            "Odenwald hills. The compact medieval center is charming. Restaurant "
            "Burgblick near the castle offers regional dishes with a view\u2014try "
            "the Odenw\u00e4lder Kochk\u00e4se."
        ),
        "highlights": [
            "The legendary Nibelungenstra\u00dfe (B47) through deep forest",
            "Lindenfels castle ruins with panoramic views",
            "Dense Odenwald forest with excellent curves",
            "Mythology and motorcycling combined",
        ],
        "road_character": (
            "The Nibelungenstra\u00dfe is a proper motorcycle road\u2014well-surfaced with a "
            "mix of flowing and tight curves through dense forest. The climb to "
            "Lindenfels features some rewarding switchbacks. Watch for logging "
            "trucks on weekdays."
        ),
    },
    {
        "number": 8,
        "name": "Deep Odenwald \u2013 Michelstadt & Amorbach",
        "slug": "michelstadt_amorbach",
        "region": "Odenwald",
        "distance_km": 230,
        "difficulty": "Moderate to Challenging",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Heidelberg", 49.409, 8.693, "Head east", False),
            ("Neckargem\u00fcnd", 49.393, 8.797, "Neckar valley", False),
            ("Sch\u00f6nau", 49.438, 8.811, "Into the hills", False),
            ("Waldbrunn", 49.454, 9.103, "Deep forest", False),
            ("Mudau", 49.534, 9.208, "Remote Odenwald", False),
            ("Amorbach", 49.645, 9.221, "Baroque abbey", False),
            ("Michelstadt", 49.676, 9.004, "Fairy-tale Rathaus \u2013 midpoint", True),
            ("Erbach", 49.659, 8.994, "Ivory museum", False),
            ("Reichelsheim", 49.710, 8.837, "Continue south", False),
            ("Lindenfels", 49.568, 8.780, "Pearl of the Odenwald", False),
            ("Bensheim", 49.681, 8.618, "Bergstra\u00dfe", False),
            ("Hockenheim", 49.322, 8.548, "End (via A5)", False),
        ],
        "overview": (
            "Penetrate the most remote reaches of the Odenwald to discover "
            "Amorbach\u2019s stunning Baroque abbey and Michelstadt\u2019s fairy-tale "
            "medieval Rathaus. Long stretches through dark forest with barely a "
            "village in sight."
        ),
        "route_description": (
            "From Heidelberg, ride through Neckargem\u00fcnd and Sch\u00f6nau into the "
            "rising hills, continuing east to Waldbrunn and deeper into the "
            "Odenwald. The forest becomes denser and villages rarer as you approach "
            "Mudau. Continue north to Amorbach, where an unexpectedly magnificent "
            "Baroque abbey awaits in this tiny town. Then ride west to Michelstadt, "
            "home to one of Germany\u2019s most photographed half-timbered Rathaus "
            "buildings. From neighboring Erbach (famous for its ivory carving "
            "tradition), head south through Reichelsheim and Lindenfels, descending "
            "to the Bergstra\u00dfe at Bensheim before returning via the A5."
        ),
        "midpoint_name": "Michelstadt",
        "midpoint_description": (
            "The medieval Marktplatz is dominated by the spectacular Rathaus, a "
            "half-timbered structure from 1484 perched on oak pillars\u2014one of the "
            "most photographed buildings in Germany. The Altstadt is full of "
            "crooked alleys and timber-framed houses. Gasthaus Drei Hasen serves "
            "traditional Odenwald cuisine; try the Odenw\u00e4lder Apfelwein."
        ),
        "highlights": [
            "Michelstadt Rathaus \u2013 one of Germany\u2019s finest half-timbered buildings",
            "Amorbach Abbey \u2013 stunning Baroque interior in a tiny forest town",
            "Remote, traffic-free forest roads through deep Odenwald",
            "Erbach\u2019s unexpected ivory carving museum",
        ],
        "road_character": (
            "This is the most remote tour in the Odenwald. Long stretches of forest "
            "road with flowing curves and very little traffic. The roads around "
            "Mudau are narrow but well-surfaced. Technical but never "
            "intimidating\u2014a rewarding ride for confident riders."
        ),
    },
    {
        "number": 9,
        "name": "Bergstra\u00dfe & Melibokus",
        "slug": "bergstrasse_melibokus",
        "region": "Odenwald / Bergstra\u00dfe",
        "distance_km": 175,
        "difficulty": "Easy",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Weinheim", 49.550, 8.667, "Castle gardens", False),
            ("Birkenau", 49.563, 8.707, "Into Odenwald", False),
            ("Gorxheimertal", 49.560, 8.728, "Hill country", False),
            ("Rimbach", 49.621, 8.761, "Forest edge", False),
            ("Lindenfels", 49.568, 8.780, "Pearl of the Odenwald", False),
            ("Bensheim", 49.681, 8.618, "Bergstra\u00dfe", False),
            ("Auerbacher Schloss", 49.709, 8.652, "Castle and viewpoint \u2013 midpoint", True),
            ("Zwingenberg", 49.726, 8.613, "Oldest Bergstra\u00dfe town", False),
            ("Alsbach-H\u00e4hnlein", 49.740, 8.638, "Continue north", False),
            ("Seeheim", 49.765, 8.648, "Northern Bergstra\u00dfe", False),
            ("Hockenheim", 49.322, 8.548, "End (via A5/A67)", False),
        ],
        "overview": (
            "A relaxed ride along the Bergstra\u00dfe\u2014Germany\u2019s \u201cspring garden\u201d with "
            "its Mediterranean microclimate\u2014combined with a loop through the western "
            "Odenwald hills and the panoramic Auerbacher Schloss."
        ),
        "route_description": (
            "Head north to Weinheim, known for its exotic castle gardens, then turn "
            "east into the Odenwald via Birkenau. Ride through the Gorxheimertal "
            "and over the hills to Rimbach and Lindenfels. Descend west to Bensheim "
            "on the Bergstra\u00dfe, then continue north to Auerbach where the impressive "
            "Auerbacher Schloss overlooks the Rhine plain. Continue through the "
            "charming towns of Zwingenberg, Alsbach, and Seeheim before returning "
            "south to Hockenheim."
        ),
        "midpoint_name": "Auerbacher Schloss",
        "midpoint_description": (
            "The largest and best-preserved castle ruin on the Bergstra\u00dfe offers "
            "views from the Taunus to the Black Forest on clear days. The Schloss "
            "restaurant serves seasonal dishes on a terrace with views over the "
            "Rhine plain\u2014you can see the Palatinate Forest and the Vosges beyond."
        ),
        "highlights": [
            "Bergstra\u00dfe\u2019s Mediterranean microclimate \u2013 almond and peach trees",
            "Auerbacher Schloss \u2013 largest castle ruin on the Bergstra\u00dfe",
            "Zwingenberg \u2013 oldest town on the Bergstra\u00dfe",
            "Relaxed pace, perfect for a shorter day or riding two-up",
        ],
        "road_character": (
            "Gentle and flowing\u2014this is one of the easiest tours in the collection. "
            "The Bergstra\u00dfe is smooth and scenic, the Odenwald section has moderate "
            "curves through orchards and forest. Ideal for a relaxed day."
        ),
    },
    {
        "number": 10,
        "name": "Katzenbuckel & Mosbach",
        "slug": "katzenbuckel_mosbach",
        "region": "Odenwald",
        "distance_km": 195,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Sinsheim", 49.253, 8.879, "Head east", False),
            ("Neckarbischofsheim", 49.296, 8.955, "Rolling hills", False),
            ("Schwarzach", 49.374, 8.976, "Cross Neckar", False),
            ("Eberbach", 49.467, 8.988, "Neckar town", False),
            ("Str\u00fcmpfelbrunn", 49.500, 9.040, "Into deep forest", False),
            ("Katzenbuckel (626 m)", 49.483, 9.004, "Highest Odenwald peak", False),
            ("Waldbrunn", 49.454, 9.103, "Health resort \u2013 midpoint", True),
            ("Mudau", 49.534, 9.208, "Remote Odenwald", False),
            ("Mosbach", 49.353, 9.146, "Half-timbered town", False),
            ("Neckarzimmern", 49.319, 9.138, "Burg Hornberg", False),
            ("Gundelsheim", 49.285, 9.159, "Neckar valley", False),
            ("Bad Rappenau", 49.239, 8.993, "Return west", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Climb to the Katzenbuckel\u2014at 626 m the highest peak in the "
            "Odenwald\u2014on switchback roads through dense forest, then discover the "
            "beautifully preserved half-timbered town of Mosbach."
        ),
        "route_description": (
            "Ride east through Sinsheim into the rolling hills via "
            "Neckarbischofsheim. Cross the Neckar at Schwarzach and head into the "
            "forest toward Eberbach and Str\u00fcmpfelbrunn. A winding road leads up to "
            "the Katzenbuckel (626 m), the Odenwald\u2019s highest point\u2014an ancient "
            "volcanic plug now wooded to the summit with a viewing tower. Continue "
            "to Waldbrunn and loop through Mudau before descending south to Mosbach, "
            "where the Altstadt is a treasure chest of half-timbered architecture. "
            "Pass Neckarzimmern\u2014note Burg Hornberg, the castle of the knight "
            "G\u00f6tz von Berlichingen\u2014and return through Gundelsheim and Bad Rappenau."
        ),
        "midpoint_name": "Waldbrunn & Katzenbuckel",
        "midpoint_description": (
            "The Katzenbuckel summit features a viewing tower with panoramic views "
            "over the Odenwald. Waldbrunn, just below, is a peaceful health resort. "
            "Gasthof Katzenbuckel near the summit serves hearty Odenwald "
            "fare\u2014Wildschweingulasch (wild boar) is the house specialty."
        ),
        "highlights": [
            "Katzenbuckel (626 m) \u2013 Odenwald\u2019s highest peak with viewing tower",
            "Mosbach \u2013 outstanding half-timbered Altstadt",
            "Burg Hornberg \u2013 castle of G\u00f6tz von Berlichingen",
            "Technical switchback climb to the summit",
        ],
        "road_character": (
            "The approach through the hills is flowing and pleasant. The climb to "
            "the Katzenbuckel is the highlight\u2014tight switchbacks through forest. "
            "The Mudau-to-Mosbach descent features continuous curves. Good road "
            "surfaces throughout."
        ),
    },
    # ------------------------------------------------------------------
    # SCHWARZWALD / BLACK FOREST  (Tours 11-16)
    # ------------------------------------------------------------------
    {
        "number": 11,
        "name": "Schwarzwaldhochstra\u00dfe \u2013 The Classic",
        "slug": "schwarzwaldhochstrasse",
        "region": "Schwarzwald",
        "distance_km": 280,
        "difficulty": "Moderate to Challenging",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Karlsruhe", 49.006, 8.404, "A5 south", False),
            ("Baden-Baden", 48.761, 8.241, "Spa city", False),
            ("Geroldsau", 48.722, 8.240, "Waterfall", False),
            ("B\u00fchlerh\u00f6he", 48.683, 8.223, "Join B500", False),
            ("Sand", 48.654, 8.226, "B500 junction", False),
            ("Unterstmatt", 48.620, 8.210, "Ridge road", False),
            ("Mummelsee (1036 m)", 48.596, 8.201, "Mountain lake \u2013 midpoint", True),
            ("Ruhestein", 48.561, 8.221, "Nationalpark center", False),
            ("Kniebis", 48.483, 8.287, "Pass village", False),
            ("Freudenstadt", 48.462, 8.411, "Germany\u2019s largest Marktplatz", False),
            ("Calw", 48.714, 8.741, "Hermann Hesse\u2019s birthplace", False),
            ("Pforzheim", 48.891, 8.704, "Gold City", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Germany\u2019s most famous motorcycle road. The B500 "
            "Schwarzwaldhochstra\u00dfe runs along the northern Black Forest ridge at "
            "over 1000 m altitude, with panoramic views, alpine meadows, and "
            "sweeping curves that make this an absolute must-ride."
        ),
        "route_description": (
            "Head south on the A5 past Karlsruhe to elegant Baden-Baden, then climb "
            "into the Black Forest via Geroldsau. Join the legendary B500 at "
            "B\u00fchlerh\u00f6he\u2014from here, the Schwarzwaldhochstra\u00dfe follows the ridge for "
            "over 60 km of pure riding pleasure. Pass through Unterstmatt to the "
            "Mummelsee, a mystical circular lake at 1036 m. Continue past the "
            "Ruhestein, gateway to the Black Forest National Park. The road "
            "eventually descends through Kniebis to Freudenstadt, laid out on "
            "Germany\u2019s largest market square. Return east through the scenic "
            "Nagoldtal via Calw\u2014Hermann Hesse\u2019s birthplace\u2014and Pforzheim."
        ),
        "midpoint_name": "Mummelsee (1036 m)",
        "midpoint_description": (
            "This small, dark lake at 1036 m altitude is steeped in legend\u2014water "
            "spirits were said to dwell in its depths. The Berghotel Mummelsee, "
            "right on the lakeside, serves Black Forest cuisine including "
            "Schwarzw\u00e4lder Schinken and K\u00e4sesp\u00e4tzle. The terrace overlooks the lake "
            "with the Hornisgrinde rising behind it. A short walk takes you to the "
            "summit for 360\u00b0 views."
        ),
        "highlights": [
            "B500 Schwarzwaldhochstra\u00dfe \u2013 Germany\u2019s most iconic motorcycle road",
            "Mummelsee \u2013 legendary mountain lake at 1036 m",
            "Hornisgrinde (1164 m) \u2013 highest peak of the northern Black Forest",
            "Over 60 km of continuous ridge-top curves",
            "Alpirsbach Klosterbr\u00e4u \u2013 one of Germany\u2019s finest small breweries",
        ],
        "road_character": (
            "This is THE ride. The B500 serves up sweeping, well-surfaced curves "
            "along the ridge with spectacular views. Speed is tempting but watch "
            "for slower traffic and tourists, especially on weekends. The road is "
            "in excellent condition and offers curves of every radius. After "
            "Freudenstadt, the roads become quieter and faster."
        ),
    },
    {
        "number": 12,
        "name": "Murgtal & Northern Heights",
        "slug": "murgtal_northern_heights",
        "region": "Schwarzwald",
        "distance_km": 270,
        "difficulty": "Moderate to Challenging",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Rastatt", 48.858, 8.204, "Enter valley (via A5)", False),
            ("Gaggenau", 48.809, 8.320, "Industrial town", False),
            ("Gernsbach", 48.771, 8.364, "Old town", False),
            ("Weisenbach", 48.732, 8.365, "Valley deepens", False),
            ("Forbach", 48.685, 8.347, "Wooden bridge \u2013 midpoint", True),
            ("Schwarzenbachtalsperre", 48.667, 8.322, "Forest reservoir", False),
            ("Herrenwies", 48.658, 8.253, "Mountain village", False),
            ("Sand", 48.654, 8.226, "Join B500", False),
            ("B\u00fchlerh\u00f6he", 48.683, 8.223, "Viewpoint", False),
            ("B\u00fchl", 48.696, 8.136, "Ortenau", False),
            ("Hockenheim", 49.322, 8.548, "End (via A5)", False),
        ],
        "overview": (
            "Ride through the dramatic Murg valley\u2014a deep gorge cutting into the "
            "Black Forest\u2014past a stunning reservoir and up to the ridge, combining "
            "valley drama with mountain panoramas."
        ),
        "route_description": (
            "From Rastatt, follow the B462 into the Murgtal at Gaggenau. The valley "
            "narrows dramatically at Gernsbach, and the road begins its winding "
            "course along the rushing Murg river. Continue through Weisenbach to "
            "Forbach, where a unique covered wooden bridge spans the gorge. Above "
            "Forbach, detour to the Schwarzenbachtalsperre, a reservoir surrounded "
            "by dark forest. Climb to Herrenwies and join the B500 at Sand for a "
            "taste of the Schwarzwaldhochstra\u00dfe. Descend via B\u00fchlerh\u00f6he to B\u00fchl "
            "and return on the A5."
        ),
        "midpoint_name": "Forbach & Schwarzenbachtalsperre",
        "midpoint_description": (
            "Forbach sits in the deepest part of the Murg gorge, its covered wooden "
            "bridge a striking landmark. Above town, the Schwarzenbachtalsperre is "
            "a beautiful reservoir surrounded by dense forest\u2014perfect for a short "
            "walk. Gasthaus Waldlust in Forbach serves traditional Black Forest "
            "dishes in a rustic setting."
        ),
        "highlights": [
            "Murg valley \u2013 a dramatic gorge with continuous curves",
            "Forbach\u2019s covered wooden bridge",
            "Schwarzenbachtalsperre \u2013 atmospheric forest reservoir",
            "Connection to the legendary B500",
            "Impressive elevation gain from valley to ridge",
        ],
        "road_character": (
            "The Murgtal road is demanding\u2014narrow, with tight curves following the "
            "river through the gorge. The climb from Forbach to the ridge is steep "
            "with switchbacks. Well-surfaced but technically engaging. This tour "
            "rewards confident, precise riding."
        ),
    },
    {
        "number": 13,
        "name": "Kinzigtal & Gutachtal",
        "slug": "kinzigtal_gutachtal",
        "region": "Schwarzwald",
        "distance_km": 340,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Pforzheim", 48.891, 8.704, "Gold City", False),
            ("Calw", 48.714, 8.741, "Hermann Hesse\u2019s birthplace", False),
            ("Freudenstadt", 48.462, 8.411, "Largest Marktplatz", False),
            ("Alpirsbach", 48.346, 8.403, "Klosterbr\u00e4u brewery", False),
            ("Schiltach", 48.290, 8.339, "Half-timbered gem", False),
            ("Wolfach", 48.293, 8.219, "Glassblowing", False),
            ("Vogtsbauernhof, Gutach", 48.256, 8.180, "Open-air museum \u2013 midpoint", True),
            ("Hausach", 48.282, 8.175, "Valley junction", False),
            ("Haslach im Kinzigtal", 48.278, 8.087, "Trachtmuseum", False),
            ("Gengenbach", 48.407, 8.015, "Beautiful old town", False),
            ("Oberkirch", 48.528, 8.078, "Renchtal", False),
            ("Baden-Baden", 48.761, 8.241, "Spa city", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Explore the central Black Forest\u2019s most scenic valleys\u2014the Kinzigtal "
            "and Gutachtal\u2014with their traditional farmhouses, half-timbered towns, "
            "and the famous Vogtsbauernhof open-air museum."
        ),
        "route_description": (
            "Head south through Pforzheim and Calw\u2014Hermann Hesse\u2019s birthplace on "
            "the Nagold river\u2014descending through the Nagoldtal to Freudenstadt. "
            "Continue to Alpirsbach for the famous Klosterbr\u00e4u brewery, then into "
            "the central valleys. Follow the Kinzig through Schiltach\u2014a half-timbered "
            "masterpiece\u2014and Wolfach to the Vogtsbauernhof, the premier open-air "
            "museum of Black Forest farmhouse architecture. Exit the Kinzigtal "
            "through Gengenbach, one of the Black Forest\u2019s most beautiful towns. "
            "Return north through the Renchtal via Oberkirch and Baden-Baden."
        ),
        "midpoint_name": "Vogtsbauernhof (Open-Air Museum)",
        "midpoint_description": (
            "The Black Forest Open-Air Museum features original 16th\u201319th century "
            "farmhouses reassembled on site, complete with their massive hipped "
            "roofs. It\u2019s the best place to understand Black Forest rural culture. "
            "The Hofstube restaurant inside the museum serves traditional "
            "Schwarzwald dishes\u2014Sch\u00e4ufele, Bibilisk\u00e4s, and homemade Black Forest "
            "cake."
        ),
        "highlights": [
            "Gengenbach \u2013 \u201cthe Nice of the Black Forest,\u201d stunning Altstadt",
            "Vogtsbauernhof \u2013 premier open-air museum of Black Forest culture",
            "Schiltach \u2013 one of Germany\u2019s best-preserved half-timbered towns",
            "Alpirsbach Klosterbr\u00e4u brewery",
            "Continuous valley curves through the central Black Forest",
        ],
        "road_character": (
            "Valley roads that follow rivers\u2014sweeping and flowing with a good mix "
            "of straights and curves. Well-surfaced and mostly wide enough for "
            "comfortable riding. The Gutachtal is narrower and more technical than "
            "the Kinzigtal."
        ),
    },
    {
        "number": 14,
        "name": "Allerheiligen Waterfalls & Renchtal",
        "slug": "allerheiligen_renchtal",
        "region": "Schwarzwald",
        "distance_km": 320,
        "difficulty": "Moderate to Challenging",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Rastatt", 48.858, 8.204, "Via Rhine valley", False),
            ("Achern", 48.628, 8.075, "Enter hills", False),
            ("Kappelrodeck", 48.592, 8.113, "Red wine village", False),
            ("Ottenh\u00f6fen", 48.570, 8.152, "Valley end", False),
            ("Kloster Allerheiligen", 48.538, 8.132, "Ruined monastery \u2013 midpoint", True),
            ("Oppenau", 48.474, 8.161, "Renchtal", False),
            ("Bad Peterstal-Griesbach", 48.427, 8.202, "Spa village", False),
            ("Kniebis", 48.483, 8.287, "Pass", False),
            ("Ruhestein", 48.561, 8.221, "Join B500", False),
            ("Sand", 48.654, 8.226, "B500 north", False),
            ("Baden-Baden", 48.761, 8.241, "Spa city", False),
            ("Hockenheim", 49.322, 8.548, "End (via A5)", False),
        ],
        "overview": (
            "A stunning loop combining the atmospheric ruins of Allerheiligen "
            "monastery, its cascading waterfalls, and the beautiful "
            "Renchtal\u2014finished off with a stretch of the legendary B500."
        ),
        "route_description": (
            "Head south through Rastatt to Achern and climb into the hills through Kappelrodeck, "
            "the heart of the Baden red wine country. Continue up through "
            "Ottenh\u00f6fen into the mountains, climbing steeply to the ruins of "
            "Allerheiligen\u2014a Gothic monastery in a forest clearing with "
            "spectacular waterfalls cascading down below. Cross the Zuflucht pass "
            "and descend into the Renchtal at Oppenau. Ride south to Bad "
            "Peterstal-Griesbach, then climb to Kniebis and join the B500 "
            "northbound at Ruhestein. Ride the Schwarzwaldhochstra\u00dfe to Sand "
            "and Baden-Baden, then return via the A5."
        ),
        "midpoint_name": "Kloster Allerheiligen",
        "midpoint_description": (
            "The ruined Gothic monastery of All Saints sits in a remote forest "
            "clearing at 620 m. Its roofless walls are draped in ivy, creating an "
            "ethereal atmosphere. Below, the Allerheiligen Waterfalls cascade 83 m "
            "down a series of steps carved in dark rock. The Klosterst\u00fcble "
            "restaurant serves simple but excellent Black Forest "
            "fare\u2014Maultaschen and Flammkuchen."
        ),
        "highlights": [
            "Allerheiligen \u2013 atmospheric ruined monastery in the forest",
            "83 m cascading waterfalls below the monastery",
            "Steep mountain climbing through dense forest",
            "Connection to the B500 Schwarzwaldhochstra\u00dfe",
            "Kappelrodeck red wine village",
        ],
        "road_character": (
            "Challenging and rewarding. The climb from Ottenh\u00f6fen to Allerheiligen "
            "is steep with tight switchbacks\u2014the best technical riding in this "
            "collection. The descent to Oppenau is equally demanding. The B500 "
            "section is more relaxed with sweeping ridge curves."
        ),
    },
    {
        "number": 15,
        "name": "Nagoldtal & Calw",
        "slug": "nagoldtal_calw",
        "region": "Schwarzwald",
        "distance_km": 260,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Wiesloch", 49.294, 8.698, "Head south", False),
            ("Bretten", 49.036, 8.707, "Melanchthon\u2019s birthplace", False),
            ("Pforzheim", 48.891, 8.704, "Gold city", False),
            ("Tiefenbronn", 48.825, 8.802, "Into the forest", False),
            ("Calw", 48.714, 8.741, "Hesse\u2019s birthplace \u2013 midpoint", True),
            ("Bad Teinach", 48.692, 8.688, "Spa in the valley", False),
            ("Zavelstein", 48.698, 8.668, "Castle ruin", False),
            ("Bad Liebenzell", 48.775, 8.732, "Thermal springs", False),
            ("Enzkl\u00f6sterle", 48.665, 8.469, "Remote forest village", False),
            ("Bad Wildbad", 48.756, 8.550, "Thermal spa", False),
            ("Pforzheim", 48.891, 8.704, "Return north", False),
            ("Hockenheim", 49.322, 8.548, "End (via A5/A8)", False),
        ],
        "overview": (
            "Explore the eastern Black Forest through the winding Nagold valley "
            "and the charming town of Calw\u2014birthplace of Hermann Hesse. Forested "
            "valleys, castle ruins, and thermal spa towns."
        ),
        "route_description": (
            "Head south through Wiesloch and Bretten to Pforzheim, the \u201cGold "
            "City\u201d at the northern gate of the Black Forest. Turn south through "
            "Tiefenbronn to Calw, beautifully set on the Nagold river\u2014this is "
            "where Hermann Hesse was born, and his spirit pervades the "
            "half-timbered Altstadt. Continue south through Bad Teinach and "
            "detour to the ruined castle of Zavelstein with its stunning views. "
            "Ride north to Bad Liebenzell, then cut west through the deep forest "
            "to Enzkl\u00f6sterle. Return via Bad Wildbad, famous for its thermal "
            "springs, and Pforzheim."
        ),
        "midpoint_name": "Calw",
        "midpoint_description": (
            "Hermann Hesse\u2019s birthplace is a gem of a Black Forest town. The "
            "half-timbered houses along the Nagold river inspired many of his "
            "early works. Visit the Hesse Museum in his birth house. The "
            "Ratskeller Calw serves Swabian-Black Forest dishes\u2014Maultaschen, "
            "Schupfnudeln, and excellent local wines\u2014in a historic setting."
        ),
        "highlights": [
            "Calw \u2013 Hermann Hesse\u2019s birthplace, beautiful Nagold-river setting",
            "Nagold valley curves through dense Black Forest",
            "Zavelstein castle ruin with panoramic views",
            "Enzkl\u00f6sterle \u2013 remote forest village",
            "Eastern Black Forest character \u2013 different from the western ridge",
        ],
        "road_character": (
            "The Nagold valley is winding and picturesque\u2014flowing curves following "
            "the river. The forest roads around Enzkl\u00f6sterle are narrower and more "
            "technical. Overall well-surfaced with moderate traffic. Good mix of "
            "fast and slow sections."
        ),
    },
    {
        "number": 16,
        "name": "Titisee & Southern Black Forest",
        "slug": "titisee_southern_bf",
        "region": "Schwarzwald",
        "distance_km": 530,
        "difficulty": "Moderate to Challenging",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Pforzheim", 48.891, 8.704, "Gold City", False),
            ("Calw", 48.714, 8.741, "Hermann Hesse\u2019s birthplace", False),
            ("Freudenstadt", 48.462, 8.411, "Marktplatz", False),
            ("Schiltach", 48.290, 8.339, "Half-timbered town", False),
            ("Triberg", 48.133, 8.237, "Black Forest waterfalls", False),
            ("Furtwangen", 48.055, 8.208, "Cuckoo clock museum", False),
            ("Titisee", 47.903, 8.157, "Iconic lake \u2013 midpoint", True),
            ("Hinterzarten", 47.906, 8.110, "Health resort", False),
            ("H\u00f6llental", 47.897, 8.050, "Hell Valley gorge", False),
            ("Kirchzarten", 47.963, 7.952, "Valley exit", False),
            ("Freiburg im Breisgau", 47.999, 7.842, "Black Forest capital", False),
            ("Offenburg", 48.473, 7.954, "Ortenau", False),
            ("Baden-Baden", 48.761, 8.241, "Spa city", False),
            ("Hockenheim", 49.322, 8.548, "End (via A5)", False),
        ],
        "overview": (
            "The longest tour in the collection reaches deep into the southern "
            "Black Forest to the iconic Titisee lake via scenic forest roads, "
            "returning through the dramatic H\u00f6llental (Hell Valley). A full-day "
            "adventure through the most dramatic Black Forest landscapes."
        ),
        "route_description": (
            "Head south through Pforzheim and Calw into the Black Forest interior "
            "via the Nagoldtal to Freudenstadt. Continue through Schiltach and "
            "into the Kinzigtal, stopping at Triberg\u2019s famous waterfalls. Climb "
            "to Furtwangen, home of the German Clock Museum, then south to the "
            "Titisee, the Black Forest\u2019s most famous lake, set at 858 m between "
            "dark forested hills. After lunch, ride west through Hinterzarten and "
            "plunge into the H\u00f6llental\u2014the \u201cHell Valley\u201d\u2014a dramatic gorge with "
            "near-vertical walls. Emerge at Kirchzarten and continue to Freiburg, "
            "the \u201ccapital\u201d of the Black Forest, before returning north via "
            "Offenburg and Baden-Baden."
        ),
        "midpoint_name": "Titisee",
        "midpoint_description": (
            "The quintessential Black Forest lake, dark and mirror-still, "
            "surrounded by forested hills. Avoid the touristy lakefront shops "
            "and head to Bergsee-Restaurant for traditional Schwarzwald "
            "fare\u2014Forelle (trout), Sch\u00e4ufele, and of course authentic "
            "Schwarzw\u00e4lder Kirschtorte. The lakeside terrace is worth the visit."
        ),
        "highlights": [
            "Titisee \u2013 iconic Black Forest lake at 858 m",
            "H\u00f6llental (Hell Valley) \u2013 dramatic gorge with sheer walls",
            "Furtwangen German Clock Museum \u2013 cuckoo clock tradition",
            "Freiburg \u2013 one of Germany\u2019s most livable cities",
            "Full spectrum of Black Forest landscapes",
        ],
        "road_character": (
            "A long tour requiring stamina. The approach via the Elztal is flowing "
            "and fast. The roads around Titisee are well-surfaced with moderate "
            "curves. The H\u00f6llental is the showpiece\u2014a steep, winding descent "
            "through the gorge with tunnels and dramatic views. Allow a full day."
        ),
    },
    # ------------------------------------------------------------------
    # ALSACE / VOSGES  (Tours 17-19)
    # ------------------------------------------------------------------
    {
        "number": 17,
        "name": "Fleckenstein & Northern Vosges",
        "slug": "fleckenstein_vosges",
        "region": "Elsass / Alsace",
        "distance_km": 230,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Landau in der Pfalz", 49.199, 8.117, "Head south", False),
            ("Bad Bergzabern", 49.100, 8.001, "Spa town", False),
            ("Wissembourg", 49.037, 7.945, "Cross into France", False),
            ("Lembach", 49.003, 7.788, "Vosges forest", False),
            ("Ch\u00e2teau du Fleckenstein", 49.033, 7.774, "Sandstone castle \u2013 midpoint", True),
            ("Niederbronn-les-Bains", 48.952, 7.643, "Thermal spa", False),
            ("W\u00f6rth-sur-Sauer", 48.938, 7.737, "Through the forest", False),
            ("Lauterbourg", 48.974, 8.176, "Back to Germany", False),
            ("Germersheim", 49.216, 8.366, "Cross Rhine", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Cross into France to discover the Ch\u00e2teau du Fleckenstein\u2014a medieval "
            "fortress carved into a 30-meter sandstone cliff\u2014and ride the forested "
            "roads of the northern Vosges, a UNESCO Biosphere Reserve."
        ),
        "route_description": (
            "Cross the Rhine at Speyer, ride through Landau and Bad Bergzabern to "
            "Wissembourg, then cross into France. Follow the D3 to Lembach and "
            "turn south to the Ch\u00e2teau du Fleckenstein, one of the most "
            "spectacular castle ruins in Europe\u2014half-built, half-carved from a "
            "massive sandstone pillar. Continue through the northern Vosges forest "
            "to Niederbronn-les-Bains, a charming thermal spa town. Head east "
            "through the forest to W\u00f6rth-sur-Sauer, then back to Germany at "
            "Lauterbourg. Return via Germersheim."
        ),
        "midpoint_name": "Ch\u00e2teau du Fleckenstein",
        "midpoint_description": (
            "This medieval castle is literally carved into a 30-meter sandstone "
            "cliff\u2014rooms, staircases, and cisterns chiseled from living rock. The "
            "scale is breathtaking. Built in the 12th century, it controlled the "
            "border between Alsace and the Palatinate. Restaurant Au Fleckenstein "
            "at the castle base serves excellent Alsatian-Pf\u00e4lzer fusion "
            "cuisine\u2014try the Flammekueche."
        ),
        "highlights": [
            "Ch\u00e2teau du Fleckenstein \u2013 castle carved from a sandstone cliff",
            "Cross-border riding (Germany \u2192 France \u2192 Germany)",
            "Northern Vosges forest roads (UNESCO Biosphere Reserve)",
            "Wissembourg \u2013 charming Alsatian-German border town",
            "Niederbronn-les-Bains thermal spa",
        ],
        "road_character": (
            "The German side is familiar Pf\u00e4lzerwald riding. Once in France, the "
            "forest roads become even quieter with excellent surfaces and flowing "
            "curves. The northern Vosges has a wilder, more remote feel than the "
            "Pf\u00e4lzerwald. Watch for different traffic rules in France."
        ),
    },
    {
        "number": 18,
        "name": "Alsace Wine Route",
        "slug": "alsace_wine_route",
        "region": "Elsass / Alsace",
        "distance_km": 370,
        "difficulty": "Easy to Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Karlsruhe", 49.006, 8.404, "A5 south", False),
            ("Kehl", 48.572, 7.818, "Cross Rhine", False),
            ("Strasbourg", 48.573, 7.752, "Alsatian capital", False),
            ("Molsheim", 48.542, 7.493, "Bugatti birthplace", False),
            ("Rosheim", 48.496, 7.471, "Romanesque church", False),
            ("Obernai", 48.462, 7.483, "Alsatian jewel \u2013 midpoint", True),
            ("Barr", 48.407, 7.449, "Wine capital", False),
            ("Andlau", 48.387, 7.417, "Romanesque abbey", False),
            ("S\u00e9lestat", 48.260, 7.453, "Humanist Library", False),
            ("Rhinau", 48.318, 7.711, "Cross Rhine back", False),
            ("Lahr", 48.343, 7.871, "Return to Germany", False),
            ("Baden-Baden", 48.761, 8.241, "Spa city", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Cross into France for a day on the famous Route des Vins "
            "d\u2019Alsace\u2014half-timbered villages, vineyards climbing steep hillsides, "
            "and some of the best food in Europe. Alsatian cuisine is the perfect "
            "midpoint reward."
        ),
        "route_description": (
            "Head south on the A5 to Kehl, cross the Rhine into Strasbourg, and "
            "ride through Molsheim\u2014birthplace of Bugatti\u2014to join the Alsace Wine "
            "Route. Head south through a succession of wine villages\u2014each more "
            "picturesque than the last\u2014with their distinctive colombage "
            "(half-timbered) houses, window boxes overflowing with geraniums, and "
            "stork nests on every chimney. Rosheim and Obernai are gems. Continue "
            "to Barr, the wine capital, and Andlau with its Romanesque abbey. "
            "Ride south to S\u00e9lestat, cross back to Germany at Rhinau, and "
            "return north via Lahr and Baden-Baden."
        ),
        "midpoint_name": "Obernai",
        "midpoint_description": (
            "One of the most beautiful towns in Alsace, Obernai\u2019s Marktplatz is "
            "a feast of color\u2014half-timbered houses in every shade, the "
            "six-bucket well, and the Kappelturm tower. The Winstub Le Caveau "
            "de Gail serves classic Alsatian cuisine\u2014choucroute garnie, "
            "Baeckeoffe, tarte flamb\u00e9e\u2014paired with local Gew\u00fcrztraminer or "
            "Riesling."
        ),
        "highlights": [
            "Alsace Wine Route \u2013 one of France\u2019s most scenic drives",
            "Obernai \u2013 jewel of Alsatian architecture",
            "Half-timbered villages draped in flowers",
            "Alsatian cuisine \u2013 France\u2019s most hearty and Germanic",
            "Stork nests, vineyards, and castle ruins at every turn",
        ],
        "road_character": (
            "Relaxed and scenic\u2014the wine route winds gently through villages and "
            "vineyards without demanding technical riding. The charm is in the "
            "scenery, not the curves. Perfect for a day focused on eating and "
            "sightseeing rather than fast riding."
        ),
    },
    {
        "number": 19,
        "name": "Col de Saverne & Vosges Loop",
        "slug": "col_de_saverne",
        "region": "Elsass / Pfalz / Vosges",
        "distance_km": 320,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Through Pf\u00e4lzerwald", False),
            ("Johanniskreuz", 49.348, 7.850, "Forest crossroads", False),
            ("Pirmasens", 49.201, 7.605, "Border region", False),
            ("Bitche", 49.052, 7.430, "Vauban citadel (France)", False),
            ("Saverne", 48.742, 7.362, "Rose City \u2013 midpoint", True),
            ("Col de Saverne", 48.736, 7.303, "Historic mountain pass", False),
            ("Bouxwiller", 48.824, 7.484, "Alsatian village", False),
            ("Niederbronn-les-Bains", 48.952, 7.643, "Spa town", False),
            ("Wissembourg", 49.037, 7.945, "Back to Germany", False),
            ("Schweigen-Rechtenbach", 49.049, 8.054, "Wine Gate", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "A grand cross-border loop from the Pf\u00e4lzerwald into the French "
            "Vosges mountains via the Col de Saverne. Combines German forest "
            "roads with French mountain passes and the impressive Citadel of "
            "Bitche."
        ),
        "route_description": (
            "From Speyer, ride through the Pf\u00e4lzerwald to Johanniskreuz, then "
            "continue west past Pirmasens and across into France. Visit the "
            "impressive Citadel of Bitche, a Vauban fortress atop sandstone "
            "cliffs, then ride south through the Vosges forest to Saverne, a "
            "charming town dominated by its massive red sandstone ch\u00e2teau. Cross "
            "the Col de Saverne, then head northeast through Bouxwiller and "
            "Niederbronn-les-Bains\u2014a charming spa town in the northern Vosges. "
            "Re-enter Germany at Wissembourg for the return via Speyer."
        ),
        "midpoint_name": "Saverne",
        "midpoint_description": (
            "Known as the \u201cRose City\u201d for its municipal rose garden, Saverne is "
            "dominated by the enormous Ch\u00e2teau des Rohan, built in red Vosges "
            "sandstone. The town sits at the foot of the Col de Saverne, which "
            "has been a strategic pass since Roman times. Taverne Katz on the "
            "Grand\u2019Rue serves Alsatian-Lorraine classics\u2014Quiche Lorraine, "
            "Fleischnaka, and tarte aux mirabelles."
        ),
        "highlights": [
            "Cross-border loop through two countries",
            "Citadel of Bitche \u2013 Vauban\u2019s masterpiece fortress",
            "Col de Saverne \u2013 historic mountain pass",
            "Combines Pf\u00e4lzerwald and Vosges mountain riding",
        ],
        "road_character": (
            "A diverse tour mixing Pf\u00e4lzerwald forest roads, French "
            "departmental roads through the Vosges, and mountain pass climbing. "
            "The French roads are generally quieter and well-surfaced. The Col "
            "de Saverne is not technically demanding but atmospherically "
            "rewarding. A long, varied day."
        ),
    },
    # ------------------------------------------------------------------
    # NECKAR VALLEY & SWABIA  (Tours 20-23)
    # ------------------------------------------------------------------
    {
        "number": 20,
        "name": "Burg Hornberg & Neckar Loop",
        "slug": "burg_hornberg_neckar",
        "region": "Neckartal",
        "distance_km": 180,
        "difficulty": "Easy to Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Sinsheim", 49.253, 8.879, "Head east", False),
            ("Bad Rappenau", 49.239, 8.993, "Saline tower", False),
            ("Bad Wimpfen", 49.231, 9.165, "Imperial palace \u2013 midpoint", True),
            ("Gundelsheim", 49.285, 9.159, "Deutschordensschloss", False),
            ("Burg Guttenberg", 49.283, 9.142, "Raptor center", False),
            ("Neckarzimmern", 49.319, 9.138, "Burg Hornberg", False),
            ("Ha\u00dfmersheim", 49.300, 9.157, "Neckar valley", False),
            ("Mosbach", 49.353, 9.146, "Half-timbered town", False),
            ("Obrigheim", 49.352, 9.087, "Continue west", False),
            ("Sinsheim", 49.253, 8.879, "Return", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "A relaxed loop along the middle Neckar valley, visiting some of the "
            "finest castles in Baden-W\u00fcrttemberg and the stunning hilltop town "
            "of Bad Wimpfen with its imperial palace ruins."
        ),
        "route_description": (
            "Head east through Sinsheim to Bad Rappenau, then continue to Bad "
            "Wimpfen\u2014spectacularly perched on a ridge above the Neckar, with "
            "the remains of the largest imperial palace north of the Alps. "
            "Follow the Neckar south to Gundelsheim and Burg Guttenberg, home to "
            "a famous birds of prey center. Continue to Neckarzimmern, where Burg "
            "Hornberg\u2014the castle of the legendary knight G\u00f6tz von "
            "Berlichingen\u2014produces excellent wines from its own terraced "
            "vineyard. Loop through Mosbach and return via quieter roads through "
            "Obrigheim to Sinsheim."
        ),
        "midpoint_name": "Bad Wimpfen",
        "midpoint_description": (
            "Perched dramatically on a ridge above the Neckar, Bad Wimpfen\u2019s "
            "skyline of towers and half-timbered houses is unforgettable. The "
            "Kaiserpfalz (imperial palace) ruins include the Blue Tower and Red "
            "Tower. Feyerabend Gasthaus serves classic Swabian "
            "dishes\u2014Sp\u00e4tzle, Maultaschen\u2014in a centuries-old half-timbered setting."
        ),
        "highlights": [
            "Bad Wimpfen \u2013 dramatic hilltop Kaiserpfalz and Altstadt",
            "Burg Hornberg \u2013 G\u00f6tz von Berlichingen\u2019s castle with wine estate",
            "Burg Guttenberg \u2013 live raptor demonstrations",
            "Scenic Neckar valley riding",
        ],
        "road_character": (
            "Gentle, scenic valley riding. The roads follow the Neckar through "
            "open landscape with views of castles on every hilltop. Well-surfaced, "
            "moderate curves, rarely congested. Ideal for a relaxed day or when "
            "riding two-up."
        ),
    },
    {
        "number": 21,
        "name": "Jagsttal & Kochertal",
        "slug": "jagsttal_kochertal",
        "region": "Hohenloher Land",
        "distance_km": 250,
        "difficulty": "Easy to Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Sinsheim", 49.253, 8.879, "Head east", False),
            ("Bad Rappenau", 49.239, 8.993, "Saline", False),
            ("Bad Friedrichshall", 49.231, 9.211, "Salt mining town", False),
            ("Jagsthausen", 49.309, 9.469, "G\u00f6tzenburg", False),
            ("Berlichingen", 49.302, 9.451, "Knight\u2019s village", False),
            ("Kloster Sch\u00f6ntal", 49.328, 9.500, "Baroque abbey", False),
            ("K\u00fcnzelsau", 49.282, 9.685, "Hohenlohe capital \u2013 midpoint", True),
            ("Ingelfingen", 49.300, 9.650, "Wine town", False),
            ("Forchtenberg", 49.290, 9.560, "Sophie Scholl birthplace", False),
            ("\u00d6hringen", 49.201, 9.501, "Hohenlohe residency", False),
            ("Neuenstadt am Kocher", 49.234, 9.329, "Kocher valley", False),
            ("Neckarsulm", 49.192, 9.225, "Deutsches Zweirad-Museum!", False),
            ("Hockenheim", 49.322, 8.548, "End (via A6)", False),
        ],
        "overview": (
            "Explore the peaceful Jagst and Kocher valleys\u2014parallel river "
            "valleys winding through the gentle Hohenloher Land, where time "
            "seems to have stopped in the Baroque era. Discover monasteries, "
            "castles, and the Deutsches Zweirad-Museum (German Motorcycle "
            "Museum) in Neckarsulm."
        ),
        "route_description": (
            "Head east through Sinsheim and Bad Rappenau to Bad Friedrichshall, "
            "then follow the Jagst valley north through Jagsthausen (another "
            "G\u00f6tz von Berlichingen castle) and Berlichingen village. Visit "
            "Kloster Sch\u00f6ntal, a magnificent Baroque abbey in the valley. "
            "Continue to K\u00fcnzelsau, the Hohenlohe capital, then trace the Kocher "
            "valley back south through Ingelfingen, Forchtenberg (birthplace of "
            "Sophie Scholl), and \u00d6hringen. Finish at Neckarsulm, where the "
            "Deutsches Zweirad-Museum\u2014Germany\u2019s motorcycle museum\u2014is an "
            "absolute must-visit for any rider."
        ),
        "midpoint_name": "K\u00fcnzelsau",
        "midpoint_description": (
            "The quiet capital of the Hohenloher Land sits in the Kocher valley, "
            "surrounded by vineyards and orchards. It\u2019s the hometown of astronaut "
            "Alexander Gerst and the W\u00fcrth industrial empire (visit the excellent "
            "W\u00fcrth art museum). Gasthaus Krone serves Hohenloher "
            "K\u00fcche\u2014Hohenloher Maultaschen, Saure Kutteln, and excellent local "
            "wines."
        ),
        "highlights": [
            "Jagst and Kocher valleys \u2013 parallel river valleys with castle views",
            "Kloster Sch\u00f6ntal \u2013 magnificent Baroque abbey",
            "Deutsches Zweirad-Museum (Neckarsulm) \u2013 THE motorcycle museum",
            "Forchtenberg \u2013 birthplace of Sophie Scholl",
            "Peaceful Hohenloher countryside",
        ],
        "road_character": (
            "Gentle, flowing river-valley roads ideal for relaxed riding. The "
            "Jagst and Kocher valleys wind through open farmland with occasional "
            "forest stretches. Long, sweeping curves rather than tight "
            "switchbacks. Very light traffic."
        ),
    },
    {
        "number": 22,
        "name": "Schw\u00e4bisch Hall & Comburg",
        "slug": "schwaebisch_hall_comburg",
        "region": "Hohenloher Land",
        "distance_km": 270,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Sinsheim", 49.253, 8.879, "Head east", False),
            ("Heilbronn", 49.142, 9.220, "Bypass south", False),
            ("Weinsberg", 49.151, 9.286, "Weibertreu castle", False),
            ("L\u00f6wenstein", 49.093, 9.380, "L\u00f6wensteiner Berge", False),
            ("Mainhardt", 49.079, 9.558, "Roman Limes", False),
            ("Schw\u00e4bisch Hall", 49.112, 9.738, "Theatrical Marktplatz \u2013 midpoint", True),
            ("Comburg", 49.101, 9.743, "Monastery fortress", False),
            ("Gaildorf", 48.995, 9.770, "Kocher valley", False),
            ("Murrhardt", 48.978, 9.586, "Swabian Forest", False),
            ("Sulzbach an der Murr", 48.879, 9.474, "Forest edge", False),
            ("Backnang", 48.948, 9.432, "Return west", False),
            ("Heilbronn", 49.142, 9.220, "A6 west", False),
            ("Hockenheim", 49.322, 8.548, "End (via A6)", False),
        ],
        "overview": (
            "A full-day ride to one of southern Germany\u2019s most spectacular "
            "medieval towns\u2014Schw\u00e4bisch Hall, with its theatrical market "
            "square\u2014and the imposing Comburg monastery fortress perched on a "
            "hill above."
        ),
        "route_description": (
            "Head east through Sinsheim and past Heilbronn to Weinsberg, where "
            "the hilltop Weibertreu castle tells the story of loyal wives who "
            "carried their husbands to safety. Climb through the L\u00f6wensteiner "
            "Berge and Mainhardt, where the Roman Limes once marked the border "
            "of the empire, to Schw\u00e4bisch Hall. This magnificent town centers "
            "on a theatrical Marktplatz with a broad staircase rising to St. "
            "Michael\u2019s church. Across the valley, Comburg is a fortified "
            "monastery of extraordinary presence. Return via Gaildorf and "
            "Murrhardt through the Swabian Forest."
        ),
        "midpoint_name": "Schw\u00e4bisch Hall",
        "midpoint_description": (
            "The Marktplatz is one of Germany\u2019s most dramatic\u2014a sloping square "
            "with the massive staircase to St. Michael\u2019s church that doubles as "
            "theater seating in summer. The covered Henkerbr\u00fccke bridge and the "
            "half-timbered houses along the Kocher are stunning. Across the "
            "valley, Comburg monastery is a must-see. Brauereigasthof Zum "
            "L\u00f6wen serves Hallisch dishes with beer brewed on-site."
        ),
        "highlights": [
            "Schw\u00e4bisch Hall \u2013 theatrical Marktplatz and medieval Altstadt",
            "Comburg \u2013 hilltop monastery fortress of extraordinary presence",
            "Roman Limes at Mainhardt",
            "Weibertreu castle at Weinsberg \u2013 a great story",
            "Diverse landscape from vineyards to forest",
        ],
        "road_character": (
            "Mixed riding. The L\u00f6wensteiner Berge offer enjoyable hilly curves. "
            "The approach to Schw\u00e4bisch Hall winds through forest and farmland. "
            "The return through the Swabian Forest via Murrhardt features flowing "
            "curves through mixed terrain. A long day requiring good planning."
        ),
    },
    {
        "number": 23,
        "name": "Hohenloher Land",
        "slug": "hohenloher_land",
        "region": "Hohenloher Land",
        "distance_km": 360,
        "difficulty": "Easy to Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Sinsheim", 49.253, 8.879, "Head east", False),
            ("Bad Rappenau", 49.239, 8.993, "Saline", False),
            ("Neckarsulm", 49.192, 9.225, "Motorcycle Museum", False),
            ("\u00d6hringen", 49.201, 9.501, "Hohenlohe residency", False),
            ("Neuenstein", 49.201, 9.578, "Castle", False),
            ("Waldenburg", 49.189, 9.632, "Balcony of Hohenlohe \u2013 midpoint", True),
            ("Langenburg", 49.254, 9.858, "Castle, car museum", False),
            ("Kirchberg an der Jagst", 49.201, 9.982, "Hilltop town", False),
            ("Gerabronn", 49.253, 9.919, "Rolling farmland", False),
            ("Crailsheim", 49.134, 10.072, "Eastern edge", False),
            ("Schw\u00e4bisch Hall", 49.112, 9.738, "Bypass south", False),
            ("Heilbronn", 49.142, 9.220, "Return west", False),
            ("Hockenheim", 49.322, 8.548, "End (via A6)", False),
        ],
        "overview": (
            "Discover the gentle hills and castle-studded villages of the "
            "Hohenloher Land\u2014\u201cthe Balcony of Franconia\u201d\u2014with its aristocratic "
            "residences, car museum at Langenburg, and sweeping views from "
            "Waldenburg\u2019s ridge-top setting."
        ),
        "route_description": (
            "Head east through Sinsheim and Neckarsulm to \u00d6hringen, the former "
            "Hohenlohe residence. Continue through Neuenstein (impressive moated "
            "castle) to Waldenburg, spectacularly perched on a narrow ridge "
            "150 m above the Hohenlohe plain\u2014justifying its \u201cBalcony of "
            "Hohenlohe\u201d nickname. Head north to Langenburg, where the hilltop "
            "castle houses an excellent automobile museum. Loop through Kirchberg "
            "and Gerabronn, then south through Crailsheim and past Schw\u00e4bisch "
            "Hall back to the A6."
        ),
        "midpoint_name": "Waldenburg",
        "midpoint_description": (
            "Perched on a narrow ridge with sheer drops on both sides, "
            "Waldenburg offers panoramic views over the entire Hohenlohe "
            "plain. The tiny town has a castle, churches, and the "
            "Panorama-Restaurant with its aptly named terrace. On clear days, "
            "you can see all the way to the Schw\u00e4bische Alb."
        ),
        "highlights": [
            "Waldenburg \u2013 ridge-top town with 360\u00b0 panoramic views",
            "Langenburg Castle \u2013 with automobile museum",
            "\u00d6hringen \u2013 elegant Hohenlohe residency town",
            "Rolling Hohenlohe countryside with minimal traffic",
        ],
        "road_character": (
            "Gentle, sweeping roads through rolling farmland. The Hohenloher "
            "Land is flat-to-hilly, so curves are moderate but continuous. Very "
            "light traffic once east of \u00d6hringen. Relaxed riding through "
            "beautiful, open countryside."
        ),
    },
    # ------------------------------------------------------------------
    # KRAICHGAU & RHINE  (Tours 24-27)
    # ------------------------------------------------------------------
    {
        "number": 24,
        "name": "Zaberg\u00e4u & Heuchelberg",
        "slug": "zabergaeu_heuchelberg",
        "region": "Kraichgau / Zaberg\u00e4u",
        "distance_km": 175,
        "difficulty": "Easy",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Wiesloch", 49.294, 8.698, "Head southeast", False),
            ("Eppingen", 49.136, 8.912, "Fachwerkstadt", False),
            ("G\u00fcglingen", 49.064, 9.001, "Wine country", False),
            ("Brackenheim", 49.077, 9.067, "Wine capital \u2013 midpoint", True),
            ("Zaberfeld", 49.056, 8.928, "Zaberg\u00e4u", False),
            ("Cleebronn", 49.043, 9.031, "Tripsdrill", False),
            ("B\u00f6nnigheim", 49.040, 9.093, "Wine town", False),
            ("Vaihingen an der Enz", 48.933, 8.962, "Enz valley", False),
            ("Maulbronn", 49.002, 8.812, "UNESCO monastery", False),
            ("Bretten", 49.036, 8.707, "Melanchthon", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "A shorter, relaxed tour through the gentle wine hills of the "
            "Zaberg\u00e4u and Heuchelberg\u2014discover the UNESCO-listed Maulbronn "
            "Monastery and charming wine villages without breaking a sweat."
        ),
        "route_description": (
            "Head southeast through Wiesloch to Eppingen, a well-preserved "
            "Fachwerkstadt. Continue south through the Zaberg\u00e4u wine country to "
            "G\u00fcglingen and Brackenheim\u2014birthplace of Theodor Heuss, Germany\u2019s "
            "first Federal President. The rolling Heuchelberg ridge offers "
            "panoramic views over vineyards. Loop through Zaberfeld, Cleebronn, "
            "and B\u00f6nnigheim, then turn west to the magnificent Kloster "
            "Maulbronn\u2014the best-preserved medieval monastery north of the Alps, "
            "a UNESCO World Heritage Site. Return via Bretten."
        ),
        "midpoint_name": "Brackenheim",
        "midpoint_description": (
            "The largest wine-producing community in W\u00fcrttemberg, Brackenheim "
            "is surrounded by vineyards on every side. Visit the "
            "Theodor-Heuss-Museum in his birth house. Weinstube R\u00f6ssle serves "
            "excellent W\u00fcrttemberg wines with Maultaschen, Ofenschlupfer, and "
            "other Swabian classics."
        ),
        "highlights": [
            "Kloster Maulbronn \u2013 UNESCO World Heritage monastery",
            "Brackenheim \u2013 W\u00fcrttemberg\u2019s wine capital",
            "Eppingen \u2013 outstanding half-timbered architecture",
            "Gentle Zaberg\u00e4u wine hills \u2013 perfect for a half-day ride",
        ],
        "road_character": (
            "Very easy riding through gentle, vineyard-covered hills. The roads "
            "wind between villages on well-surfaced minor roads with sweeping "
            "curves. Minimal traffic, no steep climbs, no technical challenges. "
            "Pure relaxation."
        ),
    },
    {
        "number": 25,
        "name": "Kraichgau H\u00fcgelland",
        "slug": "kraichgau_huegelland",
        "region": "Kraichgau",
        "distance_km": 165,
        "difficulty": "Easy",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Walldorf", 49.306, 8.643, "SAP town", False),
            ("Wiesloch", 49.294, 8.698, "Into the hills", False),
            ("Meckesheim", 49.334, 8.819, "Kraichgau", False),
            ("Zuzenhausen", 49.351, 8.824, "Rolling hills", False),
            ("Burg Steinsberg", 49.239, 8.825, "Compass of the Kraichgau \u2013 midpoint", True),
            ("Sinsheim", 49.253, 8.879, "Technik Museum", False),
            ("Ittlingen", 49.198, 8.933, "Wine country", False),
            ("Eppingen", 49.136, 8.912, "Fachwerkstadt", False),
            ("Sulzfeld", 49.106, 8.860, "Wine village with town wall", False),
            ("Bretten", 49.036, 8.707, "Melanchthon house", False),
            ("Bruchsal", 49.124, 8.598, "Baroque palace", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Explore the Kraichgau\u2014the rolling hill country between the Rhine "
            "and the Odenwald that\u2019s often called the \u201cland of a thousand "
            "hills.\u201d Gentle curves through orchards and vineyards with the Burg "
            "Steinsberg as the panoramic highlight."
        ),
        "route_description": (
            "Head east through Walldorf and Wiesloch into the heart of the "
            "Kraichgau. Ride through Meckesheim and Zuzenhausen to Burg "
            "Steinsberg, known as the \u201cCompass of the Kraichgau\u201d for its "
            "prominence\u2014a volcanic hill topped by an octagonal tower with views "
            "in every direction. Continue to Sinsheim (consider a stop at the "
            "Technik Museum with its Concorde and Soviet space shuttle). Loop "
            "south through Ittlingen and Eppingen, then west through Sulzfeld "
            "and Bretten to Bruchsal and home."
        ),
        "midpoint_name": "Burg Steinsberg",
        "midpoint_description": (
            "The \u201cCompass of the Kraichgau\u201d sits atop a volcanic hill that "
            "rises prominently from the surrounding landscape. The octagonal "
            "tower offers 360\u00b0 views over the gently rolling Kraichgau. "
            "Burgsch\u00e4nke Steinsberg serves Pf\u00e4lzer-Badisch cuisine on a "
            "terrace with views to the Odenwald and Pf\u00e4lzerwald."
        ),
        "highlights": [
            "Burg Steinsberg \u2013 panoramic \u201cCompass of the Kraichgau\u201d",
            "Sinsheim Technik Museum \u2013 Concorde, Tupolev Tu-144, Buran",
            "Rolling Kraichgau landscape \u2013 \u201cland of a thousand hills\u201d",
            "Closest tour to home \u2013 perfect for a spontaneous afternoon ride",
        ],
        "road_character": (
            "Very gentle riding through softly rolling hills. The Kraichgau is "
            "characterized by long, sweeping curves through open farmland, "
            "orchards, and vineyards. Well-surfaced minor roads with minimal "
            "traffic."
        ),
    },
    {
        "number": 26,
        "name": "Kaiserstuhl \u2013 Volcanic Hills",
        "slug": "kaiserstuhl_volcanic",
        "region": "Oberrhein / Kaiserstuhl",
        "distance_km": 400,
        "difficulty": "Easy to Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Karlsruhe", 49.006, 8.404, "A5 south", False),
            ("Offenburg", 48.473, 7.954, "Ortenau", False),
            ("Ettenheim", 48.257, 7.813, "Baroque town", False),
            ("Endingen am Kaiserstuhl", 48.142, 7.700, "Wine town", False),
            ("Vogtsburg im Kaiserstuhl", 48.092, 7.655, "Wine village \u2013 midpoint", True),
            ("Ihringen", 48.042, 7.651, "Warmest place in Germany", False),
            ("Breisach am Rhein", 48.028, 7.583, "Rhine fortress", False),
            ("Burkheim", 48.085, 7.619, "Fortified wine village", False),
            ("Sasbach am Kaiserstuhl", 48.136, 7.613, "Northern Kaiserstuhl", False),
            ("Emmendingen", 48.121, 7.849, "Markgr\u00e4flerland", False),
            ("Lahr", 48.343, 7.871, "Return to A5", False),
            ("Baden-Baden", 48.761, 8.241, "Spa city", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Ride to the Kaiserstuhl\u2014a volcanic hill rising from the Rhine "
            "plain like a Mediterranean island, with terraced vineyards, exotic "
            "vegetation, and the warmest climate in Germany. Wine and food here "
            "are exceptional."
        ),
        "route_description": (
            "Take the A5 south via Karlsruhe and Offenburg to Ettenheim, then "
            "head west to the Kaiserstuhl. This volcanic massif rises unexpectedly "
            "from the flat Rhine plain, creating a unique microclimate where "
            "orchids, lizards, and even praying mantises thrive. Explore the "
            "terraced vineyards via the Kaiserstuhl panoramic road through "
            "Endingen and Vogtsburg. Visit Ihringen, officially the warmest "
            "place in Germany. Ride down to Breisach am Rhein, a fortress town "
            "on the Rhine with views to France, then loop back through the "
            "medieval fortified wine village of Burkheim and Sasbach. Return "
            "north via Emmendingen, Lahr, and Baden-Baden."
        ),
        "midpoint_name": "Vogtsburg im Kaiserstuhl",
        "midpoint_description": (
            "The central wine community of the Kaiserstuhl, surrounded by "
            "volcanic terraces covered in Sp\u00e4tburgunder (Pinot Noir) and "
            "Grauburgunder (Pinot Gris) vines. Schwarzer Adler in "
            "Vogtsburg-Oberbergen is one of the top wine restaurants in "
            "Baden\u2014Michelin-recommended, with an extraordinary wine list "
            "and refined regional cuisine. Book ahead."
        ),
        "highlights": [
            "Kaiserstuhl \u2013 volcanic hills with Mediterranean microclimate",
            "Terraced vineyards unlike anywhere else in Germany",
            "Ihringen \u2013 warmest place in Germany",
            "Breisach \u2013 Rhine fortress with views to Alsace",
            "Exceptional wines \u2013 Sp\u00e4tburgunder at its German best",
        ],
        "road_character": (
            "The Kaiserstuhl panoramic road is narrow and winding, looping "
            "around the volcanic slopes between terraced vineyards. The curves "
            "are moderate but the views are distracting. The approach via the "
            "A5 is fast but necessary. Once on the Kaiserstuhl, everything "
            "slows down."
        ),
    },
    {
        "number": 27,
        "name": "Enztal to Besigheim",
        "slug": "enztal_besigheim",
        "region": "Enztal / W\u00fcrttemberg",
        "distance_km": 220,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Bruchsal", 49.124, 8.598, "Head south", False),
            ("Bretten", 49.036, 8.707, "Melanchthon", False),
            ("Maulbronn", 49.002, 8.812, "UNESCO monastery", False),
            ("M\u00fchlacker", 48.948, 8.839, "Enz valley", False),
            ("Vaihingen an der Enz", 48.933, 8.962, "River town", False),
            ("Bietigheim-Bissingen", 48.962, 9.127, "Enz confluence", False),
            ("Besigheim", 48.999, 9.142, "Wine terrace town \u2013 midpoint", True),
            ("Hessigheim", 49.012, 9.185, "Felseng\u00e4rten cliffs", False),
            ("Mundelsheim", 49.010, 9.208, "K\u00e4sberg vineyard", False),
            ("Lauffen am Neckar", 49.074, 9.145, "H\u00f6lderlin birthplace", False),
            ("Brackenheim", 49.077, 9.067, "Wine capital", False),
            ("Eppingen", 49.136, 8.912, "Fachwerkstadt", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Follow the Enz river from Maulbronn\u2019s UNESCO monastery to the "
            "stunning wine terraces of Besigheim and Hessigheim, where vineyards "
            "cling to dramatic limestone cliffs above the river."
        ),
        "route_description": (
            "Head south through Bruchsal and Bretten to Maulbronn\u2014pause at "
            "this exceptional UNESCO monastery. Follow the Enz downstream "
            "through M\u00fchlacker and Vaihingen to its confluence with the Neckar "
            "at Bietigheim-Bissingen. Continue to Besigheim, where a hilltop "
            "old town is hemmed between the Enz and Neckar. Just downstream, "
            "the Felseng\u00e4rten at Hessigheim feature vineyards on sheer "
            "limestone cliffs\u2014one of the most spectacular vineyard landscapes "
            "in Germany. Continue through Mundelsheim and Lauffen (H\u00f6lderlin\u2019s "
            "birthplace) to Brackenheim and return via Eppingen."
        ),
        "midpoint_name": "Besigheim",
        "midpoint_description": (
            "Wedged between two rivers on a hilltop, Besigheim is regularly "
            "voted among Germany\u2019s most beautiful wine towns. The Altstadt is "
            "a compact maze of half-timbered houses crowned by two medieval "
            "towers. Weinstube Friedrich serves excellent local Trollinger and "
            "Lemberger wines with Swabian small plates\u2014Maultaschen, "
            "Zwiebelrostbraten."
        ),
        "highlights": [
            "Besigheim \u2013 hilltop wine town between two rivers",
            "Hessigheim Felseng\u00e4rten \u2013 vineyards on sheer cliffs",
            "Maulbronn \u2013 UNESCO World Heritage monastery",
            "Lauffen \u2013 birthplace of Friedrich H\u00f6lderlin",
            "W\u00fcrttemberg wine terraces at their finest",
        ],
        "road_character": (
            "Flowing valley roads following the Enz and Neckar rivers. Moderate "
            "curves through vine-covered hills. The roads through the wine "
            "terraces between Besigheim and Mundelsheim are particularly scenic "
            "with some narrow sections. Generally relaxed riding."
        ),
    },
    # ------------------------------------------------------------------
    # SPECIAL / COMBINATION  (Tours 28-30)
    # ------------------------------------------------------------------
    {
        "number": 28,
        "name": "Pf\u00e4lzerwald Grand Tour",
        "slug": "pfaelzerwald_grand_tour",
        "region": "Pf\u00e4lzerwald",
        "distance_km": 290,
        "difficulty": "Challenging",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Neustadt a.d. Weinstra\u00dfe", 49.355, 8.142, "Wine gateway", False),
            ("Bad D\u00fcrkheim", 49.462, 8.172, "World\u2019s largest wine barrel", False),
            ("Enkenbach-Alsenborn", 49.486, 7.907, "Northern Pf\u00e4lzerwald", False),
            ("Otterberg", 49.504, 7.770, "Cistercian abbey", False),
            ("Kaiserslautern", 49.445, 7.769, "Brief pass", False),
            ("Johanniskreuz", 49.348, 7.850, "Forest crossroads", False),
            ("Elmstein", 49.360, 7.940, "Elmstein Valley", False),
            ("Heltersberg", 49.297, 7.676, "Western forest", False),
            ("Pirmasens", 49.201, 7.605, "Shoe city", False),
            ("Dahn", 49.151, 7.790, "Felsenland \u2013 midpoint", True),
            ("Annweiler am Trifels", 49.204, 7.969, "Trifels Castle", False),
            ("Landau in der Pfalz", 49.199, 8.117, "Wine route", False),
            ("Edenkoben", 49.284, 8.120, "Weinstra\u00dfe", False),
            ("Speyer", 49.317, 8.431, "Cross Rhine", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "The ultimate Pf\u00e4lzerwald experience\u2014a grand loop covering the "
            "entire forest from north to south. Bad D\u00fcrkheim\u2019s famous "
            "Wurstmarkt grounds, the legendary Johanniskreuz, the wild Dahner "
            "Felsenland, and the wine route. A full day of forest riding."
        ),
        "route_description": (
            "Cross the Rhine at Speyer and head north to Bad D\u00fcrkheim\u2014home "
            "of the D\u00fcrkheimer Wurstmarkt, the world\u2019s largest wine festival. "
            "Continue north through Enkenbach to Otterberg, with its magnificent "
            "Cistercian abbey. Swing past Kaiserslautern and deep into the "
            "forest to Johanniskreuz. Ride south through Elmstein and the "
            "western Pf\u00e4lzerwald to Heltersberg and Pirmasens, then into the "
            "Dahner Felsenland. After exploring Dahn\u2019s rock landscape, head "
            "east through Annweiler and Landau, following the Weinstra\u00dfe north "
            "through Edenkoben back to Speyer."
        ),
        "midpoint_name": "Dahn",
        "midpoint_description": (
            "After riding through the heart of the forest, Dahn provides the "
            "perfect break surrounded by sandstone towers. Burgsch\u00e4nke Altdahn "
            "at the foot of the triple-castle ruin serves game dishes, "
            "Saumagen, and Pf\u00e4lzer wines. The castle ruin itself is worth "
            "the short hike\u2014three castles on three rock pillars."
        ),
        "highlights": [
            "Complete Pf\u00e4lzerwald circuit \u2013 forest from end to end",
            "Bad D\u00fcrkheim \u2013 world\u2019s largest wine barrel",
            "Otterberg \u2013 hidden Cistercian abbey",
            "Johanniskreuz AND Dahner Felsenland in one ride",
            "The full Deutsche Weinstra\u00dfe on the return leg",
        ],
        "road_character": (
            "This is the most demanding Pf\u00e4lzerwald tour\u2014290 km of mostly "
            "forest roads requiring focus and stamina. The roads are "
            "well-surfaced but endlessly winding. The northern Pf\u00e4lzerwald has "
            "faster, more flowing curves; the south around Dahn is tighter and "
            "more technical. Plan fuel stops carefully\u2014gas stations are sparse "
            "in the forest."
        ),
    },
    {
        "number": 29,
        "name": "Bergstra\u00dfe Express \u2013 North to Otzberg",
        "slug": "bergstrasse_otzberg",
        "region": "Bergstra\u00dfe / Odenwald",
        "distance_km": 280,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("Weinheim", 49.550, 8.667, "Bergstra\u00dfe start", False),
            ("Bensheim", 49.681, 8.618, "Bergstra\u00dfe", False),
            ("Zwingenberg", 49.726, 8.613, "Oldest Bergstra\u00dfe town", False),
            ("Reinheim", 49.830, 8.834, "Eastern turn", False),
            ("Veste Otzberg", 49.832, 8.912, "White tower", False),
            ("Burg Breuberg", 49.828, 9.033, "Medieval castle", False),
            ("H\u00f6chst im Odenwald", 49.800, 8.983, "Odenwald descent", False),
            ("Bad K\u00f6nig", 49.744, 9.017, "Spa town", False),
            ("Michelstadt", 49.676, 9.004, "Fairy-tale Rathaus \u2013 midpoint", True),
            ("Erbach", 49.659, 8.994, "Ivory museum", False),
            ("Lindenfels", 49.568, 8.780, "Pearl of the Odenwald", False),
            ("Heppenheim", 49.642, 8.650, "Wine town", False),
            ("Hockenheim", 49.322, 8.548, "End (via A5)", False),
        ],
        "overview": (
            "A long northern arc combining the Bergstra\u00dfe, two impressive "
            "castles\u2014Veste Otzberg and Burg Breuberg\u2014and the scenic "
            "Odenwald heartland. An ambitious day exploring the northern "
            "reaches of the riding area."
        ),
        "route_description": (
            "Ride north along the Bergstra\u00dfe through Weinheim, Bensheim, and "
            "Zwingenberg, then turn east to Reinheim. Continue to the striking "
            "Veste Otzberg (with its iconic white tower visible for miles) and "
            "Burg Breuberg, one of the best-preserved medieval castles in "
            "southern Hesse. Descend into the Odenwald through H\u00f6chst and Bad "
            "K\u00f6nig to Michelstadt for lunch, then ride south through Erbach "
            "and Lindenfels to Heppenheim, a vibrant wine town at the northern "
            "end of the Baden Bergstra\u00dfe. Return via the A5."
        ),
        "midpoint_name": "Michelstadt",
        "midpoint_description": (
            "The medieval Marktplatz is dominated by the spectacular Rathaus "
            "from 1484\u2014one of Germany\u2019s most photographed buildings. For this "
            "northern tour, try Restaurant Zum Gr\u00fcnen Baum for seasonal "
            "Odenwald dishes\u2014asparagus in spring, wild mushrooms in autumn, "
            "game in winter."
        ),
        "highlights": [
            "Veste Otzberg \u2013 white tower visible across the Odenwald",
            "Burg Breuberg \u2013 one of Hesse\u2019s best-preserved castles",
            "The full Bergstra\u00dfe from Hockenheim to Zwingenberg",
            "Michelstadt\u2019s fairy-tale Rathaus (second chance if you missed Tour 8)",
        ],
        "road_character": (
            "The Bergstra\u00dfe heading north is smooth and flowing along the "
            "Odenwald edge. The eastern section through Otzberg and Breuberg "
            "is rolling farmland with gentle curves. The Odenwald section from "
            "Bad K\u00f6nig south through Lindenfels is the riding highlight\u2014winding "
            "forest roads with good surfaces."
        ),
    },
    {
        "number": 30,
        "name": "Three Black Forest Valleys",
        "slug": "three_bf_valleys",
        "region": "Schwarzwald",
        "distance_km": 320,
        "difficulty": "Moderate",
        "waypoints": [
            ("Hockenheim", 49.322, 8.548, "Start/End", False),
            ("B\u00fchl", 48.696, 8.136, "Enter Black Forest (via A5)", False),
            ("B\u00fchlertal", 48.669, 8.168, "Valley climb", False),
            ("Sand", 48.654, 8.226, "B500 junction", False),
            ("Unterstmatt", 48.620, 8.210, "Leave B500 west", False),
            ("Sasbachwalden", 48.619, 8.120, "Flower village \u2013 midpoint", True),
            ("Achern", 48.628, 8.075, "Ortenau", False),
            ("Oberkirch", 48.528, 8.078, "Renchtal", False),
            ("Oppenau", 48.474, 8.161, "Deep Renchtal", False),
            ("Bad Peterstal-Griesbach", 48.427, 8.202, "Spa", False),
            ("Freudenstadt", 48.462, 8.411, "Marktplatz", False),
            ("Calw", 48.714, 8.741, "Hermann Hesse\u2019s birthplace", False),
            ("Pforzheim", 48.891, 8.704, "Gold City", False),
            ("Hockenheim", 49.322, 8.548, "End", False),
        ],
        "overview": (
            "Three distinct Black Forest valleys in one tour\u2014climb through "
            "B\u00fchlertal to the B500, descend into the flower-bedecked village "
            "of Sasbachwalden, then ride the Renchtal south before looping "
            "back through Freudenstadt."
        ),
        "route_description": (
            "Take the A5 to B\u00fchl and climb through B\u00fchlertal\u2014a steep, "
            "switchback-rich ascent to the Black Forest ridge. Join the B500 "
            "briefly at Sand, riding south to Unterstmatt, then descend "
            "westward to Sasbachwalden, one of the most beautiful Black Forest "
            "villages. Famous for its flower displays and half-timbered houses "
            "against a mountain backdrop. After lunch, drop to Achern and head "
            "south into the Renchtal at Oberkirch. Follow the Rench river "
            "through Oppenau and Bad Peterstal-Griesbach\u2014classic Black Forest "
            "valley riding. Climb east to Freudenstadt, then return through "
            "the scenic Nagoldtal via Calw and Pforzheim."
        ),
        "midpoint_name": "Sasbachwalden",
        "midpoint_description": (
            "A gem of a Black Forest village draped in flowers, Sasbachwalden "
            "has won countless beautification prizes. The half-timbered houses, "
            "fountain-lined streets, and backdrop of forested mountains make it "
            "postcard-perfect. Weingut und Gasthaus Alde Gott serves Black "
            "Forest cuisine paired with their own wines\u2014try the Sch\u00e4ufele "
            "with Br\u00e4gele (fried potatoes)."
        ),
        "highlights": [
            "B\u00fchlertal switchbacks \u2013 steep, technical Black Forest climbing",
            "A taste of the B500 Schwarzwaldhochstra\u00dfe",
            "Sasbachwalden \u2013 one of the Black Forest\u2019s prettiest villages",
            "Renchtal \u2013 classic Black Forest valley riding",
            "Three distinct valley characters in one tour",
        ],
        "road_character": (
            "Varied and engaging. The B\u00fchlertal climb is steep and technical "
            "with tight switchbacks\u2014the most challenging start of any tour. "
            "The B500 section is sweeping and fast. The descent to Sasbachwalden "
            "is moderate. The Renchtal is flowing valley riding. A good "
            "all-round tour that tests different skills."
        ),
    },
]


# ---------------------------------------------------------------------------
# GPX generation
# ---------------------------------------------------------------------------
GPX_NS = "http://www.topografix.com/GPX/1/1"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMA_LOC = (
    "http://www.topografix.com/GPX/1/1 "
    "http://www.topografix.com/GPX/1/1/gpx.xsd"
)


def _gpx_pretty(root):
    """Return pretty-printed XML bytes for a GPX ElementTree root."""
    rough = ET.tostring(root, encoding="unicode")
    dom = minidom.parseString(rough)
    return dom.toprettyxml(indent="  ", encoding="UTF-8")


def generate_gpx(tour, outdir):
    """Write a GPX file for *tour* into *outdir*."""
    gpx = ET.Element("gpx")
    gpx.set("xmlns", GPX_NS)
    gpx.set("xmlns:xsi", XSI_NS)
    gpx.set("xsi:schemaLocation", SCHEMA_LOC)
    gpx.set("version", "1.1")
    gpx.set("creator", "Hockenheim Motorcycle Tour Planner")

    meta = ET.SubElement(gpx, "metadata")
    ET.SubElement(meta, "name").text = (
        f"Tour {tour['number']:02d}: {tour['name']}"
    )
    ET.SubElement(meta, "desc").text = tour["overview"]
    author = ET.SubElement(meta, "author")
    ET.SubElement(author, "name").text = "Hockenheim Motorcycle Tours"

    # Waypoints (POIs) -- start, midpoint, notable stops
    waypoints = tour["waypoints"]
    for i, (name, lat, lon, desc, is_mid) in enumerate(waypoints):
        wpt = ET.SubElement(gpx, "wpt")
        wpt.set("lat", f"{lat:.6f}")
        wpt.set("lon", f"{lon:.6f}")
        ET.SubElement(wpt, "name").text = name
        if desc:
            ET.SubElement(wpt, "desc").text = desc
        if is_mid:
            ET.SubElement(wpt, "sym").text = "Restaurant"
            ET.SubElement(wpt, "type").text = "Midpoint"
        elif name == HOME_NAME:
            ET.SubElement(wpt, "sym").text = "Flag, Blue"
            ET.SubElement(wpt, "type").text = "Start" if i == 0 else "End"
        else:
            ET.SubElement(wpt, "type").text = "Via"

    # Route
    rte = ET.SubElement(gpx, "rte")
    ET.SubElement(rte, "name").text = (
        f"Tour {tour['number']:02d}: {tour['name']}"
    )
    ET.SubElement(rte, "desc").text = (
        f"{tour['region']} | ~{tour['distance_km']} km | "
        f"{tour['difficulty']}"
    )
    for name, lat, lon, desc, _ in tour["waypoints"]:
        rtept = ET.SubElement(rte, "rtept")
        rtept.set("lat", f"{lat:.6f}")
        rtept.set("lon", f"{lon:.6f}")
        ET.SubElement(rtept, "name").text = name

    fname = f"tour_{tour['number']:02d}_{tour['slug']}.gpx"
    path = os.path.join(outdir, fname)
    with open(path, "wb") as f:
        f.write(_gpx_pretty(gpx))
    return fname


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------
def _register_fonts():
    fonts = {
        "NotoSans": "NotoSans-Regular.ttf",
        "NotoSans-Bold": "NotoSans-Bold.ttf",
        "NotoSans-Italic": "NotoSans-Italic.ttf",
        "NotoSans-BoldItalic": "NotoSans-BoldItalic.ttf",
        "NotoSerif": "NotoSerif-Regular.ttf",
        "NotoSerif-Bold": "NotoSerif-Bold.ttf",
    }
    for name, filename in fonts.items():
        path = os.path.join(FONT_DIR, filename)
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))

    # Register font families for bold/italic markup in Paragraph
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily(
        "NotoSans",
        normal="NotoSans",
        bold="NotoSans-Bold",
        italic="NotoSans-Italic",
        boldItalic="NotoSans-BoldItalic",
    )


def _make_styles():
    return {
        "title": ParagraphStyle(
            "Title", fontName="NotoSerif-Bold", fontSize=26,
            alignment=TA_CENTER, textColor=GREEN, leading=32,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", fontName="NotoSans", fontSize=12,
            alignment=TA_CENTER, textColor=MID_GREY, leading=16,
        ),
        "heading1": ParagraphStyle(
            "Heading1", fontName="NotoSerif-Bold", fontSize=16,
            textColor=GREEN, spaceBefore=6, spaceAfter=4, leading=20,
        ),
        "heading2": ParagraphStyle(
            "Heading2", fontName="NotoSans-Bold", fontSize=11,
            textColor=ACCENT, spaceBefore=10, spaceAfter=3, leading=14,
        ),
        "body": ParagraphStyle(
            "Body", fontName="NotoSans", fontSize=9.5,
            alignment=TA_JUSTIFY, leading=13.5, textColor=DARK,
        ),
        "body_bold": ParagraphStyle(
            "BodyBold", fontName="NotoSans-Bold", fontSize=9.5,
            alignment=TA_LEFT, leading=13.5, textColor=DARK,
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontName="NotoSans", fontSize=9.5,
            leftIndent=16, bulletIndent=4, leading=13, textColor=DARK,
        ),
        "meta": ParagraphStyle(
            "Meta", fontName="NotoSans", fontSize=9,
            textColor=MID_GREY, leading=12,
        ),
        "toc_region": ParagraphStyle(
            "TOCRegion", fontName="NotoSans-Bold", fontSize=11,
            textColor=GREEN, spaceBefore=10, spaceAfter=2,
        ),
        "toc_entry": ParagraphStyle(
            "TOCEntry", fontName="NotoSans", fontSize=9.5,
            textColor=DARK, leftIndent=10, leading=14,
        ),
        "gpx_ref": ParagraphStyle(
            "GpxRef", fontName="NotoSans-Italic", fontSize=8.5,
            textColor=MID_GREY, spaceBefore=6,
        ),
    }


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("NotoSans", 8)
    canvas.setFillColor(MID_GREY)
    canvas.drawCentredString(
        A4[0] / 2, 1.2 * cm,
        f"Motorcycle Day Tours from Hockenheim  \u2022  Page {doc.page}",
    )
    canvas.restoreState()


def generate_pdf(tours, outpath):
    _register_fonts()
    S = _make_styles()

    doc = SimpleDocTemplate(
        outpath, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    story = []

    # --- Title page ---
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph(
        "Motorcycle Day Tours<br/>from Hockenheim", S["title"],
    ))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(
        "30 Curated Routes Through Southwest Germany", S["subtitle"],
    ))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f"Start &amp; End: {HOME_ADDRESS}", S["subtitle"],
    ))
    story.append(Spacer(1, 2 * cm))
    intro = (
        "This guide presents 30 motorcycle day tours ranging from 150 to "
        "300 km, all starting and ending at your front door in Hockenheim. "
        "The routes are designed to chase curves and avoid cities, covering "
        "the Pf\u00e4lzerwald, Odenwald, Black Forest, Alsace, Neckar Valley, "
        "Kraichgau, and Hohenlohe regions. Each tour includes a recommended "
        "midpoint stop with food and sights. A matching GPX file is "
        "provided for every tour."
    )
    story.append(Paragraph(intro, S["body"]))
    story.append(PageBreak())

    # --- Table of Contents ---
    story.append(Paragraph("Contents", S["title"]))
    story.append(Spacer(1, 0.5 * cm))

    current_region = None
    for t in tours:
        region = t["region"].split("/")[0].strip()
        if region != current_region:
            current_region = region
            story.append(Paragraph(region, S["toc_region"]))
        entry = (
            f"<b>Tour {t['number']:02d}</b> &nbsp; {t['name']} "
            f"<font color='#888888'>({t['region']}, "
            f"~{t['distance_km']} km, {t['difficulty']})</font>"
        )
        story.append(Paragraph(entry, S["toc_entry"]))

    story.append(PageBreak())

    # --- Individual tours ---
    for t in tours:
        elems = []
        # Horizontal rule
        elems.append(HRFlowable(
            width="100%", thickness=1.5, color=GREEN,
            spaceBefore=0, spaceAfter=6,
        ))
        # Tour number + region line
        elems.append(Paragraph(
            f"Tour {t['number']:02d} &nbsp;&nbsp; "
            f"<font color='#888888'>{t['region']}</font>",
            S["meta"],
        ))
        # Tour name
        elems.append(Paragraph(t["name"], S["heading1"]))
        # Metadata
        elems.append(Paragraph(
            f"Distance: ~{t['distance_km']} km &nbsp; | &nbsp; "
            f"Difficulty: {t['difficulty']}",
            S["meta"],
        ))
        elems.append(Spacer(1, 4 * mm))

        # Overview
        elems.append(Paragraph(t["overview"], S["body"]))
        elems.append(Spacer(1, 3 * mm))

        # Route
        elems.append(Paragraph("Route", S["heading2"]))
        elems.append(Paragraph(t["route_description"], S["body"]))

        # Midpoint
        elems.append(Paragraph(
            f"Midpoint Stop: {t['midpoint_name']}", S["heading2"],
        ))
        elems.append(Paragraph(t["midpoint_description"], S["body"]))

        # Highlights
        elems.append(Paragraph("Highlights", S["heading2"]))
        for h in t["highlights"]:
            elems.append(Paragraph(
                f"\u2022 &nbsp; {h}", S["bullet"],
            ))

        # Road character
        elems.append(Paragraph("Road Character", S["heading2"]))
        elems.append(Paragraph(t["road_character"], S["body"]))

        # GPX reference
        gpx_name = f"tour_{t['number']:02d}_{t['slug']}.gpx"
        elems.append(Paragraph(
            f"GPX file: {gpx_name}", S["gpx_ref"],
        ))

        story.extend(elems)
        story.append(PageBreak())

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(GPX_DIR, exist_ok=True)

    print(f"Generating {len(TOURS)} GPX files ...")
    for t in TOURS:
        fname = generate_gpx(t, GPX_DIR)
        print(f"  {fname}")

    print(f"\nGenerating PDF: {PDF_FILE} ...")
    generate_pdf(TOURS, PDF_FILE)
    print("Done.")


if __name__ == "__main__":
    main()
