# india-plant-mite-database

Literature-derived records of plant-associated mites in India: which species is recorded from which state and on which host plant, each row traced to its printed source.

This is the data repository for Paper 2 of the project *Agricultural mites in India*. Paper 1 (COI coverage and name reliability) lives in [india-agri-mite-coi](https://github.com/vkcvaibhav-eng/india-agri-mite-coi); its species checklist is the name backbone used here.

## Status (12 November 2026)

Eleven layers so far: Gupta & Mondal (2023), *Handbook: Plant Mites of India* (literature up to 2022, 1,249 numbered accounts); the survey tables in the All India Coordinated Research Project / All India Network Project on Agricultural Acarology reports from 1988 to 2024-25 (layers 2-10, typed by hand from the reports; the older reports are available on Krishikosh and the recent progress reports are published); and the regional and family checklists used for the Paper 1 species list (layer 11). Every layer is joined to the Paper 1 checklist, and `data/combined/species_state_all_sources.csv` puts all of them in one species x state table.

### Layer 1: Gupta & Mondal (2023)

| Measure | Value |
| --- | ---: |
| Accounts | 1,249 |
| Accounts linked to a checklist species | 1,088 |
| Species × state records | 1,966 |
| States and union territories | 31 |
| Species × host records | 1,588 |
| Distinct host names | 918 |
| Host text not parsed (review queue) | 117 |
| Locality text not matched to a state (review queue) | 46 |
| Accounts with no host text | 404 |

The 161 unlinked accounts are the 150 accounts of predatory families other than Phytoseiidae, which the Paper 1 checklist does not cover, and 11 genus-level `sp.`/`spp.` accounts.

### Layer 2: AICRP annual report 1996–98 (survey chapter, printed pp. 185–213)

Survey tables from seven centres: Bangalore, Coimbatore, Ludhiana, Hisar, Varanasi, Kalyani and Pusa. This is unpublished project-report literature, so it adds records the book may not carry.

| Measure | Value |
| --- | ---: |
| Observation rows (mite × host and/or place as printed) | 1,109 |
| Distinct mite species names | 128 |
| Distinct host common names | 272 |
| Species × state pairs joined to the checklist | 171 |
| ...of which not in the Gupta & Mondal (2023) layer | 85 |

The 85 new pairs are mostly Uttar Pradesh (34), Tamil Nadu (10), Punjab (10) and Chandigarh (8). Species names in the six checklist families that do not join to the checklist (for example *Tetranychus evansi* from Hisar, and *Tenuipalpus convolvulae* from Coimbatore) are in `data/review/aicrp_names_not_in_checklist.csv`.

- `data/aicrp/aicrp_observations.csv`: one row per observation, both AICRP reports (`report` column). `obs_id` is regenerated at each build, so do not cite it. `pairing` says what the table printed: `host_and_place_paired`, or `host_only` / `place_only` where the table gave a species its host list and its locality list separately. Those two lists are never crossed.
- `data/aicrp/aicrp_species_state_vs_gm2023.csv`: each joined species × state pair, and whether the book layer already has it.
- `data/aicrp/transcription/`: the typed source tables (`paired.txt`, `lists.txt`, `host_mites.txt`) and `blocks.csv` with the PDF and printed page of each table. The `note` column marks OCR noise that was corrected.
- `config/name_crosswalk.csv`: old-to-current name joins used for the checklist (for example *Amblyseius alstoniae* to *Euseius alstoniae*), each with its basis.

Limits of layer 2:
- Hisar does not say which of Haryana and Himachal Pradesh a record comes from, so its state is "Haryana; Himachal Pradesh (not split)" and it is left out of the state comparison.
- Navsari's 1996–98 survey section gives only sample counts and family names, so it is not in the records.
- Names marked "sp. nov." in the report are kept as printed. They are report names and are not counted as published species.
- Status words (High, Medium, Severe and so on) are the centres' own and are not comparable between centres.

### Layer 3: AICRP annual report 1990–91 (survey chapter I and taxonomic chapter II, printed pp. 9–58)

Seven centres: Kalyani, Coimbatore, Navsari, Varanasi, Ludhiana, Pusa and Hisar from the survey chapter, plus Bangalore from Chapter II (host × place table, with localities in Andhra Pradesh and Karnataka). Chapter II also adds Kalyani, Pusa (phytoseiids of Bihar) and Hisar (taxonomy tables 13–17). The tables were typed from the page images; the transcription notes, including rows left out and uncertain readings, are in `data/aicrp/transcription/NOTES_1990-91.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 1,000 |
| Distinct mite species names | 95 |
| Distinct host names | 250 |
| Species × state pairs joined to the checklist | 147 (69 species) |
| ...of which not in the Gupta & Mondal (2023) layer | 74 |
| ...of which also not in the 1996–98 or 1988 layers | 49 |

The 49 pairs new to the book and the other two AICRP layers are Haryana (14), Gujarat (10), Andhra Pradesh (9), West Bengal and Bihar (4 each), Karnataka (3), Tamil Nadu (2), and one each for Kerala, Himachal Pradesh and Punjab. Gujarat and Andhra Pradesh come only from this report. Navsari, Hisar (Table 8) and Kalyani (Table 1) print no locality per row, so their state is the centre's state. Navsari rows are one per slide, so a host and mite can repeat. Hisar's Chapter II tables 13–17 (block C11) aggregate the same Haryana collection as Table 8 (block C07) with specimen counts, so the two blocks must not be summed.

### Layer 4: AICRP First Workshop report, October 1988 (printed pp. 24–89, 112)

The report covers 1987–88. It gives usable survey tables for six centres: Bangalore (identifications with host and locality), Coimbatore (40 mite × host rows, no locality), Ludhiana (Table I, mite × host × locality), Hisar (material identified at Ludhiana), Pusa (a brief survey, with population classes) and Varanasi (the largest part: mite–host indexes for fruit, vegetable, field/ornamental crops and aquatic weeds across Uttar Pradesh districts). Kalyani's survey is narrative only (36 crops in ten districts of West Bengal, no species list) and Navsari gives only an abstract, so neither is in the records. Hisar's own report was not received. Notes on rows left out and uncertain readings are in `data/aicrp/transcription/NOTES_1988.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 510 |
| Distinct mite species names | 105 |
| Distinct host names | 124 |
| Species × state pairs joined to the checklist | 95 (73 species) |
| ...of which not in the Gupta & Mondal (2023) layer | 56 |
| ...of which also not in the other two AICRP layers | 23 |

Varanasi's tables print hosts and districts as separate lists for each mite, so they are recorded as `host_only` and `place_only` rows and never crossed. Almora and Nainital were in Uttar Pradesh in 1988 and are recorded under Uttarakhand, which is why that state appears. Several mite names are species described in the report as new (marked `sp. nov.`); they are kept as printed and are not counted as published species.

### Layer 5: AICRP report 1992–94 (survey chapter, printed pp. 40–62)

Most of this report is experiments. Its survey material is tables from Bangalore (20 crop-place-mite rows with status), Coimbatore (9 rows), Navsari (four rice species), Ludhiana (Table A: 33 species with hosts, localities and specimen counts for Punjab and Himachal Pradesh), Varanasi (Table B: 14 hosts), Pusa (Table C by month and village, and Table 29 on litchi erineum mite by district), Kalyani (a species list for West Bengal without hosts) and the pigeonpea sterility mosaic survey (Aceria cajani at district level in Karnataka). Notes on rows left out and uncertain readings are in `data/aicrp/transcription/NOTES_1992-94.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 347 |
| Distinct mite species names | 79 |
| Distinct host names | 72 |
| Species × state pairs joined to the checklist | 116 (59 species) |
| ...of which not in the Gupta & Mondal (2023) layer | 52 |
| ...of which also not in the other AICRP layers | 13 |

The 13 pairs new to the other AICRP layers are West Bengal (6), Karnataka (2), Tamil Nadu (2), Himachal Pradesh (2) and Gujarat (1). Ludhiana prints hosts and localities as separate lists for each species, so they are recorded as `host_only` and `place_only` rows and never crossed; Varanasi's multi-locality hosts are handled the same way. Kalyani's species list has no host or place, so its state is the centre's state.

### Layer 6: AICRP Second Workshop report, December 1989 (progress for 1988–89)

Mostly technical programmes and experiments. The survey material is Kalyani's table of 57 hosts with places, dates and mites (the largest part), Coimbatore's list of 68 eriophyoid, tetranychid and tenuipalpid species and hosts for Tamil Nadu and Kerala (no locality), Ludhiana's table of mites on 19 hosts in Punjab and Himachal Pradesh, Bangalore's taxonomic notes with host and place, Navsari's host and mite index for Gujarat with survey results at Surat and Bharuch, and a note on Petrobia latens outbreaks in Rajasthan. Varanasi, Hisar and Pusa give families only or nothing usable. Notes on rows left out and uncertain readings are in `data/aicrp/transcription/NOTES_1989.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 545 |
| Distinct mite species names | 95 |
| Distinct host names | 181 |
| Species × state pairs joined to the checklist | 69 (43 species) |
| ...of which not in the Gupta & Mondal (2023) layer | 34 |
| ...of which also not in the other AICRP layers | 22 |

Coimbatore and Bangalore cover two states each without saying which record is from which, so rows without a place keep a "(not split)" state and are left out of the state comparison. Kalyani's hosts and places are printed as separate lists, so multi-place hosts are recorded as `host_only` and `place_only` rows.

Combined AICRP layers: 3,511 observation rows, 339 species × state pairs, 186 of them not in the Gupta & Mondal (2023) layer.

### Layer 7: AICRP First Group Meeting report, December 1990 (survey chapter, printed pp. 139-154, and disease chapters I-III)

Survey tables from six centres: Bangalore's species list with host and place (Karnataka), Kalyani's 50-host table for West Bengal, Bihar and Odisha (no place per row) with stigmaeid and tarsonemid tables that have places and months, Ludhiana's Table 5 of 26 species with separate host and locality lists, Coimbatore's district tables for Tamil Nadu and Kerala, and Navsari's family-level text. Pusa is text only; Varanasi and Hisar sent no report. The disease chapters add survey and natural-incidence records: mites on litchi (Kalyani, Pusa), Aceria mangiferae at seven mango-growing places in West Bengal with the mite complex of mango buds, and Aceria cajani on pigeonpea at Bangalore, Chitradurga, Coimbatore and Navsari. Spray and resurgence experiments (chapter IV) are not records and are left out. Notes are in `data/aicrp/transcription/NOTES_1990-group-meeting.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 322 |
| Distinct mite species names | 73 |
| Distinct host names | 130 |

Combined AICRP layers: 3,833 observation rows, 347 species x state pairs, 191 of them not in the Gupta & Mondal (2023) layer.

### Layer 8: AICRP Progress Report 2020-21 (XVII Group Meeting, survey chapter III.1)

The first of the modern reports. Kalyani's tables for West Bengal and Bihar make up most of the rows (species, host habitat and districts), with Navsari's table for South Gujarat, Ludhiana's surveillance table, Jorhat's list for Assam and Thrissur's table of spider mites in Kerala. Mashobra's Table 157 gives European red mite, two-spotted mite and flat mites by host and locality across Himachal Pradesh. Bangalore and Coimbatore give counts only. Notes are in `data/aicrp/transcription/NOTES_2020-21.md`. The big tables were read from the text layer with `scripts/tools/layout_table.py` and checked by eye.

| Measure | Value |
| --- | ---: |
| Observation rows | 1,978 |
| Distinct mite species names | 88 |
| Distinct host names | 405 |

Combined AICRP layers: 5,811 observation rows, 441 species x state pairs, 251 of them not in the Gupta & Mondal (2023) layer.

### Layer 9: AICRP Progress Report 2021-22 (XVIII Group Meeting, survey chapter III.1)

Smaller than the previous year: Coimbatore's place, host and mite table, Ludhiana's surveillance table for Punjab and nearby states, Jorhat's new rows and Thrissur's table of 16 spider mite species on 35 hosts in Kerala. Navsari's table repeats 2020-21 and Kalyani gives narrative only. Mashobra's status tables for Himachal Pradesh (fruits, vegetables, ornamentals, medicinal plants by locality and month) add European red mite and two-spotted mite by host and place, with flat mites at family level. Notes are in `data/aicrp/transcription/NOTES_2021-22.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 317 |
| Distinct mite species names | 31 |
| Distinct host names | 114 |

Combined AICRP layers: 6,128 observation rows, 454 species x state pairs, 262 of them not in the Gupta & Mondal (2023) layer.

### Layer 10: AICRP Progress Report 2024-25 (XXI Group Meeting, chapter on diversity of plant-associated mites)

The most recent report in the set. Seven centres give species and host tables: Bangalore, Coimbatore, Navsari (new host and state records), Ludhiana (67 predatory mite species on plants across Punjab and the neighbouring states), Mashobra (Himachal Pradesh), Jorhat (Assam) and Thrissur (Kerala). The tables rarely give a place, so most rows are host-level records for a state. Notes are in `data/aicrp/transcription/NOTES_2024-25.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 757 |
| Distinct mite species names | 122 |
| Distinct host names | 197 |

Combined AICRP layers: 6,885 observation rows, 497 species x state pairs, 293 of them not in the Gupta & Mondal (2023) layer. Counting a record from a state that was later split or shared (Telangana, Uttarakhand, Jharkhand, Chhattisgarh, Chandigarh) as matching the parent state in the book, 286 are not in the book layer.

State names are compared through `scripts/states_norm.py`, which gives one spelling (Odisha for the book's Orissa, Puducherry for Pondicherry) and lists parent and child states. The record files keep the state as the source prints it.

### Layer 11: regional and family checklists

The ten checklist extracts that built the Paper 1 species list, copied from india-agri-mite-coi at the pinned commit, turned into species x state and species x host rows (`scripts/build_regional.py`).

| Source | Coverage | Species x state pairs | Species x host rows | Pairs not in the book layer |
| --- | --- | ---: | ---: | ---: |
| Chalil et al. (2024), Persian Journal of Acarology 13(1): 29-75 | Tetranychidae of India | 453 | 921 | 186 |
| Mitra (2025), International Journal of Tropical Insect Science 45: 1041-1055 | Tenuipalpidae of India | 175 | 657 | 48 |
| Dyamanagouda et al. (2020), Journal of Entomology and Zoology Studies 8(6): 137-146 | Eriophyoidea of Tamil Nadu | 277 | 270 | 53 |
| Dyamanagouda et al. (2025) | Eriophyoidea of Karnataka (no hosts) | 49 | 0 | 37 |
| Som et al. (2025) | Eriophyoidea of South Bengal (no hosts) | 58 | 0 | 36 |
| Mandal et al. (2026) | Eriophyoidea of West Bengal | 230 | 270 | 100 |
| Mondal et al. (2023) and Karmakar (2016) | Tarsonemidae of West Bengal (no hosts) | 25 | 0 | 10 |
| Gupta & Bose (2017), Records of the Zoological Survey of India 117(2): 154-181 | mites on medicinal plants, South Bengal | 73 | 163 | 33 |
| Mitra et al. (2018), Acarologia 58(4): 850-854 | Tenuipalpidae of southern West Bengal | 17 | 39 | 14 |
| Papers dated 2022-2026 | new species and records after the book | 64 | 37 | 58 |

Of the 186 Chalil et al. pairs missing from the book layer, 5 are states the book prints but the parser missed; in 159 the state does not appear in the book's distribution text at all, and 22 are species the book does not list. Host lists are taken as each checklist prints them; the checklists are of the Indian fauna but do not always say whether every host was recorded in India. Of 2,357 host rows, 2,269 resolve to a plant species or genus; host text the splitter could not read (authorities, coordinates, collector names) is in `data/review/regional_hosts_unparsed.csv`.

### All layers combined

`data/combined/species_state_all_sources.csv`: 2,458 species x state pairs for 1,187 of the 1,221 checklist species. 1,451 pairs rest on one layer only, 845 on two and 162 on three or more. 732 pairs are not in the book layer (721 counting parent and child states as the same area): Tetranychidae 264, Eriophyidae 227, Tenuipalpidae 98, Phytoseiidae 84, Tarsonemidae 34, Diptilomiopidae 24, Tuckerellidae 1. Counts by layer are in `data/combined/summary.csv`.




## Host names (standardised)

Host names are printed in many forms: English, Hindi, Bengali and Gujarati local names, misspellings, scientific names with old genus names. `config/host_dictionary.txt` maps each printed string to an accepted taxon, plant family and standard common name, and `scripts/host_names.py` applies it in both builds. The new columns, present in `data/aicrp/aicrp_observations.csv` and `data/records/species_host.csv`, are:

- `host_taxon_std`: binomial, `Genus sp.`, a family, or a group label.
- `host_rank_std`: `species`, `genus`, `family`, `group` (weeds, ornamentals, forest plants and so on), `substrate` (stored products), `ambiguous` (a local name that could be more than one plant) or `unresolved`.
- `host_family`, `host_std_common`, `host_basis` (how the name was resolved) and `host_confidence` (`medium` for local names and context-based readings).
- `host_crop_type` (rule file `config/host_crop_type.txt`): `field_crop`, `vegetable`, `fruit`, `plantation_spice` (plantation, spice and industrial tree crops, including mulberry), `ornamental`, `medicinal_aromatic`, `fodder`, `tree_forest` (timber, avenue and forest trees, bamboo), `weed_wild`, `aquatic`, `stored_product`, or `not_assigned`. It is a broad grouping by where the plant is mainly grown or met, set by genus unless a species is listed on its own, so wild species of cultivated genera take the genus type.
- `host_check` (AICRP only, rows that print both a common and a scientific name): `agree`, `species_differs` or `genus_differs`.

Rules: the printed common name is looked up first; if it is only a genus or group, a printed scientific name in the same genus refines it; names that cannot be decided are left as `ambiguous` and listed in `data/review/aicrp_hosts_to_review.csv` (with the pairs where the printed common and scientific names point to different plants, for example green gram printed with *Cicer arietinum*). Scientific names are kept as printed apart from spelling fixes and a few old genus names; they are not matched against a plant-name database, so a synonym in the printed name stays as printed. `data/aicrp/aicrp_host_crosswalk.csv` lists every printed host string with the name it was given.

| Measure | AICRP layers | Gupta & Mondal (2023) |
| --- | ---: | ---: |
| Rows with a host | 4,809 | 1,569 (in India) |
| Rows resolved to species or genus | 4,553 | 1,473 |
| Distinct host species | 284 | |
| Plant families | 92 | 117 |

Repair of the 2020-21 Kalyani tables: abundance counts, diversity-index rows and district names had run into the host lists when the two-column text layer was read, and some host names were split across cells. `scripts/tools/clean_host_lists.py` removed 18 non-host rows, moved district names to the locality field and rejoined split names; every change is in `data/review/aicrp_host_list_repairs.csv`.

## Files

- `data/records/species_state.csv`: one row per species and Indian state.
- `data/records/species_host.csv`: one row per species and host. `host_as_printed` keeps the source text; `host_rank` is `species`, `genus`, `common_name`, `species_genus_expanded` or `undetermined_plant`; `in_india` is 0 for hosts the book lists as recorded outside India.
- `data/records/summary.csv`: the counts above.
- `data/regional/`: layer 11 records. `data/combined/`: all layers in one species x state table.
- `data/review/`: text the parser could not place. Nothing in these files is in the records.
- `data/raw/`: source files copied from the checklist repository at the commit pinned in `config/sources.json`.

## Rebuild

```bash
python scripts/fetch_sources.py
python scripts/build_records.py
```

Python standard library only. Then run `python scripts/build_aicrp.py` (AICRP layers) and `python scripts/build_regional.py` (layer 11 and the combined table), in that order.

## Limits

- `host_as_printed` keeps the source text. The standardised host columns come from a hand-made dictionary, not a plant-name database; local names marked `medium` confidence and the `ambiguous` rows need a check by someone who knows the region.
- The book prints hosts for phytophagous mites and habitats for most predatory mites. Habitat plants are not in this layer.
- State names follow the book (for example Orissa, Pondicherry). Records dated before state reorganisations are not reassigned.
- Records carry the book as their source, not the original paper behind each record.
