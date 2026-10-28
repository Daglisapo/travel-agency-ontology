"""Εκτέλεση των ερωτημάτων SPARQL (queries/q*.rq) με το rdflib.

Κάθε ερώτημα εκτελείται και στην asserted οντολογία (travel_agency.owl) και στην
οντολογία με τα συμπεράσματα του reasoner (travel_agency_inferred.owl), ώστε να
φαίνεται ποια αποτελέσματα οφείλονται στον συλλογισμό. Τα αποτελέσματα του
γραφήματος που δηλώνει κάθε ερώτημα («# Γράφημα: ...») γράφονται σε CSV και σε
ένα συγκεντρωτικό Markdown. Επίσης συγκεντρώνονται όλα τα ερωτήματα σε ένα αρχείο
(queries/all_queries.rq) για την υποβολή.

    python scripts/run_queries.py
"""
import csv
import re
from decimal import Decimal
from pathlib import Path

from rdflib import Graph, Literal, URIRef

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ROOT / "queries"
OUT = ROOT / "results" / "sparql"
GRAPHS = {
    "asserted": ROOT / "ontology" / "travel_agency.owl",
    "inferred": ROOT / "ontology" / "travel_agency_inferred.owl",
}


def fmt(value):
    if value is None:
        return ""
    if isinstance(value, URIRef):
        return value.split("#")[-1]
    if isinstance(value, Literal):
        py = value.toPython()
        if isinstance(py, Decimal):
            py = py.quantize(Decimal("0.01")) if py != py.to_integral() else py.to_integral()
            return str(py)
        return str(py)
    return str(value)


def header_field(text, name):
    m = re.search(rf"^# {name}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def main():
    graphs = {k: Graph().parse(v, format="xml") for k, v in GRAPHS.items()}
    OUT.mkdir(parents=True, exist_ok=True)

    md = ["# Αποτελέσματα ερωτημάτων SPARQL", "",
          "Παράγεται από το `scripts/run_queries.py`. Για κάθε ερώτημα δίνεται το πλήθος "
          "γραμμών στην asserted οντολογία και στην οντολογία με τα συμπεράσματα του reasoner.", ""]
    summary = ["| Ερώτημα | Γράφημα | Γραμμές (asserted) | Γραμμές (inferred) |", "|---|---|---:|---:|"]
    combined = []

    for path in sorted(QUERIES.glob("q*.rq")):
        text = path.read_text(encoding="utf-8")
        target = header_field(text, "Γράφημα").split()[0]
        title = text.splitlines()[0].lstrip("# ").strip()
        counts = {}
        rows = None
        for name, g in graphs.items():
            res = g.query(text)
            table = [[fmt(r[v]) for v in res.vars] for r in res]
            counts[name] = len(table)
            if name == target:
                cols = [str(v) for v in res.vars]
                rows = table

        with open(OUT / f"{path.stem}.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)

        summary.append(f"| {path.stem} | {target} | {counts['asserted']} | {counts['inferred']} |")
        md += [f"## {title}", "", f"Αρχείο: `queries/{path.name}` — γράφημα: **{target}** "
               f"(asserted: {counts['asserted']} γραμμές, inferred: {counts['inferred']} γραμμές)", "",
               "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        md += ["| " + " | ".join(c.replace("|", "\\|") for c in r) + " |" for r in rows]
        md.append("")
        combined.append(f"# {'=' * 76}\n# {path.name}\n# {'=' * 76}\n{text}")
        print(f"{path.stem:40s} {target:9s} asserted={counts['asserted']:3d} inferred={counts['inferred']:3d}")

    (ROOT / "results" / "sparql_results.md").write_text(
        "\n".join(md[:4] + summary + [""] + md[4:]) + "\n", encoding="utf-8")
    (QUERIES / "all_queries.rq").write_text(
        "# Όλα τα ερωτήματα SPARQL της εργασίας (παράγεται από το scripts/run_queries.py).\n"
        "# Κάθε ερώτημα εκτελείται χωριστά· στο Protégé: Window > Tabs > SPARQL Query.\n\n"
        + "\n".join(combined), encoding="utf-8")


if __name__ == "__main__":
    main()
