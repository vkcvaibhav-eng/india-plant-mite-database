# india-plant-mite-database

Literature-derived records of plant-associated mites in India: which species is recorded from which state and on which host plant, each row traced to its printed source.

This is the data repository for Paper 2 of the project *Agricultural mites in India*. Paper 1 (COI coverage and name reliability) lives in [india-agri-mite-coi](https://github.com/vkcvaibhav-eng/india-agri-mite-coi); its species checklist is the name backbone used here.

## Status (11 November 2026)

Two layers so far: Gupta & Mondal (2023), *Handbook: Plant Mites of India* (literature up to 2022, 1,249 numbered accounts), and the survey tables in the All India Coordinated Research Project on Agricultural Acarology annual report for 1996–98. The book layer is machine-parsed from an OCR transcription. The AICRP layer is typed by hand from the scan's text layer. Neither has been checked page by page against the printed source.

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
| Distinct host common names | 277 |
| Species × state pairs joined to the checklist | 169 |
| ...of which not in the Gupta & Mondal (2023) layer | 85 |

The 85 new pairs are mostly Uttar Pradesh (34), Tamil Nadu (10), Punjab (10) and Chandigarh (8). Species names in the six checklist families that do not join to the checklist (8 names, for example *Tetranychus evansi* from Hisar) are in `data/review/aicrp_names_not_in_checklist.csv`.

- `data/aicrp/aicrp_observations.csv`: one row per observation. `pairing` says what the table printed: `host_and_place_paired`, or `host_only` / `place_only` where the table gave a species its host list and its locality list separately. Those two lists are never crossed.
- `data/aicrp/aicrp_species_state_vs_gm2023.csv`: each joined species × state pair, and whether the book layer already has it.
- `data/aicrp/transcription/`: the typed source tables (`paired.txt`, `lists.txt`, `host_mites.txt`) and `blocks.csv` with the PDF and printed page of each table. The `note` column marks OCR noise that was corrected.
- `config/name_crosswalk.csv`: old-to-current name joins used for the checklist (for example *Amblyseius alstoniae* to *Euseius alstoniae*), each with its basis.

Limits of layer 2:
- Hisar does not say which of Haryana and Himachal Pradesh a record comes from, so its state is "Haryana; Himachal Pradesh (not split)" and it is left out of the state comparison.
- Navsari's 1996–98 survey section gives only sample counts and family names, so it is not in the records.
- The 1992–94 report is not yet included. Its survey tables are rotated scans that the text layer cannot read and need transcribing from the page images.
- Names marked "sp. nov." in the report are kept as printed. They are report names and are not counted as published species.
- Status words (High, Medium, Severe and so on) are the centres' own and are not comparable between centres.

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
