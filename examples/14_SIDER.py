"""
SIDER - Side Effect Resource
Category: Drug-centric | Type: DB | Subcategory: Adverse Drug Reaction (ADR)
Link: http://sideeffects.embl.de/
Paper: https://doi.org/10.1093/nar/gkv1075

SIDER contains information on marketed medicines and their recorded adverse
drug reactions, mined from public documents and package inserts.

Access method: Download flat files from the SIDER website.
Files are available at http://sideeffects.embl.de/media/files/
"""

import urllib.request
import os
import gzip

# SIDER download URLs
FILES = {
    "meddra_freq": "http://sideeffects.embl.de/media/files/meddra_freq.tsv.gz",
    "meddra_all_se": "http://sideeffects.embl.de/media/files/meddra_all_se.tsv.gz",
    "drug_names": "http://sideeffects.embl.de/media/files/drug_names.tsv",
}
OUTPUT_DIR = "SIDER"


def download_sider_files(files: dict = None):
    if files is None:
        files = FILES
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, url in files.items():
        fname = os.path.join(OUTPUT_DIR, os.path.basename(url))
        print(f"Downloading {name} from {url} ...")
        try:
            urllib.request.urlretrieve(url, fname)
            print(f"  Saved to {fname}")
        except Exception as e:
            print(f"  Failed: {e}")


def preview_drug_names(n: int = 10):
    fpath = os.path.join(OUTPUT_DIR, "drug_names.tsv")
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}. Run download_sider_files() first.")
        return
    print(f"First {n} entries from drug_names.tsv:")
    with open(fpath, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            parts = line.strip().split("\t")
            print(f"  STITCH: {parts[0]} | Name: {parts[1] if len(parts) > 1 else ''}")


def preview_side_effects(n: int = 5):
    fpath = os.path.join(OUTPUT_DIR, "meddra_all_se.tsv.gz")
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}. Run download_sider_files() first.")
        return
    print(f"First {n} entries from meddra_all_se.tsv.gz:")
    with gzip.open(fpath, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            parts = line.strip().split("\t")
            print(f"  STITCH_flat: {parts[0]} | SE_name: {parts[-1] if len(parts) > 1 else ''}")


if __name__ == "__main__":
    download_sider_files()
    preview_drug_names()
    preview_side_effects()
