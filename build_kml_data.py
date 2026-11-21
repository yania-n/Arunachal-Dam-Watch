#!/usr/bin/env python3
"""Catalogue the Parivesh EC-proposal KML files and link them to DHPD / GEM projects.

Run from the repo root:  python build_kml_data.py   (standard library only)

Inputs (never modified):
  data/kml/parivesh_kml_manifest(2).csv    149 rows, one per KML (3 failed downloads have no file)
  data/kml/*.kml
  data/official/dhpd_projects.csv, gem_projects.csv   written by build_official_data.py / build_gem_data.py

Outputs (data/official/):
  kml_catalogue.csv      one row per manifest row: geometry, centroid, bbox, size, flags, role, dedupe status
  kml_match_table.csv    one row per EC proposal: matched DHPD / GEM project, method, notes
  kml_review.md          roles that are uncertain and matches that need a human decision
  kml_geojson/<slug>.geojson       one simplified file per project
  kml_geojson/<slug>_cad.geojson   CAD / survey line-work (Kurung, Niare), off by default on the map
  kml_projects.json                project list the map reads
  kml_summary.json                 file counts and sizes before and after simplification

Rule: nothing is guessed silently. A role or match the rules cannot settle is written to
"needs review" and left as "other" / unmatched.
"""
import csv
import hashlib
import json
import math
import re
import statistics
import sys
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KML_DIR = ROOT / "data" / "kml"
MANIFEST = KML_DIR / "parivesh_kml_manifest(2).csv"
OUT = ROOT / "data" / "official"
GEOJSON_DIR = OUT / "kml_geojson"

# Arunachal Pradesh, rough box (the task's own limits)
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = 26.5, 29.5, 91.5, 97.5

DELISTED = "DELISTED_BY_SYSTEM"

# ------------------------------------------------------------------ project identity
# Parivesh project text -> (slug, display name). Written by hand because the raw text is
# messy ("Environment Clearance of Etalin HEP 3097 MW", all-caps Naying with village text).
PROJECTS = OrderedDict([
    ("kurung", "Kurung"), ("etalin", "Etalin"), ("kamala", "Kamala"),
    ("demwe-lower", "Demwe Lower"), ("kalai-ii", "Kalai II"), ("tato-i", "Tato-I"),
    ("hirong", "Hirong"), ("subansiri-upper", "Subansiri Upper"), ("tato-ii", "Tato-II"),
    ("attunli", "Attunli"), ("emra-ii", "Emra II"), ("naying", "Naying"),
    ("heo", "Heo"), ("niare", "Niare"),
])

# ------------------------------------------------------------------ manual match overrides
# slug -> (dhpd_id or None, gem_unit_id or None, note). Reported as match_method "manual".
# Empty on purpose: every project below matched by name. Add a row here to force a match
# the rules get wrong (only when you have a reason you can write in the note).
MANUAL_MATCH = {}

ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5"}
MW_TOL = 0.05          # name-MW vs register-MW gap (share of the larger) beyond which a match is noted
DIST_WARN_KM = 10.0    # KML centroid vs GEM pin


# ================================================================== helpers: names and MW
def parse_project_text(raw):
    """-> (normalised key, MW stated in the text or None)."""
    s = raw or ""
    m = re.search(r"(\d[\d,]*\.?\d*)\s*MW", s, re.I)
    mw = float(m.group(1).replace(",", "")) if m else None
    s = re.sub(r"^\s*environment clearance of\s+", "", s, flags=re.I)
    s = re.split(r"\s*-?\s*\b(?:near|districts?|state)\b", s, flags=re.I)[0]
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"\d[\d,]*\.?\d*\s*MW", " ", s, flags=re.I)
    s = re.sub(r"hydro\s*electric\s*projects?|hydroelectric\s*(?:plant|projects?)|h\.?e\.?\s*projects?|\bhep\b",
               " ", s, flags=re.I)
    return name_key(s), mw


def name_key(s):
    toks = re.findall(r"[a-z0-9]+", (s or "").lower())
    toks = [ROMAN.get(t, t) for t in toks if t not in ("stage", "st")]
    return " ".join(sorted(toks))   # sorted: "Subansiri Upper" == "Upper Subansiri"


def project_slug(raw):
    key, _ = parse_project_text(raw)
    for slug, disp in PROJECTS.items():
        if name_key(disp) == key:
            return slug
    return None


# ================================================================== KML parsing
def local(tag):
    return tag.split("}")[-1]


def read_tree(path):
    data = path.read_bytes()
    try:
        return ET.fromstring(data)
    except ET.ParseError as e:
        if "unbound prefix" in str(e):  # Google Earth Pro writes xsi: without declaring it
            fixed = data.replace(b"<kml ", b'<kml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ', 1)
            return ET.fromstring(fixed)
        raise


def parse_coords(text):
    """-> (list of (lon, lat), n_bad)."""
    pts, bad = [], 0
    for tok in (text or "").split():
        parts = tok.split(",")
        try:
            lon, lat = float(parts[0]), float(parts[1])
            if not (math.isfinite(lon) and math.isfinite(lat)) or abs(lat) > 90 or abs(lon) > 180:
                raise ValueError
            pts.append((lon, lat))
        except (ValueError, IndexError):
            bad += 1
    return pts, bad


