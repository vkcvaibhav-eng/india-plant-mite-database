"""State names shared by all comparisons.

Sources spell states differently (the Gupta & Mondal book uses Orissa and Pondicherry; the AICRP
reports and recent lists use Odisha and Puducherry). `canon()` gives one spelling for comparing
layers; the record files keep the name as the source prints it.

Some states were carved out of others (Telangana 2014, Uttarakhand, Jharkhand and Chhattisgarh 2000)
and Chandigarh is a union territory shared by Punjab and Haryana. A record from the new state may
appear in an older source under the parent state. `related()` lists the states treated as the same
area for the lenient comparison.
"""

CANON = {
    "Orissa": "Odisha",
    "Pondicherry": "Puducherry",
    "Andaman and Nicobar Islands": "Andaman & Nicobar Islands",
    "Jammu and Kashmir": "Jammu & Kashmir",
    "Uttaranchal": "Uttarakhand",
    "NCT of Delhi": "Delhi",
}

PARENT = {
    "Telangana": {"Andhra Pradesh"},
    "Uttarakhand": {"Uttar Pradesh"},
    "Jharkhand": {"Bihar"},
    "Chhattisgarh": {"Madhya Pradesh"},
    "Chandigarh": {"Punjab", "Haryana"},
    "Ladakh": {"Jammu & Kashmir"},
}
CHILD = {}
for child, parents in PARENT.items():
    for p in parents:
        CHILD.setdefault(p, set()).add(child)


def canon(state):
    s = (state or "").strip()
    return CANON.get(s, s)


def related(state):
    """The state itself plus parent or child states, all in canonical spelling."""
    s = canon(state)
    return {s} | PARENT.get(s, set()) | CHILD.get(s, set())
