"""Build species x state and species x host records from Gupta & Mondal (2023).

Inputs  : data/raw/ (copied by fetch_sources.py from the Paper 1 checklist repository)
Outputs : data/records/species_state.csv, data/records/species_host.csv,
          data/review/*.csv (everything the parser could not place), data/records/summary.csv

Rules
- Nothing is guessed. A host or locality the parser cannot read goes to data/review/ with its printed text.
- Hosts printed after "outside" / "outside India" are kept but marked in_india=0.
- Abbreviated genera ("C. morifolium") are expanded only from the genus printed earlier in the same list.
"""
import csv, re, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, REC, REV = ROOT / "data/raw", ROOT / "data/records", ROOT / "data/review"
REC.mkdir(parents=True, exist_ok=True); REV.mkdir(parents=True, exist_ok=True)
SRC = "gm2023"

def read(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write(p, rows, cols):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)

accounts = read(RAW / "gupta_mondal2023_all.csv")
species = {r["species_id"]: r for r in read(RAW / "species_list.csv")}
name2id = collections.defaultdict(set)
for r in read(RAW / "species_list_names.csv"):
    name2id[r["name"]].add(r["species_id"])

def link(name):
    ids = name2id.get(name, set())
    if len(ids) == 1:
        sid = next(iter(ids)); s = species[sid]
        return sid, s["species"], s["group"], s["counted"]
    return "", "", "", ""

NARRATIVE = re.compile(r"\b(reported|recorded|listed|mentioned|refer|hosts?\b|et al|ef a/)", re.I)
BINOMIAL = re.compile(r"^([A-Z][a-z]+) ([a-z][a-z\-]+)$")
GENUS_SP = re.compile(r"^([A-Z][a-z]+) spp?\.?$")
ABBREV = re.compile(r"^([A-Z])\. ?([a-z][a-z\-]+)$")
COMMON = re.compile(r"^[A-Za-z][a-z]+( [a-z]+){0,2}$")
UNDET = re.compile(r"^(undet|unident|undeterm|unknown)", re.I)

def clean(tok):
    t = tok.strip()
    t = re.sub(r"\s*\(([a-z ]+)\)$", "", t)                 # "Tectona grandis (teak)"
    t = re.sub(r"[\s|_—\-:;.>]+$", "", t)                    # trailing OCR rules
    t = re.sub(r"^[\[/](?=[a-z])", "I", t)                   # "/pomoea" -> "Ipomoea"
    return re.sub(r"\s+", " ", t).strip()

def parse_hosts(raw):
    """Return (records, leftovers). Each record: printed, name, genus, rank, in_india."""
    out, left = [], []
    in_india, last_genus = "1", ""
    for sentence in re.split(r"(?<=[a-z\)])\.\s+(?=[A-Z])", raw):
        if NARRATIVE.search(sentence) and not re.match(r"^[A-Z][a-z]+ [a-z]+,", sentence):
            left.append(sentence.strip()); continue
        for tok in re.split(r"[,;]", sentence):
            tok = tok.strip()
            if not tok: continue
            m = re.match(r"^outside(?: India)?(?: on)?:?\s*(.*)$", tok, re.I)
            if m:
                in_india, tok = "0", m.group(1)
                if not tok: continue
            t = clean(tok)
            if not t: continue
            if UNDET.match(t):
                out.append((tok, "", "", "undetermined_plant", in_india)); continue
            if (m := GENUS_SP.match(t)):
                last_genus = m.group(1); out.append((tok, m.group(1) + " sp.", m.group(1), "genus", in_india)); continue
            if (m := BINOMIAL.match(t)):
                last_genus = m.group(1); out.append((tok, t, m.group(1), "species", in_india)); continue
            if (m := ABBREV.match(t)) and last_genus.startswith(m.group(1)):
                out.append((tok, f"{last_genus} {m.group(2)}", last_genus, "species_genus_expanded", in_india)); continue
            if COMMON.match(t) and len(t) > 2:
                out.append((tok, t.lower(), "", "common_name", in_india)); continue
            left.append(tok)
    return out, left

state_rows, host_rows, host_left, state_left, no_host, no_dist = [], [], [], [], [], []
for a in accounts:
    sid, valid, group, counted = link(a["species"])
    base = {"account_number": a["number"], "species_id": sid, "valid_name": valid,
            "name_in_source": a["species"], "family": a["family"], "section": a["section"],
            "level": a["level"], "source": SRC, "page": a["pages"]}
    for st in filter(None, a["india_states"].split(";")):
        state_rows.append({**base, "state": st})
    if a["india_unmatched"]:
        state_left.append({**base, "locality_text": a["india_unmatched"], "distribution_raw": a["distribution_raw"]})
    if not a["india_states"] and not a["india_unmatched"]:
        no_dist.append({**base, "distribution_raw": a["distribution_raw"], "flags": a["flags"]})
    raw = a["host_raw"].strip()
    if not raw:
        no_host.append({**base, "flags": a["flags"]}); continue
    recs, left = parse_hosts(raw)
    for printed, name, genus, rank, ind in recs:
        host_rows.append({**base, "host_as_printed": printed, "host_name": name, "host_genus": genus,
                          "host_rank": rank, "in_india": ind})
    for l in left:
        host_left.append({**base, "unparsed_text": l, "host_raw": raw})

base_cols = ["account_number", "species_id", "valid_name", "name_in_source", "family", "section", "level"]
tail = ["source", "page"]
write(REC / "species_state.csv", state_rows, base_cols + ["state"] + tail)
write(REC / "species_host.csv", host_rows, base_cols + ["host_as_printed", "host_name", "host_genus", "host_rank", "in_india"] + tail)
write(REV / "host_unparsed.csv", host_left, base_cols + ["unparsed_text", "host_raw"] + tail)
write(REV / "state_unmatched.csv", state_left, base_cols + ["locality_text", "distribution_raw"] + tail)
write(REV / "accounts_without_host.csv", no_host, base_cols + ["flags"] + tail)
write(REV / "accounts_without_indian_state.csv", no_dist, base_cols + ["distribution_raw", "flags"] + tail)

linked = [a for a in accounts if link(a["species"])[0]]
summary = [
    ("accounts", len(accounts)), ("accounts_linked_to_checklist", len(linked)),
    ("accounts_not_linked", len(accounts) - len(linked)),
    ("species_state_records", len(state_rows)), ("states_and_territories", len({r["state"] for r in state_rows})),
    ("accounts_with_a_state", len({r["account_number"] for r in state_rows})),
    ("species_host_records", len(host_rows)),
    ("host_records_in_india", sum(r["in_india"] == "1" for r in host_rows)),
    ("host_records_outside_india", sum(r["in_india"] == "0" for r in host_rows)),
    ("accounts_with_a_parsed_host", len({r["account_number"] for r in host_rows})),
    ("distinct_host_names", len({r["host_name"] for r in host_rows if r["host_name"]})),
    ("distinct_host_genera", len({r["host_genus"] for r in host_rows if r["host_genus"]})),
    ("review_host_unparsed", len(host_left)), ("review_state_unmatched", len(state_left)),
    ("review_accounts_without_host", len(no_host)), ("review_accounts_without_indian_state", len(no_dist)),
]
write(REC / "summary.csv", [{"measure": k, "value": v} for k, v in summary], ["measure", "value"])
for k, v in summary: print(f"{k:40s}{v}")
print(collections.Counter(r["host_rank"] for r in host_rows))
