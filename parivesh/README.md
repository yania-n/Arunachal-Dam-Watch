# Parivesh data

Forest clearance proposals for hydropower projects, from the Parivesh portal ([FC public dashboard](https://forestsclearance.nic.in/FCDashboard/FCPublicDashboard.aspx)).

`hydel_only_merged_final.xlsx` is the main file: one row per proposal, with the forest area requested and the proposal status.

`data&exploration/` holds earlier files and the notebook used to explore them.

Parivesh is the only source of forest clearance figures in this repo. Power capacity comes from DHPD (see `../DHPD/`). The two are never merged.

The data feeds the second dashboard, [Arunachal Dam Watch II](https://yania-n.github.io/Arunachal-Dam-Watch/v2/). See the main `README.md` for how proposal statuses are grouped (Fully approved, Approved in principle, Waiting for a decision, Turned down).
