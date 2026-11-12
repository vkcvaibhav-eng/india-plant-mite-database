"""Paper 2 analyses: where, when, who, hosts, and the link to Paper 1 (COI coverage).

Run after build_records.py, build_aicrp.py and build_regional.py. Writes tables to data/analysis/.
All counts use the 1,221 counted species of the Paper 1 checklist, grouped as in Paper 1
(Tetranychidae, Tenuipalpidae, Eriophyoidea, Tarsonemidae, Tuckerellidae, Phytoseiidae).

Rules
- Species x state pairs and species x host pairs are sets, so a collection repeated in two reports counts once.
- Counts per AICRP report use distinct species x state pairs within each report.
- Host breadth counts distinct host genera; host rows at family or group level do not count.
- Phytoseiidae are predators, so their plants are habitats; host analyses keep them separate.
"""
import csv, re, sys, pathlib, collections, statistics

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import states_norm
from scipy import stats

OUT = ROOT / "data/analysis"
OUT.mkdir(parents=True, exist_ok=True)


def read(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(name, rows, cols=None):
    cols = cols or (list(rows[0].keys()) if rows else [])
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)


GROUPS = ["Tetranychidae", "Tenuipalpidae", "Eriophyoidea", "Tarsonemidae", "Tuckerellidae", "Phytoseiidae"]
PHYTOPHAGOUS = set(GROUPS) - {"Phytoseiidae"}
sp = {r["species_id"]: r for r in read(ROOT / "data/raw/species_list.csv") if r["counted"] == "1"}
group = {k: v["group"] for k, v in sp.items()}
summary = []          # (section, measure, value) for the findings table


def note(section, measure, value):
    summary.append({"section": section, "measure": measure, "value": value})


# ======================================================================= WHERE
REGION = {
    "Jammu & Kashmir": "North", "Ladakh": "North", "Himachal Pradesh": "North", "Punjab": "North", "Haryana": "North",
    "Chandigarh": "North", "Delhi": "North", "Uttarakhand": "North", "Uttar Pradesh": "North", "Rajasthan": "North",
    "Bihar": "East", "Jharkhand": "East", "West Bengal": "East", "Odisha": "East",
    "Assam": "North-East", "Arunachal Pradesh": "North-East", "Meghalaya": "North-East", "Manipur": "North-East",
    "Mizoram": "North-East", "Nagaland": "North-East", "Tripura": "North-East", "Sikkim": "North-East",
    "Madhya Pradesh": "Central", "Chhattisgarh": "Central",
    "Gujarat": "West", "Maharashtra": "West", "Goa": "West",
    "Karnataka": "South", "Kerala": "South", "Tamil Nadu": "South", "Andhra Pradesh": "South", "Telangana": "South",
    "Puducherry": "South",
    "Andaman & Nicobar Islands": "Islands", "Lakshadweep": "Islands",
}
comb = [r for r in read(ROOT / "data/combined/species_state_all_sources.csv") if r["species_id"] in sp]
states_of = collections.defaultdict(set)
for r in comb:
    states_of[r["species_id"]].add(r["state"])

by_state = collections.defaultdict(lambda: {"species": set(), "single": 0, "pairs": 0, "by_group": collections.Counter()})
for r in comb:
    d = by_state[r["state"]]
    d["species"].add(r["species_id"]); d["pairs"] += 1; d["by_group"][group[r["species_id"]]] += 1
    if r["n_layers"] == "1":
        d["single"] += 1
rows = []
for st, d in sorted(by_state.items(), key=lambda x: -len(x[1]["species"])):
    only_here = sum(1 for s in d["species"] if states_of[s] == {st})
    rows.append({"state": st, "region": REGION.get(st, ""), "species": len(d["species"]),
                 **{g: d["by_group"][g] for g in GROUPS},
                 "pairs_on_one_layer_only": d["single"], "share_on_one_layer": round(d["single"] / d["pairs"], 3),
                 "species_recorded_only_from_this_state": only_here})
