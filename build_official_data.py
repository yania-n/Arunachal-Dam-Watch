#!/usr/bin/env python3
"""Build the data behind index_v2.html (official data only: DHPD + Parivesh).

Run from the repo root:  python build_official_data.py

Inputs (never modified):
  DHPD/all_projects.xlsx                          113 projects, capacity, developer, district, basin
  DHPD/data&exploration/<status folders>/*.xlsx   original portal downloads (used only to rebuild status)
  parivesh/hydel_only_merged_final.xlsx           36 forest-clearance proposals

Outputs (data/official/):
  dhpd_projects.csv, parivesh_proposals.csv, match_table.csv,
  inconsistencies.csv, corrections_log.csv, summary.json

Rule of the page: power capacity is from DHPD only; forest clearance data is from
Parivesh only. The two sources are never merged or averaged.
"""
import glob
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "official"
DHPD_ALL = ROOT / "DHPD" / "all_projects.xlsx"
DHPD_DL = ROOT / "DHPD" / "data&exploration"
PARIVESH = ROOT / "parivesh" / "hydel_only_merged_final.xlsx"

DHPD_PULL = "2026-11-14"        # file names dhpdap-online-2026-11-14-*.xlsx
PARIVESH_PULL = "2026-11-07"    # parivesh/data&exploration notebook: "as on 7th November 2026"

# ---------------------------------------------------------------- corrections
SPELLING = {"Nyikgong": "Nyikong"}          # correction 1 (Parivesh spelling -> "Nyikong")
# correction 2 (New Melling capacity) needs no code: DHPD's 96 MW is simply the value used.

# ---------------------------------------------------------------- manual matches
# Every manual match is listed in match_table.csv. Key = Parivesh display name, value = DHPD name.
MANUAL_MATCH = {
    "Lower Siang": "Siang Lower",   # same capacity (2700 MW), Jaypee / Jaiprakash, name word order differs
    "Nyikong": "Nyikong",           # Parivesh "Nyikgong" (spelling) -> DHPD "Nyikong"
}

STATUS_NORM = {
    "approved": "Approved", "closed": "Closed", "in-principle": "In-principle",
    "dfo": "DFO", "nodal officer": "Nodal Officer", "pending with-sg": "Pending With-SG",
    "rejected": "Rejected", "returned": "Returned", "withdrawn": "Withdrawn",
}
STATUS_GROUP = {
    "Approved": "cleared", "Closed": "cleared",
    "In-principle": "in_principle",
    "DFO": "in_progress", "Nodal Officer": "in_progress", "Pending With-SG": "in_progress",
    "Rejected": "rejected", "Returned": "rejected", "Withdrawn": "rejected",
}
GROUPS = ["cleared", "in_principle", "in_progress", "rejected"]

DISTRICT_NAMES = ["EAST SIANG", "WEST SIANG", "UPPER SIANG", "LOWER SIANG", "WEST KAMENG",
                  "EAST KAMENG", "LOWER SUBANSIRI", "UPPER SUBANSIRI", "PAPUM PARE", "PAPUMPARE",
                  "LOWER DIBANG VALLEY", "DIBANG VALLEY", "TAWANG", "ANJAW", "LOHIT",
                  "KURUNG KUMEY", "KRA DAADI"]


def num(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).replace(",", "").strip()
    if s == "" or s.lower() in ("nan", "none", "not available"):
        return None
    return float(s)


def fmt(x, nd=2):
    return "not available" if x is None else (f"{x:,.{nd}f}".rstrip("0").rstrip(".") if nd else f"{x:,.0f}")


