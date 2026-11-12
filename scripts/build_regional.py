"""Build record layers from the regional and family checklists used for the Paper 1 species list,
then combine every layer into one species x state table.

Inputs (copied by fetch_sources.py from india-agri-mite-coi at the pinned commit):
  chalil2024  Chalil et al. (2024), Persian Journal of Acarology 13(1): 29-75. Tetranychidae of India.
  mitra2025   Mitra (2025), International Journal of Tropical Insect Science 45: 1041-1055. Tenuipalpidae of India.
  tn2020      Dyamanagouda et al. (2020), Journal of Entomology and Zoology Studies 8(6): 137-146. Eriophyoidea of Tamil Nadu.
  karn2025    Dyamanagouda et al. (2025). Eriophyoidea of Karnataka (names and state only).
  som2025     Som et al. (2025). Eriophyoidea of South Bengal (names and state only).
  mandal2026  Mandal et al. (2026). Eriophyoidea of West Bengal, with hosts and places.
  tarswb2023  Mondal et al. (2023) and Karmakar (2016). Tarsonemidae of West Bengal (names and state only).
  gb2017      Gupta & Bose (2017), Records of the Zoological Survey of India 117(2): 154-181. Mites on medicinal plants, South Bengal.
  mitra2018   Mitra et al. (2018), Acarologia 58(4): 850-854. Tenuipalpidae of southern West Bengal.
  add2026     Describing and record papers dated 2022-2026 (one row per species, DOI given).

Outputs
  data/regional/regional_species_state.csv   one row per species x state x source
  data/regional/regional_species_host.csv    one row per species x host x source, with standardised host columns
  data/review/regional_names_not_joined.csv  names that do not join to the checklist
  data/review/regional_hosts_unparsed.csv    host text the parser could not split into names
  data/combined/species_state_all_sources.csv  every species x state pair from every layer, with the layers that record it
  data/combined/summary.csv                  counts by layer
"""
import csv, re, sys, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, REV = ROOT / "data/raw", ROOT / "data/review"
OUT, COMB = ROOT / "data/regional", ROOT / "data/combined"
for d in (OUT, COMB, REV):
    d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))
import host_names, states_norm


def read(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(p, rows, cols):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)


species = {r["species_id"]: r for r in read(RAW / "species_list.csv")}
name2id = collections.defaultdict(set)
for r in read(RAW / "species_list_names.csv"):
    name2id[r["name"]].add(r["species_id"])


def link(name):
    n = re.sub(r"\s+", " ", (name or "").strip())
    for cand in (n, re.sub(r" \([A-Z][a-z]+\)", "", n)):
        ids = name2id.get(cand, set())
        if len(ids) == 1:
            sid = next(iter(ids))
            return sid, species[sid]["species"], species[sid]["family"], ("exact" if cand == n else "subgenus_dropped")
        if len(ids) > 1:
            return "", "", "", "ambiguous"
    return "", "", "", ""


SOURCES = [
    # key, file, species column, state column (None = fixed state), fixed state, host column, place column, source year
    ("chalil2024", "chalil2024_tetranychidae.csv", "species", "india_states", None, "host_raw", None, "2024"),
    ("mitra2025", "mitra2025_tenuipalpidae_india.csv", "species", "india_states", None, "host_raw", None, "2025"),
    ("tn2020", "dyamanagouda2020_eriophyoidea_tamilnadu.csv", "species", "india_states", None, "host_raw", None, "2020"),
    ("karn2025", "dyamanagouda2025_eriophyoidea_karnataka.csv", "species", "india_states", None, None, None, "2025"),
    ("som2025", "som2025_eriophyoidea_south_bengal.csv", "species", "india_states", None, None, None, "2025"),
    ("mandal2026", "mandal2026_eriophyoidea_west_bengal.csv", "species", None, "West Bengal", "host_raw", "wb_places", "2026"),
    ("tarswb2023", "tarsonemidae_west_bengal.csv", "species", "india_states", None, None, "zones", "2023"),
    ("gb2017", "gupta_bose2017_south_bengal.csv", "species", "india_states", None, "hosts_raw", "districts", "2017"),
    ("mitra2018", "mitra2018_tenuipalpidae_west_bengal.csv", "species", "india_states", None, "hosts_raw", "localities", "2018"),
    ("add2026", "additions_2022_2026.csv", "species", "india_states", None, "hosts", None, ""),
]

