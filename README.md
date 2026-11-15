# About Arunachal Dam Watch

A single-page dashboard of hydropower projects in Arunachal Pradesh: how much power they make, how much forest they take, how late and over budget they run, and the disasters linked to them.

This repo holds two separate dashboards, both live on GitHub Pages:

| Dashboard                                            | Link                                                                                        | Data                                              |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **Arunachal Dam Watch** (`index.html`)       | [yania-n.github.io/Arunachal-Dam-Watch/](https://yania-n.github.io/Arunachal-Dam-Watch/)       | Compiled from government records and news reports |
| **Arunachal Dam Watch II** (`v2/index.html`) | [yania-n.github.io/Arunachal-Dam-Watch/v2/](https://yania-n.github.io/Arunachal-Dam-Watch/v2/) | Official portal data only: DHPD and Parivesh      |

The two are kept apart on purpose: the first mixes government records with news reports, the second uses only the two official portals. Each links to the other.

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

- **Cleared** = Approved + Closed: final forest approval granted. It does not mean trees were felled.
- **Approved in principle** = In-principle (Stage-I granted, final approval awaited).
- **In progress** = DFO, Nodal Officer, Pending With-SG.
- **Rejected** = Rejected, Returned, Withdrawn.
- **Refilings:** proposals are grouped by project. A later full proposal supersedes an earlier one, so the project's area is counted once. Ancillary proposals (quarry-patch changes) add their own area. Raw proposal totals are shown too.
- **Corrections:** only the spelling "Nyikong", New Melling's capacity (DHPD's 96 MW), and the district of Attunli, Etalin and Anonpani (shown as Dibang Valley, as the project owner says; DHPD says Lower Dibang Valley and the mismatch is still listed). DHPD's district and basin are otherwise shown unchanged, including for Yammeng and Halaipani, whose discrepancies are listed with the project owner's notes.
