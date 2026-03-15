"""
PharmKG - Pharmacology Knowledge Graph Benchmark
Category: Drug-centric | Type: KG | Subcategory: Drug Knowledgebase
Link: https://github.com/MindRank-Biotech/PharmKG
Paper: https://academic.oup.com/bib/article/22/4/bbaa344/6042240

PharmKG is a multi-relational, attributed biomedical knowledge graph benchmark
integrating gene-disease, chemical-gene, chemical-disease, and chemical-chemical
relationships for link prediction tasks.

Access method: Download from GitHub.
"""

import urllib.request
import os
import zipfile
import csv

REPO_ZIP = "https://github.com/MindRank-Biotech/PharmKG/archive/refs/heads/master.zip"
OUTPUT_DIR = "PharmKG"

# PharmKG data also available via Zenodo or Figshare
ZENODO_URL = "https://zenodo.org/records/4077338/files/PharmKG-8k.zip?download=1"


def download_pharmkg():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls = [ZENODO_URL, REPO_ZIP]
    for url in urls:
        fname = os.path.join(OUTPUT_DIR, "PharmKG.zip")
        print(f"Trying: {url[:80]} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(fname, "wb") as f:
                    f.write(resp.read())
            print(f"  Saved to {fname}")
            with zipfile.ZipFile(fname, "r") as zf:
                zf.extractall(OUTPUT_DIR)
            print(f"  Extracted to {OUTPUT_DIR}/")
            return True
        except Exception as e:
            print(f"  Failed: {e}")
    return False


def preview_pharmkg_triples(data_dir: str, n: int = 10):
    """Preview PharmKG knowledge graph triples."""
    for root, dirs, files in os.walk(data_dir):
        for fname in files:
            if "train" in fname.lower() and fname.endswith((".tsv", ".txt", ".csv")):
                fpath = os.path.join(root, fname)
                print(f"\nPreview of {fpath}:")
                with open(fpath, encoding="utf-8", errors="replace") as f:
                    for i, line in enumerate(f):
                        if i >= n:
                            break
                        parts = line.strip().split("\t")
                        if len(parts) == 3:
                            print(f"  ({parts[0]}) --[{parts[1]}]--> ({parts[2]})")
                        else:
                            print(f"  {line.strip()[:100]}")
                return


def describe_pharmkg():
    print("=== PharmKG ===")
    print("Version: PharmKG-8k (8,000+ entities)")
    print("Entity types:")
    print("  - Chemical/Drug (DrugBank, ChEMBL)")
    print("  - Gene/Protein (Entrez, UniProt)")
    print("  - Disease (DO, MeSH)")
    print("Relation types:")
    print("  - chemical-gene: inhibition, activation, binding, ...")
    print("  - chemical-disease: treatment, marker, risk factor")
    print("  - gene-disease: association, marker")
    print("  - chemical-chemical: similarity, interaction")
    print("Scale: ~500K triplets, 8,000+ entities")


if __name__ == "__main__":
    describe_pharmkg()
    print()
    success = download_pharmkg()
    if success:
        preview_pharmkg_triples(OUTPUT_DIR)
    else:
        print("\nVisit https://github.com/MindRank-Biotech/PharmKG to access PharmKG.")