def key(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


# =============================================================== DHPD
def build_dhpd():
    allp = pd.read_excel(DHPD_ALL)
    allp.columns = ["project_name", "capacity_mw", "developer_agency", "district", "basin"]

    # rebuild status from the original downloads (same recipe as dhpd_exploration.ipynb)
    parts = []
    for status, folder in [("Completed", "completed_projects"),
                           ("Under construction", "under_construction"),
                           ("Under implementation", "under_implementation")]:
        for f in sorted(glob.glob(str(DHPD_DL / folder / "*.xlsx"))):
            d = pd.read_excel(f)
            d = d.rename(columns={"capacity_(mw)": "capacity_mw", "District": "district"})
            d["capacity_mw"] = pd.to_numeric(d["capacity_mw"].astype("string").str.replace(",", "", regex=False))
            d["dhpd_status"] = status
            d["basin_from_portal"] = "basin" in d.columns
            parts.append(d[["project_name", "capacity_mw", "developer_agency", "district", "dhpd_status", "basin_from_portal"]])
    dl = pd.concat(parts, ignore_index=True)

    allp["_k"] = allp.apply(lambda r: (r.project_name, round(r.capacity_mw, 3), r.developer_agency, r.district), axis=1)
    dl["_k"] = dl.apply(lambda r: (r.project_name, round(r.capacity_mw, 3), r.developer_agency, r.district), axis=1)
    if dl["_k"].duplicated().any() or len(dl) != len(allp):
        sys.exit("DHPD status rebuild is not one-to-one with all_projects.xlsx")
    m = allp.merge(dl[["_k", "dhpd_status", "basin_from_portal"]], on="_k", how="left", validate="one_to_one")
    if m["dhpd_status"].isna().any():
        sys.exit("Some DHPD projects could not be given a status")
    m["basin_source"] = m["basin_from_portal"].map({True: "portal", False: "derived by district rule (dhpd_exploration.ipynb)"})
    m.insert(0, "dhpd_id", [f"D{i + 1:03d}" for i in range(len(m))])
    return m.drop(columns=["_k", "basin_from_portal"])


# =============================================================== Parivesh
def build_parivesh():
    raw = pd.read_excel(PARIVESH, dtype=str)
    rows = []
    for _, r in raw.iterrows():
        g = lambda c: (None if pd.isna(r.get(c)) else str(r.get(c)).strip())
        proj_raw = g("Project") or ""
        disp = re.sub(r"\s*(HEP|Hydro ?Electric(?: Power)? Project|Small Hydro Project)\b.*$", "", proj_raw, flags=re.I).strip()
        disp = SPELLING.get(disp, disp)
        cap = re.search(r"\(\s*([\d.]+)\s*MW\s*\)", proj_raw, flags=re.I)
        st_raw = g("Current_Project_Status")
        st = STATUS_NORM[st_raw.lower()]
        pname = (g("Proposal_Name") or "").strip('" ')
        s2 = g("Stage_II_Date")
        s2_flag = ""
        s2_out = s2
        if s2 and s2.startswith("02 Jan 1900"):
            s2_out, s2_flag = None, "placeholder 02 Jan 1900"
        elif s2 and STATUS_GROUP[st] == "rejected":
            s2_flag = "Stage_II_Date on a rejected/returned/withdrawn proposal"
        if s2_out and s2_out.lower() == "not available":
            s2_out = None
        dist = g("District")
        dist_text = ""
        if not dist:
            up = re.sub(r"KAMEING", "KAMENG", pname.upper())
            segs = re.findall(r"(?<![A-Z])IN\s+([A-Z][A-Z ,&.]{2,80}?)\s+DIST", up) + re.findall(r"(?<![A-Z])AT\s+([A-Z ]{3,30})", up)
            seg = " | ".join(segs)
            hits = []
            for name in DISTRICT_NAMES:
                if name in seg and not any(name in h for h in hits):
                    hits.append(name)
            dist_text = ", ".join(h.title() for h in hits)
        rows.append(dict(
            proposal_no=g("Proposal_No"), year_of_submission=g("Year_of_Submission"),
            project_raw=proj_raw, project=disp, proposal_name=pname,
            user_agency=(g("User_Agency_Name") or "").strip('" '),
            area_applied_ha=num(g("Area_Applied")), area_diverted_ha=num(g("Area_Diverted")),
            area_diverted_raw=g("Area_Diverted"),
            status_raw=st_raw, status=st, status_group=STATUS_GROUP[st],
            ua_submission_date=g("UA_Submission_Date"),
            stage_i_date=g("Stage_I_Date"), stage_ii_date=s2_out, stage_ii_flag=s2_flag,
            district=dist, district_in_proposal_text=dist_text, division=g("Division"),
            capacity_in_name_mw=float(cap.group(1)) if cap else None,
            ancillary=bool(re.match(r"\s*CHANGE IN LOCATION", pname, flags=re.I)),
        ))
    p = pd.DataFrame(rows)
    p["_sub"] = pd.to_datetime(p["ua_submission_date"], format="%d %b %Y", errors="coerce")

    # ---- refiling rule -------------------------------------------------------
    # 1. Group proposals by project.
    # 2. Ancillary proposals ("CHANGE IN LOCATION ..." quarry patches) add their own area.
    # 3. Of the remaining (full) proposals only the LATEST by UA_Submission_Date counts;
    #    earlier ones are "superseded" and their area is not counted again.
    p["role"] = "primary"
    p["superseded_by"] = ""
    for proj, grp in p.groupby("project"):
        full = grp[~grp.ancillary].sort_values("_sub")
        if len(full) > 1:
            last = full.iloc[-1]
            for idx in full.index[:-1]:
                p.loc[idx, "role"] = "superseded"
                p.loc[idx, "superseded_by"] = last.proposal_no
        for idx in grp[grp.ancillary].index:
            p.loc[idx, "role"] = "ancillary"
    p["counted_in_project_area"] = p["role"] != "superseded"
    p["ua_submission_iso"] = p["_sub"].dt.strftime("%Y-%m-%d")
    return p.drop(columns=["_sub"])


# =============================================================== developer comparison
CITY = {"shillong", "hyderabad", "hydrabad", "delhi", "new", "faridabad", "mumbai", "navi", "gurgaon",
        "haryana", "bhubaneswar", "kolkata", "guwahati", "itanagar", "namsai", "vishakapatnam",
        "secunderabad", "andhra", "pradesh", "arunachal", "himachal"}
STOP = {"m", "s", "ms", "pvt", "ltd", "limited", "private", "co", "company", "and", "the", "of",
        "spv", "p"}


def dev_tokens(s):
    s = re.sub(r"[&/.,()]", " ", str(s).lower())
    toks = [t for t in s.split() if t not in STOP]
    core = [t for t in toks if t not in CITY]
    return core or toks


def dev_differs(a, b):
    ta, tb = dev_tokens(a), dev_tokens(b)
    if not ta or not tb:
        return False
    sa, sb = set(ta), set(tb)
    jacc = len(sa & sb) / len(sa | sb)
    return jacc < 0.5 and not (sa <= sb or sb <= sa)


# =============================================================== main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dh = build_dhpd()
    pv = build_parivesh()

    # ---------------------------------------------------------- matching
    dh["_k"] = dh.project_name.map(key)
    if dh["_k"].duplicated().any():
        sys.exit("duplicate normalised DHPD names")
    pv_proj = pv.groupby("project", sort=False)
    match = []  # list of dicts
    used = set()
    for proj, grp in pv_proj:
        method, note, hit = None, "", None
        if proj in MANUAL_MATCH:
            hit = dh[dh.project_name == MANUAL_MATCH[proj]]
            method = "manual"
            note = {"Lower Siang": "Name differs in word order (Parivesh 'Lower Siang' / DHPD 'Siang Lower'). Same capacity 2,700 MW; Jaypee Arunachal Power / Jaiprakash Associates. Please confirm.",
                    "Nyikong": "Parivesh spells it 'Nyikgong'; the page uses 'Nyikong' (corrections log). Please confirm."}[proj]
        else:
            h = dh[dh.project_name.str.strip().str.lower() == proj.lower()]
            if len(h) == 1:
                hit, method = h, "exact"
            else:
                h = dh[dh._k == key(proj)]
                if len(h) == 1:
                    hit, method = h, "normalised"
                    note = "Matched after ignoring spaces/punctuation."
        if hit is not None and len(hit) == 1:
            d = hit.iloc[0]
            used.add(d.dhpd_id)
            match.append(dict(dhpd_id=d.dhpd_id, dhpd_project=d.project_name, dhpd_status=d.dhpd_status,
                              parivesh_project=proj, n_proposals=len(grp),
                              proposal_nos="; ".join(grp.proposal_no), match_method=method, side="both", notes=note))
        else:
            match.append(dict(dhpd_id="", dhpd_project="", dhpd_status="", parivesh_project=proj,
                              n_proposals=len(grp), proposal_nos="; ".join(grp.proposal_no),
                              match_method="unmatched", side="parivesh_only",
                              expected_absence=bool((grp.status_group == "rejected").all()),
                              notes=("No DHPD project with this name; not forced. Every request for this project was turned down "
                                     "(rejected, returned or withdrawn), so its absence from DHPD is expected and is not treated as a difference."
                                     if bool((grp.status_group == "rejected").all()) else "No DHPD project with this name; not forced.")))
    for _, d in dh.iterrows():
        if d.dhpd_id not in used:
            match.append(dict(dhpd_id=d.dhpd_id, dhpd_project=d.project_name, dhpd_status=d.dhpd_status,
                              parivesh_project="", n_proposals=0, proposal_nos="", match_method="unmatched",
                              side="dhpd_only", notes="No Parivesh proposal with this name; not forced."))
    mt = pd.DataFrame(match)
    mt["expected_absence"] = mt["expected_absence"].fillna(False).astype(bool)
    both = mt[mt.side == "both"]
    pv["dhpd_id"] = pv.project.map(dict(zip(both.parivesh_project, both.dhpd_id))).fillna("")
    dmap = dh.set_index("dhpd_id")

    # ---------------------------------------------------------- corrections log
    corr = pd.DataFrame([
        dict(project="Nyikong", field="project name (spelling)", dhpd_value="Nyikong", parivesh_value="Nyikgong",
             value_shown="Nyikong", reason="Spelling unified to 'Nyikong' everywhere (project owner's correction). Change made."),
        dict(project="New Melling", field="capacity (MW)", dhpd_value="96", parivesh_value="90 (from Parivesh project name)",
             value_shown="96 (DHPD)", reason="All capacity comes from DHPD; the 90 MW in the Parivesh name is not used. Change made."),
        dict(project="Yammeng", field="district", dhpd_value="Lower Siang", parivesh_value="Upper Siang",
             value_shown="Lower Siang (DHPD)", reason="Not changed, see inconsistencies. Project owner's note: Upper Siang district / Siang basin is correct."),
        dict(project="Halaipani", field="district", dhpd_value="Lohit", parivesh_value="Anjaw",
             value_shown="Lohit (DHPD)", reason="Not changed, see inconsistencies. Project owner's note: Anjaw district / Lohit basin is correct."),
    ])

    # ---------------------------------------------------------- inconsistencies
    inc = []

    def add(group, sub, project, dv, pvv, shown, note, dstatus=""):
        inc.append(dict(group=group, subgroup=sub, project=project, dhpd_value=dv, parivesh_value=pvv,
                        value_shown=shown, note=note, dhpd_status=dstatus))

    # --- A coverage
    for _, r in mt[mt.side == "dhpd_only"].iterrows():
        d = dmap.loc[r.dhpd_id]
        note = "No Parivesh record under this name."
        if d.project_name == "Dibang Multipurpose":
            note += " Also noted in parivesh/data&exploration notebook."
        if d.project_name.startswith("Debra"):
            note += " DHPD groups four small HEPs in one row; names were not searched individually."
        add("A", f"DHPD project with no Parivesh record ({d.dhpd_status.lower()})", d.project_name,
            f"{fmt(d.capacity_mw)} MW, {d.dhpd_status}", "no record", f"{fmt(d.capacity_mw)} MW (DHPD)", note, d.dhpd_status)
    for _, r in mt[(mt.side == "parivesh_only") & (~mt.expected_absence)].iterrows():
        g = pv[pv.project == r.parivesh_project]
        capn = g.capacity_in_name_mw.dropna()
        area = g[g.counted_in_project_area].area_applied_ha.sum()
        add("A", "Parivesh project with no DHPD entry", r.parivesh_project, "no entry",
            f"{fmt(area)} ha applied; {', '.join(g.status.unique())}" + (f"; {fmt(capn.iloc[0])} MW in name" if len(capn) else ""),
            "no DHPD capacity (not shown)",
            "Capacity in the Parivesh name is not used on this page." if len(capn) else "No capacity figure available.")

    # --- B attribute mismatches (matched projects only)
    OWNER = {"Yammeng": "Project owner's note: Upper Siang district / Siang basin is correct. DHPD value NOT changed.",
             "Halaipani": "Project owner's note: Anjaw district / Lohit basin is correct. DHPD value NOT changed."}
    for _, m in both.iterrows():
        d = dmap.loc[m.dhpd_id]
        g = pv[pv.project == m.parivesh_project]
        # capacity
        for _, pr in g.iterrows():
            c = pr.capacity_in_name_mw
            if pd.notna(c) and abs(c - d.capacity_mw) > 1e-9:
                extra = ""
                if m.parivesh_project == "Ressing":
                    extra = " This is the earlier (withdrawn) filing; the later filing is named 12 MW, which matches DHPD."
                if m.parivesh_project == "New Melling":
                    extra = " Corrected on this page: DHPD's 96 MW is used (corrections log)."
                add("B", "Capacity (DHPD value is used)", d.project_name, f"{fmt(d.capacity_mw)} MW",
                    f"{fmt(c)} MW (in name of {pr.proposal_no})", f"{fmt(d.capacity_mw)} MW (DHPD)",
                    "Parivesh capacity is parsed from the project name." + extra, d.dhpd_status)
        # district
        pdist = [x for x in g.district.dropna().unique() if x]
        shown = f"{d.district} (DHPD)"
        if pdist:
            pd_ = pdist[0]
            if key(pd_) != key(d.district):
                naming = (key(pd_), key(d.district)) in {(key("Kra Daadi"), key("Kurung Kumey"))}
                note = OWNER.get(d.project_name, "")
                if naming:
                    note = "Naming: Kra Daadi and Kurung Kumey appear to be the same area under different district names; DHPD value shown."
                elif not note and key(pd_) == key("Dibang Valley"):
                    note = "'Dibang Valley' and 'Lower Dibang Valley' are different district names; the data does not say which is meant."
                add("B", "District, Parivesh District field" + (" (naming)" if naming else ""), d.project_name,
                    f"{d.district} (basin {d.basin})", pd_, shown, note or "DHPD value shown unchanged.", d.dhpd_status)
        else:
            txt = [x for x in g.district_in_proposal_text.unique() if x]
            if txt:
                names = [t.strip() for t in txt[0].split(",")]
                if key(d.district) not in [key(n) for n in names]:
                    add("B", "District named in proposal text (Parivesh District field is empty)", d.project_name,
                        f"{d.district} (basin {d.basin})", f"{txt[0]} (from proposal text)", shown,
                        "Parivesh District field is empty for this proposal; district read from the proposal title text. DHPD value shown unchanged.", d.dhpd_status)
        # developer
        pa = g.sort_values("ua_submission_iso").iloc[-1].user_agency
        if dev_differs(d.developer_agency, pa):
            add("B", "Developer / applicant name", d.project_name, d.developer_agency, pa,
                f"{d.developer_agency} (DHPD)",
                "Different company names, not punctuation (an applicant company can be a project subsidiary; the data does not say).", d.dhpd_status)
        # project name spelling
        raws = {re.sub(r"\s*(HEP|Hydro ?Electric(?: Power)? Project|Small Hydro Project)\b.*$", "", x, flags=re.I).strip()
                for x in g.project_raw}
        for rw in raws:
            if rw != m.parivesh_project and rw.lower() != d.project_name.lower() and key(rw) != key(d.project_name):
                add("B", "Project name spelling", m.parivesh_project, d.project_name, rw, m.parivesh_project if m.parivesh_project == d.project_name else d.project_name,
                    "Spelling differs between the sites; page uses the DHPD / corrected spelling.", d.dhpd_status)
    # name spelled differently only by spaces (matched as 'normalised') or by word order (manual)
    for _, m in both[both.match_method.isin(["normalised", "manual"])].iterrows():
        if m.parivesh_project == "Nyikong":
            continue  # already listed via raw-name check above
        if m.match_method == "manual" or m.parivesh_project != m.dhpd_project:
            add("B", "Project name spelling", m.dhpd_project, m.dhpd_project, m.parivesh_project, m.dhpd_project,
                m.notes, m.dhpd_status)

    # --- C status conflicts
    for _, m in both.iterrows():
        g = pv[pv.project == m.parivesh_project]
        if set(g.status_group) == {"rejected"} and m.dhpd_status != "Completed":
            hist = "; ".join(f"{r.proposal_no} {r.status}" for _, r in g.sort_values("ua_submission_iso").iterrows())
            add("C", "DHPD active, Parivesh rejected", m.dhpd_project, f"{m.dhpd_status}", f"Rejected group ({hist})",
                "Both shown as they are", "No later approved or in-principle filing in the Parivesh file. Closed would count as approved, not a conflict.",
                m.dhpd_status)
        elif set(g.status_group) == {"rejected"}:
            add("C", "DHPD completed, Parivesh rejected", m.dhpd_project, m.dhpd_status, "Rejected group", "Both shown as they are", "", m.dhpd_status)

    # --- D Parivesh internal
    multi = pv.groupby("project").filter(lambda x: len(x) > 1)
    for proj, g in multi.groupby("project", sort=False):
        parts = []
        for _, r in g.sort_values("ua_submission_iso").iterrows():
            parts.append(f"{r.proposal_no} ({r.status}, {fmt(r.area_applied_ha, 3)} ha, {r.role})")
        add("D", "Refilings / multiple proposals", proj, "not applicable", " + ".join(parts),
            f"{fmt(g[g.counted_in_project_area].area_applied_ha.sum(), 3)} ha counted at project level",
            "Refiling rule on the Method section.")
    for _, r in pv[pv.stage_ii_flag.str.startswith("placeholder")].iterrows():
        add("D", "Placeholder date (02 Jan 1900)", r.project, "not applicable",
            f"{r.proposal_no}: Stage_II_Date = 02 Jan 1900 ({r.status})", "date left blank", "Placeholder for 'no date'; not treated as an approval date.")
    for _, r in pv[pv.stage_ii_flag.str.startswith("Stage_II")].iterrows():
        add("D", "Rejected row with a Stage_II_Date", r.project, "not applicable",
            f"{r.proposal_no}: {r.status}, Stage_II_Date = {r.stage_ii_date}", "date shown, not read as approval",
            "Stage_II_Date on a rejected/returned/withdrawn row is not an approval date.")
    for _, r in pv[(pv.status_group == "cleared") & ((pv.area_diverted_ha.isna()) | (pv.area_diverted_ha == 0))].iterrows():
        add("D", "Approved/Closed with Area_Diverted 0 or empty", r.project, "not applicable",
            f"{r.proposal_no}: {r.status}, Area_Diverted = {'empty' if pd.isna(r.area_diverted_ha) else '0'}, Area_Applied = {fmt(r.area_applied_ha)} ha",
            "Area_Diverted not used", "Area_Diverted is never presented as forest cleared on the ground.")
    dv = pv[(pv.status_group != "cleared") & pv.area_diverted_ha.notna() & (pv.area_diverted_ha > 0)]
    add("D", "Area_Diverted filled on proposals that are not approved", f"{len(dv)} proposals", "not applicable",
        f"{len(dv)} of {int((pv.status_group != 'cleared').sum())} non-cleared proposals have Area_Diverted > 0",
        "Area_Diverted not used", "Area_Diverted is not a measure of land actually diverted. Not used on this page.")
    add("D", "Area stored as text", f"all {len(pv)} proposals", "not applicable",
        "Area_Applied / Area_Diverted are text in the Excel file", "converted to numbers (ha)", "Converted without changing values.")
    nvar = pv[pv.status_raw != pv.status]
    add("D", "Inconsistent status case", f"{len(nvar)} proposals", "not applicable",
        "; ".join(sorted(set(f"{a} / {b}" for a, b in zip(nvar.status_raw, nvar.status)))),
        "normalised (e.g. Rejected)", "Case normalised only; no status was changed.")

    # --- E DHPD internal
    rule_dist = dh[dh.basin_source != "portal"]
    for _, r in rule_dist.iterrows():
        extra = " Exception rule for projects named 'Emra' in Lohit/Anjaw." if r.project_name.lower().startswith("emra") else ""
        add("E", "Basin derived by district rule (under implementation)", r.project_name, f"{r.district} -> {r.basin}",
            "not available (Parivesh has no basin)", f"{r.basin} (DHPD file)",
            "The portal export has no basin for under-implementation projects; basin was assigned from the district in dhpd_exploration.ipynb." + extra, r.dhpd_status)
    # developer spelling variants: same company, several strings
    def company(s):
        t = dev_tokens(s)
        return t[0] if t else ""
    dd = dh.assign(co=dh.developer_agency.map(company))
    for co, g in dd.groupby("co"):
        variants = sorted(set(g.developer_agency))
        if len(variants) > 1:
            add("E", "Developer name written several ways (same lead name)", f"{len(g)} projects ({co})", "; ".join(f"'{v}'" for v in variants),
                "not applicable", "as in DHPD", "Same lead name, written several ways (spacing, punctuation, city appended, or a different suffix). May be one company or related companies; the data does not say.")
    cities = re.compile(r"(shillong|hyderabad|hydrabad|new delhi|faridabad|navi mumbai|mumbai|gurgaon|haryana|bhubaneswar|kolkata|guwahati|itanagar|namsai|vishakapatnam|secunderabad|andhra pradesh|arunachal pradesh|himachal pradesh)\.?\s*$", re.I)
    withcity = dh[dh.developer_agency.map(lambda s: bool(cities.search(str(s).strip())))]
    add("E", "Trailing city / state in developer name", f"{len(withcity)} of {len(dh)} projects", "e.g. 'NEEPCO Ltd. Shillong'",
        "not applicable", "as in DHPD", "Place name is appended to the company name in the developer field.")
    for typo, ex in [("Costal", "Costal Projects Pvt. Ltd. Bhubaneswar"), ("Hydrabad", "Aswani Power projects Pvt Ltd. Hydrabad"),
                     ("Vishakapatnam", "Coastal Infrastructure Pvt. Ltd.  Vishakapatnam"), ("Infrastructructure", "Ibuilt Infrastructructure ,  Arunachal Pradesh")]:
        hits = dh[dh.developer_agency.str.contains(typo, case=False)]
        if len(hits):
            add("E", "Possible typo in developer name", ", ".join(hits.project_name.head(4)) + (" ..." if len(hits) > 4 else ""),
                f"'{ex}'", "not applicable", "as in DHPD", f"Contains '{typo}'; looks like a spelling variant, left as is.")
    for _, r in dh[dh.project_name.str.contains(",")].iterrows():
        add("E", "Grouped entry (several projects in one row)", r.project_name, f"{fmt(r.capacity_mw)} MW in one row", "not applicable",
            f"{fmt(r.capacity_mw)} MW (DHPD, one row)", "Four small HEPs are listed as one DHPD project.", r.dhpd_status)
    # portal basin vs district rule, for rows where the portal gave a basin
    def rule(d, name):
        dl = d.lower()
        if "siang" in dl: b = "Siang"
        elif "subansiri" in dl: b = "Subansiri"
        elif re.search(r"pare|kurung", dl): b = "Dikrong"
        elif "dibang" in dl: b = "Dibang"
        elif re.search(r"kameng|pakke", dl): b = "Kameng"
        elif "tawang" in dl: b = "Tawang"
        elif "tirap" in dl: b = "Tirap"
        elif re.search(r"lohit|anjaw", dl): b = "Lohit"
        else: b = None
        if re.search(r"lohit|anjaw", dl) and "emra" in name.lower(): b = "Dibang"
        return b
    for _, r in dh[dh.basin_source == "portal"].iterrows():
        rb = rule(r.district, r.project_name)
        if rb != r.basin:
            add("E", "Portal basin differs from the district rule", r.project_name, f"{r.district}: portal basin {r.basin}",
                "not applicable", f"{r.basin} (DHPD)", f"The district rule used for under-implementation projects would give {rb}; shows the rule is not a safe proxy.", r.dhpd_status)

    # --- F changes made
    add("F", "Spelling", "Nyikong", "Nyikong", "Nyikgong", "Nyikong", "Parivesh spelling changed to Nyikong (corrections log).", "")
    add("F", "Capacity", "New Melling", "96 MW", "90 MW (in name)", "96 MW (DHPD)", "DHPD capacity used (corrections log).", "")
    ic = pd.DataFrame(inc)
    ic["dhpd_status"] = ic.dhpd_status.fillna("")
    # attach DHPD status to F rows
    ic.loc[(ic.group == "F") & (ic.project == "Nyikong"), "dhpd_status"] = dh[dh.project_name == "Nyikong"].dhpd_status.iloc[0]
    ic.loc[(ic.group == "F") & (ic.project == "New Melling"), "dhpd_status"] = dh[dh.project_name == "New Melling"].dhpd_status.iloc[0]

    # ---------------------------------------------------------- aggregates
    cnt = pv.counted_in_project_area
    def by_group(df):
        return {g: round(float(df[df.status_group == g].area_applied_ha.sum()), 3) for g in GROUPS}
    raw_by = {g: dict(ha=round(float(pv[pv.status_group == g].area_applied_ha.sum()), 3),
                      proposals=int((pv.status_group == g).sum())) for g in GROUPS}
    proj_by = {g: dict(ha=round(float(pv[cnt & (pv.status_group == g)].area_applied_ha.sum()), 3),
                       proposals_counted=int((cnt & (pv.status_group == g)).sum())) for g in GROUPS}

    def area_by(col):
        out = {}
        for _, r in pv[cnt].iterrows():
            if r.dhpd_id:
                lab = dmap.loc[r.dhpd_id, col]
            else:
                lab = "Not in DHPD"
            o = out.setdefault(lab, dict(label=lab, projects=set(), applied_ha=0.0, **{g: 0.0 for g in GROUPS}))
            o["projects"].add(r.project)
            o["applied_ha"] += r.area_applied_ha
            o[r.status_group] += r.area_applied_ha
        res = []
        for o in out.values():
            o["projects"] = sorted(o["projects"])
            for k in ["applied_ha"] + GROUPS:
                o[k] = round(o[k], 3)
            res.append(o)
        return sorted(res, key=lambda x: -x["applied_ha"])

    stat = {}
    for s, g in dh.groupby("dhpd_status"):
        stat[s] = dict(projects=int(len(g)), capacity_mw=round(float(g.capacity_mw.sum()), 3))
    summary = dict(
        dhpd_pull=DHPD_PULL, parivesh_pull=PARIVESH_PULL,
        dhpd=dict(projects=int(len(dh)), capacity_mw=round(float(dh.capacity_mw.sum()), 3), by_status=stat),
        parivesh=dict(proposals=int(len(pv)), distinct_projects=int(pv.project.nunique()),
                      raw_total_ha=round(float(pv.area_applied_ha.sum()), 3),
                      project_total_ha=round(float(pv[cnt].area_applied_ha.sum()), 3),
                      raw_by_group=raw_by, project_by_group=proj_by,
                      superseded=[dict(proposal_no=r.proposal_no, project=r.project, area_ha=r.area_applied_ha, superseded_by=r.superseded_by)
                                  for _, r in pv[pv.role == "superseded"].iterrows()]),
        coverage=dict(matched=int((mt.side == "both").sum()), dhpd_only=int((mt.side == "dhpd_only").sum()),
                      parivesh_only=int((mt.side == "parivesh_only").sum()),
                      parivesh_only_flagged=int(((mt.side == "parivesh_only") & (~mt.expected_absence)).sum()),
                      parivesh_only_expected=int(((mt.side == "parivesh_only") & (mt.expected_absence)).sum()),
                      manual_matches=int((mt.match_method == "manual").sum())),
        area_by_basin=area_by("basin"), area_by_district=area_by("district"),
        inconsistency_counts={g: int((ic.group == g).sum()) for g in "ABCDEF"},
    )

    # ---------------------------------------------------------- write
    dh_out = dh.drop(columns=["_k"]).rename(columns={"project_name": "project"})
    dh_out.to_csv(OUT / "dhpd_projects.csv", index=False)
    pv.drop(columns=["area_diverted_raw"]).to_csv(OUT / "parivesh_proposals.csv", index=False)
    mt.to_csv(OUT / "match_table.csv", index=False)
    ic.to_csv(OUT / "inconsistencies.csv", index=False)
    corr.to_csv(OUT / "corrections_log.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")

    # ---------------------------------------------------------- reconciliation
    src = pd.read_excel(DHPD_ALL)
    pv_src = pd.read_excel(PARIVESH, dtype=str)
    chk_d = pd.read_csv(OUT / "dhpd_projects.csv")
    chk_p = pd.read_csv(OUT / "parivesh_proposals.csv")
    src_area = sum(num(x) or 0 for x in pv_src["Area_Applied"])
    rows = [
        ("DHPD projects", len(src), len(chk_d), len(src) == len(chk_d) == 113),
        ("DHPD capacity (MW)", round(src["capacity_(mw)"].sum(), 3), round(chk_d.capacity_mw.sum(), 3), abs(src["capacity_(mw)"].sum() - chk_d.capacity_mw.sum()) < 1e-6 and round(src["capacity_(mw)"].sum(), 1) == 43094.3),
        ("Parivesh proposals", len(pv_src), len(chk_p), len(pv_src) == len(chk_p) == 36),
        ("Parivesh Area_Applied (ha)", round(src_area, 3), round(chk_p.area_applied_ha.sum(), 3), abs(src_area - chk_p.area_applied_ha.sum()) < 1e-6),
        ("Status groups cover all rows", 36, int(chk_p.status_group.notna().sum()), True),
        ("Matched + DHPD-only = DHPD", len(src), summary["coverage"]["matched"] + summary["coverage"]["dhpd_only"], summary["coverage"]["matched"] + summary["coverage"]["dhpd_only"] == len(src)),
        ("Matched + Parivesh-only = distinct Parivesh projects", summary["parivesh"]["distinct_projects"], summary["coverage"]["matched"] + summary["coverage"]["parivesh_only"],
         summary["coverage"]["matched"] + summary["coverage"]["parivesh_only"] == summary["parivesh"]["distinct_projects"]),
    ]
    print("\nRECONCILIATION  (source Excel vs CSV)")
    print(f"{'check':58s}{'source':>14s}{'csv':>14s}  ok")
    for n, a, b, ok in rows:
        print(f"{n:58s}{a:>14}{b:>14}  {'OK' if ok else 'MISMATCH'}")
    print("\nDHPD by status:", json.dumps(stat))
    print("\nForest area, raw 36 proposals (ha) vs the checks you gave:")
    expect = dict(cleared=(6598.37, 8), in_principle=(224.0, 8), in_progress=(5257.33, 12), rejected=(2205.37, 8))
    for g in GROUPS:
        e = expect[g]
        o = raw_by[g]
        print(f"  {g:13s} computed {o['ha']:>10.3f} ({o['proposals']:2d})   expected {e[0]:>9.2f} ({e[1]})   {'OK' if abs(o['ha'] - e[0]) < 0.006 and o['proposals'] == e[1] else 'DIFFERS'}")
    print(f"  total         computed {summary['parivesh']['raw_total_ha']:>10.3f}        expected 14285.27")
    print("Project-level (refilings once):", json.dumps({g: proj_by[g]['ha'] for g in GROUPS}), "total", summary["parivesh"]["project_total_ha"])
    print("Coverage:", summary["coverage"])
    print("Inconsistency counts:", summary["inconsistency_counts"])
    if not all(r[3] for r in rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
