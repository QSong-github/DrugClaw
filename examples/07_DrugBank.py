"""
DrugBank - Comprehensive Drug Information and Interactions
Category: Drug-centric | Type: DB | Subcategory: Drug Knowledgebase
Link: https://go.drugbank.com/releases/latest
Paper: https://academic.oup.com/nar/article/46/D1/D1074/4602867

DrugBank integrates chemical, pharmacological, and pharmaceutical data with
drug targets, transporters, enzymes, and carriers.

Access method:
  - Free account required at https://go.drugbank.com/
  - After login, download XML/CSV from https://go.drugbank.com/releases/latest
  - DrugBank API (commercial): https://docs.drugbankplus.com/

This script demonstrates parsing the locally downloaded DrugBank Open Data CSV.
"""

import os
import csv
import urllib.request

# DrugBank Open Data (vocabulary only, no registration needed)
OPEN_DATA_URL = (
    "https://go.drugbank.com/releases/latest/downloads/drug-vocabulary"
)
# Fallback: DrugBank open vocabulary on GitHub
VOCAB_URL = (
    "https://raw.githubusercontent.com/dhimmel/drugbank/gh-pages/data/drugbank.tsv"
)
OUTPUT_FILE = "drugbank_vocabulary.tsv"


def download_open_vocabulary():
    """Download DrugBank open vocabulary (no login required)."""
    print(f"Downloading DrugBank open vocabulary ...")
    try:
        urllib.request.urlretrieve(VOCAB_URL, OUTPUT_FILE)
        print(f"Saved to {OUTPUT_FILE}")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        print("For full DrugBank data, register at https://go.drugbank.com/ "
              "and download from https://go.drugbank.com/releases/latest")
        return False


def preview_vocabulary(n: int = 5):
    if not os.path.exists(OUTPUT_FILE):
        print("File not found. Run download_open_vocabulary() first.")
        return
    with open(OUTPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        print(f"Columns: {reader.fieldnames}")
        for i, row in enumerate(reader):
            if i >= n:
                break
            print(row)


def parse_drugbank_xml(xml_path: str):
    """
    Parse the full DrugBank XML file (requires registration download).
    Example usage after downloading full_database.xml.zip.
    """
    import xml.etree.ElementTree as ET

    NS = "http://www.drugbank.ca"
    tree = ET.parse(xml_path)
    root = tree.getroot()
    drugs = []
    for drug_el in root.findall(f"{{{NS}}}drug"):
        name = drug_el.findtext(f"{{{NS}}}name")
        db_id = drug_el.findtext(f"{{{NS}}}drugbank-id[@primary='true']")
        drug_type = drug_el.get("type")
        drugs.append({"id": db_id, "name": name, "type": drug_type})
    return drugs


if __name__ == "__main__":
    ok = download_open_vocabulary()
    if ok:
        preview_vocabulary()
    else:
        print("\nTo use DrugBank XML after downloading:")
        print("  drugs = parse_drugbank_xml('full_database.xml')")
        print("  print(drugs[:3])")
