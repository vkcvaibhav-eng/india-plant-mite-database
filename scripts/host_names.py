"""Standardise host names printed in the AICRP reports.

Reads config/host_dictionary.txt (see the header of that file for the format) and
resolves a printed host string, optionally with the printed scientific name and the
report block, to an accepted taxon, rank, plant family and standard common name.

Resolution order
  1. the printed common name, looked up as 'name@BLOCK' and then 'name' in the dictionary;
  2. if the common name is not in the dictionary (or is marked '?'), the printed scientific
     name, either in the dictionary or parsed as a binomial and placed in a family through the
     genus table;
  3. if the dictionary gives only a genus, family or group and the printed scientific name falls
     inside it, the printed name refines the result.
The printed scientific name is kept next to the result, and `host_check` says whether the two agree.
"""
import re
from pathlib import Path

DICT_PATH = Path(__file__).resolve().parents[1] / "config" / "host_dictionary.txt"

RANKS = ("species", "genus", "family", "group", "substrate", "ambiguous", "unresolved")


def norm(s):
    s = (s or "").replace("’", "'").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip(" .,;:")


def _rank_of(taxon):
    if taxon == "?":
        return "ambiguous"
    if taxon.startswith("[substrate]"):
        return "substrate"
    if taxon.startswith("[group]"):
        return "group"
    if re.fullmatch(r"[A-Z][a-z]+aceae", taxon):
        return "family"
    if taxon.endswith(" sp."):
        return "genus"
    return "species"


class HostDictionary:
    def __init__(self, path=DICT_PATH):
        self.entries = {}
        self.genus_family = {}
        self.genus_fix = {}
        section = "entries"
        for raw in Path(path).read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line.strip("[]")
                continue
            if section == "genus":
                g, fam = [x.strip() for x in line.split(":")]
                self.genus_family[g.lower()] = (g, fam)
                continue
            if section == "genus spellings":
                a, b = [x.strip() for x in line.split("=>")]
                self.genus_fix[a.lower()] = b
                continue
            keys, rest = line.split("=>")
            parts = [p.strip() for p in rest.split("|")]
            parts += [""] * (4 - len(parts))
            taxon, family, common, flag = parts[:4]
            rank = _rank_of(taxon)
            entry = {
                "taxon": taxon if rank in ("species", "genus", "family") else ("" if rank == "ambiguous" else re.sub(r"^\[[a-z]+\]\s*", "", taxon)),
                "rank": rank,
                "family": family,
                "common": common,
                "medium": flag == "m",
            }
            for k in keys.split(";"):
                k = norm(k.split("@")[0]) + ("@" + k.split("@")[1].strip() if "@" in k else "")
                if k:
                    self.entries[k] = entry
            if rank in ("species", "genus") and family:
                g = taxon.split()[0]
                self.genus_family.setdefault(g.lower(), (g, family))

    # ------------------------------------------------------------------
    def parse_scientific(self, s):
        """Return (genus, species_or_None, family) when the string reads as a plant binomial."""
        s = norm(s)
        s = re.sub(r"\(.*?\)", " ", s)
        words = re.findall(r"[a-z][a-z\-]+", s)
        if not words:
            return None
        g = self.genus_fix.get(words[0], words[0])
        fam = self.genus_family.get(g.lower())
        if not fam:
            return None
        sp = None
        if len(words) > 1 and words[1] not in ("sp", "spp", "var", "and") and len(words[1]) > 2:
            sp = words[1]
        return fam[0], sp, fam[1]

    def _result(self, taxon, rank, family, common, basis, confidence):
        return {
            "host_taxon_std": taxon,
            "host_rank_std": rank,
            "host_family": family,
            "host_std_common": common,
            "host_basis": basis,
            "host_confidence": confidence,
        }

    def resolve(self, common, sci, block=""):
        c, s = norm(common), norm(sci)
        entry = None
        for k in ((c + "@" + block), c, ):
            if c and k in self.entries:
                entry = self.entries[k]
                break
        used_sci_key = False
        if (entry is None or entry["rank"] == "ambiguous") and s:
            if (s + "@" + block) in self.entries or s in self.entries:
                e2 = self.entries.get(s + "@" + block) or self.entries[s]
                if e2["rank"] != "ambiguous":
                    entry, used_sci_key = e2, True
        parsed = self.parse_scientific(s) if s else None
        if entry is None and not c and s is not None and parsed is None and s in self.entries:
            entry = self.entries[s]

        if entry is not None and entry["rank"] != "ambiguous":
            taxon, rank, family, comm = entry["taxon"], entry["rank"], entry["family"], entry["common"]
            basis = "printed_scientific_name_via_dictionary" if (used_sci_key or (not c)) else "dictionary"
            conf = "medium" if entry["medium"] else "high"
            if rank in ("genus", "family", "group") and parsed and not used_sci_key:
                g, sp, fam = parsed
                same = (rank == "genus" and taxon.split()[0].lower() == g.lower()) or (
                    rank == "family" and family == fam
                )
                if same and sp:
                    taxon, rank, family, basis = f"{g} {sp}", "species", fam, "dictionary_refined_by_printed_scientific_name"
                elif same:
                    pass
            return self._result(taxon, rank, family, comm, basis, conf)

        # no usable dictionary entry: try the printed scientific name (or a scientific-looking common name)
        for cand, label in ((s, "printed_scientific_name"), (c, "printed_name_as_scientific")):
            if not cand:
                continue
            p = self.parse_scientific(cand)
            if p:
                g, sp, fam = p
                taxon = f"{g} {sp}" if sp else f"{g} sp."
                return self._result(taxon, "species" if sp else "genus", fam, "", label, "high" if sp else "medium")
        if entry is not None and entry["rank"] == "ambiguous":
            return self._result("", "ambiguous", "", entry["common"], "context_dependent_name", "")
        # a well-formed binomial whose genus is not in the table: keep the printed name, family unknown
        for cand in (sci, common):
            m = re.match(r"^\s*([A-Z][a-z]{2,})\s+([a-z][a-z\-]{2,}|sp\.?|spp\.?)\s*$", cand or "")
            if m:
                taxon = f"{m.group(1)} sp." if m.group(2).startswith("sp") else f"{m.group(1)} {m.group(2)}"
                return self._result(taxon, "genus" if taxon.endswith(" sp.") else "species", "", "",
                                    "printed_binomial_genus_not_in_table", "medium")
        return self._result("", "unresolved", "", "", "not_in_dictionary", "")


