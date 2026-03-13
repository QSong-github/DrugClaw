"""
WebMD Drug Reviews - Patient-Reported Drug Effectiveness and Side Effects
Category: Drug-centric | Type: Dataset | Subcategory: Drug Review/Patient Report
Link: https://www.kaggle.com/datasets/rohanharode07/webmd-drug-reviews-dataset

A dataset of patient drug reviews from WebMD, including drug name, condition,
effectiveness rating, ease of use, and side effect descriptions.

Access method: Download from Kaggle (requires Kaggle account & kaggle API token).
Install kaggle CLI: pip install kaggle
Place ~/.kaggle/kaggle.json with your credentials.
"""

import os
import subprocess
import csv


DATASET = "rohanharode07/webmd-drug-reviews-dataset"
OUTPUT_DIR = "webmd_drug_reviews"


def download_via_kaggle():
    """Download WebMD drug reviews dataset using the Kaggle CLI."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cmd = ["kaggle", "datasets", "download", "-d", DATASET,
           "--path", OUTPUT_DIR, "--unzip"]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("Download successful.")
        return True
    else:
        print(f"Kaggle CLI error: {result.stderr}")
        print("Ensure kaggle is installed and ~/.kaggle/kaggle.json is configured.")
        return False


def preview_reviews(csv_file: str, n: int = 5):
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return
    with open(csv_file, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        print(f"Columns: {reader.fieldnames}")
        for i, row in enumerate(reader):
            if i >= n:
                break
            print(f"  Drug: {row.get('drug')}, Condition: {row.get('condition')}, "
                  f"Rating: {row.get('rating')}")


if __name__ == "__main__":
    success = download_via_kaggle()
    if success:
        # The file is typically named 'webmd.csv'
        csv_file = os.path.join(OUTPUT_DIR, "webmd.csv")
        preview_reviews(csv_file)
    else:
        print("\nAlternative: Visit the Kaggle page directly:")
        print(f"  https://www.kaggle.com/datasets/{DATASET}")