write("where_species_by_state.csv", rows)
reg = collections.defaultdict(set)
for r in comb:
    reg[REGION.get(r["state"], "unassigned")].add(r["species_id"])
write("where_species_by_region.csv",
      [{"region": k, "species": len(v), "states": sum(1 for s in by_state if REGION.get(s) == k)} for k, v in sorted(reg.items(), key=lambda x: -len(x[1]))])

n_states = {s: len(states_of.get(s, ())) for s in sp}
cls = collections.Counter()
rows = []
for g in GROUPS:
    ids = [s for s in sp if group[s] == g]
    c = collections.Counter(min(n_states[s], 4) for s in ids)
    rows.append({"group": g, "species": len(ids), "no_state": c[0], "one_state": c[1], "two_states": c[2], "three_states": c[3],
                 "four_or_more": c[4], "share_one_state": round(c[1] / len(ids), 3) if ids else ""})
allc = collections.Counter(min(n_states[s], 4) for s in sp)
rows.append({"group": "All", "species": len(sp), "no_state": allc[0], "one_state": allc[1], "two_states": allc[2], "three_states": allc[3],
             "four_or_more": allc[4], "share_one_state": round(allc[1] / len(sp), 3)})
write("where_states_per_species.csv", rows)
top3 = sorted(by_state.items(), key=lambda x: -len(x[1]["species"]))[:3]
note("where", "states and territories with a record", len(by_state))
note("where", "species with at least one state", sum(1 for s in sp if n_states[s]))
note("where", "species known from one state only", allc[1])
note("where", "species known from one state only (share of species with a state)", round(allc[1] / sum(1 for s in sp if n_states[s]), 3))
note("where", "three richest states", "; ".join(f"{k} {len(v['species'])}" for k, v in top3))
note("where", "species recorded from the three richest states (union)", len(set().union(*[v["species"] for _, v in top3])))
for k in ("North-East", "Central", "West", "Islands"):
    note("where", f"species in region {k}", len(reg.get(k, ())))

# AICRP coverage by state and period
obs = read(ROOT / "data/aicrp/aicrp_observations.csv")
per_report = collections.defaultdict(lambda: {"pairs": set(), "species": set(), "centres": set(), "states": set()})
for r in obs:
    if r["species_id"] in sp and r["state"] and "(not split)" not in r["state"]:
        d = per_report[r["report"]]
        st = states_norm.canon(r["state"])
        d["pairs"].add((r["species_id"], st)); d["species"].add(r["species_id"]); d["states"].add(st)
    if r["centre"]:
        per_report[r["report"]]["centres"].add(r["centre"])
ORDER = ["AICRP 1988", "AICRP 1989", "AICRP 1990 Group Meeting", "AICRP 1990-91", "AICRP 1992-94", "AICRP 1996-98",
         "AICRP 2020-21", "AICRP 2021-22", "AICRP 2024-25"]
write("when_aicrp_by_report.csv",
      [{"report": k, "centres": len(per_report[k]["centres"]), "states": len(per_report[k]["states"]),
        "checklist_species": len(per_report[k]["species"]), "species_state_pairs": len(per_report[k]["pairs"])} for k in ORDER if k in per_report])