# genus pairs that are the same plant under an old and a current name
SAME_GENUS = {("lycopersicon", "solanum"), ("eujenia", "syzygium"), ("achras", "manilkara"), ("mimusops", "manilkara"),
              ("feronia", "limonia"), ("emblica", "phyllanthus"), ("kirganelia", "phyllanthus"), ("althaea", "alcea"),
              ("pyrus", "malus"), ("citrullus", "cucumis"), ("licopersicon", "solanum")}


def agree(D, result, sci):
    """Compare the resolved taxon with the printed scientific name.

    '' when no usable scientific name was printed, 'agree' when the genus matches (or is the same plant
    under an old genus name), 'species_differs' when the genus matches but the epithet does not (usually a
    synonym or a different species of the same genus), 'genus_differs' when they point to different plants.
    """
    p = D.parse_scientific(sci) if norm(sci) else None
    if not p or result["host_rank_std"] in ("unresolved", "ambiguous", "group", "substrate", "family"):
        return ""
    gs, es, _ = p
    words = result["host_taxon_std"].split()
    if not words:
        return ""
    gt, et = words[0], (words[1] if len(words) > 1 else "sp.")
    if gs.lower() != gt.lower() and (gs.lower(), gt.lower()) not in SAME_GENUS:
        return "genus_differs"
    if es and et != "sp." and es != et:
        return "species_differs"
    return "agree"


# ----------------------------------------------------------------------------------------------
CROP_PATH = DICT_PATH.parent / "host_crop_type.txt"
_GROUP_TYPES = {"weeds and wild plants": "weed_wild", "forest plants": "tree_forest", "ornamentals": "ornamental",
                "medicinal plants": "medicinal_aromatic", "vegetables": "vegetable", "fruits": "fruit",
                "fodder crops": "fodder", "cucurbits": "vegetable", "grasses": "weed_wild", "shade crop": "tree_forest"}


class CropTypes:
    def __init__(self, path=CROP_PATH):
        self.exact, self.genus = {}, {}
        for raw in Path(path).read_text(encoding="utf-8").splitlines():
            if not raw.strip() or raw.startswith("#"):
                continue
            t, items = raw.split(":", 1)
            for it in items.split(";"):
                it = it.strip()
                if it.endswith("*"):
                    self.genus[it[:-1].lower()] = t.strip()
                elif it:
                    self.exact[it.lower()] = t.strip()

    def of(self, taxon, rank):
        if rank == "substrate":
            return "stored_product"
        if rank == "group":
            for k, v in _GROUP_TYPES.items():
                if taxon.lower().startswith(k):
                    return v
            return "not_assigned"
        if not taxon or rank in ("ambiguous", "unresolved"):
            return ""
        t = taxon.lower()
        if t in self.exact:
            return self.exact[t]
        return self.genus.get(t.split()[0], "not_assigned")
