#!/usr/bin/env python3
"""Repair host lists in data/aicrp/transcription/lists.txt for blocks H01 and H02.

The Kalyani tables (2020-21 report) were read from a two-column text layer, so
district names, abundance counts and diversity-index rows leaked into the host
lists and some host names were split across cells ("Ash ... gourd").  This
script, run once on the transcription, does four things:

  1. drops rows that are abundance / diversity-index values, not host lists;
  2. moves district and locality names found in the host list to the locality list;
  3. re-joins host names split by a cell break (Ash + gourd, Ladies + finger, ...),
     including a fragment at the end of one row completed at the start of the next;
  4. splits tokens that hold two hosts run together (SPLITS below).

Every change is written to data/review/aicrp_host_list_repairs.csv so it can be
checked against the report.  Running it a second time changes nothing.

Usage: python3 scripts/tools/clean_host_lists.py
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTS = ROOT / "data/aicrp/transcription/lists.txt"
LOG = ROOT / "data/review/aicrp_host_list_repairs.csv"
BLOCKS = {"H01", "H02"}

PLACE_RX = re.compile(
    r"(?:\b24\s*parganas?\s*\((?:n|s|north|south)\)\.?"
    r"|\b24\s*pgs?\s*\((?:n|s)\)"
    r"|\b(?:north|south)\s+24\s*(?:parganas|pgs)\b"
    r"|\bnew\s+jalpaiguri\b|\bcooch\s*behar\b|\bcooch\b|\bbehar\b"
    r"|\bburdwan\b|\bbankura\b|\bhooghly\b|\bnadia\b|\bmurshi?dabad\b"
    r"|\bmald(?:h)?a\b|\bsiliguri\b|\bjalpaiguri\b|\bsantipur\b|\bkly\b"
    r"|\bmuzaffarpur\b|\bsitamarhi\b|\bmotihari\b|\bmotihary\b|\bdarbhanga\b|\bmadhuban\b)",
    re.I)
PLACE_TOKENS = {"susnia", "dhaldanga", "awalsiddhi", "kalyani"}
PLACE_FIX = {"behar": "Cooch Behar", "cooch": "Cooch Behar", "kly": "Kalyani"}

PREFIX_FRAGS = {"ash", "pointed", "bottle", "ridge", "bitter", "snake", "sponge"}
SPLITS = {
    "hibiscus lemon": ["Hibiscus", "Lemon"],
    "marigold bel": ["Marigold", "Bel"],
    "jatropha mango": ["Jatropha", "Mango"],
    "brinjal tomato": ["Brinjal", "Tomato"],
    "wild bhendi forest plants": ["Wild bhendi", "Forest plants"],
    "banana tulsi": ["Banana", "Tulsi"],
    "cucumber jatropha": ["Cucumber", "Jatropha"],
    "papaya mulberry": ["Papaya", "Mulberry"],
    "seuliflower sirish": ["Seuliflower", "Sirish"],
    "arjun tulsi": ["Arjun", "Tulsi"],
    "mango kadam": ["Mango", "Kadam"],
    "pitali papaya": ["Pitali", "Papaya"],
    "karipata (murraya koenigi) fig plant": ["Karipata (Murraya koenigi)", "Fig plant"],
    "cucumber vendi": ["Cucumber", "Vendi"],
    "litchi. mango": ["Litchi", "Mango"],
    "shiuli (nyctanthes sp.) polyalthia longifolia": ["Shiuli (Nyctanthes sp.)", "Polyalthia longifolia"],
    "pointed gourd coconut": ["Pointed gourd", "Coconut"],
    "pointed gourd 24 parganas": ["Pointed gourd"],
    "vendi bottle gourd": ["Vendi", "Bottle gourd"],
    "hibiscus tuberose": ["Hibiscus", "Tuberose"],
    "dahlia chandramallika et.": ["Dahlia", "Chandramallika"],
    "dahlia chandramallika et": ["Dahlia", "Chandramallika"],
}


def tidy(s):
    return re.sub(r"\s+", " ", s).strip(" .,")


def split_places(token):
    """Return (host_remainder, [places]) for one host token."""
    places = [PLACE_FIX.get(m.lower(), re.sub(r"\s+", " ", m.rstrip(". "))) for m in PLACE_RX.findall(token)]
    rest = tidy(PLACE_RX.sub(" ", token))
    if rest.lower() in PLACE_TOKENS:
        places.append(rest)
        rest = ""
    return rest, places


def merge_fragments(tokens):
    out = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        tl = t.lower()
        if tl in PREFIX_FRAGS and nxt and nxt.lower() == "gourd":
            out.append(t.capitalize() + " gourd")
            i += 2
            continue
        if tl == "ladies" and nxt and nxt.lower() == "finger":
            out.append("Ladies finger")
            i += 2
            continue
        if tl == "pigeon" and nxt and nxt.lower() == "pea":
            out.append("Pigeon pea")
            i += 2
            continue
        out.append(t)
        i += 1
    return out


def main():
    lines = LISTS.read_text(encoding="utf-8").split("\n")
    parsed = []  # (index, fields) for H01/H02 data rows
    for idx, ln in enumerate(lines):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.split("|")
        if f[0] in BLOCKS and len(f) == 6:
            parsed.append([idx, f])

    log = []
    drop = set()

    # 1. abundance / index rows
    for idx, f in parsed:
        hosts = f[2].strip()
        if (re.fullmatch(r"[=\d\.\s;%-]+", hosts) and hosts) or re.search(r"\d+\s*%", hosts) or re.search(
            r"shannon|evenness|dominance", f[1], re.I
        ):
            log.append(("dropped_non_host_row", f[0], f[1], f[2], ""))
            drop.add(idx)

    rows = [(i, f) for i, f in parsed if i not in drop]

    # 2-4. places, fragments, splits
    carry = None  # prefix fragment left at the end of the previous row
    prev_f = None
    for i, f in rows:
        before = f[2]
        places = [p for p in f[3].split(";") if p.strip()]
        toks = []
        for raw in before.split(";"):
            raw = raw.strip()
            if not raw:
                continue
            key = tidy(PLACE_RX.sub(" ", raw)).lower()
            if raw.lower() in SPLITS:
                toks.extend(SPLITS[raw.lower()])
                continue
            host, found = split_places(raw)
            places.extend(found)
            if host:
                toks.append(host)
        toks = merge_fragments(toks)
        # fragment at the start of a row completing the previous row's trailing prefix
        if toks and toks[0].lower() == "gourd" and prev_f is not None:
            last = prev_f[2].split("; ")[-1] if prev_f[2] else ""
            if last.lower() in PREFIX_FRAGS:
                prev_f[2] = "; ".join(prev_f[2].split("; ")[:-1] + [last.capitalize() + " gourd"])
                toks = toks[1:]
        # standalone single-word cell fragments
        fixed = []
        for t in toks:
            tl = t.lower()
            if tl in ("ladies", "finger"):
                fixed.append("Ladies finger")
            else:
                fixed.append(t)
        # drop duplicate hosts created by repairs, keep order
        seen, uniq = set(), []
        for t in fixed:
            if t.lower() not in seen:
                seen.add(t.lower())
                uniq.append(t)
        f[2] = "; ".join(uniq)
        merged, k = [], 0
        places = [tidy(p) for p in places]
        while k < len(places):
            if places[k] == "24" and k + 1 < len(places) and places[k + 1].lower().startswith("parganas"):
                tail = re.sub(r"parganas\s*\(?", "", places[k + 1], flags=re.I).rstrip(")").strip()
                merged.append("24 Parganas" + (f" ({tail})" if tail else ""))
                k += 2
            else:
                merged.append(places[k])
                k += 1
        places = merged
        seen = set()
        pl = []
        for p in places:
            p = tidy(p)
            if p and p.lower() not in seen:
                seen.add(p.lower())
                pl.append(p)
        f[3] = "; ".join(pl)
        prev_f = f
        if f[2] != before.strip():
            log.append(("repaired_host_list", f[0], f[1], before, f[2] + " || places: " + f[3]))

    # rows left with no host and no place after repair are removed
    for i, f in rows:
        if not f[2].strip() and not f[3].strip():
            log.append(("dropped_empty_row", f[0], f[1], "", ""))
            drop.add(i)

    # a bare leading 'gourd' that could not be attached is reported, not guessed
    for i, f in rows:
        if i in drop:
            continue
        if re.search(r"(^|; )(gourd|finger|pea)(;|$)", f[2], re.I):
            log.append(("fragment_left_for_review", f[0], f[1], f[2], ""))

    out = []
    for idx, ln in enumerate(lines):
        if idx in drop:
            continue
        hit = next((f for i, f in rows if i == idx), None)
        out.append("|".join(hit) if hit else ln)
    LISTS.write_text("\n".join(out), encoding="utf-8")

    if not log:
        print("nothing to repair")
        return
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["action", "block", "mite", "host_before", "host_after_and_places"])
        w.writerows(log)
    kinds = {}
    for r in log:
        kinds[r[0]] = kinds.get(r[0], 0) + 1
    print(kinds)


if __name__ == "__main__":
    main()
