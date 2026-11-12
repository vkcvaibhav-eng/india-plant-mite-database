"""How a species x state record from another layer stands against the Gupta & Mondal (2023) layer.

status(species_id, state) returns one of
  state_in_book                  the book names this state for the species
  parent_or_child_state_in_book  the book names the parent or a child of this state (Telangana/Andhra Pradesh,
                                 Uttarakhand/Uttar Pradesh, Jharkhand/Bihar, Chhattisgarh/Madhya Pradesh, Chandigarh/Punjab or Haryana)
  book_gives_no_state            the book lists the species but names no state ("throughout the country", "Cosmopolitan", "India")
  new_state_for_a_book_species   the book lists the species with states, and this state is not among them
  species_not_in_book            the species has no account in the book

Only the last two are additions to what the book records; "book_gives_no_state" is detail the book does not give,
not a new record. Run build_records.py first (it writes species_state.csv and species_in_book.csv).
"""
import csv, collections, pathlib
import states_norm

ROOT = pathlib.Path(__file__).resolve().parents[1]
NEW = ("new_state_for_a_book_species", "species_not_in_book")
ORDER = ("state_in_book", "parent_or_child_state_in_book", "book_gives_no_state", "new_state_for_a_book_species", "species_not_in_book")


class Book:
    def __init__(self):
        self.states = collections.defaultdict(set)
        with open(ROOT / "data/records/species_state.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["species_id"] and r["state"]:
                    self.states[r["species_id"]].add(states_norm.canon(r["state"]))
        with open(ROOT / "data/records/species_in_book.csv", newline="", encoding="utf-8") as f:
            self.listed = {r["species_id"] for r in csv.DictReader(f)}

    def status(self, sid, state):
        st = states_norm.canon(state)
        have = self.states.get(sid, set())
        if st in have:
            return "state_in_book"
        if sid not in self.listed:
            return "species_not_in_book"
        if not have:
            return "book_gives_no_state"
        if states_norm.related(st) & have:
            return "parent_or_child_state_in_book"
        return "new_state_for_a_book_species"
