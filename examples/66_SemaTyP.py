"""
SemaTyP - Drug-Disease Association Knowledge Graph
Category: Drug-centric | Type: KG | Subcategory: Drug–Disease Associations
Link: https://github.com/ShengtianSang/SemaTyP
Paper: https://link.springer.com/article/10.1186/s12859-018-2167-5

SemaTyP is a knowledge graph linking drugs, diseases, and biomedical entities
extracted from literature for drug discovery and repositioning.

Access method: Download from GitHub.
"""

import urllib.request
import os
import zipfile
import csv

REPO_ZIP = "https://github.com/ShengtianSang/SemaTyP/archive/refs/heads/master.zip"
OUTPUT_DIR = "SemaTyP"


def download_sematyp():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "SemaTyP-master.zip")
    print("Downloading SemaTyP from GitHub ...")
    try:
        urllib.request.urlretrieve(REPO_ZIP, fname)
        print(f"Saved to {fname}")
        with zipfile.ZipFile(fname, "r") as zf:
            zf.extractall(OUTPUT_DIR)
        print(f"Extracted to {OUTPUT_DIR}/SemaTyP-master/")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def explore_dataset(base_dir: str):
    """Explore the SemaTyP dataset structure."""
    extract_dir = os.path.join(base_dir, "SemaTyP-master")
    if not os.path.exists(extract_dir):
        extract_dir = base_dir
    print(f"\nContents of {extract_dir}:")
    for root, dirs, files in os.walk(extract_dir):
        depth = root.replace(extract_dir, "").count(os.sep)
        if depth <= 2:
            indent = "  " * depth
            print(f"{indent}{os.path.basename(root)}/")
            for f in sorted(files)[:5]:
                print(f"{indent}  {f}")


def preview_triples(data_dir: str, n: int = 10):
    """Preview knowledge graph triples from SemaTyP."""
    for root, dirs, files in os.walk(data_dir):
        for fname in files:
            if fname.endswith((".tsv", ".txt", ".csv")) and "train" in fname.lower():
                fpath = os.path.join(root, fname)
                print(f"\nTriples from {fpath}:")
                with open(fpath, encoding="utf-8", errors="replace") as f:
                    for i, line in enumerate(f):
                        if i >= n:
                            break
                        parts = line.strip().split("\t")
                        if len(parts) >= 3:
                            print(f"  ({parts[0]}) --[{parts[1]}]--> ({parts[2]})")
                        else:
                            print(f"  {line.strip()[:100]}")
                return


if __name__ == "__main__":
    success = download_sematyp()
    if success:
        explore_dataset(OUTPUT_DIR)
        preview_triples(OUTPUT_DIR)
    else:
        print("\nVisit https://github.com/ShengtianSang/SemaTyP to access SemaTyP.")
        print("\nSemaTyP KG contains:")
        print("  - Drug-Disease associations mined from PubMed")
        print("  - Semantic type annotations (drug, disease, gene, etc.)")
        print("  - Relation types: treats, causes, associated_with, ...")
