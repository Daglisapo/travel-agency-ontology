"""Διαγράμματα της οντολογίας με Graphviz (dot):

  paper/figures/class_hierarchy.png   ιεραρχία κλάσεων (με τις ορισμένες κλάσεις)
  paper/figures/object_properties.png object properties ως ακμές domain → range
  paper/figures/instance_graph.png    απόσπασμα στιγμιοτύπων: asserted vs inferred ακμές

    python scripts/diagrams.py
"""
import io
import shutil
import subprocess
from pathlib import Path

from PIL import Image
from rdflib import BNode, Graph, Namespace, RDF, RDFS, OWL

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "paper" / "figures"
TA = Namespace("http://www.semanticweb.org/dagklis/ontologies/2026/travel-agency#")
DOT = shutil.which("dot") or r"C:\Program Files\Graphviz\bin\dot.exe"
FONT = "Arial"


def short(term):
    return str(term).split("#")[-1]


def el_label(g, term):
    for lbl in g.objects(term, RDFS.label):
        if lbl.language == "el":
            return str(lbl)
    return short(term)


def to_png(dot_source):
    # Μέσω stdin/stdout: το dot στα Windows δεν ανοίγει διαδρομές με ελληνικούς χαρακτήρες.
    return subprocess.run([DOT, "-Tpng", "-Gdpi=220"], input=dot_source.encode("utf-8"),
                          capture_output=True, check=True).stdout


def render(name, dot_source):
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / f"{name}.png").write_bytes(to_png(dot_source))
    print(f"-> paper/figures/{name}.png")


def class_hierarchy(g):
    """Κάθε υποδέντρο σχεδιάζεται χωριστά και τα υποδέντρα τοποθετούνται σε δύο στήλες,
    ώστε η εικόνα να χωρά σε πλάτος σελίδας."""
    defined = {s for s in g.subjects(OWL.equivalentClass, None)}
    classes = sorted(c for c in g.subjects(RDF.type, OWL.Class) if not isinstance(c, BNode))
    parents = {c: [] for c in classes}       # (υπερκλάση, συναγόμενη;)
    for c in classes:
        parents[c] += [(s, False) for s in g.objects(c, RDFS.subClassOf) if not isinstance(s, BNode)]
        if c in defined:
            # Η υπερκλάση των ορισμένων κλάσεων προκύπτει από τον ορισμό (συνάγεται από τον reasoner)
            for eq in g.objects(c, OWL.equivalentClass):
                first = g.value(g.value(eq, OWL.intersectionOf), RDF.first)
                if first is not None and not isinstance(first, BNode):
                    parents[c].append((first, True))
    children = {c: [x for x in classes if any(p == c for p, _ in parents[x])] for c in classes}

    def node(c):
        label = f"{short(c)}\\n({el_label(g, c)})"
        style = ' style="rounded,filled,dashed", fillcolor="#fff4e0", color="#c77800"' if c in defined else ""
        return f'"{short(c)}" [label="{label}"{style}];'

    head = [f'node [shape=box, style="rounded,filled", fillcolor="#eef3fb", color="#4a6fa5", '
            f'fontname="{FONT}", fontsize=10, margin="0.08,0.03"];',
            'edge [arrowhead=empty, color="#555555"];']
    roots = [c for c in classes if not parents[c]]
    trees = [r for r in roots if children[r]]
    singles = [r for r in roots if not children[r]]

    images = []
    for root in sorted(trees, key=lambda r: -len(children[r])):
        members, stack = [], [root]
        while stack:
            c = stack.pop()
            members.append(c)
            stack += children[c]
        lines = ["digraph T {", "rankdir=RL; nodesep=0.12; ranksep=0.35;", *head]
        lines += [node(c) for c in members]
        for c in members:
            for p, inferred in parents[c]:
                style = ' [style=dashed, color="#c77800"]' if inferred else ""
                lines.append(f'"{short(c)}" -> "{short(p)}"{style};')
        images.append(Image.open(io.BytesIO(to_png("\n".join(lines + ["}"])))))
    # Κλάσεις χωρίς υποκλάσεις και υπερκλάσεις: σε ζεύγη, χωρίς ακμές
    lines = ["digraph S {", "rankdir=TB; nodesep=0.3; ranksep=0.15;", *head]
    lines += [node(c) for c in singles]
    pairs = [singles[i:i + 2] for i in range(0, len(singles), 2)]
    lines += ["{rank=same; " + " ".join(f'"{short(c)}";' for c in p) + "}" for p in pairs]
    lines += [f'"{short(a[0])}" -> "{short(b[0])}" [style=invis];' for a, b in zip(pairs, pairs[1:])]
    images.append(Image.open(io.BytesIO(to_png("\n".join(lines + ["}"])))))

    # Τοποθέτηση σε δύο στήλες: κάθε εικόνα πηγαίνει στη χαμηλότερη στήλη
    gap = 60
    cols = [[], []]
    heights = [0, 0]
    for im in sorted(images, key=lambda im: -im.height):
        i = heights.index(min(heights))
        cols[i].append(im)
        heights[i] += im.height + gap
    widths = [max((im.width for im in col), default=0) for col in cols]
    canvas = Image.new("RGB", (sum(widths) + 3 * gap, max(heights) + gap), "white")
    x = gap
    for col, w in zip(cols, widths):
        y = gap
        for im in col:
            canvas.paste(im, (x, y))
            y += im.height + gap
        x += w + gap
    FIG.mkdir(parents=True, exist_ok=True)
    canvas.save(FIG / "class_hierarchy.png")
    print("-> paper/figures/class_hierarchy.png")