HD = host_names.HostDictionary()
CT = host_names.CropTypes()
AUTH = re.compile(r"\b(?:L|Linn|Roxb|Willd|Wall|Benth|Hook|DC|Lam|Blume|Jacq|Mill|Merr|Gaertn|Burm|Sw|Moench|Spreng|Retz|Kunth|Schott|Nees)\b\.?")


def split_hosts(raw):
    """Split a host list into plant names. Returns (names, leftovers)."""
    raw = re.sub(r"\(([A-Z][a-z]+aceae|[A-Z][a-z]+ae)\)", " ", raw)         # (Anacardiaceae)
    parts = re.split(r";|,|\s+&\s+|\s+and\s+", raw)
    names, left, last_genus, seen = [], [], "", []
    for p in parts:
        t = re.sub(r"\s+", " ", p).strip(" .:")
        t = re.sub(r"^[a-z]{1,3}\s+(?=[A-Z][a-z]+ [a-zA-Z])", "", t)          # OCR leftovers ("ti Clerodendrum ...")
        t = re.sub(r"^([A-Z][a-z]+) ([A-Z])([a-z]+)\b", lambda m: f"{m.group(1)} {m.group(2).lower()}{m.group(3)}", t)  # "Persea Americana"
        if not t:
            continue
        m = re.match(r"^([A-Z][a-z]+)\s+(sp|spp)\b\.?", t)
        if m:
            last_genus = m.group(1); seen.append(last_genus); names.append(f"{m.group(1)} sp."); continue
        m = re.match(r"^([A-Z][a-z]+)\s+(x\s+)?([a-z][a-z\-]+)", t)
        if m and m.group(3) not in ("and", "var", "on"):
            last_genus = m.group(1); seen.append(last_genus); names.append(f"{m.group(1)} {m.group(3)}"); continue
        m = re.match(r"^([A-Z][a-z]?)\.\s*([a-z][a-z\-]+)", t)
        if m:
            g = next((x for x in reversed(seen) if x.startswith(m.group(1))), "")
            if g:
                names.append(f"{g} {m.group(2)}"); continue
        if re.fullmatch(r"[A-Z][a-z]+", t) and t.lower() in HD.genus_family:
            names.append(f"{t} sp."); continue
        if re.fullmatch(r"[A-Za-z][a-z]+(?: [a-z]+){0,2}", t) and not AUTH.fullmatch(t):
            names.append(t); continue
        if AUTH.search(t) and len(t) < 25:
            continue                                                      # stray authority fragment
        left.append(t)
    return names, left


state_rows, host_rows, unjoined, host_left = [], [], collections.Counter(), []
STD = ["host_taxon_std", "host_rank_std", "host_family", "host_std_common", "host_basis", "host_confidence", "host_crop_type"]
for key, fname, spcol, stcol, fixed, hcol, pcol, syear in SOURCES:
    for r in read(RAW / fname):
        name = (r.get(spcol) or "").strip()
        if not name or (key == "gb2017" and r.get("in_scope_family") != "1"):
            continue
        sid, valid, fam, basis = link(name)
        if not sid:
            unjoined[(key, name, basis or "not_found")] += 1
        base = {"source": key, "source_year": syear or (r.get("year") if key == "add2026" else ""), "name_in_source": name,
                "species_id": sid, "valid_name": valid, "family": fam, "join_basis": basis,
                "place_as_printed": (r.get(pcol) or "").strip() if pcol else ""}
        states = [fixed] if fixed else [s.strip() for s in (r.get(stcol) or "").split(";") if s.strip()]
        for st in states:
            state_rows.append({**base, "state": st, "state_canon": states_norm.canon(st)})
        if hcol and (r.get(hcol) or "").strip():
            names, left = split_hosts(r[hcol])
            for h in left:
                host_left.append({"source": key, "name_in_source": name, "fragment": h, "host_raw": r[hcol]})
            for h in names:
                sci = h if re.match(r"^[A-Z][a-z]+ ([a-z\-]+|sp\.)$", h) else ""
                res = HD.resolve("" if sci else h, sci, "")
                res["host_crop_type"] = CT.of(res["host_taxon_std"], res["host_rank_std"])
                host_rows.append({**base, "host_as_printed": h, **{k: res[k] for k in STD}})