def geom_units(pm):
    """Flatten one Placemark into [(type, coords)] with coords: Point [(x,y)], Line [(x,y)...],
    Polygon [outer, hole...]. Returns (units, n_bad)."""
    units, bad = [], 0
    for el in pm.iter():
        t = local(el.tag)
        if t == "Point":
            c = next((e for e in el.iter() if local(e.tag) == "coordinates"), None)
            pts, b = parse_coords(c.text if c is not None else "")
            bad += b
            if pts:
                units.append(("Point", [pts[0]]))
        elif t == "LineString":
            c = next((e for e in el.iter() if local(e.tag) == "coordinates"), None)
            pts, b = parse_coords(c.text if c is not None else "")
            bad += b
            if len(pts) >= 2:
                units.append(("LineString", pts))
        elif t == "Polygon":
            rings = []
            for ring in el.iter():
                if local(ring.tag) == "LinearRing":
                    c = next((e for e in ring if local(e.tag) == "coordinates"), None)
                    pts, b = parse_coords(c.text if c is not None else "")
                    bad += b
                    if len(pts) >= 4:
                        rings.append(pts)
            if rings:
                units.append(("Polygon", rings))
    return units, bad


def walk(el, path, out):
    """Collect Placemarks with the names of their ancestor Folders / Documents."""
    for ch in el:
        t = local(ch.tag)
        if t in ("Document", "Folder"):
            nm = next((c.text.strip() for c in ch if local(c.tag) == "name" and c.text), "")
            walk(ch, path + ([nm] if nm else []), out)
        elif t == "Placemark":
            nm = next((c.text.strip() for c in ch if local(c.tag) == "name" and c.text), "")
            out.append((nm, path, ch))
        elif t == "kml":
            walk(ch, path, out)


# ================================================================== geometry maths
def all_pts(unit):
    t, c = unit
    if t == "Polygon":
        return [p for ring in c for p in ring]
    return list(c)


def ring_area_m2(ring, lat0):
    kx = 111320.0 * math.cos(math.radians(lat0))
    ky = 110540.0
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        s += (x1 * kx) * (y2 * ky) - (x2 * kx) * (y1 * ky)
    return abs(s) / 2


def unit_area_ha(unit):
    if unit[0] != "Polygon":
        return 0.0
    rings = unit[1]
    lat0 = rings[0][0][1]
    return (ring_area_m2(rings[0], lat0) - sum(ring_area_m2(r, lat0) for r in rings[1:])) / 1e4


def haversine_km(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(a))


def unit_length_km(unit):
    if unit[0] != "LineString":
        return 0.0
    pts = unit[1]
    return sum(haversine_km(a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:]))


