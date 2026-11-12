"""List checklist species whose description year differs between the source extracts in data/raw/.

The checklist (Paper 1) picks one year per species. This check reads the year each source prints for the
same species and writes the cases that differ by three years or more to
data/review/checklist_years_that_differ_between_sources.csv, for checking against the original papers.
"""
import csv, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw"
cfg = json.loads((ROOT / "config/sources.json").read_text())


def read(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def key(name):
    t = re.sub(r"\([^)]*\)", " ", name or "").split()
    return (t[0].lower(), t[1].lower()) if len(t) >= 2 else None


species = {r["species_id"]: r for r in read(RAW / "species_list.csv")}
by_name = {}
for r in read(RAW / "species_list_names.csv"):
    k = key(r["name"])
    if k:
        by_name.setdefault(k, r["species_id"])
years = {}
for layer, rel in cfg["files"].items():
    if layer in ("species_list", "species_list_names") or "coverage" in rel:
        continue
    for r in read(RAW / pathlib.Path(rel).name):
        y = (r.get("year") or "").strip()
        k = key(r.get("species", ""))
        if k and k in by_name and re.fullmatch(r"\d{4}", y):
            years.setdefault(by_name[k], {})[layer] = int(y)
rows = []
for sid, d in sorted(years.items()):
    s = species[sid]
    if s["counted"] != "1" or len(set(d.values())) < 2 or max(d.values()) - min(d.values()) < 3:
        continue
    rows.append({"species_id": sid, "species": s["species"], "authority_in_checklist": s["authority"],
                 "year_in_checklist": s["year"], "years_printed_by_sources": "; ".join(f"{k} {v}" for k, v in sorted(d.items())),
                 "decade_would_change": int(len({v // 10 for v in d.values()}) > 1)})
out = ROOT / "data/review/checklist_years_that_differ_between_sources.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
print(len(rows), "species written to", out.relative_to(ROOT))
