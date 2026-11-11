"""Build AICRP survey observations from the hand transcriptions in data/aicrp/transcription/.

Source reports (annual reports of the All India Coordinated Research Project on Agricultural Acarology):
  AICRP 1996-98  (survey chapter IV.1, printed pp. 185-212)
  AICRP 1992-94  (survey chapter III.1, printed pp. 40-62: Bangalore, Coimbatore, Navsari, Ludhiana, Varanasi, Pusa, Kalyani, pigeonpea sterility mosaic survey)
  AICRP 1989     (Second Workshop, Hisar; survey tables and notes of Kalyani, Coimbatore, Ludhiana, Bangalore, Navsari, Varanasi)
  AICRP 1988     (First Workshop, 5-7 October 1988; survey tables of Bangalore, Coimbatore, Ludhiana, Hisar material, Pusa, Varanasi)
  AICRP 1990-91  (survey chapter I, printed pp. 9-39; Bangalore has localities only, Chapter II taxonomic study not yet transcribed)
Each transcribed row keeps the text as printed apart from obvious OCR noise (flagged in 'note').

Outputs
  data/aicrp/aicrp_observations.csv        one row per mite x host x place as printed
  data/review/aicrp_places_unresolved.csv  places with no state assigned
  data/review/aicrp_names_not_in_checklist.csv  mite names that do not join to the Paper 1 checklist
"""
import csv, re, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
TR = ROOT / "data/aicrp/transcription"
OUT = ROOT / "data/aicrp"
REV = ROOT / "data/review"

def read_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(p, rows, cols):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)