def object_properties(g):
    skip = {TA.employs, TA.hasBranch, TA.guides, TA.offersPackage, TA.promotedBy,
            TA.writesReview, TA.hasBooking}           # αντίστροφες: σχεδιάζεται μόνο η μία φορά
    implicit_domain = {TA.locatedIn: TA.Place, TA.hasGuide: TA.Excursion}
    chains = set(g.subjects(OWL.propertyChainAxiom, None))
    lines = ["digraph P {", "rankdir=LR; nodesep=0.25; ranksep=0.6; splines=true;",
             f'node [shape=box, style="rounded,filled", fillcolor="#eef3fb", color="#4a6fa5", '
             f'fontname="{FONT}", fontsize=10];',
             f'edge [fontname="{FONT}", fontsize=8, color="#4a6fa5", fontcolor="#1f3b63"];']
    for p in sorted(g.subjects(RDF.type, OWL.ObjectProperty)):
        if p in skip:
            continue
        dom = g.value(p, RDFS.domain) or implicit_domain.get(p)
        rng = g.value(p, RDFS.range)
        if dom is None or rng is None:
            continue
        chars = [short(t)[0] for t in g.objects(p, RDF.type)
                 if t in (OWL.TransitiveProperty, OWL.SymmetricProperty, OWL.FunctionalProperty)]
        label = short(p) + (f" [{','.join(sorted(chars))}]" if chars else "")
        style = ', style=dashed, color="#c77800", fontcolor="#c77800"' if p in chains else ""
        lines.append(f'"{short(dom)}" -> "{short(rng)}" [label="{label}"{style}];')
    lines.append("}")
    render("object_properties", "\n".join(lines))


def instance_graph(asserted, inferred):
    nodes = [TA.DimitrisKarras, TA.ElenaKarra, TA.Booking01, TA.SantoriniEscape,
             TA.NikosGeorgiou, TA.Santorini, TA.Cyclades, TA.Greece, TA.CalderaViewHotel,
             TA.Flight_HA101, TA.VolcanoBoatTour, TA.SofiaAlexiou, TA.Confirmed, TA.Payment01]
    classes = [TA.VIPCustomer, TA.FlightPackage, TA.IslandPackage, TA.GuidedPackage,
               TA.LongStayPackage]
    props = {TA.bookedBy, TA.hasBooking, TA.forPackage, TA.handledBy, TA.servedBy, TA.hasStatus,
             TA.hasPayment, TA.hasDestination, TA.locatedIn, TA.visitsPlace, TA.includesService,
             TA.hasGuide, TA.travelsWith}
    lines = ["digraph I {", "rankdir=LR; nodesep=0.2; ranksep=0.5;",
             f'node [shape=ellipse, style=filled, fillcolor="#eef7ee", color="#3d7a3d", '
             f'fontname="{FONT}", fontsize=10];',
             f'edge [fontname="{FONT}", fontsize=8];']
    for n in nodes:
        lines.append(f'"{short(n)}";')
    for c in classes:
        lines.append(f'"{short(c)}" [shape=box, style="rounded,filled,dashed", '
                     f'fillcolor="#fff4e0", color="#c77800"];')
    wanted = set(nodes)
    for s, p, o in inferred:
        if s not in wanted:
            continue
        is_new = (s, p, o) not in asserted
        if p == RDF.type and o in classes:
            pass
        elif p in props and o in wanted:
            pass
        else:
            continue
        label = "rdf:type" if p == RDF.type else short(p)
        style = 'style=dashed, color="#c0392b", fontcolor="#c0392b"' if is_new else 'color="#333333"'
        lines.append(f'"{short(s)}" -> "{short(o)}" [label="{label}", {style}];')
    lines.append("}")
    render("instance_graph", "\n".join(lines))


def main():
    asserted = Graph().parse(ROOT / "ontology" / "travel_agency.owl", format="xml")
    inferred = Graph().parse(ROOT / "ontology" / "travel_agency_inferred.owl", format="xml")
    class_hierarchy(asserted)
    object_properties(asserted)
    instance_graph(asserted, inferred)


if __name__ == "__main__":
    main()
