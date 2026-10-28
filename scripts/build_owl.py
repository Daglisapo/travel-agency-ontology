"""Μετατροπή της οντολογίας από Turtle σε RDF/XML (.owl για το Protégé) και στατιστικά.

    python scripts/build_owl.py
"""
from collections import Counter
from pathlib import Path

import owlready2
from rdflib import BNode, Graph, Literal, Namespace, RDF, OWL, XSD
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parent.parent
TTL = ROOT / "ontology" / "travel_agency.ttl"
OWL_FILE = ROOT / "ontology" / "travel_agency.owl"
STATS = ROOT / "results" / "ontology_stats.txt"

ONTOLOGY_IRI = "http://www.semanticweb.org/dagklis/ontologies/2026/travel-agency"
TA = Namespace(ONTOLOGY_IRI + "#")


def normalized(g):
    """Ίδιος γράφος με ενιαία μορφή literal (plain = xsd:string, 640.00 = 640.0)."""
    out = Graph()
    for s, p, o in g:
        if isinstance(o, Literal) and not o.language:
            if o.datatype in (None, XSD.string):
                o = Literal(str(o), datatype=XSD.string)
            elif o.datatype == XSD.decimal:
                o = Literal(str(o.toPython().normalize()), datatype=XSD.decimal)
        out.add((s, p, o))
    return out


def named(g, rdf_type):
    return sorted(s for s in g.subjects(RDF.type, rdf_type) if not isinstance(s, BNode))


def main():
    g = Graph()
    g.parse(TTL, format="turtle")
    g.bind("", TA)
    g.bind("owl", OWL)
    # Το "pretty-xml" του rdflib παραλείπει τα facets μέσα σε λίστες (owl:withRestrictions),
    # γι' αυτό η σειριοποίηση γίνεται με το owlready2, που γράφει RDF/XML όπως το Protégé.
    nt = OWL_FILE.with_suffix(".nt")
    g.serialize(nt, format="nt", encoding="utf-8")
    world = owlready2.World()
    with open(nt, "rb") as f:
        world.get_ontology(ONTOLOGY_IRI).load(fileobj=f).save(str(OWL_FILE), format="rdfxml")
    nt.unlink()
    xml = OWL_FILE.read_text(encoding="utf-8")
    OWL_FILE.write_text(xml.replace("x_1.1", "dc"), encoding="utf-8")

    check = Graph().parse(OWL_FILE, format="xml")
    if not isomorphic(normalized(g), normalized(check)):
        raise SystemExit("Το .owl δεν είναι ισόμορφο με το .ttl")

    classes = named(g, OWL.Class)
    obj_props = named(g, OWL.ObjectProperty)
    data_props = named(g, OWL.DatatypeProperty)
    individuals = named(g, OWL.NamedIndividual)

    # Πλήθος στιγμιοτύπων ανά (ρητά δηλωμένη) κλάση
    per_class = Counter()
    for ind in individuals:
        for t in g.objects(ind, RDF.type):
            if t != OWL.NamedIndividual:
                per_class[t.split("#")[-1]] += 1

    characteristics = Counter()
    for p in obj_props + data_props:
        for t in g.objects(p, RDF.type):
            if t not in (OWL.ObjectProperty, OWL.DatatypeProperty):
                characteristics[t.split("#")[-1]] += 1

    lines = [
        f"Triples:             {len(g)}",
        f"Classes:             {len(classes)}",
        f"Object properties:   {len(obj_props)}",
        f"Data properties:     {len(data_props)}",
        f"Properties (total):  {len(obj_props) + len(data_props)}",
        f"Named individuals:   {len(individuals)}",
        f"Equivalent-class axioms (defined classes): {len(set(g.subjects(OWL.equivalentClass, None)))}",
        f"Property chains:     {len(set(g.subjects(OWL.propertyChainAxiom, None)))}",
        f"Inverse pairs:       {len(set(g.subject_objects(OWL.inverseOf)))}",
        "",
        "Property characteristics:",
        *[f"  {k}: {v}" for k, v in sorted(characteristics.items())],
        "",
        "Individuals per asserted class:",
        *[f"  {k}: {v}" for k, v in sorted(per_class.items())],
    ]
    STATS.parent.mkdir(exist_ok=True)
    STATS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:9]))
    print(f"-> {OWL_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