def pipe_rows(p, n):
    for line in open(p, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("|")
        parts += [""] * (n - len(parts))
        yield [x.strip() for x in parts[:n]]

blocks = {b["block_id"]: b for b in read_csv(TR / "blocks.csv")}

ABBREV = {
    **{f"T. {s}": f"Tetranychus {s}" for s in ("urticae", "macfarlanei", "ludeni", "neocaledonicus", "fijiensis", "cinnabarinus")},
    **{f"A. {s}": f"Amblyseius {s}" for s in ("longispinosus", "multidentatus", "fallacis", "indicus", "ovalis", "alstoniae", "largoensis", "coccineae")},
    "A. indica": "Amblyseius indicus", "A. fleschneri": "Agistemus fleschneri",
    "A. (E.) coccosocius": "Amblyseius (Euseius) coccosocius", "A. (A.) largoensis": "Amblyseius (Amblyseius) largoensis",
    "A. (A.) longispinosus": "Amblyseius (Amblyseius) longispinosus",
    "A. mangiferae": "Aceria mangiferae", "A. litchii": "Aceria litchii",
    "O. thelytokus": "Oligonychus thelytokus", "O. indicus": "Oligonychus indicus", "O. mangiferus": "Oligonychus mangiferus",
    "R. indica": "Raoiella indica",
    "B. californicus": "Brevipalpus californicus", "B. phoenicis": "Brevipalpus phoenicis", "B. obovatus": "Brevipalpus obovatus",
    "E. orientalis": "Eutetranychus orientalis", "E. bredini": "Eutetranychus bredini", "E. africanus": "Eutetranychus africanus",
    "P. latus": "Polyphagotarsonemus latus", "P. latens": "Petrobia latens", "P. harti": "Petrobia harti",
    "C. setirostris": "Cunaxa setirostris",
    "Amblyseius ovalis": "Amblyseius ovalis", "Amblyseius sp.": "Amblyseius sp.",
}
FAMILY_WORDS = {"phytoseiid": "Phytoseiidae", "tydeid": "Tydeidae", "tarsonemid": "Tarsonemidae", "tenuipalpid": "Tenuipalpidae",
                "tetranychid": "Tetranychidae", "stigmaeid": "Stigmaeidae", "bdellid": "Bdellidae", "eriophyid": "Eriophyidae", "acarid": "Acaridae"}
HIGHER = {"mesostigmata", "cryptostigmata", "astigmata", "macroseiinae"}
GENUS_FAMILY = {}
for fam, gens in {
    "Tetranychidae": "Eonychus Tetranychus Eutetranychus Eotetranychus Oligonychus Schizotetranychus Panonychus Bryobia Petrobia Aponychus Bryobiella Stylophoronychus",
    "Tenuipalpidae": "Brevipalpus Tenuipalpus Raoiella Larvacarus Dolichotetranychus Pentamerismus Terminalichus Obuloides Krugeria",
    "Tarsonemidae": "Polyphagotarsonemus Tarsonemus Stenotarsonemus Steneotarsonemus Fungitarsonemus Lupotarsonemus",
    "Eriophyidae": "Aceria Eriophyes Acalitus Cisaberoptus Colomerus Acaphylla Calacarus Paraphytoptus Aculus Aculops Chiracus Diptilomiopus Ditrimacus Tegonotus Neocalaconus Acaphyllisa Anthocoptes Ashieldophyes Calepitrimerus Cheiracus Ditrymacus Floracarus Metaculus Neocalacarus Phyllocoptruta Rhombacus Tetra",
    "Pyemotidae": "Pyemotes",
    "Phytoseiidae": "Amblyseius Phytoseius Typhlodromus Indodromus Platyseiella",
    "Tuckerellidae": "Tuckerella", "Anystidae": "Anystis",
    "Cunaxidae": "Cunaxa Neocunaxoides Dactyloscirus Pseudocunaxa Scirula", "Laelapidae": "Ololaelaps Pseudoparasitus Hypoaspis", "Galumnidae": "Galumna",
    "Ameroseiidae": "Neocypholaelaps",
    "Tydeidae": "Pronematus Tydeus Lorryia", "Stigmaeidae": "Agistemus Mediolata", 
    "Cheyletidae": "Cheletogenes Cheletominus Hemicheyletia Cheyletus Cheletomorpha Chelacaropsis Cheletacarus Chelonotus Neoacaropsis Acaropsis",
    "Erythraeidae": "Sphaerolophus", "Bdellidae": "Bdella",
    "Acaridae": "Acarus Tyrophagus Rhizoglyphus Suidasia Lardoglyphus", "Ascidae": "Lasioseius",
    "Hydrozetidae": "Hydrozetes", "Malaconothridae": "Trimalaconothrus", "Oribatulidae": "Scheloribates", "Liacaridae": "Liacarus",
    "Pygmephoridae": "Pygmephorus", "Glycyphagidae": "Austroglycyphagus Glycyphagus",
}.items():
    for g in gens.split():
        GENUS_FAMILY[g] = fam

PLACE_STATE = {}
for st, places in {
    "Punjab": "Fazilka Mukerian Ludhiana Ropar Balachaur Hoshiarpur Amritsar Rajpura Abohar Fatehgarh Sahib|Sunam Patiala Batala Gurdaspur Sangrur Kartarpur Kapurthala Ladhowal Pathankot Ferozepur Ajnala|Dehra Baba Nanak|Bathinda Nangal Jalandhar Garshankar",
    "Himachal Pradesh": "Palampur Solan Nalagarh Una Shimla Jasur Jassur Hamirpur",
    "Chandigarh": "Chandigarh", "Haryana": "Kalka", "Rajasthan": "Ganganagar", "Jammu & Kashmir": "Kathua",
    "Kerala": "Kottayam Calicut Palghat", "Tamil Nadu": "Coimbatore Sivagangai Trichy Bhavanisagar",
    "Karnataka": "Mangalore Dharwad Bangalore Hosakote",
    "Uttar Pradesh": "Varanasi Allahabad Azamgarh Jaunpur Ghazipur Lucknow Kanpur Ballia Pratapgarh Mirzapur",
    "Bihar": "Madhubani Saharsa Khagaria Samastipur Muzaffarpur Vaishali Purnea Motihari Patna Dholi Pusa",
    "Andhra Pradesh": "Ananthapalle Anakapalle Vijayanagaram Vizianagaram Vishakapatnam Tallapalem Makavarpalem Makavarapallem Tirupathi",
    "West Bengal": "Kalyani Itachuna Bhaluka Harindanga",
}.items():
    for p in re.split(r"[ |]", places.replace("|", "|")):
        pass
    for chunk in places.split("|"):
        # chunks hold space-separated one-word places, except the explicit multi-word ones between pipes
        words = chunk.split()
        if chunk in ("Fatehgarh Sahib", "Dehra Baba Nanak"):
            PLACE_STATE[chunk] = st
        else:
            for w in words:
                PLACE_STATE[w] = st
    # multi-word names listed without pipes above
PLACE_STATE.update({
    "Sirsa": "Haryana",
    **{w: "Tamil Nadu" for w in ("Kannampalayam", "TNAU, Coimbatore", "Thirumalayampalayam", "Nachipalayam", "Karamadai", "Aathipalayam", "Bhavanisagar", "Aandipalayam", "Kothagiri", "Gudaloor", "Ooty", "Vellakovil", "Tamil Nadu")},
    **{w: "Kerala" for w in ("Ambalavayal", "Mattampuram", "Kanjikkode", "Cherpu", "Palode", "Kochi", "Vandanmedu", "Thottapadi", "Sreekaryam", "Elavenchery", "Alathur", "Anakkara", "Edappalam", "Kannothuchal")},
    "Kaziranga National Park": "Assam",
    **{w: "Punjab" for w in ("Kabulshah Khuban", "Fazilka", "Faridkot", "Batala", "Sangrur", "Abohar", "Jalandhar", "Ballowal Saunkhri", "Anandpur Sahib", "Punjab", "Bhai Rupa", "Bathinda", "Kapurthala", "Gurdaspur", "Sri Muktsar Sahib", "Hoshiarpur")},
    **{w: "Rajasthan" for w in ("Durgapura", "Neemrana", "Bikaner", "Jaisalmer", "Bhojka", "Sagra", "Jaipur", "Dudu", "Dausa", "Tonk")},
    **{w: "Himachal Pradesh" for w in ("Mashobra", "Naggar", "Himachal Pradesh")},
    **{w: "Assam" for w in ("Jorhat", "Sibsagar", "Nagaon", "Karbi-Anglong", "Tinsukia", "Golaghat", "Guwahati", "Kahikuchi")},
    **{w: "Kerala" for w in ("Vellanikkara", "Madakkathara", "Elanadu", "Aryampadam", "Parappur", "Pattancherry", "Nenmara", "Villadam", "Mannuthy", "Puthukaad", "Odakkali", "Cheroor", "Malapuzha", "Muvattupuzha", "Chirakkakkode", "Vellayani", "Chelakkara", "Vyttila", "Wadakkanchery", "Manalur", "Mundathikkode", "Pazhayannur")},
    **{w: "West Bengal" for w in ("Chandamari", "Madanpur", "Kathaltala", "Gayeshpur", "Kuntighat", "Birpara", "Akna", "Sarati", "Mondouri", "Jirat", "Behula", "Bolaghar", "Nakashipara", "Bethuadahari", "Baharampur", "Murshidabad", "Malda", "Burdwan", "Hooghly", "Nadia", "Bankura", "Simurali", "Ranaghat", "Haringhata", "Santipur", "Chakdha", "Chakdhah", "Natunpally", "Muratipur", "Ghoshpara", "Badkulla", "Iswaripur", "Barohat", "Charsarati", "Tarenipur", "Amdanga", "Habra", "Barasat", "Bira", "Awalsiddhi", "Baruipara", "Birpar", "Jalpaiguri", "Cooch Behar", "New Jalpaiguri", "Siliguri", "Nimpith", "Susnia", "Susunia", "Dhaldanga", "Sunukpahari", "Bisnupur", "Joynagar", "Kalimpong")},
    **{w: "Bihar" for w in ("Muzaffarpur", "Sitamarhi", "Motihari", "Darbhanga", "Madhuban", "Modhubani", "Misrolipara", "Motihary", "Pipra", "Srikrishna priya")},"Fatehgarh Sahib": "Punjab", "Dehra Baba Nanak": "Punjab", "Dera Baba Nanak": "Punjab"})
for bad in ("Fatehgarh", "Sahib", "Dehra", "Baba", "Nanak"):
    PLACE_STATE.pop(bad, None)
PLACE_STATE.update({"Almora": "Uttarakhand", "Nainital": "Uttarakhand", "Shahjahanpur": "Uttar Pradesh", "Sitapur": "Uttar Pradesh", "Rae Bareli": "Uttar Pradesh",
                    "Jullundur": "Punjab", "Bhatinda": "Punjab", "Faridkot": "Punjab", "Kapurthala": "Punjab", "Gurdaspur": "Punjab", "Solan": "Himachal Pradesh",
                    "Rane Bennur": "Karnataka", "Hiriyur": "Karnataka", "HAU Hisar": "Haryana"})
PLACE_STATE.update({"Jog falls": "Karnataka", "Ghati Subramanya": "Karnataka", "Makali Durga": "Karnataka",
                    "Pothnal": "Karnataka", "Raichur": "Karnataka", "Sindhanur": "Karnataka", "Chintamani": "Karnataka",
                    "Hessarghatta": "Karnataka", "Jawalgere": "Karnataka", "Jawalgare": "Karnataka", "Mandya": "Karnataka", "Hebbal": "Karnataka"})
PLACE_STATE.update({
    "Madurai": "Tamil Nadu", "Dindigul": "Tamil Nadu", "Oddanchetram": "Tamil Nadu", "Naraseepuram": "Tamil Nadu", "Thadagam": "Tamil Nadu", "Arruapukottai": "Tamil Nadu",
    "Hoskote": "Karnataka", "Kanakapura": "Karnataka", "Rajankunte": "Karnataka", "Chikkaballapur": "Karnataka", "Honnenahalli": "Karnataka", "Chamarajanagar": "Karnataka",
    "Thindlu": "Karnataka", "Lakshmipura Cross": "Karnataka", "IIHR": "Karnataka", "Chettahalli": "Karnataka", "Horticultural Research Station, GKVK": "Karnataka", "GKVK": "Karnataka", "GKVK, Bangalore": "Karnataka",
    "Chitradurga": "Karnataka", "Bidar": "Karnataka", "Belgaum": "Karnataka",
    "Bakhari": "Bihar", "Dubaha": "Bihar", "Hazipur": "Bihar", "Lalganj": "Bihar", "Harpur": "Bihar", "Biraul": "Bihar", "Saidpur": "Bihar", "Tara": "Bihar", "Mahamada": "Bihar", "Malinagar": "Bihar",
    "Sitamarhi": "Bihar", "Bhagalpur": "Bihar", "East Champaran": "Bihar", "Pusa Farm": "Bihar", "Dholi Farm": "Bihar",
    "Dang": "Gujarat", "Navsari": "Gujarat", "Plassey": "West Bengal", "Garhshankar": "Punjab",
})
PLACE_STATE.update({
    **{w: "West Bengal" for w in ("Kalyani", "Madanpur", "Sonarpur", "Mondouri", "Bankura", "Halisahar", "Santipur", "Chakdah", "Bagnan", "Guptipara", "Burdwan", "Mohitnagar",
                                  "Chinsura", "Chinsurah", "Barasat", "Barrackpur", "Coochbehar", "Baruipur", "Malda", "Murshidabad", "Debali", "Jhargram", "Krishnagar", "Mirik",
                                  "Pedong", "Haringhata", "Midnapore", "Howrah", "Sonamukhi")},
    "Puri": "Odisha", "Udala": "Odisha", "Chandikhal": "Odisha", "Mahimada": "Bihar",
    "Dholakuan": "Himachal Pradesh", "Kulu": "Himachal Pradesh", "Malerkotla": "Punjab",
    "Karnataka": "Karnataka", "GKVK, Bangalore": "Karnataka", "Botanical Gardens, GKVK, Bangalore": "Karnataka", "Mangalore": "Karnataka", "Mysore": "Karnataka",
    "North Karnataka": "Karnataka", "Western Ghats of Karnataka": "Karnataka", "Hirehalli": "Karnataka", "Bangalore": "Karnataka",
    "APAU, Hyderabad": "Telangana", "APAU campus, Hyderabad": "Telangana", "Kalyani Dam, Thirupathi": "Andhra Pradesh",
    "Surat": "Gujarat", "Bharuch": "Gujarat", "Durgapura (Jaipur)": "Rajasthan", "Jobner": "Rajasthan",
})
PLACE_STATE.update({
    **{w: "West Bengal" for w in ("Calcutta", "Shibpore", "Kalimpong", "Canning", "Contai", "Tarakeswar", "Hooghly")},
    **{w: "Tamil Nadu" for w in ("Nanjagoundenpudur", "Velur", "Bhavani", "Pugalur", "Chidambarum", "Ootacamund", "Periyakulam")},
    "Calicut University": "Kerala", "Kadalundi": "Kerala", "Chaliyam": "Kerala", "Kerala": "Kerala", "Jammu": "Jammu & Kashmir",
    **{w: "Karnataka" for w in ("Nandagudi", "Kengeri", "Devarayana Durga", "Anekal", "Puttur", "Chintamani", "Hirehalli")},
})
AMBIGUOUS_PLACES = {"Sujanpur": "Sujanpur exists in Himachal Pradesh and in Punjab", "Jakhal": "Jakhal is in Haryana (Fatehabad); the report lists it among its Punjab surveys"}

def split_authority(mite):
    m = re.match(r"^([A-Z][a-z]+(?: \([A-Z][a-z]+\))? [a-z]+)\s+(\(.+\)|[A-Z].*)$", mite)
    return (m.group(1), m.group(2)) if m else (mite, "")

def expand(name):
    return ABBREV.get(name, name)

def classify(name):
    n = name.strip()
    low = n.lower()
    if low in FAMILY_WORDS: return FAMILY_WORDS[low], "family"
    if low in HIGHER: return n, "higher"
    if n.endswith("idae") and " " not in n: return n, "family"
    if n.startswith("New genus"): return n, "unresolved"
    g = n.split()[0]
    if re.match(r"^[A-Z][a-z]+( \([A-Z][a-z]+\))? (sp\.?|spp\.?)$", n) or re.match(r"^[A-Z][a-z]+$", n):
        return n, "genus"
    if re.match(r"^[A-Z][a-z]+( \([A-Z][a-z]+\))? [a-z\-]+$", n): return n, "species"
    return n, "unresolved"

def host_parts(h):
    m = re.match(r"^([A-Z][a-z]+ (?:[a-z\-]+|sp\.))\s*\(([A-Z][a-z]+(?: [a-z]+)?)\)\s*$", h)   # Scientific name (Common name)
    if m and not re.match(r"^[A-Z][a-z]+ [a-z]+$", m.group(2)): return m.group(2), m.group(1)
    if h.startswith("sci:"): return "", h[4:].strip()   # host printed as a scientific name
    m = re.match(r"^(.*?)\s*\(([A-Z][a-z]+ .*?)\)\s*$", h)
    if m: return m.group(1).strip(), m.group(2).strip()
    return h.strip(), ""

def place_state(place, default):
    p = re.sub(r",\s*Tamil Nadu$", "", place.strip())
    for key in sorted(PLACE_STATE, key=len, reverse=True):
        if p == key: return PLACE_STATE[key], "place_lookup"
    if p in AMBIGUOUS_PLACES: return "", "ambiguous_place"
    return default, "centre_state"

MULTI_STATE = {"B04", "B05", "B06", "B07", "B08", "C05", "C08", "E04", "F01", "F03", "F04", "G01", "G04", "H05", "I02"}
obs, unresolved = [], collections.Counter()

def add(block_id, mite, hosts, places, status, note, pairing, code=""):
    b = blocks[block_id]
    stages = {}
    clean = []
    for h in hosts:   # lower-case bracket text after a host is a plant part or stage, kept in the remark
        m = re.match(r"^(.*?)\s*\(([a-z][^()]*)\)\s*$", h)
        if m and m.group(1): stages[m.group(1)] = m.group(2); clean.append(m.group(1))
        else: clean.append(h)
    hosts = clean
    for piece in re.split(r"\s+and\s+(?=[A-Z][a-z]+id\b)", mite) if " and " in mite and mite.lower().endswith(("bdellid", "bdellidae")) else [mite]:
        remark = ""
        if " ~ " in piece: piece, remark = [x.strip() for x in piece.split(" ~ ", 1)]
        if piece.endswith(" sp. nov."):
            piece = piece[:-len(" sp. nov.")].strip(); remark = "; ".join(x for x in (remark, "printed as sp. nov. in the report") if x)
        base, auth = split_authority(piece)
        name = expand(base)
        name, rank = classify(name)
        family = name if rank == "family" else GENUS_FAMILY.get(name.split()[0], "")
        combos = []
        if len(places) > 1 and hosts and pairing != "force":
            combos = [(h, "", "host_only") for h in hosts] + [("", pl, "place_only") for pl in places]
        elif places:
            combos = [(h, pl, "host_and_place_paired" if h else "place_only") for h in (hosts or [""]) for pl in places]
        else:
            combos = [(h, "", "host_only" if h else "no_host_no_place") for h in (hosts or [""])]
        for h, pl, how in combos:
            hc, hs = host_parts(h)
            if h.startswith("sci:"): h = h[4:]
            st, basis = (place_state(pl, b["state"]) if pl else (b["state"], "centre_state"))
            if pl and block_id in MULTI_STATE and basis in ("centre_state", "ambiguous_place"):
                unresolved[(block_id, pl, b["state"], basis)] += 1
            extra = "host and place lists printed separately for this species" if len(places) > 1 and hosts and pairing != "force" else ""
            obs.append({
                "obs_id": "", "block_id": block_id, "report": b["report"], "centre": b["centre"], "institute": b["institute"],
                "survey_period": b["survey_period"], "pdf_pages": b["pdf_pages"], "printed_pages": b["printed_pages"],
                "mite_as_printed": piece, "mite_name": name, "mite_rank": rank, "mite_family": family, "mite_authority": auth,
                "host_as_printed": h, "host_common": hc, "host_scientific": hs,
                "place_as_printed": pl, "state": st, "state_basis": basis if pl else "centre_state",
                "status": status, "occurrence_code": code, "pairing": how,
                "remark": "; ".join(x for x in (remark, note, extra, ("host: " + stages[h]) if h in stages else "") if x),
            })

def semis(s): return [x.strip() for x in s.split(";") if x.strip()]

for bid, crop, place, mite, status, note in pipe_rows(TR / "paired.txt", 6):
    pairing = "force" if place.startswith("=") else ""
    ps = semis(place.lstrip("="))
    mites = semis(mite)
    stats = [x.strip() for x in status.split(";")] if status else [""]
    for m in mites:
        add(bid, m, semis(crop), ps, status, note, pairing)

for bid, mite, hosts, locs, status, note in pipe_rows(TR / "lists.txt", 6):
    role = {"predator": "predator", "stored product": "stored_product", "phytophagous": "phytophagous"}
    st = status
    rem = note
    pairing = ""
    substrate = "stored_product" if "stored product" in status else ""
    add(bid, mite, semis(hosts), semis(locs), st, rem, pairing)

for bid, host, places, mites, extra in pipe_rows(TR / "host_mites.txt", 5):
    for m in semis(mites):
        code = ""
        if m.startswith("**"): code, m = "moderate", m[2:].strip()
        elif m.startswith("*"): code, m = "stray", m[1:].strip()
        add(bid, m, [host], semis(places), "", extra, "", code)

for i, r in enumerate(obs, 1):
    r["obs_id"] = f"AIC{i:04d}"

cols = list(obs[0].keys())
write_csv(OUT / "aicrp_observations.csv", obs, cols)
write_csv(REV / "aicrp_places_unresolved.csv",
          [{"block_id": k[0], "place": k[1], "centre_state_used": k[2], "basis": k[3], "rows": v} for k, v in sorted(unresolved.items())],
          ["block_id", "place", "centre_state_used", "basis", "rows"])

# join mite names to the Paper 1 checklist
COVERED = {"Tetranychidae", "Tenuipalpidae", "Eriophyidae", "Tarsonemidae", "Tuckerellidae", "Phytoseiidae"}
species = {r["species_id"]: r for r in read_csv(ROOT / "data/raw/species_list.csv")}
name2id = collections.defaultdict(set)
valid2id = {}
for r in read_csv(ROOT / "data/raw/species_list_names.csv"):
    name2id[r["name"]].add(r["species_id"])
    if r["kind"] == "valid": valid2id[r["name"]] = r["species_id"]
cross = {r["aicrp_name"]: r for r in read_csv(ROOT / "config/name_crosswalk.csv")}
missing = collections.defaultdict(lambda: {"rows": 0, "centres": set(), "family": ""})
for r in obs:
    r["species_id"] = r["checklist_name"] = r["join_basis"] = ""
    r["checklist_family_covered"] = int(r["mite_family"] in COVERED)
    if r["mite_rank"] != "species": continue
    nm = r["mite_name"]
    if nm in cross and cross[nm]["checklist_name"] in valid2id:
        r["species_id"] = valid2id[cross[nm]["checklist_name"]]; r["checklist_name"] = cross[nm]["checklist_name"]; r["join_basis"] = "crosswalk"
        continue
    ids = name2id.get(nm, set())
    alt = re.sub(r" \([A-Z][a-z]+\)", "", nm)   # subgenus dropped
    if not ids and alt != nm:
        if alt in cross and cross[alt]["checklist_name"] in valid2id:
            r["species_id"] = valid2id[cross[alt]["checklist_name"]]; r["checklist_name"] = cross[alt]["checklist_name"]; r["join_basis"] = "crosswalk"
            continue
        ids = name2id.get(alt, set())
        if len(ids) == 1:
            sid = next(iter(ids)); r["species_id"] = sid; r["checklist_name"] = species[sid]["species"]; r["join_basis"] = "subgenus_dropped"
            continue
    if len(ids) == 1:
        sid = next(iter(ids)); r["species_id"] = sid; r["checklist_name"] = species[sid]["species"]
        r["join_basis"] = "exact" if species[sid]["species"] == nm else "listed_synonym"
    elif r["checklist_family_covered"]:
        missing[nm]["rows"] += 1; missing[nm]["centres"].add(r["centre"]); missing[nm]["family"] = r["mite_family"]
        missing[nm]["multi"] = len(ids) > 1

cols = list(obs[0].keys())
write_csv(OUT / "aicrp_observations.csv", obs, cols)
write_csv(REV / "aicrp_places_unresolved.csv",
          [{"block_id": k[0], "place": k[1], "centre_state_used": k[2], "basis": k[3], "rows": v} for k, v in sorted(unresolved.items())],
          ["block_id", "place", "centre_state_used", "basis", "rows"])
write_csv(REV / "aicrp_names_not_in_checklist.csv",
          [{"mite_name": k, "family": v["family"], "rows": v["rows"], "centres": ";".join(sorted(v["centres"])), "ambiguous_join": int(v.get("multi", False))}
           for k, v in sorted(missing.items())], ["mite_name", "family", "rows", "centres", "ambiguous_join"])

# compare with the Gupta & Mondal (2023) species x state layer
gm_state = {(r["species_id"], r["state"]) for r in read_csv(ROOT / "data/records/species_state.csv") if r["species_id"]}
gm_species = {sid for sid, _ in gm_state}
NOT_SINGLE = ("(not split)",)
pairs = collections.defaultdict(lambda: {"rows": 0, "centres": set(), "periods": set(), "names": set()})
for r in obs:
    if not r["species_id"] or not r["state"] or any(x in r["state"] for x in NOT_SINGLE): continue
    k = (r["species_id"], r["state"]); pairs[k]["rows"] += 1; pairs[k]["centres"].add(r["centre"]); pairs[k]["periods"].add(r["survey_period"]); pairs[k]["names"].add(r["mite_as_printed"])
cmp_rows = []
for (sid, st), v in sorted(pairs.items()):
    cmp_rows.append({"species_id": sid, "valid_name": species[sid]["species"], "family": species[sid]["family"], "state": st,
                     "in_gupta_mondal_2023": int((sid, st) in gm_state), "species_in_gupta_mondal_2023": int(sid in gm_species),
                     "aicrp_rows": v["rows"], "centres": ";".join(sorted(v["centres"])), "survey_periods": ";".join(sorted(v["periods"])),
                     "printed_names": " | ".join(sorted(v["names"]))})
write_csv(OUT / "aicrp_species_state_vs_gm2023.csv", cmp_rows,
          ["species_id", "valid_name", "family", "state", "in_gupta_mondal_2023", "species_in_gupta_mondal_2023", "aicrp_rows", "centres", "survey_periods", "printed_names"])

print("observations", len(obs))
print(collections.Counter(r["centre"] for r in obs))
print(collections.Counter(r["mite_rank"] for r in obs))
print(collections.Counter(r["join_basis"] for r in obs if r["mite_rank"] == "species"))
print("species x state pairs:", len(cmp_rows), "already in G&M:", sum(c["in_gupta_mondal_2023"] for c in cmp_rows),
      "species new to G&M layer:", sum(1 for c in cmp_rows if not c["species_in_gupta_mondal_2023"]))
print("names in covered families not joined:", len(missing))