base_cols = ["source", "source_year", "name_in_source", "species_id", "valid_name", "family", "join_basis", "place_as_printed"]
write(OUT / "regional_species_state.csv", state_rows, base_cols + ["state", "state_canon"])
write(OUT / "regional_species_host.csv", host_rows, base_cols + ["host_as_printed"] + STD)
write(REV / "regional_names_not_joined.csv",
      [{"source": k[0], "name_in_source": k[1], "reason": k[2], "rows": v} for k, v in sorted(unjoined.items())],
      ["source", "name_in_source", "reason", "rows"])
write(REV / "regional_hosts_unparsed.csv", host_left, ["source", "name_in_source", "fragment", "host_raw"])

# ------------------------------------------------------------------ combine every layer
layers = collections.defaultdict(lambda: collections.defaultdict(set))   # (sid, state) -> layer -> detail
for r in read(ROOT / "data/records/species_state.csv"):
    if r["species_id"] and r["state"]:
        layers[(r["species_id"], states_norm.canon(r["state"]))]["gm2023"].add("")
for r in read(ROOT / "data/aicrp/aicrp_observations.csv"):
    if r["species_id"] and r["state"] and "(not split)" not in r["state"]:
        layers[(r["species_id"], states_norm.canon(r["state"]))]["aicrp"].add(r["survey_period"])
for r in state_rows:
    if r["species_id"]:
        layers[(r["species_id"], r["state_canon"])][r["source"]].add("")

by_species = collections.defaultdict(set)
for sid, st in layers:
    by_species[sid].add(st)
comb = []
for (sid, st), v in sorted(layers.items(), key=lambda x: (species[x[0][0]]["family"], species[x[0][0]]["species"], x[0][1])):
    gm_related = any("gm2023" in layers.get((sid, s), {}) for s in states_norm.related(st))
    comb.append({"species_id": sid, "valid_name": species[sid]["species"], "family": species[sid]["family"], "state": st,
                 "layers": ";".join(sorted(v)), "n_layers": len(v), "in_gm2023": int("gm2023" in v),
                 "in_gm2023_same_or_parent_state": int(gm_related), "in_aicrp": int("aicrp" in v),
                 "aicrp_periods": ";".join(sorted(p for p in v.get("aicrp", set()) if p))})
write(COMB / "species_state_all_sources.csv", comb,
      ["species_id", "valid_name", "family", "state", "layers", "n_layers", "in_gm2023", "in_gm2023_same_or_parent_state", "in_aicrp", "aicrp_periods"])

summary = []
for key, *_ in SOURCES:
    srows = [r for r in state_rows if r["source"] == key]
    hrows = [r for r in host_rows if r["source"] == key]
    pairs = {(r["species_id"], r["state_canon"]) for r in srows if r["species_id"]}
    new = sum(1 for p in pairs if "gm2023" not in layers[p])
    summary.append({"layer": key, "species_state_rows": len(srows), "species_host_rows": len(hrows),
                    "names_not_joined": sum(v for k, v in unjoined.items() if k[0] == key),
                    "species_state_pairs": len(pairs), "pairs_not_in_gm2023": new})
summary.append({"layer": "all layers combined", "species_state_rows": "", "species_host_rows": "", "names_not_joined": "",
                "species_state_pairs": len(comb), "pairs_not_in_gm2023": sum(1 for c in comb if not c["in_gm2023"])})
write(COMB / "summary.csv", summary, ["layer", "species_state_rows", "species_host_rows", "names_not_joined", "species_state_pairs", "pairs_not_in_gm2023"])
for s in summary:
    print(s)
print("combined pairs:", len(comb), "not in G&M (strict):", sum(1 for c in comb if not c["in_gm2023"]),
      "not in G&M same or parent state:", sum(1 for c in comb if not c["in_gm2023_same_or_parent_state"]),
      "species with any state:", len(by_species))
