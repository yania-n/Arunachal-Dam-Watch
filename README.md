# About Arunachal Dam Watch

A single-page dashboard of hydropower projects in Arunachal Pradesh: how much power they make, how much forest they take, how late and over budget they run, and the disasters linked to them.

This repo holds two separate dashboards, both live on GitHub Pages:

| Dashboard                                            | Link                                                                                        | Data                                              |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **Arunachal Dam Watch** (`index.html`)       | [yania-n.github.io/Arunachal-Dam-Watch/](https://yania-n.github.io/Arunachal-Dam-Watch/)       | Compiled from government records and news reports |
| **Arunachal Dam Watch II** (`v2/index.html`) | [yania-n.github.io/Arunachal-Dam-Watch/v2/](https://yania-n.github.io/Arunachal-Dam-Watch/v2/) | Official portal data only: DHPD and Parivesh      |
| **Dam map** (`map/index.html`)               | [yania-n.github.io/Arunachal-Dam-Watch/map/](https://yania-n.github.io/Arunachal-Dam-Watch/map/)   | Global Energy Monitor (independent) shown beside DHPD and Parivesh |

The two dashboards are kept apart on purpose: the first mixes government records with news reports, the second uses only the two official portals. Each links to the other.

The rest of this file up to "Conclusions" describes the first dashboard. The second is described in its own section near the end.

*NOTE: Impact figures cover only what was reported, so treat them as a minimum.*

## First Dashboard: Where the data comes from

The data is compiled from government records (CEA, PIB, CERC, NHPC, MoEFCC clearance papers) and news reports up to 3 November 2026. Every figure links back to its source in the Sources section at the bottom of the dashboard.

The data lives in four spreadsheets in the `data/` folder. The page reads them when it opens:

| File                                     | What it holds                                                                                                          |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `data/projects.csv`                    | One row per large hydro project (over 25 MW): status, capacity, dam height, land, forest, trees, dates, notes, sources |
| `data/disasters_and_site_failures.csv` | One row per disaster or site failure, with people affected and other losses                                            |
| `data/build_time_and_cost.csv`         | Start and finish years, original and latest cost                                                                       |
| `data/official_figures.csv`            | Official state totals (projects coming up, small hydro capacity, and so on)                                            |

`arunachal-dam-watch-data.xlsx` is a backup copy of the same data, with a summary tab and a glossary of every field.

## Summary: (`index.html`)

### What exists today

- 4 large dams (over 25 MW) are running: Panyor Lower (Ranganadi), Kameng, Pare and Subansiri Lower. Subansiri Lower has only 5 of its 8 units running.
- Together they make about 2,365 MW. Small hydro adds another 140.61 MW.
- The state says 33 more projects are coming, with about 19,165 MW. The government estimates Arunachal could support 50,064 MW, so most of the building is still ahead.

### Forest

- Projects built or being built have taken 7,761 ha of forest. Projects approved or being planned are asking for 9,381 ha more.
- About 324,000 trees have been cleared for felling, and around 2.8 million more are set to be felled.
- Most projects don't publish a forest figure (including Kameng, Panyor Lower and Pare), so the real numbers are higher.

### Time and money

Every finished project took much longer and cost much more than planned:

- **Kameng** was meant to take 5 years and took about 16. Its cost went from ₹2,497 crore to ₹8,450 crore, about 3.4 times the plan.
- **Pare** opened 70 months late. Its cost went from ₹574 crore to ₹1,657 crore, about 2.9 times the plan.
- **Subansiri Lower** was due in 2012 and is now targeted for March 2027. Its cost went from ₹6,285 crore to about ₹26,000 crore, about 4 times the plan. Protests also stopped work for nearly 8 years.

### Disasters and failures

- The dashboard records 17 events: 7 disasters (floods or failures that hit people or the river) and 10 site failures (walls collapsing, landslides, a sinkhole, a washed-away riverside barrier, leaks).
- At least 106,786 people were affected. The real number is higher, because many events have no published count.
- Almost every event is at two projects:
  - **Subansiri Lower:** 11 events (2 disasters, 9 site failures)
  - **Panyor Lower:** 5 events (all disasters)
  - **Kameng:** 1 event (a site failure)
  - **Pare:** none recorded

## Conclusions: From first dashboard

**Quality and state of the projects:** the record is poor. None of the large projects finished on time or on budget. The biggest project, Subansiri Lower, had repeated wall collapses, landslides, a sinkhole and floods during construction. In 2023 the government treated one of these as a major dam failure under the Dam Safety Act. The projects do work once built, but building them in Arunachal's steep, landslide-prone hills has been much harder than the plans assumed.

**Risks to people:**

- **Floods from dam releases.** Water released from Panyor Lower has flooded Lakhimpur in 2008, 2015, 2017 and 2025. Those people live downstream in Assam, so the dams' risk doesn't stop at the state border.
- **Disasters at the project site.** In June 2026 a flash flood at the NEEPCO colony in Keyi Panyor, Arunachal, affected about 350 people and destroyed 30 houses. NEEPCO says local heavy rain caused it, while SANDRP points to the collapse of an unfinished retaining wall. Either way, people living near projects face this risk directly.
- **Rivers drying up.** In 2023 the Subansiri ran dry downstream for about 12 hours after a tunnel got blocked. That raised concerns for fish, river dolphins and riverside communities.
- **Forest loss.** Thousands of hectares and millions of trees are going, and the full total is unknown.
- **Scale.** With 33 more projects planned and many on the same rivers, the risks above could grow if the lessons from Subansiri and Ranganadi aren't applied.

**What needs to improve:**

1. **Open data.** Most projects don't publish forest area, trees felled or people affected. Every project should publish these, plus its dam safety reports.
2. **Safe water releases.** There should be clear rules and early warnings before water is released, agreed with downstream districts in both Arunachal and Assam.
3. **Better ground studies before building.** Many failures were landslides and slope problems, so geology checks need to be stronger.
4. **Honest timelines and budgets.** Costs tripling or quadrupling means the plans aren't realistic.

**Focus for the government:** fix safety and openness before speeding up the 33 new projects. Learn from what went wrong at Subansiri Lower and Panyor Lower, look at the combined effect of many dams on the same river, and make data on forests, people and incidents public.

**Focus for the people of Arunachal:** ask for this data, take part in the public hearings held before projects are cleared, and push for warning systems and fair compensation where they live near a project or downstream of one.

*A note on the evidence:* these conclusions come only from the sourced data in the dashboard. The dashboard doesn't track the benefits (power supply, revenue, jobs), so this isn't a full cost-benefit judgment.

## Second dashboard: official data only (`v2/index.html`)

Live at [yania-n.github.io/Arunachal-Dam-Watch/v2/](https://yania-n.github.io/Arunachal-Dam-Watch/v2/). `v2/index.html` is a separate, plainer page built only from the two official portals. The original `index.html` and the files in `data/` are untouched.

The page is written for readers who do not know the data. The first tab, **The story**, walks through seven short chapters (the plan, the forest, the decisions, the biggest requests, the rivers, whether the two sites agree, and what the data cannot tell you). The other tabs hold the detail: **Forest requests**, **The dams**, **Where the two sites disagree** and **How we did this** (method, glossary, open questions). In the page, the four forest groups are called Fully approved (= Cleared), Approved in principle, Waiting for a decision (= In progress) and Turned down (= Rejected).

**The rule:** all power capacity figures come from DHPD (`DHPD/all_projects.xlsx`). All forest clearance figures come from Parivesh (`parivesh/hydel_only_merged_final.xlsx`). The two are shown side by side and never merged or averaged. Capacity is never read from Parivesh project names.

### Build script

`python build_official_data.py` (needs `pandas` and `openpyxl`) reads the two Excel files and rewrites `data/official/`:

| File                       | Contents                                                                                                                                |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `dhpd_projects.csv`      | 113 DHPD projects with status (rebuilt from the original downloads in `DHPD/data&exploration/`), capacity, developer, district, basin |
| `parivesh_proposals.csv` | 36 proposals, numeric areas, normalised status and status group, refiling role                                                          |
| `match_table.csv`        | DHPD project to Parivesh proposals, with `exact` / `normalised` / `manual` match method                                           |
| `inconsistencies.csv`    | Every difference found, groups A to F                                                                                                   |
| `corrections_log.csv`    | The only changes made, plus Yammeng and Halaipani marked "not changed"                                                                  |
| `summary.json`           | Headline numbers read by the page                                                                                                       |

The script prints a reconciliation table (CSV totals against the source Excel sums). The page reads the CSVs with `fetch`, so serve it over http, not from a local file. For local viewing run `python -m http.server 8000 --bind 127.0.0.1` in the repo and open `http://localhost:8000/v2/` (do not open `http://[::]:8000`).

### Folders for the second dashboard

| Folder             | Contents                                                                                                                                                                                            |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DHPD/`          | Hydropower project data from the DHPD portal ([dhpdap.online](https://dhpdap.online/)); `all_projects.xlsx` is the main file                                                                         |
| `parivesh/`      | Forest clearance proposals from the Parivesh portal ([forestsclearance.nic.in](https://forestsclearance.nic.in/FCDashboard/FCPublicDashboard.aspx)); `hydel_only_merged_final.xlsx` is the main file |
| `data/official/` | CSV and JSON files written by the build script and read by the page                                                                                                                                 |
| `v2/`            | The page itself (`v2/index.html`)                                                                                                                                                                 |

### Definitions

- **Scope of the forest figures:** only projects that are on the DHPD list (28 projects, 14,127.8 ha). Three projects found only on Parivesh (Phudung, Simang-I, Tagurshit; 98.3 ha) are left out of the totals. They stay in `parivesh_proposals.csv` and in the discrepancy lists, and `summary.json` reports them under `parivesh.not_on_dhpd`. The whole Parivesh file is 31 projects and 14,226.1 ha (`parivesh.all`).
- **Cleared** = Approved + Closed: final forest approval granted. It does not mean trees were felled.
- **Approved in principle** = In-principle (Stage-I granted, final approval awaited).
- **In progress** = DFO, Nodal Officer, Pending With-SG.
- **Rejected** = Rejected, Returned, Withdrawn.
- **Refilings:** proposals are grouped by project. A later full proposal supersedes an earlier one, so the project's area is counted once. Ancillary proposals (quarry-patch changes) add their own area. Raw proposal totals are shown too.
- **Corrections:** only the spelling "Nyikong", New Melling's capacity (DHPD's 96 MW), and the district of Attunli, Etalin and Anonpani (shown as Dibang Valley, as the project owner says; DHPD says Lower Dibang Valley and the mismatch is still listed). DHPD's district and basin are otherwise shown unchanged, including for Yammeng and Halaipani, whose discrepancies are listed with the project owner's notes.

## Map of the dam sites (`map/index.html`)

A separate mobile-first page with its own dark look. One marker per dam in the Global Energy Monitor (GEM) Global Hydropower Tracker (March 2026 release, CC BY 4.0): 61 Arunachal rows plus Subansiri Lower, which GEM tags as Assam (pulled from the full tracker file). Tapping a marker opens a bottom sheet with DHPD, Parivesh and GEM figures side by side. Nothing is averaged or merged; every number carries its source. Below the map are the dams the map cannot place and six combined insights (status and capacity disagreements, forest vs GEM status, coverage, pipeline MW by basin, location quality).

Serve it like v2: `python -m http.server 8000 --bind 127.0.0.1`, then open `http://localhost:8000/map/`. It links back to `v2/`, and `v2/index.html` links to it.

**Basemap:** CARTO `dark_all` now returns an "API key required" tile, so the page uses OpenStreetMap tiles darkened with CSS. The `TILES` constant in `map/index.html` shows where to swap in CARTO with a key.

### New files

| File | Contents |
| ---- | -------- |
| `build_gem_data.py` | Matches GEM rows to DHPD and Parivesh (needs `pandas` and `openpyxl`); prints a reconciliation |
| `data/official/gem_projects.csv` | 62 GEM sites: GEM fields, `dhpd_id`, `parivesh_project`, basin |
| `data/official/gem_match_table.csv` | GEM to DHPD match with `match_method` (`exact` / `normalised` / `manual` / `unmatched`) and notes; DHPD-only rows included |

### Matching rules

Names are lowercased; the suffixes "hydroelectric plant", "hydro electric project" and "HEP" are stripped, as is any "(NNN MW)"; punctuation is dropped. Then, in order: exact, stage/roman-numeral equal ("Siang Upper II" = "Siang Upper St-II"), word-order swap ("Siang Lower" = "Lower Siang"), spaces removed ("Mago Chu" = "Magochu"), and a lone name equal to stage I ("Oju" = "Oju - I"). Each match is checked on capacity and district and the differences are written to the notes. Manual: Ranganadi 405 MW to Panyor Lower (the 130 MW row stays unmatched) and Upper Subansiri to Subansiri Upper (flagged for confirmation). Parivesh is linked through `dhpd_id`, or by name for GEM dams not on DHPD (Simang-I, Tagurshit). A dam is flagged "Sources disagree" when capacities differ by more than 5% of the larger figure, or the statuses conflict (DHPD Completed vs GEM not operating; DHPD Under construction vs GEM not construction; DHPD Under implementation vs GEM shelved, cancelled or operating). GEM's "inferred" statuses are GEM's own inference, not an official finding.

## Map of the EC proposals (`map/kml.html`)

A second map page, built from the KML files uploaded with Parivesh **environment clearance (EC)** proposals (IDs like `IA/AR/RIV/…`, not the forest-clearance `FP/AR/HYD/…` IDs used elsewhere). 149 manifest rows (`data/kml/parivesh_kml_manifest(2).csv`) cover 24 proposals and 14 projects. One marker per project; opening it loads that project's GeoJSON and draws it: dam axes as lines, project area, reservoir and forest land as polygons, ancillary works as points. Filters cover proposal status, which proposals to draw (default, delisted, earlier, returned) and the layer by role. A details panel shows capacity, district and developer (DHPD, else GEM, else "Not stated"), every proposal with its status and files, and the match status.

Serve it like the other pages: `python -m http.server 8000 --bind 127.0.0.1`, then open `http://localhost:8000/map/kml.html`.

### New files

| File | Contents |
| ---- | -------- |
| `build_kml_data.py` | Parses the KMLs, classifies roles, removes duplicates, matches projects, simplifies the geometry and writes everything below (standard library only) |
| `data/official/kml_catalogue.csv` | One row per manifest row: geometry types, feature counts, centroid, bounding box, area or length, flags, role, `role_confidence`, proposal kind and `dedupe_status` (`mapped` / `duplicate` / `excluded` / `missing`) |
| `data/official/kml_match_table.csv` | One row per EC proposal: matched DHPD and GEM id, `match_method` (`exact` / `fuzzy` / `manual` / `unmatched`), notes, MW and distance checks |
| `data/official/kml_projects.json` | What the page reads: marker position, proposals, files, counts and GeoJSON paths per project |
| `data/official/kml_geojson/<slug>.geojson` | Simplified geometry per project, with `role`, `proposal_no`, `status`, `layer` and `role_confidence` on each feature |
| `data/official/kml_geojson/<slug>_cad.geojson` | CAD / survey line-work (Kurung, Niare), loaded only when that layer is switched on |
| `data/official/kml_summary.json` | File counts and sizes before and after simplification |
| `data/official/kml_review.md` | Roles and matches that need a human decision |

### Rules

- **Files:** 54 mapped, 90 duplicates (same geometry as another file), 2 excluded and 3 missing. The two `PLATE-1_14.3.24.kml` files are NetworkLinks to a .KMZ that is not in the download set; the 3 missing files failed to download (HTTP 500). All are listed on the page and in the catalogue. A few files have an undeclared `xsi:` prefix, which the script patches in memory; no KML is changed.
- **Duplicates:** geometry is hashed after rounding to 5 decimals and normalising ring start and direction, then de-duplicated per project at the level of one shape.
- **Default proposal:** the newest proposal that is not "Proposal returned in present form" and not `DELISTED_BY_SYSTEM`. Returned and delisted proposals stay as toggleable layers. A delisted proposal draws grey only for geometry no other proposal has (Kamala 562202); one that repeats another proposal draws nothing and the panel says so (Naying 573573 is "DELISTED, same geometry as 470969/2024").
- **Roles** are read from the placemark name, its attributes and folders, then the document and file name, then the upload prefix. Each feature stores `role_confidence`: `high` for a placemark, attribute or folder name or the `FORM_C_FOREST_LAND_PROPOSED_DIVERSION` prefix, `medium` for a file name only or the plain `FC_KML` prefix, `low` when nothing matched (role `other`). Hirong's MDA / CBP / RQ / RBM labels are kept as written. Subansiri Upper Sites A to E are marked "alternative site (inferred from file names)". Tato-I's "Project Area" is its own role, `project_area`. Unlabelled shapes are labelled with their area.
- **CAD / survey detail** (`cad_detail`): Kurung's unlabelled lines and Niare's `power house alt-N` lines. They are simplified more coarsely and are off by default.
- **Matching** uses the same name rules as the GEM match (suffixes, "(NNN MW)" and village or district text stripped, roman numerals, word order), then checks MW against DHPD and GEM and the KML centroid against the GEM pin. `exact`: name matches and MW and location agree. `fuzzy`: name matches but MW or location does not (shown as "match unverified (name/MW only)"). `unmatched`: name matches but MW and location both disagree (Hirong: 351 vs 500 MW, 61 km; it may be a re-scoped version of D010 / G100000604428). The manual override table is empty. Unmatched projects are shown as "EC proposal only" at the KML centroid.
- **Marker position:** the GEM pin when the KML centroid is within 10 km of it, otherwise the KML centroid; the details panel gives the pin distance.
- **Simplification:** Douglas-Peucker at 0.00003 degrees (about 3 m), or 0.0001 for CAD detail, coordinates to 5 decimals. About 53.6 MB of KML became 9.6 MB of de-duplicated GeoJSON and 3.3 MB after simplification (1.6 MB drawn by default, 1.7 MB CAD detail).
- **Not stated:** anything missing from the KMLs, the manifest, DHPD, GEM or Parivesh reads "Not stated". The page links to the Parivesh home page and shows each proposal number to search for; no deep link is used because none could be checked.

Re-run with `python build_kml_data.py` from the repo root. It never writes to `map/index.html` or to any existing data file.
