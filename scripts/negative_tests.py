"""Σκόπιμα λάθη μοντελοποίησης: ελέγχει ότι ο HermiT τα εντοπίζει.

Κάθε σενάριο προσθέτει μερικά triples σε αντίγραφο της οντολογίας και τρέχει τον
reasoner. Η πραγματική οντολογία δεν αλλάζει.

    python scripts/negative_tests.py
"""
import tempfile
from pathlib import Path

import owlready2
from owlready2 import OwlReadyInconsistentOntologyError, World, sync_reasoner_hermit
from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL

ROOT = Path(__file__).resolve().parent.parent
OWL_FILE = ROOT / "ontology" / "travel_agency.owl"
REPORT = ROOT / "results" / "negative_tests.txt"
TA = Namespace("http://www.semanticweb.org/dagklis/ontologies/2026/travel-agency#")

SCENARIOS = [
    ("Α. Το ξενοδοχείο ως οργανισμός (Hotel ⊑ Organization)",
     "Εναλλακτική μοντελοποίηση που εξετάστηκε: το ξενοδοχείο ως συνεργαζόμενη επιχείρηση. "
     "Συγκρούεται με το Hotel ⊑ Accommodation ⊑ TravelService και με την ξενότητα "
     "Organization / TravelService.",
     [(TA.Hotel, RDFS.subClassOf, TA.Organization)]),
    ("Β. Βαθμολογία εκτός ορίων (rating = 7)",
     "Το range της rating είναι xsd:integer[1..5].",
     [(TA.Review01, TA.rating, Literal(7))]),
    ("Γ. Ταξιδιωτικός σύμβουλος ως συνοδός εκδρομής",
     "Το range της hasGuide είναι TourGuide, άρα ο Νίκος Γεωργίου θα ήταν και TourGuide· "
     "όμως TravelAgent και TourGuide είναι ξένες κλάσεις.",
     [(TA.LouvreTour, TA.hasGuide, TA.NikosGeorgiou)]),
    ("Δ. Κράτηση με δύο πελάτες",
     "Η bookedBy είναι functional, οπότε ο reasoner (χωρίς Unique Name Assumption) θα "
     "ταύτιζε τους δύο πελάτες· αυτό είναι αδύνατο γιατί έχουν διαφορετικούς πόντους "
     "και η loyaltyPoints είναι επίσης functional.",
     [(TA.Booking01, TA.bookedBy, TA.KaterinaLazarou)]),
]


def tbox_only(g):
    """Αφαιρεί τις δηλώσεις για τα στιγμιότυπα (ABox), ώστε να φαίνονται οι unsatisfiable
    κλάσεις χωρίς ασυνέπεια. Οι δηλώσεις NamedIndividual μένουν, γιατί τα στιγμιότυπα
    του BookingStatus ≡ {Confirmed, Pending, Cancelled} είναι μέρος του ορισμού της κλάσης."""
    out = Graph()
    individuals = set(g.subjects(RDF.type, OWL.NamedIndividual))
    for s, p, o in g:
        if s not in individuals or (p, o) == (RDF.type, OWL.NamedIndividual):
            out.add((s, p, o))
    return out


def check(g):
    with tempfile.TemporaryDirectory() as tmp:
        nt = Path(tmp) / "test.nt"
        g.serialize(nt, format="nt", encoding="utf-8")
        world = World()
        with open(nt, "rb") as f:
            onto = world.get_ontology("http://test.example/onto").load(fileobj=f)
        try:
            with onto:
                sync_reasoner_hermit(world, debug=0)
        except OwlReadyInconsistentOntologyError:
            return False, []
        unsat = [c.name for c in world.inconsistent_classes() if c is not owlready2.Nothing]
        return True, unsat


def main():
    base = Graph().parse(OWL_FILE, format="xml")
    lines = [f"Reasoner: HermiT (owlready2 {owlready2.VERSION})", ""]
    ok, unsat = check(base)
    lines += ["Αρχική οντολογία: " + ("συνεπής" if ok else "ΑΣΥΝΕΠΗΣ") +
              f", unsatisfiable κλάσεις: {unsat or 'καμία'}", ""]

    for title, why, triples in SCENARIOS:
        g = Graph()
        g += base
        for t in triples:
            g.add(t)
        consistent, unsat = check(g)
        tbox_consistent, tbox_unsat = check(tbox_only(g))
        lines += [title, f"  Αιτία: {why}",
                  "  Προστέθηκε: " + "; ".join(f"{s.split('#')[-1]} {p.split('#')[-1]} "
                                               f"{o.split('#')[-1] if not isinstance(o, Literal) else o}"
                                               for s, p, o in triples),
                  f"  Πλήρης οντολογία: {'συνεπής' if consistent else 'ΑΣΥΝΕΠΗΣ (inconsistent)'}",
                  f"  Μόνο TBox: unsatisfiable κλάσεις = {', '.join(tbox_unsat) or 'καμία'}", ""]
        print(f"{title}: consistent={consistent}, TBox unsatisfiable={tbox_unsat}")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
