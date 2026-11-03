# About Arunachal Dam Watch

A single-page dashboard of hydropower projects in Arunachal Pradesh: how much power they make, how much forest they take, how late and over budget they run, and the disasters linked to them.

The site is at [https://yania-n.github.io/Arunachal-Dam-Watch/](https://yania-n.github.io/Arunachal-Dam-Watch/).

*NOTE: Impact figures cover only what was reported, so treat them as a minimum.*

## Where the data comes from

The data is compiled from government records (CEA, PIB, CERC, NHPC, MoEFCC clearance papers) and news reports up to 3 November 2026. Every figure links back to its source in the Sources section at the bottom of the dashboard.

The data lives in four spreadsheets in the `data/` folder. The page reads them when it opens:

| File                                     | What it holds                                                                                                          |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `data/projects.csv`                    | One row per large hydro project (over 25 MW): status, capacity, dam height, land, forest, trees, dates, notes, sources |
| `data/disasters_and_site_failures.csv` | One row per disaster or site failure, with people affected and other losses                                            |
| `data/build_time_and_cost.csv`         | Start and finish years, original and latest cost                                                                       |
| `data/official_figures.csv`            | Official state totals (projects coming up, small hydro capacity, and so on)                                            |

`arunachal-dam-watch-data.xlsx` is a backup copy of the same data, with a summary tab and a glossary of every field. To view the dashboard on your own computer, see [PREVIEW_LOCALLY.md](PREVIEW_LOCALLY.md).

## Summary of the dashboard

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

## Conclusions

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
