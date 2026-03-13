"""
DrugProt - Drug-Protein Relation Extraction Benchmark
Category: Drug-centric | Type: Dataset | Subcategory: Drug NLP/Text Mining
Link: https://zenodo.org/records/5119892
Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC10683943/

DrugProt is a BioCreative VII track dataset for relation extraction between
drugs/chemicals and gene/proteins in biomedical literature, covering 13 relation types.

Access method: Download from Zenodo.
"""

import urllib.request
import os
import zipfile

OUTPUT_DIR = "DrugProt"
ZENODO_URL = "https://zenodo.org/records/5119892/files/drugprot-gs-training-development.zip?download=1"


def download_drugprot():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "drugprot-gs.zip")
    print(f"Downloading DrugProt from Zenodo ...")
    try:
        req = urllib.request.Request(ZENODO_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        with zipfile.ZipFile(fname, "r") as zf:
            zf.extractall(OUTPUT_DIR)
        print(f"Extracted to {OUTPUT_DIR}/")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def parse_drugprot_relations(tsv_path: str, n: int = 5):
    """Parse DrugProt relation annotations (.tsv format)."""
    if not os.path.exists(tsv_path):
        print(f"File not found: {tsv_path}")
        return
    print(f"\nFirst {n} relation examples from {tsv_path}:")
    with open(tsv_path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                print(f"  PMID: {parts[0]} | Relation: {parts[1]} | "
                      f"Arg1: {parts[2]} | Arg2: {parts[3]}")


if __name__ == "__main__":
    success = download_drugprot()
    if success:
        # Find relation files
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for fname in files:
                if "relations" in fname and fname.endswith(".tsv"):
                    parse_drugprot_relations(os.path.join(root, fname))
                    break
            else:
                continue
            break
        print("\nDirectory contents:")
        for root, dirs, files in os.walk(OUTPUT_DIR):
            depth = root.replace(OUTPUT_DIR, "").count(os.sep)
            if depth <= 1:
                indent = "  " * depth
                print(f"{indent}{os.path.basename(root)}/")
                for f in files[:5]:
                    print(f"{indent}  {f}")
    else:
        print("Visit https://zenodo.org/records/5119892 to download DrugProt manually.")
