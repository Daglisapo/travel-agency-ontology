"""Δημιουργία του ZIP υποβολής στο moodle (αναφορά PDF, οντολογία OWL, ερωτήματα SPARQL).

    python scripts/make_submission.py
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZIP = ROOT / "Dagklis_Apostolos_2021031.zip"
FILES = {
    "paper/paper.pdf": "Dagklis_Apostolos_2021031_report.pdf",
    "ontology/travel_agency.owl": "travel_agency.owl",
    "ontology/travel_agency_inferred.owl": "travel_agency_inferred.owl",
    "queries/all_queries.rq": "sparql_queries.rq",
}


def main():
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for src, name in FILES.items():
            z.write(ROOT / src, name)
        for rq in sorted((ROOT / "queries").glob("q*.rq")):
            z.write(rq, f"queries/{rq.name}")
    print(f"-> {ZIP.name}")
    for info in zipfile.ZipFile(ZIP).infolist():
        print(f"   {info.filename:45s} {info.file_size:>9,d} bytes")


if __name__ == "__main__":
    main()