def bbox_of(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def unit_hash(unit):
    """Hash of the geometry only (name ignored), rounded to 5 dp, ring start and direction normalised."""
    t, c = unit

    def rnd(pts):
        return [(round(x, 5), round(y, 5)) for x, y in pts]

    def canon_ring(r):
        r = rnd(r)
        if r[0] == r[-1]:
            r = r[:-1]
        i = r.index(min(r))
        r = r[i:] + r[:i]
        if len(r) > 2 and r[1] > r[-1]:     # fix direction
            r = [r[0]] + r[1:][::-1]
        return r

    if t == "Polygon":
        body = [canon_ring(r) for r in c]
        body = [body[0]] + sorted(body[1:])
    elif t == "LineString":
        pts = rnd(c)
        body = pts if pts[0] <= pts[-1] else pts[::-1]
    else:
        body = rnd(c)
    return hashlib.sha1(json.dumps([t, body]).encode()).hexdigest()[:16]


# ================================================================== role classification
# Ordered rules, first hit wins. Tried against the placemark name, then its folder names,
# then the file name; so a descriptive placemark beats a file name.
ROLES = ("project_layout", "project_area", "dam_axis", "submergence", "forest_land", "ancillary", "other", "cad_detail")

RULES = [
    ("ancillary",      r"drift|drill|muck|dump|quarry|batching|crusher|\badit\b|camp\b|colony|maga?z+ine|"
                       r"stock\s*yard|workshop|disposal|borrow|\baux|\broads?\b|bridge|\b[lr]dr\b|helipad|"
                       r"construction\s*facilit|job\s*facilit|fabrication|equipment\s*yard|\bpath\b"),
    ("dam_axis",       r"dam\s*axis|\baxis\b|dam\s*alternativ"),
    ("submergence",    r"reservoir|submerg|submegence|\bfrl\b|water\s*spread|impound"),
    ("project_layout", r"power\s*house|\bp/h\b|head\s*race|\bhrt\b|tail\s*race|\btrt\b|surge|intake|inlet|"
                       r"diversion\s*tunnel|\bdt-?\d|penstock|cofferdam|coffer\s*dam|spillway|tunnel|cavern|pressure|"
                       r"desilting|\bdam\b|barrage|switchyard|pot\s*head|portal|component|layout|project\s*feat|"
                       r"dam\s*site"),
    ("forest_land",    r"forest|\bfl\b|nfl|land\s*area|\bla[_\s-]|divers|\bfc\b|patch|\bfd\b"),
]
# Ambiguous names: a hit is kept but listed for review with the reason. Checked before RULES.
AMBIGUOUS = [
    # (pattern, role, review reason, note shown on the map or "")
    (r"project\s*area|project\s*boundary", "project_area",
     "'Project Area' kept as its own role; the file does not say whether it is the whole boundary or the works area", ""),
    (r"alternate?\s*sites?|\bsite\s*[a-e]\b|^site[_\s-]?[a-e]\b", "dam_axis",
     "'Site A-E' read as alternative dam sites; the name does not say axis or reservoir",
     "alternative site (inferred from file names)"),
    (r"^dam\s*site$", "project_layout",
     "'Dam site' is a polygon (works area), not an axis line", ""),
    (r"^(mda|cbp|rq|rbm)[\s-]*\d*$", "ancillary",
     "labels kept as written (not expanded); 'ancillary' is inferred from the neighbouring construction-area names", ""),
    (r"shoal", "other", "'Shoal area' (river bar?) has no matching role", ""),
]
# Line-work reclassified as cad_detail (analyst decision): (project slug, file-label regex, only role "other"?)
CAD_DETAIL = [
    ("kurung", r".", True),               # Kurung alt-1b / alt-2 / Alt-3 CAD line-work, no names or attributes
    ("niare", r"power house alt", False),  # Niare "power house alt-N" line-work
]
FC_PREFIX = re.compile(r"^\d+_FC_(?:FORM_C_FOREST_LAND_PROPOSED_DIVERSION_)?KML_\d+_", re.I)


def clean_label(name):
    s = FC_PREFIX.sub("", name or "")
    return re.sub(r"\.kml$", "", s, flags=re.I).replace("_", " ")


def classify_text(text):
    """-> (role, ambiguous_reason or None, note) or None."""
    t = (text or "").strip()
    if not t:
        return None
    for pat, role, why, note in AMBIGUOUS:
        if re.search(pat, t, re.I):
            return role, why, note
    for role, pat in RULES:
        if re.search(pat, t, re.I):
            return role, None, ""
    return None


def classify_unit(pm_name, attrs, folders, file_label, file_raw_name, geom_type):
    """-> (role, confidence, reason, note).
    confidence: high = placemark / attribute / inner folder name, or the FORM_C forest-land upload prefix;
    medium = file or document name only, or the plain FC_KML upload prefix; low = nothing matched."""
    cands = [pm_name] + list(attrs) + list(reversed(folders[1:]))
    for txt in cands:
        r = classify_text(txt)
        if r:
            return r[0], "high", (r[1] or ""), r[2]
    for txt in ([folders[0]] if folders else []) + [file_label]:
        r = classify_text(txt)
        if r:
            return r[0], "medium", (r[1] or "role taken from the file / document name only"), r[2]
    if FC_PREFIX.match(file_raw_name or ""):
        if "FORM_C_FOREST_LAND_PROPOSED_DIVERSION" in file_raw_name:
            return "forest_land", "high", "role from the 'FORM_C_FOREST_LAND_PROPOSED_DIVERSION' upload prefix; names are generic", ""
        return "forest_land", "medium", "role from the plain 'FC_KML' upload prefix only; names are generic", ""
    return "other", "low", "no keyword in placemark, attribute, folder or file name", ""


def alt_label(*texts):
    for t in texts:
        t = t or ""
        m = re.search(r"\balt(?:ernat(?:e|ive)s?)?(?=[\s_\-0-9.]|$)[\s_-]*(\d+[a-z]?|[ivx]+\b)?", t, re.I)
        if m:
            return "Alt " + m.group(1).upper() if m.group(1) else "Alt"
        m = re.search(r"\bsite[\s_-]*(ii|iii|[a-e])\b", t, re.I)
        if m:
            return "Site " + m.group(1).upper()
        m = re.search(r"dam\s*alternativ\w*[\s-]*(\d)", t, re.I)
        if m:
            return "Alt " + m.group(1)
    return ""


# ================================================================== step 1-3: catalogue
def load_manifest():
    with open(MANIFEST, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def proposal_num(p):
    return int(p.split("/")[3])


RETURNED = "Proposal returned in present form"
KIND_ORDER = {"default": 0, "earlier": 0, "returned": 1, "delisted": 2}


def proposal_kinds(rows):
    """proposalNo -> default | earlier | returned | delisted (default = newest live proposal)."""
    st = {r["proposalNo"]: r["status"] for r in rows}
    live = sorted((p for p, s_ in st.items() if s_ not in (DELISTED, RETURNED)), key=proposal_num, reverse=True)
    out = {}
    for p, s_ in st.items():
        out[p] = "delisted" if s_ == DELISTED else "returned" if s_ == RETURNED else (
            "default" if live and p == live[0] else "earlier")
    return out


def analyse_file(row):
    """Parse one manifest row -> dict with flags and units."""
    rec = {"flags": [], "units": [], "doc_name": ""}
    ok = row["ok"].strip().lower() == "true"
    path = KML_DIR / row["file"] if row["file"] else None
    if not ok or not path or not path.exists():
        rec["flags"].append("missing_download" + (f" ({row['error']})" if row["error"] else ""))
        rec["status"] = "missing"
        return rec
    try:
        root = read_tree(path)
    except Exception as e:  # noqa: BLE001
        rec["flags"].append(f"parse_error ({e})")
        rec["status"] = "excluded"
        return rec
    if any(local(e.tag) == "NetworkLink" for e in root.iter()):
        rec["flags"].append("network_link")
    placemarks = []
    walk(root, [], placemarks)
    rec["doc_name"] = next((c.text.strip() for e in root.iter() if local(e.tag) == "Document"
                            for c in e if local(c.tag) == "name" and c.text), "")
    n_bad = 0
    for nm, folders, pm in placemarks:
        units, b = geom_units(pm)
        n_bad += b
        attrs = [re.sub(r"^\d+(\.\d+)?\.?\s*", "", (e.text or "").strip()) for e in pm.iter()
                 if local(e.tag) in ("SimpleData", "value") and (e.text or "").strip()
                 and not re.fullmatch(r"[-\d.,eE+\s]+", e.text.strip()) and len(e.text.strip()) < 60]
        for u in units:
            rec["units"].append({"name": nm, "folders": folders, "attrs": attrs, "geom": u})
    if n_bad:
        rec["flags"].append(f"bad_coordinates ({n_bad})")
    if not rec["units"]:
        rec["flags"].append("empty")
    return rec


def build_catalogue():
    manifest = load_manifest()
    files = []
    for row in manifest:
        rec = analyse_file(row)
        rec["row"] = row
        rec["slug"] = project_slug(row["project"])
        files.append(rec)

    for rec in files:
        row = rec["row"]
        label = clean_label(row["name"])
        pts = []
        for u in rec["units"]:
            u["hash"] = unit_hash(u["geom"])
            role, conf, why, note = classify_unit(u["name"], u["attrs"], u["folders"], label, row["name"], u["geom"][0])
            for cslug, cpat, only_other in CAD_DETAIL:
                if (rec["slug"] == cslug and u["geom"][0] == "LineString" and re.search(cpat, label, re.I)
                        and (role == "other" or not only_other)):
                    role, conf, why, note = "cad_detail", "medium", "", "CAD / survey line-work (reclassified by the analyst)"
            u["role"], u["conf"], u["why"], u["note"] = role, conf, why, note
            u["alt"] = alt_label(u["name"], " ".join(u["folders"]), label, rec["doc_name"])
            pts += all_pts(u["geom"])
        rec["label"] = label
        if pts:
            x0, y0, x1, y1 = bbox_of(pts)
            rec["bbox"] = (x0, y0, x1, y1)
            rec["centroid"] = ((x0 + x1) / 2, (y0 + y1) / 2)
            outside = [p for p in pts if not (LAT_MIN <= p[1] <= LAT_MAX and LON_MIN <= p[0] <= LON_MAX)]
            if outside:
                rec["flags"].append(f"outside_arunachal ({len(outside)} of {len(pts)} points)")
            if len(outside) == len(pts):
                rec["all_outside"] = True
        rec["area_ha"] = sum(unit_area_ha(u["geom"]) for u in rec["units"])
        rec["length_km"] = sum(unit_length_km(u["geom"]) for u in rec["units"])

    # ---- dedupe: per project. Proposal order: live ones (newest first), then returned, then delisted.
    # The default proposal is the newest one that is neither returned nor delisted.
    by_proj = defaultdict(list)
    for rec in files:
        by_proj[rec["slug"]].append(rec)
    kept = {}       # (slug, hash) -> unit dict (the one that gets mapped)
    for slug, recs in by_proj.items():
        kinds = proposal_kinds([r["row"] for r in recs])
        for rec in recs:
            rec["kind"] = kinds[rec["row"]["proposalNo"]]
        def prio(rec):
            n = proposal_num(rec["row"]["proposalNo"])
            ts = re.search(r"_(\d{13})_", rec["row"]["name"])
            return (KIND_ORDER[rec["kind"]], -n, -(int(ts.group(1)) if ts else 0))
        for rec in sorted(recs, key=prio):
            if rec.get("status") in ("missing", "excluded"):
                continue
            if "network_link" in " ".join(rec["flags"]):
                rec["status"] = "excluded"
                continue
            if not rec["units"] or rec.get("all_outside"):
                rec["status"] = "excluded"
                continue
            new, dup, dup_src = 0, 0, Counter()
            for u in rec["units"]:
                k = (slug, u["hash"])
                if k not in kept:
                    kept[k] = {"unit": u, "file": rec, "also": []}
                    u["is_kept"] = True
                    new += 1
                else:
                    u["is_kept"] = False
                    kept[k]["also"].append(rec["row"]["proposalNo"])
                    dup += 1
                    dup_src[kept[k]["file"]["row"]["file"]] += 1
            if new == 0:
                rec["status"] = "duplicate"
                rec["dup_of"] = dup_src.most_common(1)[0][0]
            else:
                rec["status"] = "mapped"
                if dup:
                    rec["dup_note"] = f"{dup} of {new + dup} geometries already mapped from {dup_src.most_common(1)[0][0]}"
    return files, kept


# ================================================================== step 4: matching
def load_csv(name):
    with open(OUT / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def centroid_of(units):
    """Median of unit centres: robust to one far-away alternative."""
    cs = []
    for u in units:
        if u["role"] == "cad_detail":
            continue
        x0, y0, x1, y1 = bbox_of(all_pts(u["geom"]))
        cs.append(((x0 + x1) / 2, (y0 + y1) / 2))
    if not cs:
        return None
    return statistics.median(c[0] for c in cs), statistics.median(c[1] for c in cs)


def build_matches(files):
    dhpd = load_csv("dhpd_projects.csv")
    gem = load_csv("gem_projects.csv")
    dkey = defaultdict(list)
    for d in dhpd:
        dkey[parse_project_text(d["project"])[0]].append(d)
    gkey = defaultdict(list)
    for g in gem:
        gkey[parse_project_text(g["name"])[0]].append(g)

    projects = OrderedDict()
    for slug, disp in PROJECTS.items():
        recs = [r for r in files if r["slug"] == slug]
        props = OrderedDict()
        for r in recs:
            props.setdefault(r["row"]["proposalNo"], r["row"])
        mws = {parse_project_text(r["row"]["project"])[1] for r in recs} - {None}
        mw_note = None
        for r in recs:       # also accept an MW in an uploaded file name ("Kamala HEP 1720 MW")
            m = re.search(r"(\d[\d,]*)\s*MW", r["row"]["name"], re.I)
            if m:
                mw_note = float(m.group(1).replace(",", ""))
        kml_mw = max(mws) if mws else mw_note
        units = [u for r in recs for u in r["units"] if u.get("is_kept")]
        projects[slug] = {"slug": slug, "name": disp, "proposals": props, "kml_mw": kml_mw,
                          "mw_source": "project text" if mws else ("file name" if mw_note else ""),
                          "centroid": centroid_of(units), "recs": recs}

    matches = {}
    for slug, p in projects.items():
        key = name_key(p["name"])
        notes, method, d_id, g_id, review = [], "unmatched", "", "", False
        if slug in MANUAL_MATCH:
            d_id, g_id, note = MANUAL_MATCH[slug]
            method, notes = "manual", [note]
            d = next((x for x in dhpd if x["dhpd_id"] == d_id), None)
        else:
            cands = dkey.get(key, [])
            d = cands[0] if len(cands) == 1 else None
            if len(cands) > 1:
                notes.append(f"{len(cands)} DHPD rows share this name; left unmatched.")
                review = True
            if d:
                d_id = d["dhpd_id"]
                method = "exact"
            else:  # fuzzy: closest DHPD name, only offered when similar enough
                import difflib
                best = max(dhpd, key=lambda x: difflib.SequenceMatcher(None, key, name_key(x["project"])).ratio())
                ratio = difflib.SequenceMatcher(None, key, name_key(best["project"])).ratio()
                if ratio >= 0.85 and not cands:
                    d, d_id, method = best, best["dhpd_id"], "fuzzy"
                    notes.append(f"Name similarity {ratio:.2f} to DHPD '{best['project']}'.")
                    review = True
        # GEM: rows pointing at the DHPD id first, else name
        gcands = [g for g in gem if d_id and g["dhpd_id"] == d_id] or gkey.get(key, [])
        g = None
        if gcands:
            if p["kml_mw"]:
                g = min(gcands, key=lambda x: abs(float(x["capacity_mw"] or 0) - p["kml_mw"]))
            else:
                g = gcands[0]
            if g_id == "":
                g_id = g["gem_unit_id"]
        elif g_id:
            g = next((x for x in gem if x["gem_unit_id"] == g_id), None)
        if not d and g and method == "unmatched":
            method = "exact" if name_key(g["name"]) == key else "fuzzy"
            notes.append("No DHPD row; matched to GEM by name only.")
        # sanity: MW and distance
        d_mw = float(d["capacity_mw"]) if d else None
        g_mw = float(g["capacity_mw"]) if g and g["capacity_mw"] else None
        for who, val in (("DHPD", d_mw), ("GEM", g_mw)):
            if val and p["kml_mw"] and abs(val - p["kml_mw"]) / max(val, p["kml_mw"]) > MW_TOL:
                notes.append(f"MW differs: KML/Parivesh text {p['kml_mw']:g} ({p['mw_source']}), {who} {val:g}.")
                review = True
        dist = None
        if g and g.get("latitude") and p["centroid"]:
            dist = haversine_km(p["centroid"][0], p["centroid"][1], float(g["longitude"]), float(g["latitude"]))
            if dist > DIST_WARN_KM:
                notes.append(f"KML centroid is {dist:.0f} km from the GEM pin ({g['name']}).")
                review = True
        # Confidence tiers (name equal in every case reaching here):
        #   exact     MW agrees with a register (or the Parivesh text has no MW) and the KML is within DIST_WARN_KM
        #   fuzzy     name agrees but MW or location does not; kept, flagged for a human
        #   unmatched name agrees but MW AND location both disagree: probably a different project
        if p["kml_mw"] is None:
            notes.append("No MW in the Parivesh project text or file names; matched on name only.")
        mw_vals = [v for v in (d_mw, g_mw) if v]
        mw_ok = None if (p["kml_mw"] is None or not mw_vals) else any(
            abs(v - p["kml_mw"]) / max(v, p["kml_mw"]) <= MW_TOL for v in mw_vals)
        far = dist is not None and dist > DIST_WARN_KM
        if method != "manual" and (d or g):
            if mw_ok is False and far:
                ref = d_mw or g_mw
                notes[:] = [f"Same name as DHPD {d_id or '-'} / GEM {g['gem_unit_id'] if g else '-'}. This may be a "
                            f"re-scoped version of that project, but capacity ({p['kml_mw']:g} vs {ref:g} MW) and "
                            f"location ({dist:.0f} km apart) differ, so it is not matched. Shown as 'EC proposal only'."]
                method, d_id, g, d = "unmatched", "", None, None
            elif mw_ok is False or far:
                method = "fuzzy"
        if method == "unmatched" and not d_id and not notes:
            notes.append("No DHPD or GEM project with this name; shown as 'EC proposal only'.")
        if method == "unmatched":
            review = True
        if method == "fuzzy":
            notes.append("Match unverified (name/MW only).")
        review = review or method in ("fuzzy", "unmatched")
        matches[slug] = {"d": d, "g": g, "dhpd_id": d_id, "gem_unit_id": g["gem_unit_id"] if g else "",
                         "method": method, "notes": notes, "review": review, "dist": dist,
                         "d_mw": d_mw if d else None, "g_mw": g_mw if g else None}
    return projects, matches


# ================================================================== outputs
def fmt(v, nd=5):
    return "" if v is None else f"{v:.{nd}f}"


def write_catalogue(files):
    cols = ["proposal_no", "project", "project_slug", "status", "file", "manifest_name", "ok", "bytes",
            "proposal_kind", "dedupe_status", "duplicate_of", "geometry_types", "n_features", "n_points", "n_lines", "n_polygons",
            "centroid_lat", "centroid_lon", "bbox_west", "bbox_south", "bbox_east", "bbox_north",
            "area_ha", "length_km", "file_role", "role_confidence", "feature_roles", "needs_review", "flags", "notes"]
    rows = []
    for r in files:
        row = r["row"]
        us = r["units"]
        gt = Counter(u["geom"][0] for u in us)
        roles = Counter(u["role"] for u in us)
        confs = [u["conf"] for u in us]
        file_role = (next(iter(roles)) if len(roles) == 1 else ("mixed" if roles else ""))
        conf = "" if not confs else ("low" if "low" in confs else "medium" if "medium" in confs else "high")
        review = sorted({u["why"] for u in us if u["why"]})
        needs = "yes" if (review or "low" in confs) and r["status"] in ("mapped", "duplicate") else ""
        notes = r.get("dup_note", "")
        if r["status"] == "excluded" and "network_link" in " ".join(r["flags"]):
            notes = "NetworkLink to a .KMZ that is not in the download set. Unresolved: the real geometry is missing."
        if r["status"] == "missing":
            notes = "Download failed (HTTP 500 per manifest); no file on disk."
        c = r.get("centroid")
        b = r.get("bbox")
        rows.append({
            "proposal_no": row["proposalNo"], "project": row["project"], "project_slug": r["slug"] or "",
            "status": row["status"], "file": row["file"], "manifest_name": row["name"], "ok": row["ok"],
            "bytes": row["bytes"], "proposal_kind": r.get("kind", ""), "dedupe_status": r["status"], "duplicate_of": r.get("dup_of", ""),
            "geometry_types": "+".join(f"{k}" for k in sorted(gt)), "n_features": len(us),
            "n_points": gt["Point"], "n_lines": gt["LineString"], "n_polygons": gt["Polygon"],
            "centroid_lat": fmt(c[1]) if c else "", "centroid_lon": fmt(c[0]) if c else "",
            "bbox_west": fmt(b[0]) if b else "", "bbox_south": fmt(b[1]) if b else "",
            "bbox_east": fmt(b[2]) if b else "", "bbox_north": fmt(b[3]) if b else "",
            "area_ha": f"{r['area_ha']:.2f}" if gt["Polygon"] else "",
            "length_km": f"{r['length_km']:.2f}" if gt["LineString"] else "",
            "file_role": file_role, "role_confidence": conf,
            "feature_roles": "; ".join(f"{k} {v}" for k, v in roles.most_common()),
            "needs_review": needs, "flags": "; ".join(r["flags"]), "notes": notes,
        })
    with open(OUT / "kml_catalogue.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return rows


def write_matches(projects, matches):
    cols = ["proposal_no", "project", "project_slug", "status", "matched_dhpd_id", "matched_gem_unit_id",
            "match_method", "notes", "kml_mw", "dhpd_mw", "gem_mw", "km_to_gem_pin", "kml_centroid_lat",
            "kml_centroid_lon", "needs_review"]
    rows = []
    for slug, p in projects.items():
        m = matches[slug]
        for pno, mrow in sorted(p["proposals"].items(), key=lambda kv: -proposal_num(kv[0])):
            c = p["centroid"]
            rows.append({
                "proposal_no": pno, "project": mrow["project"], "project_slug": slug, "status": mrow["status"],
                "matched_dhpd_id": m["dhpd_id"], "matched_gem_unit_id": m["gem_unit_id"],
                "match_method": m["method"], "notes": " ".join(m["notes"]),
                "kml_mw": "" if p["kml_mw"] is None else f"{p['kml_mw']:g}",
                "dhpd_mw": "" if m["d_mw"] is None else f"{m['d_mw']:g}",
                "gem_mw": "" if m["g_mw"] is None else f"{m['g_mw']:g}",
                "km_to_gem_pin": "" if m["dist"] is None else f"{m['dist']:.1f}",
                "kml_centroid_lat": fmt(c[1]) if c else "", "kml_centroid_lon": fmt(c[0]) if c else "",
                "needs_review": "yes" if m["review"] else "",
            })
    with open(OUT / "kml_match_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return rows


def write_review(files, projects, matches, cat_rows, plist):
    L = ["# KML build: items needing review", ""]
    L += ["## Decisions applied", "",
          "- Default proposal = newest proposal whose status is neither 'Proposal returned in present form' nor DELISTED_BY_SYSTEM. "
          "Returned and delisted proposals stay as toggleable layers.",
          "- Marker = GEM pin when the KML centroid is within 10 km of it, otherwise the KML centroid. Fuzzy matches are shown as unverified.",
          "- `cad_detail` = Kurung's unlabelled lines and Niare's 'power house alt-N' lines. Written to <slug>_cad.geojson, off by default.",
          "- `project_area` = Tato-I 'Project Area'. Subansiri Upper Sites A-E carry the note 'alternative site (inferred from file names)'.",
          "- Hirong MDA / CBP / RQ / RBM labels are kept as written.",
          "- `role_confidence`: high = placemark / attribute / folder name, or the FORM_C_FOREST_LAND_PROPOSED_DIVERSION prefix; "
          "medium = file or document name only, or the plain FC_KML prefix; low = no keyword.", ""]
    L += ["## Proposals: default, kind and geometry", ""]
    for x in plist:
        for pr in x["proposals"]:
            L.append(f"- {x['slug']} | {pr['proposal_no']} | {pr['status']} | {pr['kind']} | {pr['geometry_note']}")
    L += [""]
    L += ["## Unresolved / excluded files", ""]
    for r in cat_rows:
        if r["dedupe_status"] in ("excluded", "missing"):
            L.append(f"- {r['proposal_no']} | {r['manifest_name']} | {r['dedupe_status']} | {r['flags']}")
    L += ["", "## Roles needing review (mapped geometry only; one line per project / file / reason)", ""]
    seen = set()
    for slug in projects:
        for r in files:
            if r["slug"] != slug or r["status"] != "mapped":
                continue
            why = Counter((u["role"], u["why"]) for u in r["units"] if u["why"] and u.get("is_kept"))
            for (role, w), n in why.items():
                key = (slug, r["label"], role, w)
                if key in seen:
                    continue
                seen.add(key)
                extra = ""
                if role == "other":
                    ar = sorted((round(unit_area_ha(u["geom"]), 1) for u in r["units"] if u["role"] == "other"
                                 and u.get("is_kept") and u["geom"][0] == "Polygon"), reverse=True)[:8]
                    extra = f" (polygon areas ha: {ar})" if ar else ""
                L.append(f"- {slug} | {r['row']['proposalNo']} | {r['label']} | {n}x {role}: {w}{extra}")
    L += ["", "## Matches needing review", ""]
    for slug, m in matches.items():
        if m["review"]:
            L.append(f"- {slug}: {m['method']} dhpd={m['dhpd_id'] or '-'} gem={m['gem_unit_id'] or '-'} | " + " ".join(m["notes"]))
    (OUT / "kml_review.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# ================================================================== step 5: GeoJSON for the web
SIMPLIFY_DEG = 0.00003      # Douglas-Peucker tolerance, about 3 m
SIMPLIFY_CAD_DEG = 0.0001   # about 11 m; the CAD / survey line-work is only a backdrop


def douglas_peucker(pts, eps):
    if len(pts) < 3 or eps <= 0:
        return list(pts)
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy)
        dmax, idx = 0.0, -1
        for i in range(a + 1, b):
            x, y = pts[i]
            d = (math.hypot(x - x1, y - y1) if norm == 0 else abs(dy * (x - x1) - dx * (y - y1)) / norm)
            if d > dmax:
                dmax, idx = d, i
        if dmax > eps and idx > 0:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def r5(pts):
    return [[round(x, 5), round(y, 5)] for x, y in pts]


def geom_json(unit, eps):
    t, c = unit
    if t == "Point":
        return {"type": "Point", "coordinates": r5(c)[0]}
    if t == "LineString":
        return {"type": "LineString", "coordinates": r5(douglas_peucker(c, eps))}
    rings = []
    for k, ring in enumerate(c):
        simp = douglas_peucker(ring, eps)
        if len(simp) < 4:
            if k:                      # a hole that collapsed: drop it
                continue
            simp = ring                # an outer ring that collapsed: keep it as drawn
        rings.append(r5(simp))
    return {"type": "Polygon", "coordinates": rings}


def feature_label(u):
    name = (u["name"] or "").strip()
    if name:
        return name
    if u["role"] == "cad_detail":
        return ""
    t, _ = u["geom"]
    if t == "Polygon":
        ha = unit_area_ha(u["geom"])
        return f"Unlabelled polygon, {ha:,.0f} ha" if ha >= 100 else f"Unlabelled polygon, {ha:,.1f} ha"
    if t == "LineString":
        return f"Unlabelled line, {unit_length_km(u['geom']):.2f} km"
    return "Unlabelled point"


def short_no(p):
    return "/".join(p.split("/")[3:])


def geojson_features(slug, kept, status_of, kind_of, eps_main, eps_cad):
    main, cad = [], []
    for (sl, _h), e in kept.items():
        if sl != slug:
            continue
        u, rec = e["unit"], e["file"]
        pno = rec["row"]["proposalNo"]
        props = {"role": u["role"], "proposal_no": pno, "status": status_of[pno], "layer": kind_of[pno]}
        lab = feature_label(u)
        if lab:
            props["label"] = lab
        if u["alt"]:
            props["alt"] = u["alt"]
        props["role_confidence"] = u["conf"]
        if u["note"]:
            props["note"] = u["note"]
        also = sorted({a for a in e["also"] if a != pno}, key=proposal_num, reverse=True)
        if also:
            props["also_in"] = also
        t = u["geom"][0]
        if t == "Polygon":
            props["area_ha"] = round(unit_area_ha(u["geom"]), 2)
        elif t == "LineString":
            props["length_km"] = round(unit_length_km(u["geom"]), 3)
        is_cad = u["role"] == "cad_detail"
        feat = {"type": "Feature", "properties": props,
                "geometry": geom_json(u["geom"], eps_cad if is_cad else eps_main)}
        (cad if is_cad else main).append(feat)
    order = {r: i for i, r in enumerate(ROLES)}
    for lst in (main, cad):
        lst.sort(key=lambda f: (order[f["properties"]["role"]], f["properties"].get("label", "")))
    return main, cad


def dump(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def fc(feats):
    return {"type": "FeatureCollection", "features": feats}


def feature_bbox(feats):
    pts = []
    for f in feats:
        g = f["geometry"]
        pts += [g["coordinates"]] if g["type"] == "Point" else (
            g["coordinates"] if g["type"] == "LineString" else g["coordinates"][0])
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return [min(xs), min(ys), max(xs), max(ys)]


def title_district(rows):
    for r in rows:
        m = re.search(r"districts?\s*[-:]?\s*(.+?)\s*,\s*state", r["project"], re.I)
        if m:
            return m.group(1).strip().title()
    return ""


def proposal_summaries(recs, kept, slug):
    """Per proposal: kind, files, and how its geometry relates to the other proposals."""
    props = OrderedDict()
    for r in sorted(recs, key=lambda r: -proposal_num(r["row"]["proposalNo"])):
        props.setdefault(r["row"]["proposalNo"], []).append(r)
    sets = {pno: {u["hash"] for r in rs if r["status"] in ("mapped", "duplicate") for u in r["units"]}
            for pno, rs in props.items()}
    unique = Counter(e["file"]["row"]["proposalNo"] for (sl, _h), e in kept.items() if sl == slug)
    out = []
    for pno, rs in props.items():
        row = rs[0]["row"]
        note, mine = "", sets[pno]
        if mine:
            others = [o for o in props if o != pno and mine <= sets[o]]
            pref = sorted(others, key=lambda o: (props[o][0]["kind"] in ("returned", "delisted"), -proposal_num(o)))
            if pref:
                o = pref[0]
                tag = f" ({props[o][0]['row']['status']})" if props[o][0]["kind"] in ("returned", "delisted") else ""
                note = (f"Same geometry as {short_no(o)}{tag}" if sets[o] == mine
                        else f"All of its geometry also appears in {short_no(o)}{tag}")
            elif unique[pno] < len(mine):
                note = (f"{unique[pno]} of {len(mine)} geometries are only in this proposal; "
                        "the rest also appear in other proposals")
            else:
                note = "All of its geometry is only in this proposal"
        files = []
        for r in sorted(rs, key=lambda r: r["row"]["file"]):
            files.append({"label": r["label"], "status": r["status"], "bytes": int(r["row"]["bytes"] or 0),
                          "roles": dict(Counter(u["role"] for u in r["units"])), "flags": r["flags"],
                          "duplicate_of": r.get("dup_of", "")})
        out.append({"proposal_no": pno, "status": row["status"], "kind": rs[0]["kind"],
                    "geometry_note": note, "files": files})
    return out


def build_web(kept, projects, matches):
    GEOJSON_DIR.mkdir(parents=True, exist_ok=True)
    for old in GEOJSON_DIR.glob("*.geojson"):
        old.unlink()
    raw_bytes = final_main = final_cad = 0
    plist, sizes = [], []
    for slug, p in projects.items():
        recs = p["recs"]
        status_of = {r["row"]["proposalNo"]: r["row"]["status"] for r in recs}
        kind_of = {r["row"]["proposalNo"]: r["kind"] for r in recs}
        m = matches[slug]
        raw_m, raw_c = geojson_features(slug, kept, status_of, kind_of, 0, 0)
        raw_bytes += len(dump(fc(raw_m)).encode()) + (len(dump(fc(raw_c)).encode()) if raw_c else 0)
        main, cad = geojson_features(slug, kept, status_of, kind_of, SIMPLIFY_DEG, SIMPLIFY_CAD_DEG)
        gj = f"kml_geojson/{slug}.geojson"
        cj = f"kml_geojson/{slug}_cad.geojson" if cad else None
        text = dump(fc(main))
        (OUT / gj).write_text(text, encoding="utf-8")
        b1, b2 = len(text.encode()), 0
        if cad:
            text = dump(fc(cad))
            (OUT / cj).write_text(text, encoding="utf-8")
            b2 = len(text.encode())
        final_main += b1
        final_cad += b2
        sizes.append((slug, len(main), b1, len(cad), b2))

        g = m["g"]
        pin = [float(g["longitude"]), float(g["latitude"])] if g and g.get("latitude") else None
        cen = p["centroid"]
        use_pin = bool(pin and m["dist"] is not None and m["dist"] <= DIST_WARN_KM)
        marker = pin if use_pin else cen
        defaults = [r["row"]["proposalNo"] for r in recs if r["kind"] == "default"]
        counts = Counter(f["properties"]["role"] for f in main + cad)
        plist.append({
            "slug": slug, "name": p["name"], "match_method": m["method"],
            "dhpd_id": m["dhpd_id"], "gem_unit_id": m["gem_unit_id"], "match_notes": " ".join(m["notes"]),
            "kml_mw": p["kml_mw"], "kml_mw_source": p["mw_source"],
            "title_district": title_district([r["row"] for r in recs]),
            "centroid": [round(cen[0], 5), round(cen[1], 5)],
            "pin": pin if m["method"] != "unmatched" else None,
            "pin_km": None if (m["dist"] is None or m["method"] == "unmatched") else round(m["dist"], 1),
            "marker": [round(marker[1], 5), round(marker[0], 5)],
            "marker_source": "pin" if use_pin else "kml_centroid",
            "default_proposal": defaults[0] if defaults else "",
            "proposals": proposal_summaries(recs, kept, slug),
            "geojson": gj, "cad_geojson": cj,
            "bbox": feature_bbox(main) or feature_bbox(cad),
            "counts": dict(counts),
        })
    (OUT / "kml_projects.json").write_text(json.dumps(plist, indent=1, ensure_ascii=False), encoding="utf-8")
    return plist, raw_bytes, final_main, final_cad, sizes


def write_summary(cat, plist, raw_bytes, final_main, final_cad):
    st = Counter(r["dedupe_status"] for r in cat)
    summ = {
        "manifest_rows": len(cat), "files_by_dedupe_status": dict(st), "projects": len(plist),
        "matched": sum(1 for x in plist if x["match_method"] != "unmatched"),
        "unmatched": sum(1 for x in plist if x["match_method"] == "unmatched"),
        "unique_geometries": sum(sum(x["counts"].values()) for x in plist),
        "size_bytes": {"kml_all_files": sum(int(r["bytes"] or 0) for r in cat),
                       "kml_mapped_files": sum(int(r["bytes"] or 0) for r in cat if r["dedupe_status"] == "mapped"),
                       "geojson_deduped_unsimplified": raw_bytes,
                       "geojson_simplified_main": final_main, "geojson_simplified_cad": final_cad,
                       "geojson_simplified_total": final_main + final_cad},
        "simplify_tolerance_deg": {"main": SIMPLIFY_DEG, "cad_detail": SIMPLIFY_CAD_DEG}, "coordinate_decimals": 5,
    }
    (OUT / "kml_summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    return summ


def mb(n):
    return f"{n / 1e6:.2f} MB"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files, kept = build_catalogue()
    projects, matches = build_matches(files)
    cat = write_catalogue(files)
    write_matches(projects, matches)
    plist, raw_bytes, fm, fcad, sizes = build_web(kept, projects, matches)
    write_review(files, projects, matches, cat, plist)
    summ = write_summary(cat, plist, raw_bytes, fm, fcad)
    print(f"{len(cat)} manifest rows -> {summ['files_by_dedupe_status']}; {summ['projects']} projects "
          f"({summ['matched']} matched, {summ['unmatched']} EC-proposal-only); "
          f"{summ['unique_geometries']} unique geometries")
    sz = summ["size_bytes"]
    print(f"size: KML {mb(sz['kml_all_files'])} -> de-duplicated GeoJSON {mb(sz['geojson_deduped_unsimplified'])} "
          f"-> simplified {mb(sz['geojson_simplified_total'])} (main {mb(fm)}, CAD {mb(fcad)})")
    for slug, nm, bm, nc, bc in sizes:
        print(f"  {slug:16s} main {nm:5d} feats {bm / 1e3:8.1f} kB   cad {nc:5d} feats {bc / 1e3:8.1f} kB")


if __name__ == "__main__":
    main()
