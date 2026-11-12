#!/usr/bin/env python3
"""Check transcribed AICRP rows against the text layer of the source PDF.

For each observation row of one report, the script looks for a page of the PDF on which the mite
(its species epithet, or the family or genus name for higher-rank rows) and the host (and the place,
when the row has one) all occur, allowing the neighbouring page for tables that run over a page break.
Rows that fail are written to a CSV for checking by eye. A pass shows the words stand together in the
source; it does not prove the row is right, and a fail may only mean the text layer is poor there.

Usage: verify_against_pdf.py "REPORT NAME" file.pdf out.csv [--alias printed=searched ...]
Needs pdftotext (poppler). Only useful for reports with a real text layer.
"""
import csv, re, subprocess, sys, pathlib, unicodedata, collections

ROOT = pathlib.Path(__file__).resolve().parents[2]


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def tokens(s, minlen=4):
    """Alphabetic words of a printed string, longest first, as squeezed lower-case tokens."""
    words = [w for w in re.findall(r"[A-Za-z]+", s or "") if len(w) >= minlen]
    return [norm(w) for w in sorted(words, key=len, reverse=True)]


def main():
    report, pdf, out = sys.argv[1:4]
    alias = dict(a.split("=", 1) for a in sys.argv[5:]) if len(sys.argv) > 4 and sys.argv[4] == "--alias" else {}
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, errors="replace").stdout
    pages = [norm(p) for p in text.split("\x0c")]
    index = {}

    def where(tok):
        if tok not in index:
            index[tok] = {i for i, p in enumerate(pages) if tok in p}
        return index[tok]

    rows = [r for r in csv.DictReader(open(ROOT / "data/aicrp/aicrp_observations.csv", encoding="utf-8")) if r["report"] == report]
    res, fails = collections.Counter(), []
    for r in rows:
        printed = r["mite_as_printed"]
        mite_key = alias.get(r["mite_name"]) or alias.get(printed)
        if mite_key:
            mt = [norm(mite_key)]
        elif r["mite_rank"] == "species":
            ep = re.sub(r"\(.*?\)", " ", r["mite_name"]).split()
            mt = [norm(ep[-1])] if ep else []
        else:
            mt = tokens(re.sub(r"\bspp?\b\.?", " ", printed))[:1]
        ht = tokens(r["host_as_printed"])[:1]
        pt = tokens(r["place_as_printed"])[:1]
        need = [t for t in (mt, ht, pt) if t]
        if not mt:
            res["no_mite_token"] += 1; continue
        sets = [where(t[0]) for t in need]
        ok = False
        for p in sets[0]:
            if all(any(q in s for q in (p - 1, p, p + 1)) for s in sets[1:]):
                ok = True; break
        if ok:
            res["found_together"] += 1
        else:
            missing = [lab for lab, t in (("mite", mt), ("host", ht), ("place", pt)) if t and not where(t[0])]
            kind = "word_not_in_text:" + "+".join(missing) if missing else "words_on_different_pages"
            res[kind] += 1
            fails.append({"obs_id": r["obs_id"], "block_id": r["block_id"], "mite_as_printed": printed, "host_as_printed": r["host_as_printed"],
                          "place_as_printed": r["place_as_printed"], "pairing": r["pairing"], "result": kind})
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["obs_id", "block_id", "mite_as_printed", "host_as_printed", "place_as_printed", "pairing", "result"], lineterminator="\n")
        w.writeheader(); w.writerows(fails)
    print(report, "rows", len(rows), dict(res))


if __name__ == "__main__":
    main()
