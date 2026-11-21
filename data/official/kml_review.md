# KML build: items needing review

## Decisions applied

- Default proposal = newest proposal whose status is neither 'Proposal returned in present form' nor DELISTED_BY_SYSTEM. Returned and delisted proposals stay as toggleable layers.
- Marker = GEM pin when the KML centroid is within 10 km of it, otherwise the KML centroid. Fuzzy matches are shown as unverified.
- `cad_detail` = Kurung's unlabelled lines and Niare's 'power house alt-N' lines. Written to <slug>_cad.geojson, off by default.
- `project_area` = Tato-I 'Project Area'. Subansiri Upper Sites A-E carry the note 'alternative site (inferred from file names)'.
- Hirong MDA / CBP / RQ / RBM labels are kept as written.
- `role_confidence`: high = placemark / attribute / folder name, or the FORM_C_FOREST_LAND_PROPOSED_DIVERSION prefix; medium = file or document name only, or the plain FC_KML prefix; low = no keyword.

## Proposals: default, kind and geometry

- kurung | IA/AR/RIV/592956/2026 | Proposal Accepted and Referred to EAC | default | All of its geometry is only in this proposal
- etalin | IA/AR/RIV/575562/2026 | Granted | default | Same geometry as 544875/2025
- etalin | IA/AR/RIV/544875/2025 | EC Granted | earlier | Same geometry as 575562/2026
- etalin | IA/AR/RIV/542725/2025 | Granted | earlier | Same geometry as 575562/2026
- kamala | IA/AR/RIV/562202/2026 | DELISTED_BY_SYSTEM | delisted | 90 of 458 geometries are only in this proposal; the rest also appear in other proposals
- kamala | IA/AR/RIV/465936/2024 | ToR Granted | default | All of its geometry also appears in 562202/2026 (DELISTED_BY_SYSTEM)
- demwe-lower | IA/AR/RIV/562775/2025 | Proposal returned in present form | returned | Same geometry as 554221/2025
- demwe-lower | IA/AR/RIV/554221/2025 | Granted | default | Same geometry as 562775/2025 (Proposal returned in present form)
- kalai-ii | IA/AR/RIV/557663/2025 | EC Granted | default | Same geometry as 539430/2025
- kalai-ii | IA/AR/RIV/539430/2025 | ToR Granted | earlier | Same geometry as 557663/2025
- kalai-ii | IA/AR/RIV/466561/2024 | ToR Granted | earlier | 66 of 127 geometries are only in this proposal; the rest also appear in other proposals
- tato-i | IA/AR/RIV/447696/2023 | Granted | default | All of its geometry is only in this proposal
- hirong | IA/AR/RIV/592970/2026 | Proposal Accepted and Referred to EAC | default | All of its geometry is only in this proposal
- subansiri-upper | IA/AR/RIV/584408/2026 | ADS Raised | default | Same geometry as 466971/2024
- subansiri-upper | IA/AR/RIV/466971/2024 | ToR Granted | earlier | Same geometry as 584408/2026
- tato-ii | IA/AR/RIV/537011/2025 | Proposal returned in present form | returned | Same geometry as 449080/2023
- tato-ii | IA/AR/RIV/449080/2023 | Granted | default | Same geometry as 537011/2025 (Proposal returned in present form)
- attunli | IA/AR/RIV/582227/2026 | EC Granted | default | Same geometry as 455548/2023
- attunli | IA/AR/RIV/455548/2023 | ToR Granted | earlier | Same geometry as 582227/2026
- emra-ii | IA/AR/RIV/439743/2023 | ToR Granted | default | All of its geometry is only in this proposal
- naying | IA/AR/RIV/573573/2026 | DELISTED_BY_SYSTEM | delisted | Same geometry as 470969/2024
- naying | IA/AR/RIV/470969/2024 | ToR Granted | default | Same geometry as 573573/2026 (DELISTED_BY_SYSTEM)
- heo | IA/AR/RIV/448652/2023 | Granted | default | All of its geometry is only in this proposal
- niare | IA/AR/RIV/573804/2026 | Forwarded to MS SPCB/PCC by MS | default | All of its geometry is only in this proposal

## Unresolved / excluded files

- IA/AR/RIV/562202/2026 | PLATE-1_14.3.24.kml | excluded | network_link
- IA/AR/RIV/539430/2025 | 128317503_FC_FORM_C_FOREST_LAND_PROPOSED_DIVERSION_KML_1751268549912_perfect_kalai_ii_with_hac.kml | missing | missing_download (Error: HTTP 500 application/json)
- IA/AR/RIV/465936/2024 | 29700385_FC_KML_1713613755432_Kamala_Hapoli_Forest_Area.shp.kml | missing | missing_download (Error: HTTP 500 application/json)
- IA/AR/RIV/465936/2024 | PLATE-1_14.3.24.kml | excluded | network_link
- IA/AR/RIV/465936/2024 | Project_Dam_LocationA2.kml | missing | missing_download (Error: HTTP 500 application/json)

## Roles needing review (mapped geometry only; one line per project / file / reason)

