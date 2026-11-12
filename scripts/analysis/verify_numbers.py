"""Second, separate computation of the headline numbers in data/analysis/findings_summary.csv.

analyse.py works from the combined table and shared helper modules. This script goes back to the layer files
(the book records, the AICRP observations, the regional rows, the raw checklist and the raw book accounts),
uses its own state-name table and its own handbook comparison, and stops with an error if any number differs.
Run it after analyse.py.
"""
import csv, re, sys, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[2]


def read(rel):
    with open(ROOT / rel, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


CANON = {"Orissa": "Odisha", "Pondicherry": "Puducherry", "Andaman and Nicobar Islands": "Andaman & Nicobar Islands"}
PARENTS = {"Telangana": {"Andhra Pradesh"}, "Uttarakhand": {"Uttar Pradesh"}, "Jharkhand": {"Bihar"},
           "Chhattisgarh": {"Madhya Pradesh"}, "Chandigarh": {"Punjab", "Haryana"}}
canon = lambda s: CANON.get(s.strip(), s.strip())

checklist = [r for r in read("data/raw/species_list.csv") if r["counted"] == "1"]
ids = {r["species_id"] for r in checklist}
grp = {r["species_id"]: r["group"] for r in checklist}

# ---------------------------------------------------------------- species x state pairs, layer by layer
book = collections.defaultdict(set)
for r in read("data/records/species_state.csv"):
    if r["species_id"] in ids:
        book[r["species_id"]].add(canon(r["state"]))
aicrp = collections.defaultdict(set)
for r in read("data/aicrp/aicrp_observations.csv"):
    if r["species_id"] in ids and r["state"] and "(not split)" not in r["state"] and r["state_counts"] == "1":
        aicrp[r["species_id"]].add(canon(r["state"]))
regional = collections.defaultdict(set)
for r in read("data/regional/regional_species_state.csv"):
    if r["species_id"] in ids:
        regional[r["species_id"]].add(canon(r["state"]))
allst = collections.defaultdict(set)
for d in (book, aicrp, regional):
    for k, v in d.items():
        allst[k] |= v
pairs = {(s, st) for s, v in allst.items() for st in v}
by_state = collections.Counter(st for _, st in pairs)
top3 = [st for st, _ in by_state.most_common(3)]

# which species have an account in the book: link the raw accounts by name, independently of species_in_book.csv
name_ids = collections.defaultdict(set)
for r in read("data/raw/species_list_names.csv"):
    name_ids[r["name"]].add(r["species_id"])
listed = set()
for a in read("data/raw/gupta_mondal2023_all.csv"):
    hit = name_ids.get(a["species"], set())
    if len(hit) == 1:
        listed |= hit & ids


def status(s, st):
    if st in book[s]: return "state_in_book"
    if s not in listed: return "species_not_in_book"
    if not book[s]: return "book_gives_no_state"
    rel = PARENTS.get(st, set()) | {c for c, ps in PARENTS.items() if st in ps}
    if rel & book[s]: return "parent_or_child_state_in_book"
    return "new_state_for_a_book_species"


stat = collections.Counter(status(s, st) for s, st in pairs)
aicrp_pairs = {(s, st) for s, v in aicrp.items() for st in v}
aicrp_stat = collections.Counter(status(s, st) for s, st in aicrp_pairs)
only_aicrp_new = sum(1 for s, st in aicrp_pairs if st not in book[s] and st not in regional[s]
                     and status(s, st) in ("new_state_for_a_book_species", "species_not_in_book"))

# ---------------------------------------------------------------- years and authors
years = [int(r["year"]) for r in checklist if re.fullmatch(r"\d{4}", r["year"].strip())]
dec = collections.Counter(y // 10 * 10 for y in years)
peak = max(dec, key=dec.get)
fixes = read("config/author_aliases.csv")
count, per_species = collections.Counter(), {}
for r in checklist:
    text = r["authority"]
    for f in fixes:
        if f["kind"] == "text":
            text = text.replace(f["printed"], f["read_as"])
    text = re.sub(r"et al\.?", " ", text.replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " "))
    names = []
    for part in re.split(r"&|,|\band\b", text):
        part = part.strip(" .")
        if part and not part.isdigit():
            part = next((f["read_as"] for f in fixes if f["kind"] == "name" and f["printed"] == part), part)
            if part not in names:
                names.append(part)
    per_species[r["species_id"]] = names
    count.update(names)
five = [n for n, _ in sorted(count.items(), key=lambda x: -x[1])[:5]]
with_five = sum(1 for names in per_species.values() if set(names) & set(five))
erio = [r["species_id"] for r in checklist if r["group"] == "Eriophyoidea"]

# ---------------------------------------------------------------- hosts (Indian records only)
gen = collections.defaultdict(set)
for r in read("data/records/species_host.csv"):
    if r["in_india"] == "1" and r["host_rank_std"] in ("species", "genus"):
        gen[r["species_id"]].add(r["host_taxon_std"].split()[0])
for r in read("data/aicrp/aicrp_observations.csv"):
    if r["host_rank_std"] in ("species", "genus"):
        gen[r["species_id"]].add(r["host_taxon_std"].split()[0])
for r in read("data/regional/regional_species_host.csv"):
    if r["source"] not in ("chalil2024", "mitra2025") and r["host_rank_std"] in ("species", "genus"):
        gen[r["species_id"]].add(r["host_taxon_std"].split()[0])
phyto = [s for s in ids if grp[s] != "Phytoseiidae"]
with_host = [s for s in phyto if gen[s]]
one = sum(1 for s in with_host if len(gen[s]) == 1)
per_genus = collections.Counter(g for s in with_host for g in gen[s])
top5g = sorted(per_genus.items(), key=lambda x: (-x[1], x[0]))[:5]

# ---------------------------------------------------------------- barcodes
coi = {r["species_id"]: int(r["n_coi"] or 0) for r in read("data/raw/coverage_by_species.csv")}
n_st = {s: len(allst[s]) for s in ids}
one_state = [s for s in ids if n_st[s] == 1]
ten = [s for s in ids if n_st[s] >= 10]

mine = {
    ("where", "states and territories with a record"): len(by_state),
    ("where", "species with at least one state"): sum(1 for s in ids if n_st[s]),
    ("where", "species known from one state only"): len(one_state),
    ("where", "three richest states"): "; ".join(f"{st} {by_state[st]}" for st in top3),
    ("where", "species recorded from the three richest states (union)"): len({s for s, st in pairs if st in top3}),
    ("where", "species x state pairs, all"): len(pairs),
    ("where", "species x state pairs, state_in_book"): stat["state_in_book"],
    ("where", "species x state pairs, parent_or_child_state_in_book"): stat["parent_or_child_state_in_book"],
    ("where", "species x state pairs, book_gives_no_state"): stat["book_gives_no_state"],
    ("where", "species x state pairs, new_state_for_a_book_species"): stat["new_state_for_a_book_species"],
    ("where", "species x state pairs, species_not_in_book"): stat["species_not_in_book"],
    ("where", "additions to the book (new state or species not in book)"): stat["new_state_for_a_book_species"] + stat["species_not_in_book"],
    ("where", "additions resting on AICRP reports only"): only_aicrp_new,
    ("where", "AICRP species x state pairs"): len(aicrp_pairs),
    ("where", "AICRP pairs that are additions to the book"): aicrp_stat["new_state_for_a_book_species"] + aicrp_stat["species_not_in_book"],
    ("where", "AICRP pairs where the book gives no state for the species"): aicrp_stat["book_gives_no_state"],
    ("when", "species with a description year"): len(years),
    ("when", "species described 1970-1999"): sum(1 for y in years if 1970 <= y <= 1999),
    ("when", "species described 2000-2026"): sum(1 for y in years if y >= 2000),
    ("when", "decade with most descriptions"): f"{peak}s ({dec[peak]})",
    ("who", "distinct author names in authorities"): len(count),
    ("who", "five most frequent authors"): "; ".join(f"{n} {count[n]}" for n in five),
    ("who", "species with at least one of the top five authors"): f"{with_five} ({round(with_five / len(checklist), 3)})",
    ("who", "Mohanasundaram share of Eriophyoidea"): round(sum(1 for s in erio if "Mohanasundaram" in per_species[s]) / len(erio), 3),
    ("hosts", "phytophagous species (five families)"): len(phyto),
    ("hosts", "phytophagous species with a host genus"): len(with_host),
    ("hosts", "of these, known from one host genus"): f"{one} ({round(one / len(with_host), 3)})",
    ("hosts", "phytophagous species with more than 20 host genera"): sum(1 for s in with_host if len(gen[s]) > 20),
    ("hosts", "five host genera with most phytophagous mite species"): "; ".join(f"{g} {n}" for g, n in top5g),
    ("link", "barcoded species (any COI)"): sum(1 for s in ids if coi.get(s, 0) > 0),
    ("link", "share barcoded, species from 1 states"): f"{sum(1 for s in one_state if coi.get(s, 0) > 0)}/{len(one_state)} ({round(sum(1 for s in one_state if coi.get(s, 0) > 0) / len(one_state), 3)})",
    ("link", "share barcoded, species from 10+ states"): f"{sum(1 for s in ten if coi.get(s, 0) > 0)}/{len(ten)} ({round(sum(1 for s in ten if coi.get(s, 0) > 0) / len(ten), 3)})",
}
theirs = {(r["section"], r["measure"]): r["value"] for r in read("data/analysis/findings_summary.csv")}
bad = 0
for k, v in mine.items():
    ok = k in theirs and str(theirs[k]) == str(v)
    bad += not ok
    print("OK  " if ok else "DIFF", k[0], "|", k[1], "|", v, "" if ok else f"<> analyse.py: {theirs.get(k)}")
print(f"{len(mine) - bad} of {len(mine)} numbers agree")
sys.exit(1 if bad else 0)
