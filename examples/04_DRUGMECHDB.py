"""
DrugMechDB - Drug Mechanism of Action Database
Category: Drug-centric | Type: DB | Subcategory: Drug Mechanism
Link: https://github.com/SuLab/DrugMechDB
Paper: https://www.nature.com/articles/s41597-023-02534-z

DrugMechDB provides curated drug mechanism-of-action paths describing the
biological mechanism by which a drug induces its primary indicated effect.

Access method: Download YAML/JSON data directly from GitHub.
"""

import urllib.request
import json
import os

# Direct download of the main drug mechanism JSON
JSON_URL = (
    "https://raw.githubusercontent.com/SuLab/DrugMechDB/main/indication_paths.json"
)
OUTPUT_FILE = "indication_paths.json"


def download_drugmechdb():
    print(f"Downloading DrugMechDB from GitHub ...")
    urllib.request.urlretrieve(JSON_URL, OUTPUT_FILE)
    print(f"Saved to {OUTPUT_FILE}")


def load_and_preview(n: int = 3):
    if not os.path.exists(OUTPUT_FILE):
        print("File not found. Run download_drugmechdb() first.")
        return
    with open(OUTPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    print(f"Total mechanism paths: {len(data)}")
    print(f"\nFirst {n} entries:")
    for entry in data[:n]:
        drug = entry.get("drug")
        disease = entry.get("disease")
        path_len = len(entry.get("graph", {}).get("links", []))
        print(f"  Drug: {drug} | Disease: {disease} | Path edges: {path_len}")


def search_by_drug(drug_name: str):
    if not os.path.exists(OUTPUT_FILE):
        print("File not found. Run download_drugmechdb() first.")
        return []
    with open(OUTPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    matches = [e for e in data if drug_name.lower() in str(e.get("drug", "")).lower()]
    print(f"Found {len(matches)} mechanism paths for '{drug_name}':")
    for m in matches[:5]:
        print(f"  {m.get('drug')} -> {m.get('disease')}")
    return matches


if __name__ == "__main__":
    download_drugmechdb()
    load_and_preview()
    search_by_drug("aspirin")
