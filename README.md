# india-plant-mite-database

Literature-derived records of plant-associated mites in India: which species is recorded from which state and on which host plant, each row traced to its printed source.

This is the data repository for Paper 2 of the project *Agricultural mites in India*. Paper 1 (COI coverage and name reliability) lives in [india-agri-mite-coi](https://github.com/vkcvaibhav-eng/india-agri-mite-coi); its species checklist is the name backbone used here.

## Status (13 November 2026)

Eleven layers so far: Gupta & Mondal (2023), *Handbook: Plant Mites of India* (literature up to 2022, 1,249 numbered accounts); the survey tables in the All India Coordinated Research Project / All India Network Project on Agricultural Acarology reports from 1988 to 2024-25 (layers 2-10, typed by hand from the reports; the older reports are available on Krishikosh and the recent progress reports are published); and the regional and family checklists used for the Paper 1 species list (layer 11). Every layer is joined to the Paper 1 checklist, and `data/combined/species_state_all_sources.csv` puts all of them in one species x state table.

The data and analyses were audited on 12-13 November 2026. What was checked, what was corrected and how to repeat the checks is in [Audit](#audit-12-13-november-2026).

### Layer 1: Gupta & Mondal (2023)

| Measure | Value |
| --- | ---: |
| Accounts | 1,249 |
| Accounts linked to a checklist species | 1,088 |
| Species × state records | 2,003 |
| ...of which read by the parser | 1,966 |
| ...of which added by hand from the printed text (`config/gm2023_state_additions.csv`) | 37 |
| States and union territories | 31 |
| Species × host records | 1,588 |
| Distinct host names | 918 |
| Host text not parsed (review queue) | 117 |
| Locality text not matched to a state (review queue) | 46 |
| Accounts with no host text | 404 |

The 37 hand-added states are places the book prints in a form the parser does not read: a city or valley instead of a state ("India (Kolkata)", "India (Kashmir valley)"), a state name broken by the text layer ("re Nadu"), and Lakshadweep. Each has its basis in the file and `state_basis` in `data/records/species_state.csv` says `added_by_hand`. `data/records/species_in_book.csv` lists every checklist species the book has an account for, with the number of states read and, for the 26 species with no state, the distribution text as printed ("throughout the country", "Cosmopolitan").

The 161 unlinked accounts are the 150 accounts of predatory families other than Phytoseiidae, which the Paper 1 checklist does not cover, and 11 genus-level `sp.`/`spp.` accounts.

### Layer 2: AICRP annual report 1996–98 (survey chapter, printed pp. 185–213)

Survey tables from seven centres: Bangalore, Coimbatore, Ludhiana, Hisar, Varanasi, Kalyani and Pusa. This is project-report literature, so it adds records the book may not carry.

Species names in the six checklist families that do not join to the checklist (for example *Tetranychus evansi* from Hisar, and *Tenuipalpus convolvulae* from Coimbatore) are in `data/review/aicrp_names_not_in_checklist.csv`.

- `data/aicrp/aicrp_observations.csv`: one row per observation, all AICRP reports (`report` column). `obs_id` is regenerated at each build, so do not cite it. `pairing` says what the table printed: `host_and_place_paired`, or `host_only` / `place_only` where the table gave a species its host list and its locality list separately. Those two lists are never crossed.
- `data/aicrp/aicrp_species_state_vs_gm2023.csv`: each joined species × state pair with its `book_status` (see *Comparison with the handbook*).
- `data/aicrp/transcription/`: the typed source tables (`paired.txt`, `lists.txt`, `host_mites.txt`) and `blocks.csv` with the PDF and printed page of each table. The `note` column marks OCR noise that was corrected.
- `config/name_crosswalk.csv`: old-to-current name joins used for the checklist (for example *Amblyseius alstoniae* to *Euseius alstoniae*), each with its basis.

Limits of layer 2:
- Hisar does not say which of Haryana and Himachal Pradesh a record comes from, so its state is "Haryana; Himachal Pradesh (not split)" and it is left out of the state comparison (`state_counts` = 0).
- Navsari's 1996–98 survey section gives only sample counts and family names, so it is not in the records.
- Names marked "sp. nov." in the report are kept as printed. They are report names and are not counted as published species.
- Status words (High, Medium, Severe and so on) are the centres' own and are not comparable between centres.

### Layer 3: AICRP annual report 1990–91 (survey chapter I and taxonomic chapter II, printed pp. 9–58)

Seven centres: Kalyani, Coimbatore, Navsari, Varanasi, Ludhiana, Pusa and Hisar from the survey chapter, plus Bangalore from Chapter II (host × place table, with localities in Andhra Pradesh and Karnataka). Chapter II also adds Kalyani, Pusa (phytoseiids of Bihar) and Hisar (taxonomy tables 13–17). The tables were typed from the page images; the transcription notes, including rows left out and uncertain readings, are in `data/aicrp/transcription/NOTES_1990-91.md`.

Navsari, Hisar (Table 8) and Kalyani (Table 1) print no locality per row, so their state is the centre's state. Navsari rows are one per slide, so a host and mite can repeat. Hisar's Chapter II tables 13–17 (block C11) aggregate the same Haryana collection as Table 8 (block C07) with specimen counts, so the two blocks must not be summed.

### Layer 4: AICRP First Workshop report, October 1988 (printed pp. 24–89, 112)

The report covers 1987–88. It gives usable survey tables for six centres: Bangalore (identifications with host and locality), Coimbatore (40 mite × host rows, no locality), Ludhiana (Table I, mite × host × locality), Hisar (material identified at Ludhiana), Pusa (a brief survey, with population classes) and Varanasi (the largest part: mite–host indexes for fruit, vegetable, field/ornamental crops and aquatic weeds across Uttar Pradesh districts). Kalyani's survey is narrative only (36 crops in ten districts of West Bengal, no species list) and Navsari gives only an abstract, so neither is in the records. Hisar's own report was not received. Notes on rows left out and uncertain readings are in `data/aicrp/transcription/NOTES_1988.md`.

Varanasi's tables print hosts and districts as separate lists for each mite, so they are recorded as `host_only` and `place_only` rows and never crossed. Almora and Nainital were in Uttar Pradesh in 1988 and are recorded under Uttarakhand, which is why that state appears. Several mite names are species described in the report as new (marked `sp. nov.`); they are kept as printed and are not counted as published species.

### Layer 5: AICRP report 1992–94 (survey chapter, printed pp. 40–62)

Most of this report is experiments. Its survey material is tables from Bangalore (20 crop-place-mite rows with status), Coimbatore (9 rows), Navsari (four rice species), Ludhiana (Table A: 33 species with hosts, localities and specimen counts for Punjab and Himachal Pradesh), Varanasi (Table B: 14 hosts), Pusa (Table C by month and village, and Table 29 on litchi erineum mite by district), Kalyani (a species list for West Bengal without hosts) and the pigeonpea sterility mosaic survey (Aceria cajani at district level in Karnataka). Notes on rows left out and uncertain readings are in `data/aicrp/transcription/NOTES_1992-94.md`.

Ludhiana prints hosts and localities as separate lists for each species, so they are recorded as `host_only` and `place_only` rows and never crossed; Varanasi's multi-locality hosts are handled the same way. Kalyani's species list has no host or place, so its state is the centre's state.

### Layer 6: AICRP Second Workshop report, December 1989 (progress for 1988–89)

Mostly technical programmes and experiments. The survey material is Kalyani's table of 57 hosts with places, dates and mites (the largest part), Coimbatore's list of 68 eriophyoid, tetranychid and tenuipalpid species and hosts for Tamil Nadu and Kerala (no locality), Ludhiana's table of mites on 19 hosts in Punjab and Himachal Pradesh, Bangalore's taxonomic notes with host and place, Navsari's host and mite index for Gujarat with survey results at Surat and Bharuch, and a note on Petrobia latens outbreaks in Rajasthan. Varanasi, Hisar and Pusa give families only or nothing usable. Notes on rows left out and uncertain readings are in `data/aicrp/transcription/NOTES_1989.md`.

Coimbatore and Bangalore cover two states each without saying which record is from which, so rows without a place keep a "(not split)" state and are left out of the state comparison. Kalyani's hosts and places are printed as separate lists, so multi-place hosts are recorded as `host_only` and `place_only` rows.

### Layer 7: AICRP First Group Meeting report, December 1990 (survey chapter, printed pp. 139-154, and disease chapters I-III)

Survey tables from six centres: Bangalore's species list with host and place (Karnataka), Kalyani's 50-host table for West Bengal, Bihar and Odisha (no place per row) with stigmaeid and tarsonemid tables that have places and months, Ludhiana's Table 5 of 26 species with separate host and locality lists, Coimbatore's district tables for Tamil Nadu and Kerala, and Navsari's family-level text. Pusa is text only; Varanasi and Hisar sent no report. The disease chapters add survey and natural-incidence records: mites on litchi (Kalyani, Pusa), Aceria mangiferae at seven mango-growing places in West Bengal with the mite complex of mango buds, and Aceria cajani on pigeonpea at Bangalore, Chitradurga, Coimbatore and Navsari. Spray and resurgence experiments (chapter IV) are not records and are left out. Notes are in `data/aicrp/transcription/NOTES_1990-group-meeting.md`.

### Layer 8: AICRP Progress Report 2020-21 (XVII Group Meeting, survey chapter III.1)

The first of the modern reports. Kalyani's tables for West Bengal and Bihar make up most of the rows (species, host habitat and districts), with Navsari's table for South Gujarat, Ludhiana's surveillance table, Jorhat's list for Assam and Thrissur's table of spider mites in Kerala. Mashobra's Table 157 gives European red mite, two-spotted mite and flat mites by host and locality across Himachal Pradesh. Bangalore and Coimbatore give counts only. Notes are in `data/aicrp/transcription/NOTES_2020-21.md`. The big tables were read from the text layer with `scripts/tools/layout_table.py` and checked by eye.

### Layer 9: AICRP Progress Report 2021-22 (XVIII Group Meeting, survey chapter III.1)

Smaller than the previous year: Coimbatore's place, host and mite table, Ludhiana's surveillance table for Punjab and nearby states, Jorhat's new rows and Thrissur's table of 16 spider mite species on 35 hosts in Kerala. Navsari's table repeats 2020-21 and Kalyani gives narrative only. Mashobra's status tables for Himachal Pradesh (fruits, vegetables, ornamentals, medicinal plants by locality and month) add European red mite and two-spotted mite by host and place, with flat mites at family level. Notes are in `data/aicrp/transcription/NOTES_2021-22.md`.

### Layer 10: AICRP Progress Report 2024-25 (XXI Group Meeting, chapter on diversity of plant-associated mites)

The most recent report in the set. Seven centres give species and host tables: Bangalore, Coimbatore, Navsari (new host and state records), Ludhiana (67 predatory mite species on plants across Punjab and the neighbouring states), Mashobra (Himachal Pradesh), Jorhat (Assam) and Thrissur (Kerala). The tables rarely give a place, so most rows are host-level records for a state. Notes are in `data/aicrp/transcription/NOTES_2024-25.md`.

### AICRP layers together

| Report | Observation rows | Mite species names | Host names as printed | Checklist species | Species × state pairs | Pairs that add to the handbook |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1988 (First Workshop) | 510 | 105 | 124 | 72 | 91 | 38 |
| 1989 (Second Workshop) | 545 | 95 | 181 | 75 | 69 | 25 |
| 1990 (First Group Meeting) | 322 | 73 | 130 | 55 | 62 | 18 |
| 1990-91 | 1,000 | 95 | 255 | 69 | 148 | 54 |
| 1992-94 | 347 | 79 | 72 | 58 | 115 | 30 |
| 1996-98 | 1,109 | 128 | 310 | 83 | 169 | 48 |
| 2020-21 | 1,978 | 88 | 360 | 71 | 132 | 57 |
| 2021-22 | 317 | 31 | 114 | 31 | 47 | 25 |
| 2024-25 | 757 | 122 | 197 | 80 | 93 | 56 |
| All nine reports | 6,885 | | | | 487 | 224 |

The table is `data/analysis/when_aicrp_by_report.csv`. A pair found in several reports is counted in each row but once in the total.

**Which state a record belongs to.** Each observation row carries `state_evidence` and `state_counts`. A row counts towards a species × state pair only when the report ties that mite to that state: the row prints a place, or the whole table is for one state. Where a table prints a mite's hosts and its localities as two separate lists, the host rows take the states of that line's localities; if the line's localities fall in more than one state, the host rows are marked "(not split)" and do not count. Rows of a centre that covers several states and prints no place do not count either.

**Names.** Printed names are joined to the checklist through `config/name_crosswalk.csv`. *Tetranychus cinnabarinus* (175 rows) is joined to *Tetranychus urticae*, following the Paper 1 checklist, where it is an uncounted alias; the printed name stays in `mite_name`. Two joins rest on an assumption and are marked `crosswalk_assumed`: *Eriophyes moringae* to *Aculus moringeae* and *Eriophyes ailanthes* to *Aceria ailanthae*.

### Comparison with the handbook

`scripts/gm_compare.py` puts every species × state pair of the other layers into one of five classes:

| `book_status` | Meaning | AICRP pairs | All layers |
| --- | --- | ---: | ---: |
| `state_in_book` | the book has this species from this state | 209 | 1,759 |
| `parent_or_child_state_in_book` | the book has the parent or child state (Telangana/Andhra Pradesh, Uttarakhand/Uttar Pradesh, Jharkhand/Bihar, Chhattisgarh/Madhya Pradesh, Chandigarh/Punjab and Haryana) | 7 | 11 |
| `book_gives_no_state` | the book lists the species but prints no state ("throughout the country") | 47 | 84 |
| `new_state_for_a_book_species` | the book lists the species with states, but not this one | 213 | 466 |
| `species_not_in_book` | the book has no account for the species | 11 | 148 |
| Total | | 487 | 2,468 |

Only the last two classes are counted as additions to the handbook: 224 of the 487 AICRP pairs and 614 of the 2,468 pairs of all layers. A species the book calls widespread without naming states is not treated as new for a state.

State names are compared through `scripts/states_norm.py`, which gives one spelling (Odisha for the book's Orissa, Puducherry for Pondicherry) and lists parent and child states. The record files keep the state as the source prints it.

### Layer 11: regional and family checklists

The ten checklist extracts that built the Paper 1 species list, copied from india-agri-mite-coi at the pinned commit, turned into species x state and species x host rows (`scripts/build_regional.py`).

| Source | Coverage | Species x state pairs | Species x host rows | New state for a book species | Species not in the book |
| --- | --- | ---: | ---: | ---: | ---: |
| Chalil et al. (2024), Persian Journal of Acarology 13(1): 29-75 | Tetranychidae of India | 456 | 921 | 107 | 21 |
| Mitra (2025), International Journal of Tropical Insect Science 45: 1041-1055 | Tenuipalpidae of India | 175 | 657 | 21 | 10 |
| Dyamanagouda et al. (2020), Journal of Entomology and Zoology Studies 8(6): 137-146 | Eriophyoidea of Tamil Nadu | 277 | 270 | 50 | 2 |
| Dyamanagouda et al. (2025) | Eriophyoidea of Karnataka (no hosts) | 49 | 0 | 27 | 10 |
| Som et al. (2025) | Eriophyoidea of South Bengal (no hosts) | 58 | 0 | 30 | 5 |
| Mandal et al. (2026) | Eriophyoidea of West Bengal | 230 | 270 | 68 | 30 |
| Mondal et al. (2023) and Karmakar (2016) | Tarsonemidae of West Bengal (no hosts) | 25 | 0 | 1 | 8 |
| Gupta & Bose (2017), Records of the Zoological Survey of India 117(2): 154-181 | mites on medicinal plants, South Bengal | 73 | 163 | 20 | 9 |
| Mitra et al. (2018), Acarologia 58(4): 850-854 | Tenuipalpidae of southern West Bengal | 17 | 39 | 7 | 6 |
| Papers dated 2022-2026 | new species and records after the book | 64 | 37 | 0 | 58 |

Three states that Chalil et al. (2024) print in a form the splitter did not read are added from `config/regional_state_additions.csv` (*Bryobia rubrioculus* in Jammu & Kashmir, *Tetranychus gloveri* in Kerala and Karnataka).

**Host lists of the two national checklists.** Chalil et al. (2024) and Mitra (2025) print, for widespread species, the host list known worldwide, not only the hosts recorded in India (for example *Oligonychus thelytokus* on *Caloncoba welwitschii*, *Brevipalpus essigi* on *Aucuba*, *Fuchsia* and *Kentia*). Their 1,578 host rows are therefore marked `host_scope = checklist_list_includes_hosts_outside_india` and are left out of every host analysis; the 779 host rows of the regional lists and papers are `indian_record`. Of 2,357 host rows, 2,249 resolve to a plant species or genus; host text the splitter could not read (authorities, coordinates, collector names) is in `data/review/regional_hosts_unparsed.csv`.

### All layers combined

`data/combined/species_state_all_sources.csv`: 2,468 species x state pairs for 1,192 of the 1,221 checklist species. 1,446 pairs rest on one layer only, 859 on two and 163 on three or more. 614 pairs add to the handbook (466 new states for species the book lists, 148 pairs for species it does not list): Eriophyidae 218, Tetranychidae 184, Phytoseiidae 79, Tenuipalpidae 76, Tarsonemidae 32, Diptilomiopidae 24, Tuckerellidae 1. Of the 614, 188 rest on AICRP reports alone, most of them from Uttar Pradesh (31), Gujarat (28), Assam (21), Haryana (16), Tamil Nadu (14) and Punjab (13). The columns `book_status`, `in_aicrp` and `only_aicrp` mark each pair. Counts by layer are in `data/combined/summary.csv`.

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
| Rows with a host | 5,103 | 1,569 (in India) |
| Rows resolved to species or genus | 4,839 | 1,480 |
| Distinct host species | 287 | 653 |
| Plant families | 93 | 117 |

A printed binomial is accepted as a host only when its genus is in the dictionary's genus table. An earlier rule that accepted any two-word string as a plant name was removed in the audit, because it had let through text such as "Not stated" and "House sparrow".

Repair of the 2020-21 Kalyani tables: abundance counts, diversity-index rows and district names had run into the host lists when the two-column text layer was read, and some host names were split across cells. `scripts/tools/clean_host_lists.py` removed 18 non-host rows, moved district names to the locality field and rejoined split names; every change is in `data/review/aicrp_host_list_repairs.csv`.

## Analyses (Paper 2)

`python scripts/analysis/analyse.py` writes the tables in `data/analysis/`; `python scripts/analysis/verify_numbers.py` recomputes the headline numbers a second way and stops with an error if any differs; `python scripts/analysis/figures.py` draws `figures/fig1`–`fig5` (300 dpi PNG). Counts use the 1,221 counted species of the Paper 1 checklist, in the Paper 1 groups. Species × state and species × host pairs are sets, so a collection repeated in two reports counts once. `data/analysis/findings_summary.csv` lists every headline number.

**Where** (`where_*.csv`, Fig. 1). Records come from 34 states and union territories, but three states hold most of the fauna: West Bengal 515 species, Tamil Nadu 428 and Karnataka 260, together 917 of the 1,192 species with a state. 793 species (66.5% of those with a state) are known from one state only. Central India (Madhya Pradesh, Chhattisgarh) has 25 species, Maharashtra 17, Gujarat 59 and the eight north-eastern states 206. In 25 of the 31 states outside the top three, more than 60% of the species × state pairs rest on a single source.

**When** (`when_*.csv`, Fig. 2). 1,171 species have a description year (50 lack one). The 1980s is the peak decade (381 species, 266 of them Eriophyoidea); 643 species date from 1970–1999 and 240 from 2000 onward. The 2020s already have 131, mostly Phytoseiidae (73) and Tarsonemidae (30), nearly all described from West Bengal. The year is the year a species was described, anywhere, not the year of its first Indian record. The AICRP reports list 31–83 checklist species each.

**Who** (`who_*.csv`). The authorities carry 201 author names after spelling variants are merged (`config/author_aliases.csv`). Five names appear in the authority of 690 species (56.5%): Mohanasundaram 282, Chakrabarti 145, Gupta 138, Karmakar 127, Mondal 65. Mohanasundaram is in the authority of 42% of the Indian Eriophyoidea and Chakrabarti of 25%; Karmakar of 67% of the Tarsonemidae and 28% of the Phytoseiidae. Authors are surnames, so "Gupta" and "Mondal" can join more than one person.

**Hosts** (`hosts_*.csv`, Figs 3–4). Hosts combine the book, the AICRP reports and the regional lists and papers; the host lists of the two national checklists are left out because they include hosts recorded outside India. Breadth is counted in host genera. Of 789 phytophagous species with a host genus, 581 (73.6%) are known from one host genus only (Eriophyoidea 90%, Tarsonemidae 81%, Tenuipalpidae 40%, Tetranychidae 32%); 13 species have more than 20. `hosts_sensitivity.csv` shows that the one-genus share hardly moves with the choice of layers (72.7% with the national checklists included, 83.2% without the book), while the count of very broad species does (23 with the national checklists). The host genera with most phytophagous species are *Citrus* (54), *Ficus* (51), *Prunus* (27), *Rosa* (27) and *Psidium* (26). The ranking is by genus because the sources name many hosts only to genus ("Citrus sp."), so species-level ranks (`hosts_top_plants.csv`) are not comparable between plants. 230 of the 332 Phytoseiidae have no plant in the data, because the book's habitat lines for predators are not yet parsed. Crop types are a broad grouping by genus; 204 phytophagous species are on hosts without an assigned type.

**Link to Paper 1** (`link_*.csv`, Fig. 5). 137 checklist species have a COI barcode. Barcoded species are recorded from more states (median 3 against 1; Mann-Whitney P = 7 × 10⁻³⁵) and on more host genera (2 against 1). The share with a barcode rises from 4.3% of species known from one state (34 of 793) to 69% of species known from ten or more (27 of 39). The association does not show cause: the widely recorded species are also the pest species most studied.

## Audit (12-13 November 2026)

Every layer and every analysis was rechecked. The checks can be repeated:

- **Transcription against the PDFs.** `scripts/tools/verify_against_pdf.py` tests whether the mite epithet, host and place of each AICRP row occur together on the same or the next page of the report's text layer. It was run on the four reports that have a text layer (1996-98, 2020-21, 2021-22, 2024-25): 3,919 of 4,161 rows were found together at once. Every row that failed was read against the PDF; all were spellings normalised during typing (Zizyphus to Ziziphus, Bauhenia to Bauhinia), page breaks, or the Mashobra codes (ERM, TSM). For the six scanned reports, 12 pages drawn at random (about 150 transcription lines) were compared with the page images; all matched, and one family-level row that lacked its place was completed.
- **Handbook parser.** All 1,966 states the parser read were confirmed against the printed distribution text (allowing for the book's own spellings such as Maharastra and Lakshadwip); 37 states it had missed were added by hand. All 1,588 host strings occur in the raw text, and 14 accounts drawn at random were read in full.
- **Name joins.** All 85 joins that are not exact matches follow the Paper 1 checklist or a documented crosswalk line; two are assumptions and are flagged.
- **Numbers.** `scripts/analysis/verify_numbers.py` computes 32 headline numbers from the layer files with its own state table and its own handbook comparison, sharing no code with `analyse.py`. All 32 agree.
- **Rebuild.** Running the whole chain twice gives byte-identical output for all 53 data files.

Corrections made in the audit:

| What was wrong | Effect | Fix |
| --- | --- | --- |
| Species the handbook lists without a state ("throughout the country", 26 species) were treated as absent from the handbook | AICRP additions to the handbook were overstated: 293, now 224. Additions of all layers: 732, now 614 | five-class comparison in `scripts/gm_compare.py` |
| The handbook parser missed 37 printed states | the same overstatement | `config/gm2023_state_additions.csv` |
| Host rows of list-form tables took the centre's state | two false Punjab records (*Panonychus ulmi*, *Petrobia latens*) | `state_evidence` rule in `scripts/build_aicrp.py` |
| Host lists of the two national checklists include hosts outside India | species with more than 20 host genera: 24, now 13; the ranking of host plants changed | `host_scope` column; those rows left out of host analyses |
| Any two-word string was accepted as a plant binomial | junk hosts ("Not stated", "House sparrow") | rule removed from `scripts/host_names.py` |
| *Ariocarpus* (a misreading of *Artocarpus*) placed in Cactaceae | wrong family for a few rows | `config/host_dictionary.txt` |
| *Tetranychus cinnabarinus* rows dropped from the analyses | 175 AICRP rows unused | joined to *Tetranychus urticae*, as in Paper 1 |
| Author names with spelling variants counted separately | author counts slightly low (Mohanasundaram 278, now 282) | `config/author_aliases.csv` |
| Host genus crop type taken from the first species in file order | *Saccharum* shown as a weed | taken from the most-recorded species of the genus |

The findings that did not move: the three-state concentration, the share of species known from one state (66%), the 1980s peak, the share of phytophagous species on one host genus (73-74%) and the link between how widely a species is recorded and whether it has a barcode.

## Files

- `data/records/species_state.csv`: one row per species and Indian state.
- `data/records/species_host.csv`: one row per species and host. `host_as_printed` keeps the source text; `host_rank` is `species`, `genus`, `common_name`, `species_genus_expanded` or `undetermined_plant`; `in_india` is 0 for hosts the book lists as recorded outside India.
- `data/records/species_in_book.csv`: the checklist species the book has an account for.
- `data/records/summary.csv`: the counts above.
- `data/regional/`: layer 11 records. `data/combined/`: all layers in one species x state table.
- `data/analysis/`: the tables behind the analyses. `figures/`: the five figures.
- `config/`: the hand-made files every build reads (name crosswalk, host dictionary, crop types, state additions, author aliases), each line with its basis.
- `data/review/`: text the parser could not place. Nothing in these files is in the records.
- `data/raw/`: source files copied from the checklist repository at the commit pinned in `config/sources.json`.

## Rebuild

```bash
python scripts/fetch_sources.py
python scripts/build_records.py
```

Python standard library only. Then run `python scripts/build_aicrp.py` (AICRP layers) and `python scripts/build_regional.py` (layer 11 and the combined table), in that order, then `scripts/analysis/analyse.py`, `scripts/analysis/verify_numbers.py` and `scripts/analysis/figures.py`. The analyses need `scipy` and the figures `matplotlib`; the builds need the standard library only.

## Limits

- `host_as_printed` keeps the source text. The standardised host columns come from a hand-made dictionary, not a plant-name database; local names marked `medium` confidence and the `ambiguous` rows need a check by someone who knows the region.
- The book prints hosts for phytophagous mites and habitats for most predatory mites. Habitat plants are not in this layer.
- State names follow the book (for example Orissa, Pondicherry). Records dated before state reorganisations are not reassigned.
- Records carry the book as their source, not the original paper behind each record.
- An addition to the handbook means the pair is not in the handbook's text. It does not mean the record is new to science: the original paper may predate the handbook.
- *Tetranychus cinnabarinus* records are counted under *Tetranychus urticae*. Anyone who treats the two as separate species should filter on `mite_name`.
- The checklist comes from Paper 1 at a pinned commit. Three slips seen there during the audit are not corrected here: the year of *Larvacarus transitans* (1992 for 1922), the name "Aaphyllisa parindiae" (for *Acaphyllisa*), and spelling variants in some authorities (handled here only for the author counts).