# ======================================================================= WHEN
dec = collections.defaultdict(collections.Counter)
no_year = collections.Counter()
for s, r in sp.items():
    y = r["year"].strip()
    if re.fullmatch(r"\d{4}", y):
        dec[(int(y) // 10) * 10][group[s]] += 1
    else:
        no_year[group[s]] += 1
rows, cum = [], 0
for d in sorted(dec):
    tot = sum(dec[d].values()); cum += tot
    rows.append({"decade": f"{d}s", "described": tot, "cumulative": cum, **{g: dec[d][g] for g in GROUPS}})
write("when_described_per_decade.csv", rows)
years = [int(r["year"]) for r in sp.values() if re.fullmatch(r"\d{4}", r["year"].strip())]
note("when", "species with a description year", len(years))
note("when", "species without a year", sum(no_year.values()))
note("when", "median description year", int(statistics.median(years)))
note("when", "species described 1970-1999", sum(1 for y in years if 1970 <= y <= 1999))
note("when", "species described 2000-2026", sum(1 for y in years if y >= 2000))
peak = max(rows, key=lambda r: r["described"])
note("when", "decade with most descriptions", f"{peak['decade']} ({peak['described']})")
for g in GROUPS:
    ys = [int(sp[s]["year"]) for s in sp if group[s] == g and re.fullmatch(r"\d{4}", sp[s]["year"].strip())]
    if ys:
        note("when", f"median description year, {g}", int(statistics.median(ys)))

# ======================================================================= WHO
ALIAS = {"Mohansundaram": "Mohanasundaram", "ChannaBasavanna": "Channabasavanna", "Channabasvanna": "Channabasavanna",
         "Pgst": "Pagenstecher", "Boisd": "Boisduval", "Oud": "Oudemans", "Geisk": "Geijskes", "Smith-Meyer": "Smith Meyer"}


def authors(auth):
    a = re.sub(r"[()\[\]]", "", auth or "")
    etal = bool(re.search(r"et al", a))
    a = re.sub(r"\bet al\.?", "", a)
    out = []
    for x in re.split(r"\s*(?:&|,|\band\b)\s*", a):
        x = x.strip(" .")
        if x and not re.fullmatch(r"\d+", x):
            out.append(ALIAS.get(x, x))
    return out, etal


auth_rows = collections.defaultdict(lambda: {"species": 0, "first": 0, "groups": collections.Counter(), "years": []})
species_authors = {}
for s, r in sp.items():
    names, _ = authors(r["authority"])
    species_authors[s] = names
    for i, n in enumerate(dict.fromkeys(names)):
        d = auth_rows[n]; d["species"] += 1; d["groups"][group[s]] += 1
        if i == 0:
            d["first"] += 1
        if re.fullmatch(r"\d{4}", r["year"].strip()):
            d["years"].append(int(r["year"]))
rows = []
for n, d in sorted(auth_rows.items(), key=lambda x: -x[1]["species"]):
    rows.append({"author": n, "species_named": d["species"], "as_first_author": d["first"],
                 **{g: d["groups"][g] for g in GROUPS},
                 "first_year": min(d["years"]) if d["years"] else "", "last_year": max(d["years"]) if d["years"] else ""})
write("who_authors.csv", rows)
top5 = [r["author"] for r in rows[:5]]
with_top5 = sum(1 for s in sp if set(species_authors[s]) & set(top5))
note("who", "distinct author names in authorities", len(rows))
note("who", "five most frequent authors", "; ".join(f"{r['author']} {r['species_named']}" for r in rows[:5]))
note("who", "species with at least one of the top five authors", f"{with_top5} ({round(with_top5 / len(sp), 3)})")
note("who", "Mohanasundaram share of Eriophyoidea", round(auth_rows["Mohanasundaram"]["groups"]["Eriophyoidea"] / sum(1 for s in sp if group[s] == "Eriophyoidea"), 3))
by_group_top = []
for g in GROUPS:
    c = collections.Counter(n for s in sp if group[s] == g for n in dict.fromkeys(species_authors[s]))
    tot = sum(1 for s in sp if group[s] == g)
    for n, k in c.most_common(3):
        by_group_top.append({"group": g, "author": n, "species": k, "share_of_group": round(k / tot, 3)})
write("who_top_authors_by_group.csv", by_group_top)

# ======================================================================= HOSTS
host_pairs = collections.defaultdict(set)        # species_id -> set of host genera
host_taxa = collections.defaultdict(set)         # species_id -> set of host taxa (species or genus)
host_src = collections.defaultdict(set)          # (species_id, host taxon) -> layers
crop_type = {}


def add_host(sid, taxon, rank, ctype, common, layer):
    if sid not in sp or rank not in ("species", "genus") or not taxon:
        return
    g = taxon.split()[0]
    host_pairs[sid].add(g); host_taxa[sid].add(taxon); host_src[(sid, taxon)].add(layer)
    if taxon not in crop_type or (common and not crop_type[taxon][1]) or (ctype and not crop_type[taxon][0]):
        old = crop_type.get(taxon, ("", ""))
        crop_type[taxon] = (old[0] or ctype, old[1] or common)


for r in read(ROOT / "data/records/species_host.csv"):
    if r["in_india"] == "1":
        add_host(r["species_id"], r["host_taxon_std"], r["host_rank_std"], r["host_crop_type"], r["host_std_common"], "gm2023")
for r in obs:
    add_host(r["species_id"], r["host_taxon_std"], r["host_rank_std"], r["host_crop_type"], r["host_std_common"], "aicrp")
for r in read(ROOT / "data/regional/regional_species_host.csv"):
    add_host(r["species_id"], r["host_taxon_std"], r["host_rank_std"], r["host_crop_type"], r["host_std_common"], r["source"])

rows = []
for g in GROUPS:
    ids = [s for s in sp if group[s] == g]
    b = [len(host_pairs[s]) for s in ids]
    c = collections.Counter("none" if x == 0 else "1" if x == 1 else "2-5" if x <= 5 else "6-20" if x <= 20 else ">20" for x in b)
    with_host = [x for x in b if x]
    rows.append({"group": g, "species": len(ids), "no_host_genus": c["none"], "one_host_genus": c["1"], "2_5": c["2-5"],
                 "6_20": c["6-20"], "over_20": c[">20"],
                 "share_one_host_genus_of_those_with_hosts": round(c["1"] / len(with_host), 3) if with_host else "",
                 "median_host_genera": statistics.median(with_host) if with_host else ""})
write("hosts_breadth_by_group.csv", rows)
phy_ids = [s for s in sp if group[s] in PHYTOPHAGOUS]
ph_with = [s for s in phy_ids if host_pairs[s]]
note("hosts", "phytophagous species (five families)", len(phy_ids))
note("hosts", "phytophagous species with a host genus", len(ph_with))
note("hosts", "of these, known from one host genus", f"{sum(1 for s in ph_with if len(host_pairs[s]) == 1)} ({round(sum(1 for s in ph_with if len(host_pairs[s]) == 1) / len(ph_with), 3)})")
note("hosts", "phytophagous species with more than 20 host genera", sum(1 for s in ph_with if len(host_pairs[s]) > 20))

crop_sp = collections.defaultdict(set)
crop_pred = collections.defaultdict(set)
for (sid, taxon), layers in host_src.items():
    (crop_sp if group[sid] in PHYTOPHAGOUS else crop_pred)[taxon].add(sid)
rows = []
for taxon, ids in sorted(crop_sp.items(), key=lambda x: -len(x[1]))[:40]:
    ct, common = crop_type.get(taxon, ("", ""))
    rows.append({"host": taxon, "common_name": common, "crop_type": ct, "phytophagous_species": len(ids),
                 **{g: sum(1 for s in ids if group[s] == g) for g in GROUPS if g != "Phytoseiidae"},
                 "phytoseiid_species": len(crop_pred.get(taxon, ()))})
write("hosts_top_plants.csv", rows)
ct_sp = collections.defaultdict(set)
for (sid, taxon) in host_src:
    if group[sid] in PHYTOPHAGOUS:
        ct_sp[crop_type.get(taxon, ("", ""))[0] or "not_assigned"].add(sid)
write("hosts_by_crop_type.csv", [{"crop_type": k, "phytophagous_species": len(v)} for k, v in sorted(ct_sp.items(), key=lambda x: -len(x[1]))])

KEY = ["Solanum melongena", "Abelmoschus esculentus", "Capsicum annuum", "Gossypium sp.", "Solanum lycopersicum", "Mangifera indica",
       "Cocos nucifera", "Camellia sinensis", "Oryza sativa", "Saccharum officinarum", "Psidium guajava", "Carica papaya",
       "Cajanus cajan", "Litchi chinensis", "Rosa sp.", "Morus alba", "Vitis vinifera", "Citrus sp.", "Citrus limon", "Areca catechu"]
rows = []
for taxon in KEY:
    for sid in sorted(crop_sp.get(taxon, ()), key=lambda s: (group[s], sp[s]["species"])):
        rows.append({"host": taxon, "common_name": crop_type.get(taxon, ("", ""))[1], "mite": sp[sid]["species"], "group": group[sid],
                     "layers": ";".join(sorted(host_src[(sid, taxon)])), "n_layers": len(host_src[(sid, taxon)])})
write("hosts_key_crops.csv", rows)
top = sorted(crop_sp.items(), key=lambda x: -len(x[1]))[:5]
note("hosts", "five plants with most phytophagous mite species", "; ".join(f"{crop_type.get(t, ('', ''))[1] or t} {len(v)}" for t, v in top))

# ======================================================================= LINK TO PAPER 1
cov = {r["species_id"]: r for r in read(ROOT / "data/raw/coverage_by_species.csv")}
layers_of = collections.defaultdict(set)
for r in comb:
    layers_of[r["species_id"]].update(r["layers"].split(";"))
rows = []
for s in sp:
    c = cov.get(s, {})
    rows.append({"species_id": s, "species": sp[s]["species"], "group": group[s], "n_states": n_states[s],
                 "n_host_genera": len(host_pairs[s]), "n_layers": len(layers_of[s]),
                 "n_coi": int(c.get("n_coi") or 0), "n_coi_india": int(c.get("n_coi_india") or 0)})
write("link_species_records_vs_coi.csv", rows)
bar = [r for r in rows if r["n_coi"] > 0]
nob = [r for r in rows if r["n_coi"] == 0]
note("link", "barcoded species (any COI)", len(bar))
for k in ("n_states", "n_host_genera", "n_layers"):
    u = stats.mannwhitneyu([r[k] for r in bar], [r[k] for r in nob], alternative="two-sided")
    note("link", f"median {k}: barcoded vs not", f"{statistics.median([r[k] for r in bar])} vs {statistics.median([r[k] for r in nob])} (Mann-Whitney U={u.statistic:.0f}, P={u.pvalue:.2g})")
cls_rows = []
for label, lo, hi in (("0", 0, 0), ("1", 1, 1), ("2-3", 2, 3), ("4-9", 4, 9), ("10+", 10, 999)):
    ids = [r for r in rows if lo <= r["n_states"] <= hi]
    if ids:
        k = sum(1 for r in ids if r["n_coi"] > 0)
        cls_rows.append({"states_recorded": label, "species": len(ids), "barcoded": k, "share_barcoded": round(k / len(ids), 3),
                         "barcoded_from_india": sum(1 for r in ids if r["n_coi_india"] > 0)})
write("link_barcoded_by_states.csv", cls_rows)
for r in cls_rows:
    note("link", f"share barcoded, species from {r['states_recorded']} states", f"{r['barcoded']}/{r['species']} ({r['share_barcoded']})")
rho = stats.spearmanr([r["n_states"] for r in rows], [1 if r["n_coi"] else 0 for r in rows])
note("link", "Spearman rho, states recorded vs barcoded (0/1)", f"{rho.statistic:.3f} (P={rho.pvalue:.2g})")

write("findings_summary.csv", summary, ["section", "measure", "value"])
for s in summary:
    print(s["section"], "|", s["measure"], "|", s["value"])
