#!/usr/bin/env python3
"""Match Global Energy Monitor (GEM) hydropower rows to DHPD and Parivesh projects.

Run from the repo root:  python build_gem_data.py   (needs pandas + openpyxl)

Inputs (never modified):
  data/global_energy_monitor/gem_arunachal_hydropower.xlsx            61 Arunachal rows
  data/global_energy_monitor/Global-Hydropower-Tracker-March-2026.xlsx   sheet "Data" (only for Subansiri Lower)
  data/official/dhpd_projects.csv, parivesh_proposals.csv             written by build_official_data.py

Outputs (data/official/):
  gem_projects.csv     one row per GEM site (62 = 61 + Subansiri Lower) with dhpd_id and parivesh_project
  gem_match_table.csv  GEM <-> DHPD match, with match_method and a note (like match_table.csv)

Rule: figures from the three sources are never merged or averaged. This script only
decides which rows are the same dam; every source keeps its own numbers.
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "official"
GEM_AR = ROOT / "data" / "global_energy_monitor" / "gem_arunachal_hydropower.xlsx"
GEM_ALL = ROOT / "data" / "global_energy_monitor" / "Global-Hydropower-Tracker-March-2026.xlsx"

CAP_TOL = 0.05  # capacity gap (share of the larger figure) above which a match is noted

# ------------------------------------------------------------------ manual rules
# gem_unit_id -> (dhpd_id or None, note). Anything here is reported as "manual".
MANUAL = {
    # GEM has two Ranganadi rows at one point. 405 MW (operating) is DHPD's Panyor Lower.
    "405": ("D002", "GEM 'Ranganadi' 405 MW (operating) is DHPD 'Panyor Lower (Ranganadi Stage-I)' 405 MW. Same capacity. This mapping was specified by the analyst, not inferred."),
    "130": (None, "Second GEM 'Ranganadi' row (130 MW, pre-construction) at the same point as the 405 MW plant. No DHPD project is matched to it."),
}
# GEM name (normalised key) -> (dhpd_id, note). Name rule found a candidate but something looks off.
NEEDS_CONFIRM = {
    "upper subansiri": ("D028", "Matched by word order (GEM 'Upper Subansiri' / DHPD 'Subansiri Upper'), but GEM's district is Lower Subansiri and its pin (27.54 N, 93.82 E) is far from the Upper Subansiri area, and capacity differs (1,605 vs 2,000 MW). Please confirm."),
}
# GEM name -> note for rows left unmatched on purpose
UNMATCHED_NOTES = {
    "siang upper": "DHPD has only 'Siang Upper St-II' (matched to GEM 'Siang Upper II'). No DHPD row for the 10,000 MW 'Siang Upper' project.",
    "papu": "Possible DHPD 'Papu Valley' (48 MW, East Kameng) but GEM says 100 MW; not matched. Please confirm if you know they are the same.",
    "phanchung pachi": "Possible DHPD 'Phanchung' (45 MW, West Kameng) but GEM says 36 MW on the Pachi river in East Kameng; not matched. Please confirm.",
    "simang i": "DHPD lists only Simang-II, so there is no DHPD partner.",
    }
# GEM special case outside the Arunachal extract
SPECIAL = {
    "Subansiri Lower hydroelectric plant": "GEM lists this in Assam; the dam sits on the border. Row taken from the full GEM tracker, not the Arunachal extract.",
}
# river -> basin, used ONLY for GEM rows with no DHPD match (matched rows use DHPD's basin)
RIVER_BASIN = {
    "siang river": "Siang", "lohit river": "Lohit", "dibang river": "Dibang",
    "subansiri river": "Subansiri", "tawang river": "Tawang", "tawangchu river": "Tawang",
    "kameng river": "Kameng", "dikrong river": "Dikrong",
}

ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5"}
SUFFIX = re.compile(r"\b(hydroelectric plant|hydro electric project|hydroelectric project|h\.?e\.?p\.?)\s*$", re.I)


def clean_name(s):
    """Strip suffixes, '(NNN MW)' and surrounding spaces. Keeps case for display."""
    s = str(s).strip()
    s = re.sub(r"\(\s*[\d.,]+\s*MW\s*\)", "", s, flags=re.I)
    s = SUFFIX.sub("", s.strip()).strip()
    s = SUFFIX.sub("", s).strip()
    return s


def tokens(s):
    s = clean_name(s).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    out = []
    for t in s.split():
        if t in ("st", "stage"):
            continue
        out.append(ROMAN.get(t, t))
    return out


def key_norm(s):
    return " ".join(tokens(s))


def key_exact(s):
    return clean_name(s).lower().strip()


def key_swap(s):
    return " ".join(sorted(tokens(s)))


def key_compact(s):
    return "".join(tokens(s))


def key_stage1(s):
    """'Oju' -> 'oju 1' so it can meet 'Oju - I' (a lone project is stage 1)."""
    t = tokens(s)
    return " ".join(t if (t and t[-1].isdigit()) else t + ["1"])


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def tidy_district(s):
    if pd.isna(s):
        return ""
    return re.sub(r"\s+district$", "", str(s).strip(), flags=re.I)


def main():
    gem = pd.read_excel(GEM_AR)
    full = pd.read_excel(GEM_ALL, sheet_name="Data")
    sub = full[full["Project Name"] == "Subansiri Lower hydroelectric plant"]
    assert len(sub) == 1, "Subansiri Lower row not found"
    gem = pd.concat([gem, sub], ignore_index=True)
    gem["special_case"] = gem["Project Name"].map(SPECIAL).fillna("")

    dh = pd.read_csv(OUT / "dhpd_projects.csv")
    pv = pd.read_csv(OUT / "parivesh_proposals.csv")
    dh_by_id = dh.set_index("dhpd_id")
    pv_names = sorted(pv["project"].unique())
    pv_by_dhpd = pv.dropna(subset=["dhpd_id"]).groupby("dhpd_id")["project"].first().to_dict()

    # lookup tables over DHPD names, one per rule, in order of strictness
    rules = [
        ("exact", key_exact),
        ("normalised", key_norm),
        ("normalised", key_swap),       # word-order swap
        ("normalised", key_compact),    # 'Mago Chu' = 'Magochu'
        ("normalised", key_stage1),     # 'Oju' = 'Oju - I'
    ]
    rule_names = ["exact", "stage/roman/punctuation", "word order swap", "spaces removed", "lone project = stage I"]
    tables = []
    for (m, f), rn in zip(rules, rule_names):
        t = {}
        for _, r in dh.iterrows():
            t.setdefault(f(r["project"]), []).append(r["dhpd_id"])
        tables.append((m, f, rn, t))
    # DHPD names also need the (NNN MW)/stage variants for the stage1 rule to compare fairly
    used = {}  # dhpd_id -> gem_unit_id, to refuse double matches

    rows, proj = [], []
    for _, g in gem.iterrows():
        gid = str(g["GEM unit ID"])
        name = clean_name(g["Project Name"])
        cap = num(g["Capacity (MW)"])
        did, method, note = None, "unmatched", ""
        nk = key_norm(g["Project Name"])
        mw = None
        # manual overrides keyed by capacity for the two Ranganadi rows
        mkey = str(int(cap)) if nk == "ranganadi" else None
        if mkey in MANUAL:
            did, note = MANUAL[mkey]
            method = "manual" if did else "unmatched"
        elif nk in NEEDS_CONFIRM:
            did, note = NEEDS_CONFIRM[nk]
            method = "manual"
        elif nk in UNMATCHED_NOTES:
            note = UNMATCHED_NOTES[nk]
        else:
            for m, f, rn, t in tables:
                hits = t.get(f(g["Project Name"]), [])
                hits = [h for h in hits if h not in used]
                if len(hits) == 1:
                    did, method = hits[0], m
                    if m != "exact":
                        note = f"Name matched by rule: {rn}."
                    break
                if len(hits) > 1:
                    note = f"Several DHPD names fit ({', '.join(hits)}); not forced."
                    break
        if did:
            used[did] = gid
            d = dh_by_id.loc[did]
            dcap = float(d["capacity_mw"])
            gap = abs(cap - dcap) / max(cap, dcap) if cap and dcap else None
            extra = []
            if gap is not None and gap > CAP_TOL:
                extra.append(f"Capacity differs: GEM {cap:g} MW, DHPD {dcap:g} MW ({gap*100:.0f}% gap).")
            gd, dd = tidy_district(g["Major Area 1"]), str(d["district"])
            if gd and dd and gd.lower() not in dd.lower() and dd.lower() not in gd.lower():
                extra.append(f"District differs: GEM '{gd}', DHPD '{dd}'.")
            note = " ".join(x for x in [note] + extra if x)
        # Parivesh: through DHPD id, otherwise a direct name match to a Parivesh-only project
        pvp = pv_by_dhpd.get(did, "") if did else ""
        if not did:
            for pn in pv_names:
                if key_norm(pn) == nk or key_compact(pn) == key_compact(g["Project Name"]):
                    pvp = pn
                    note = (note + " " if note else "") + f"Parivesh project '{pn}' matched to GEM by name (not on DHPD)."
                    break
        if g["special_case"]:
            note = (g["special_case"] + " " + note).strip()
        river = "" if pd.isna(g["River / Watercourse"]) else str(g["River / Watercourse"])
        if did:
            basin, bsrc = str(dh_by_id.loc[did, "basin"]), "dhpd"
        elif river.lower() in RIVER_BASIN:
            basin, bsrc = RIVER_BASIN[river.lower()], "gem_river"
        else:
            basin, bsrc = "Not stated", "none"
        dstat = str(dh_by_id.loc[did, "dhpd_status"]) if did else ""
        rows.append({
            "gem_unit_id": gid, "gem_project": name, "gem_status": g["Status"], "gem_capacity_mw": cap,
            "dhpd_id": did or "", "dhpd_project": str(dh_by_id.loc[did, "project"]).strip() if did else "",
            "dhpd_capacity_mw": float(dh_by_id.loc[did, "capacity_mw"]) if did else "",
            "dhpd_status": dstat, "parivesh_project": pvp,
            "match_method": method, "side": "both" if did else "gem_only", "notes": note,
        })
        proj.append({
            "gem_unit_id": gid, "gem_location_id": g["GEM location ID"], "name": name,
            "other_names": "" if pd.isna(g["Other name(s)"]) else g["Other name(s)"],
            "capacity_mw": cap, "status": g["Status"],
            "start_year": "" if pd.isna(g["Start Year"]) else int(g["Start Year"]),
            "turbines": "" if pd.isna(g["Turbines"]) else g["Turbines"],
            "owner": "" if pd.isna(g["Owner"]) else g["Owner"],
            "operator": "" if pd.isna(g["Operator"]) else g["Operator"],
            "technology": "" if pd.isna(g["Technology Type"]) else g["Technology Type"],
            "river": river, "latitude": g["Latitude"], "longitude": g["Longitude"],
            "location_accuracy": g["Location Accuracy"],
            "district": tidy_district(g["Major Area 1"]), "state": g["State/Province 1"],
            "date_last_researched": pd.Timestamp(g["Date Last Researched"]).date().isoformat(),
            "wiki_url": g["Wiki URL"],
            "dhpd_id": did or "", "parivesh_project": pvp,
            "basin": basin, "basin_source": bsrc, "special_case": g["special_case"],
        })

    # DHPD rows with no GEM partner
    matched = {r["dhpd_id"] for r in rows if r["dhpd_id"]}
    for _, d in dh.iterrows():
        if d["dhpd_id"] not in matched:
            rows.append({
                "gem_unit_id": "", "gem_project": "", "gem_status": "", "gem_capacity_mw": "",
                "dhpd_id": d["dhpd_id"], "dhpd_project": str(d["project"]).strip(),
                "dhpd_capacity_mw": float(d["capacity_mw"]), "dhpd_status": d["dhpd_status"],
                "parivesh_project": pv_by_dhpd.get(d["dhpd_id"], ""),
                "match_method": "unmatched", "side": "dhpd_only",
                "notes": "No GEM row matched to this DHPD project.",
            })

    mt = pd.DataFrame(rows)
    gp = pd.DataFrame(proj)
    mt.to_csv(OUT / "gem_match_table.csv", index=False)
    gp.to_csv(OUT / "gem_projects.csv", index=False)

    # ---- reconciliation
    n_gem = len(gp)
    n_match = int((gp["dhpd_id"] != "").sum())
    by_m = mt[mt["side"] == "both"]["match_method"].value_counts().to_dict()
    dhpd_only = int((mt["side"] == "dhpd_only").sum())
    pv_all = set(pv["project"])
    pv_on_gem = set(gp.loc[gp["parivesh_project"] != "", "parivesh_project"])
    print("\nReconciliation (GEM / DHPD / Parivesh)")
    print("-" * 52)
    print(f"GEM rows (61 Arunachal + Subansiri Lower)     {n_gem:>4}")
    print(f"  matched to a DHPD project                   {n_match:>4}   {by_m}")
    print(f"  GEM only (no DHPD match)                    {n_gem - n_match:>4}")
    print(f"DHPD projects                                 {len(dh):>4}")
    print(f"  with a GEM partner                          {len(dh) - dhpd_only:>4}")
    print(f"  DHPD only (no GEM row)                      {dhpd_only:>4}")
    print(f"Parivesh projects                             {len(pv_all):>4}")
    print(f"  on the map via GEM                          {len(pv_on_gem):>4}")
    print(f"  not on the map                              {len(pv_all - pv_on_gem):>4}   {sorted(pv_all - pv_on_gem)}")
    assert n_gem == 62 and len(dh) - dhpd_only == n_match
    print("\nRows to confirm (manual / unmatched GEM):")
    for _, r in mt[(mt["side"] != "dhpd_only") & (mt["match_method"] != "exact") & (mt["match_method"] != "normalised")].iterrows():
        print(f"  [{r['match_method']}] {r['gem_project']} ({r['gem_capacity_mw']:g} MW): {r['notes']}")


if __name__ == "__main__":
    main()
