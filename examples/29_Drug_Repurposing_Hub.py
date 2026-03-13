"""
Drug Repurposing Hub - Curated Drug Repurposing Compound Collection
Category: Drug-centric | Type: DB | Subcategory: Drug Repurposing
Link: https://clue.io/repurposing
Paper: https://www.nature.com/articles/nm.4306

The Drug Repurposing Hub is a curated collection of FDA-approved drugs and
clinical candidates for repurposing screens, maintained by Broad Institute's
CLUE platform.

Access method: Download CSV files from the Clue.io website (free, no login).
Direct download: https://clue.io/repurposing-app
"""

import urllib.request
import os
import csv

OUTPUT_DIR = "DrugRepurposingHub"

# Direct download URL for the repurposing hub drug list
DRUG_LIST_URL = (
    "https://s3.amazonaws.com/data.clue.io/repurposing/downloads/"
    "repurposing_drugs_20200324.txt"
)
SAMPLES_URL = (
    "https://s3.amazonaws.com/data.clue.io/repurposing/downloads/"
    "repurposing_samples_20200324.txt"
)


def download_hub():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = {
        "drugs": DRUG_LIST_URL,
        "samples": SAMPLES_URL,
    }
    downloaded = {}
    for name, url in files.items():
        fname = os.path.join(OUTPUT_DIR, os.path.basename(url))
        print(f"Downloading {name} ...")
        try:
            urllib.request.urlretrieve(url, fname)
            print(f"  Saved to {fname}")
            downloaded[name] = fname
        except Exception as e:
            print(f"  Failed: {e}")
    return downloaded


def preview_drugs(fpath: str, n: int = 5):
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return
    with open(fpath, encoding="utf-8", errors="replace") as f:
        # Skip comment lines
        lines = [l for l in f if not l.startswith("!")]
    reader = csv.DictReader(lines, delimiter="\t")
    print(f"Columns: {reader.fieldnames}")
    for i, row in enumerate(reader):
        if i >= n:
            break
        print(f"  Name: {row.get('pert_iname')} | "
              f"Status: {row.get('clinical_phase')} | "
              f"MOA: {row.get('moa')}")


if __name__ == "__main__":
    downloaded = download_hub()
    if "drugs" in downloaded:
        print("\n=== Drug Repurposing Hub: Drug list preview ===")
        preview_drugs(downloaded["drugs"])
    else:
        print("\nDownload failed. Visit https://clue.io/repurposing to "
              "access the Drug Repurposing Hub.\nManual download available at "
              "https://clue.io/repurposing-app")