- etalin | IA/AR/RIV/575562/2026 | kml etalin componentwise justification | 53x project_layout: role taken from the file / document name only
- etalin | IA/AR/RIV/575562/2026 | kml etalin componentwise justification | 3x ancillary: labels kept as written (not expanded); 'ancillary' is inferred from the neighbouring construction-area names
- kamala | IA/AR/RIV/562202/2026 | Project Dam LocationA2 | 1x project_layout: role taken from the file / document name only
- kamala | IA/AR/RIV/465936/2024 | 14 updated new drift and drilling location 28-08-2024 | 146x ancillary: role taken from the file / document name only
- kamala | IA/AR/RIV/465936/2024 | kra-daadi draft | 2x forest_land: role from the plain 'FC_KML' upload prefix only; names are generic
- kamala | IA/AR/RIV/465936/2024 | Kamala HEP 1720 MW-15-3-2024 | 5x other: no keyword in placemark, attribute, folder or file name (polygon areas ha: [3926.4, 87.4, 27.8, 19.9, 10.9])
- kamala | IA/AR/RIV/465936/2024 | Kamala HEP Dam Axis Alternatives | 140x dam_axis: role taken from the file / document name only
- demwe-lower | IA/AR/RIV/554221/2025 | kml | 1x other: 'Shoal area' (river bar?) has no matching role (polygon areas ha: [12.0])
- kalai-ii | IA/AR/RIV/466561/2024 | ANFD | 9x forest_land: role taken from the file / document name only
- kalai-ii | IA/AR/RIV/466561/2024 | Namsai FD patch | 7x forest_land: role taken from the file / document name only
- kalai-ii | IA/AR/RIV/466561/2024 | KIMGFii | 10x project_layout: role taken from the file / document name only
- tato-i | IA/AR/RIV/447696/2023 | Tato-I Project Area EC | 1x project_area: 'Project Area' kept as its own role; the file does not say whether it is the whole boundary or the works area
- hirong | IA/AR/RIV/592970/2026 | hirong kml | 1x project_layout: 'Dam site' is a polygon (works area), not an axis line
- hirong | IA/AR/RIV/592970/2026 | hirong kml | 15x ancillary: labels kept as written (not expanded); 'ancillary' is inferred from the neighbouring construction-area names
- subansiri-upper | IA/AR/RIV/584408/2026 | Site A | 1x dam_axis: 'Site A-E' read as alternative dam sites; the name does not say axis or reservoir
- subansiri-upper | IA/AR/RIV/584408/2026 | Site C | 1x dam_axis: 'Site A-E' read as alternative dam sites; the name does not say axis or reservoir
- subansiri-upper | IA/AR/RIV/584408/2026 | Site D | 1x dam_axis: 'Site A-E' read as alternative dam sites; the name does not say axis or reservoir
- subansiri-upper | IA/AR/RIV/584408/2026 | ge 2 | 1x forest_land: role from the 'FORM_C_FOREST_LAND_PROPOSED_DIVERSION' upload prefix; names are generic
- subansiri-upper | IA/AR/RIV/584408/2026 | Site E | 1x dam_axis: 'Site A-E' read as alternative dam sites; the name does not say axis or reservoir
- subansiri-upper | IA/AR/RIV/584408/2026 | Alternate Sites Upper Subansiri Polygon | 2x dam_axis: 'Site A-E' read as alternative dam sites; the name does not say axis or reservoir
- subansiri-upper | IA/AR/RIV/584408/2026 | Site E (1) | 1x dam_axis: 'Site A-E' read as alternative dam sites; the name does not say axis or reservoir
- tato-ii | IA/AR/RIV/449080/2023 | Tato-II Polygon | 1x forest_land: role from the plain 'FC_KML' upload prefix only; names are generic
- emra-ii | IA/AR/RIV/439743/2023 | Project Layout | 6x project_layout: role taken from the file / document name only
- emra-ii | IA/AR/RIV/439743/2023 | Project Layout | 1x project_layout: 'Dam site' is a polygon (works area), not an axis line
- naying | IA/AR/RIV/470969/2024 | KML Naying HEP Layout 23 4 24 | 14x project_layout: role taken from the file / document name only
- naying | IA/AR/RIV/470969/2024 | naying 470.80ha full r8 | 33x forest_land: role from the plain 'FC_KML' upload prefix only; names are generic
- heo | IA/AR/RIV/448652/2023 | KML Heo-Oct-23 mod | 1x other: no keyword in placemark, attribute, folder or file name (polygon areas ha: [5.2])
- niare | IA/AR/RIV/573804/2026 | power house alt-2 niare hep | 206x project_layout: role taken from the file / document name only
- niare | IA/AR/RIV/573804/2026 | power house alt-3 niare hep | 2x project_layout: role taken from the file / document name only
- niare | IA/AR/RIV/573804/2026 | power house alt-1 niare hep | 186x project_layout: role taken from the file / document name only

## Matches needing review

- kurung: fuzzy dhpd=D034 gem=G100001073514 | MW differs: KML/Parivesh text 292 (project text), DHPD 330. MW differs: KML/Parivesh text 292 (project text), GEM 320. Match unverified (name/MW only).
- hirong: unmatched dhpd=- gem=- | Same name as DHPD D010 / GEM G100000604428. This may be a re-scoped version of that project, but capacity (351 vs 500 MW) and location (61 km apart) differ, so it is not matched. Shown as 'EC proposal only'.
- subansiri-upper: fuzzy dhpd=D028 gem=G100000604924 | KML centroid is 69 km from the GEM pin (Upper Subansiri). No MW in the Parivesh project text or file names; matched on name only. Match unverified (name/MW only).
- emra-ii: fuzzy dhpd=D059 gem=G100001030881 | KML centroid is 32 km from the GEM pin (Emra II). No MW in the Parivesh project text or file names; matched on name only. Match unverified (name/MW only).
- naying: fuzzy dhpd=D009 gem=G100000601997 | KML centroid is 104 km from the GEM pin (Naying). Match unverified (name/MW only).
- niare: fuzzy dhpd=D032 gem=G100001030877 | MW differs: KML/Parivesh text 909 (project text), DHPD 800. KML centroid is 40 km from the GEM pin (Niare). Match unverified (name/MW only).
