"""
DRKG - Drug Repurposing Knowledge Graph
Category: Drug-centric | Type: KG | Subcategory: Drug Repurposing
Link: https://github.com/gnn4dr/DRKG

DRKG is a comprehensive biomedical KG built for drug repurposing, especially
for COVID-19. Integrates DrugBank, Hetionet, GNBR, STRING, IntAct, DGIdb.

Access method: Download from GitHub or AWS S3.
"""

import urllib.request
import os

OUTPUT_DIR = "DRKG"

# DRKG data files hosted on AWS S3 and GitHub
DRKG_EDGE_URL = "https://dgl-data.s3-accelerate.amazonaws.com/dataset/DRKG/drkg.tar.gz"
GITHUB_REPO_ZIP = "https://github.com/gnn4dr/DRKG/archive/refs/heads/main.zip"


def download_drkg_repo():
    """Download DRKG GitHub repository (code + small files)."""
    import zipfile
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "DRKG-main.zip")
    print(f"Downloading DRKG repository from GitHub ...")
    try:
        urllib.request.urlretrieve(GITHUB_REPO_ZIP, fname)
        print(f"Saved to {fname}")
        with zipfile.ZipFile(fname, "r") as zf:
            zf.extractall(OUTPUT_DIR)
        print(f"Extracted to {OUTPUT_DIR}/DRKG-main/")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def download_drkg_data():
    """
    Download full DRKG edge list (~1.7M triplets, ~100MB compressed).
    This includes all KG triplets for drug repurposing.
    """
    import tarfile
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "drkg.tar.gz")
    print(f"Downloading DRKG edge data (~100MB) from AWS S3 ...")
    try:
        urllib.request.urlretrieve(DRKG_EDGE_URL, fname)
        print(f"Saved to {fname}")
        with tarfile.open(fname, "r:gz") as tf:
            tf.extractall(OUTPUT_DIR)
        print(f"Extracted edge list to {OUTPUT_DIR}/")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def preview_drkg_edges(tsv_path: str, n: int = 5):
    """Preview DRKG edge list (head, relation, tail)."""
    if not os.path.exists(tsv_path):
        print(f"File not found: {tsv_path}")
        return
    print(f"\nFirst {n} edges:")
    with open(tsv_path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            parts = line.strip().split("\t")
            if len(parts) == 3:
                print(f"  ({parts[0]}) --[{parts[1]}]--> ({parts[2]})")


if __name__ == "__main__":
    ok = download_drkg_repo()
    if ok:
        print("\n=== DRKG Repository Contents ===")
        repo_dir = os.path.join(OUTPUT_DIR, "DRKG-main")
        if os.path.exists(repo_dir):
            for item in os.listdir(repo_dir):
                print(f"  {item}")

    print("\n=== Downloading full DRKG edge list ===")
    ok2 = download_drkg_data()
    if ok2:
        tsv = os.path.join(OUTPUT_DIR, "drkg.tsv")
        if not os.path.exists(tsv):
            tsv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".tsv")]
            if tsv_files:
                tsv = os.path.join(OUTPUT_DIR, tsv_files[0])
        preview_drkg_edges(tsv)
