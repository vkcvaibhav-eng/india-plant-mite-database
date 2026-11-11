# india-plant-mite-database

Literature-derived records of plant-associated mites in India: which species is recorded from which state and on which host plant, each row traced to its printed source.

This is the data repository for Paper 2 of the project *Agricultural mites in India*. Paper 1 (COI coverage and name reliability) lives in [india-agri-mite-coi](https://github.com/vkcvaibhav-eng/india-agri-mite-coi); its species checklist is the name backbone used here.

## Status (11 November 2026)

Ten layers so far: Gupta & Mondal (2023), *Handbook: Plant Mites of India* (literature up to 2022, 1,249 numbered accounts), and the survey tables in the All India Coordinated Research Project on Agricultural Acarology (AICRP) annual reports for 1996–98, 1992–94, 1990–91, 1989 (the Second Workshop report) and 1988 (the First Workshop report). The book layer is machine-parsed from an OCR transcription. The AICRP layers are typed by hand, the 1996–98 report from the scan's text layer and the 1990–91 report from the page images. The 1988, 1989 and 1992–94 reports were typed from the page images as well. None has been checked page by page against the printed source.

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

### Layer 7: AICRP First Group Meeting report, December 1990 (survey chapter, printed pp. 139-154)

Survey tables from six centres: Bangalore's species list with host and place (Karnataka), Kalyani's 50-host table for West Bengal, Bihar and Odisha (no place per row) with stigmaeid and tarsonemid tables that have places and months, Ludhiana's Table 5 of 26 species with separate host and locality lists, Coimbatore's district tables for Tamil Nadu and Kerala, and Navsari's family-level text. Pusa is text only; Varanasi and Hisar sent no report. Notes are in `data/aicrp/transcription/NOTES_1990-group-meeting.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 275 |
| Distinct mite species names | 64 |
| Distinct host names | 129 |

Combined AICRP layers: 3,786 observation rows, 346 species x state pairs, 190 of them not in the Gupta & Mondal (2023) layer.

### Layer 8: AICRP Progress Report 2020-21 (XVII Group Meeting, survey chapter III.1)

The first of the modern reports. Kalyani's tables for West Bengal and Bihar make up most of the rows (species, host habitat and districts), with Navsari's table for South Gujarat, Ludhiana's surveillance table, Jorhat's list for Assam and Thrissur's table of spider mites in Kerala. Bangalore, Coimbatore and Mashobra give counts or experiments only. Notes are in `data/aicrp/transcription/NOTES_2020-21.md`. The big tables were read from the text layer with `scripts/tools/layout_table.py` and checked by eye.

| Measure | Value |
| --- | ---: |
| Observation rows | 1,905 |
| Distinct mite species names | 90 |
| Distinct host names | 460 |

Combined AICRP layers: 5,691 observation rows, 440 species x state pairs, 250 of them not in the Gupta & Mondal (2023) layer.

### Layer 9: AICRP Progress Report 2021-22 (XVIII Group Meeting, survey chapter III.1)

Smaller than the previous year: Coimbatore's place, host and mite table, Ludhiana's surveillance table for Punjab and nearby states, Jorhat's new rows and Thrissur's table of 16 spider mite species on 35 hosts in Kerala. Navsari's table repeats 2020-21, and Kalyani and Mashobra give narrative or counts. Notes are in `data/aicrp/transcription/NOTES_2021-22.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 181 |
| Distinct mite species names | 30 |
| Distinct host names | 84 |

Combined AICRP layers: 5,872 observation rows, 453 species x state pairs, 261 of them not in the Gupta & Mondal (2023) layer.

### Layer 10: AICRP Progress Report 2024-25 (XXI Group Meeting, chapter on diversity of plant-associated mites)

The most recent report in the set. Seven centres give species and host tables: Bangalore, Coimbatore, Navsari (new host and state records), Ludhiana (67 predatory mite species on plants across Punjab and the neighbouring states), Mashobra (Himachal Pradesh), Jorhat (Assam) and Thrissur (Kerala). The tables rarely give a place, so most rows are host-level records for a state. Notes are in `data/aicrp/transcription/NOTES_2024-25.md`.

| Measure | Value |
| --- | ---: |
| Observation rows | 757 |
| Distinct mite species names | 122 |
| Distinct host names | 197 |

Combined AICRP layers: 6,629 observation rows, 496 species x state pairs, 292 of them not in the Gupta & Mondal (2023) layer.




## Files

- `data/records/species_state.csv`: one row per species and Indian state.
- `data/records/species_host.csv`: one row per species and host. `host_as_printed` keeps the source text; `host_rank` is `species`, `genus`, `common_name`, `species_genus_expanded` or `undetermined_plant`; `in_india` is 0 for hosts the book lists as recorded outside India.
- `data/records/summary.csv`: the counts above.
- `data/review/`: text the parser could not place. Nothing in these files is in the records.
- `data/raw/`: source files copied from the checklist repository at the commit pinned in `config/sources.json`.

## Rebuild

```bash
python scripts/fetch_sources.py
python scripts/build_records.py
```

Python standard library only. Add `python scripts/build_aicrp.py` after `build_records.py` to build the AICRP layer.

## Limits

- Host names are as printed. Plant names have not been checked against a plant-name authority, so spelling variants and synonyms of one plant are still separate rows.
- The book prints hosts for phytophagous mites and habitats for most predatory mites. Habitat plants are not in this layer.
- State names follow the book (for example Orissa, Pondicherry). Records dated before state reorganisations are not reassigned.
- Records carry the book as their source, not the original paper behind each record.
