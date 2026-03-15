"""
Drug Reviews (Drugs.com) - Drug User Reviews for NLP
Category: Drug-centric | Type: Dataset | Subcategory: Drug Review/Patient Report
Link: https://archive.ics.uci.edu/dataset/461/drug+review+dataset+druglib+com
Paper: N/A

A dataset of patient drug reviews from Drugs.com available via UCI ML Repository,
containing drug name, condition, rating, and text review.

Access method: Download directly from UCI ML Repository.
"""

import urllib.request
import os
import zipfile
import csv

OUTPUT_DIR = "Drug_Reviews_Drugscom"
# UCI ML Repository dataset ID 461
UCI_URL = "https://archive.ics.uci.edu/static/public/461/drug+review+dataset+druglib+com.zip"


def download_drug_reviews():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "drug_review_dataset.zip")
    print("Downloading Drug Reviews dataset from UCI ML Repository ...")
    try:
        req = urllib.request.Request(UCI_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        with zipfile.ZipFile(fname, "r") as zf:
            print(f"Contents: {zf.namelist()}")
            zf.extractall(OUTPUT_DIR)
        print(f"Extracted to {OUTPUT_DIR}/")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def preview_reviews(n: int = 5):
    """Preview the drug review dataset."""
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for fname in files:
            if fname.endswith(".tsv") or fname.endswith(".csv"):
                fpath = os.path.join(root, fname)
                print(f"\nPreview of {fpath}:")
                sep = "\t" if fname.endswith(".tsv") else ","
                with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
                    reader = csv.DictReader(f, delimiter=sep)
                    print(f"  Columns: {reader.fieldnames}")
                    for i, row in enumerate(reader):
                        if i >= n:
                            break
                        drug = row.get("drugName", row.get("drug_name", "?"))
                        cond = row.get("condition", "?")
                        rating = row.get("rating", "?")
                        review = str(row.get("review", ""))[:80]
                        print(f"  Drug: {drug} | Condition: {cond} | "
                              f"Rating: {rating} | Review: {review}...")
                return


if __name__ == "__main__":
    success = download_drug_reviews()
    if success:
        preview_reviews()
    else:
        print(
            "\nDownload failed. Visit:\n"
            "  https://archive.ics.uci.edu/dataset/461/drug+review+dataset+druglib+com\n"
            "The dataset contains columns:\n"
            "  Unnamed:0, drugName, condition, review, rating, date, usefulCount"
        )
