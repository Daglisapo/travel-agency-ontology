"""Έλεγχος συνέπειας και συμπερασμός με HermiT και Pellet (μέσω owlready2).

Για κάθε reasoner καταγράφει: συνέπεια, unsatisfiable κλάσεις, συναγόμενους τύπους
στιγμιοτύπων και συναγόμενες τιμές ιδιοτήτων. Η οντολογία με τα συμπεράσματα
αποθηκεύεται στο ontology/travel_agency_inferred.owl, ώστε τα ερωτήματα SPARQL που
βασίζονται σε reasoning να εκτελούνται και στο SPARQL tab του Protégé.

    python scripts/reason.py
"""
import time
from collections import defaultdict
from pathlib import Path

import owlready2
from owlready2 import (OwlReadyInconsistentOntologyError, World, sync_reasoner_hermit,
                       sync_reasoner_pellet)
from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, OWL

ROOT = Path(__file__).resolve().parent.parent
OWL_FILE = ROOT / "ontology" / "travel_agency.owl"
INFERRED_FILE = ROOT / "ontology" / "travel_agency_inferred.owl"
REPORT = ROOT / "results" / "reasoning_report.txt"
INFERRED_IRI = "http://www.semanticweb.org/dagklis/ontologies/2026/travel-agency-inferred"
TA = Namespace("http://www.semanticweb.org/dagklis/ontologies/2026/travel-agency#")

owlready2.reasoning.JAVA_MEMORY = 1000


def short(term):
    return str(term).split("#")[-1]


def plain_graph(world):
    """Τα triples του world χωρίς blank nodes και χωρίς τις δηλώσεις οντολογιών."""
    g = Graph()
    for s, p, o in world.as_rdflib_graph():
        if isinstance(s, BNode) or isinstance(o, BNode):
            continue
        if p == RDF.type and o == OWL.Ontology:
            continue
        g.add((s, p, o))
    return g


def run(reasoner_name):
    world = World()
    onto = world.get_ontology(str(OWL_FILE)).load()
    asserted = plain_graph(world)

    t0 = time.perf_counter()
    try:
        with onto:
            if reasoner_name == "HermiT":
                sync_reasoner_hermit(world, infer_property_values=True, debug=0)
            else:
                # Χωρίς infer_data_property_values: η οντολογία δεν παράγει νέες τιμές
                # δεδομένων, και στα Windows η Java επιστρέφει τα ελληνικά literals ως «???».
                sync_reasoner_pellet(world, infer_property_values=True, debug=0)
        consistent = True
    except OwlReadyInconsistentOntologyError:
        consistent = False
    elapsed = time.perf_counter() - t0

    unsat = [c for c in world.inconsistent_classes() if c is not owlready2.Nothing]
    inferred = plain_graph(world) - asserted if consistent else Graph()
    return world, consistent, unsat, inferred, elapsed


def describe(name, consistent, unsat, inferred, elapsed):
    lines = [f"=== {name} ===",
             f"Χρόνος συλλογισμού: {elapsed:.1f} s",
             f"Συνεπής (consistent): {'ΝΑΙ' if consistent else 'ΟΧΙ'}",
             f"Unsatisfiable κλάσεις: {', '.join(short(c.iri) for c in unsat) or 'καμία'}"]

    types = defaultdict(list)
    props = defaultdict(list)
    subclass = []
    for s, p, o in sorted(inferred):
        if p == RDF.type:
            types[short(o)].append(short(s))
        elif p == RDFS.subClassOf:
            subclass.append(f"{short(s)} ⊑ {short(o)}")
        else:
            value = str(o) if isinstance(o, Literal) else short(o)
            props[short(p)].append(f"{short(s)} → {value}")

    lines.append(f"\nΣυναγόμενες ιεραρχικές σχέσεις κλάσεων: {len(subclass)}")
    lines += [f"  {x}" for x in subclass]
    lines.append(f"\nΣυναγόμενοι τύποι στιγμιοτύπων: {sum(map(len, types.values()))}")
    for cls, inds in sorted(types.items()):
        lines.append(f"  {cls}: {', '.join(inds)}")
    lines.append(f"\nΣυναγόμενες τιμές ιδιοτήτων: {sum(map(len, props.values()))}")
    for prop, pairs in sorted(props.items()):
        lines.append(f"  {prop} ({len(pairs)}):")
        lines += [f"      {x}" for x in pairs]
    return lines


def save_inferred(world):
    """Asserted + inferred triples σε νέα οντολογία RDF/XML (για το Protégé).

    Το as_rdflib_graph() του owlready2 περιλαμβάνει και τις τιμές που προκύπτουν από
    owl:inverseOf και owl:SymmetricProperty (π.χ. hasBooking από bookedBy).
    """
    g = Graph()
    for t in world.as_rdflib_graph():
        if t[1] == RDF.type and t[2] == OWL.Ontology:
            continue
        g.add(t)
    nt = INFERRED_FILE.with_suffix(".nt")
    g.serialize(nt, format="nt", encoding="utf-8")
    out = World()
    with open(nt, "rb") as f:
        out.get_ontology(INFERRED_IRI).load(fileobj=f).save(str(INFERRED_FILE), format="rdfxml")
    nt.unlink()
    xml = INFERRED_FILE.read_text(encoding="utf-8")
    header = f'<owl:Ontology rdf:about="{INFERRED_IRI}"/>\n'
    xml = xml.replace("x_1.1", "dc").replace(header, header.replace("/>", ">") +
          "  <rdfs:comment xml:lang=\"el\">Η οντολογία travel_agency.owl μαζί με τα συμπεράσματα "
          "του reasoner Pellet (τύποι στιγμιοτύπων και τιμές ιδιοτήτων), παραγόμενη από το "
          "scripts/reason.py.</rdfs:comment>\n</owl:Ontology>\n", 1)
    INFERRED_FILE.write_text(xml, encoding="utf-8")
    return len(set(g.triples((None, TA.hasBooking, None))))


def main():
    report = [f"Οντολογία: {OWL_FILE.name}", f"owlready2 {owlready2.VERSION}", ""]
    results = {}
    for name in ("HermiT", "Pellet"):
        world, consistent, unsat, inferred, elapsed = run(name)
        results[name] = (world, inferred)
        report += describe(name, consistent, unsat, inferred, elapsed) + [""]
        print(f"{name}: consistent={consistent}, unsatisfiable={len(unsat)}, "
              f"inferred triples={len(inferred)} ({elapsed:.1f} s)")

    only_pellet = results["Pellet"][1] - results["HermiT"][1]
    only_hermit = results["HermiT"][1] - results["Pellet"][1]
    report += ["=== Σύγκριση HermiT / Pellet ===",
               f"Συμπεράσματα μόνο από Pellet: {len(only_pellet)}",
               *[f"  {short(s)} {short(p)} {short(o)}" for s, p, o in sorted(only_pellet)],
               f"Συμπεράσματα μόνο από HermiT: {len(only_hermit)}",
               *[f"  {short(s)} {short(p)} {short(o)}" for s, p, o in sorted(only_hermit)]]

    n_has_booking = save_inferred(results["Pellet"][0])
    report += ["", f"Αρχείο {INFERRED_FILE.name}: asserted + συμπεράσματα Pellet, μαζί με τις "
               f"τιμές αντίστροφων/συμμετρικών ιδιοτήτων (π.χ. {n_has_booking} τιμές hasBooking, "
               "που δεν δηλώνονται ρητά αλλά προκύπτουν από το bookedBy)."]
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"-> {REPORT.relative_to(ROOT)}, {INFERRED_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
