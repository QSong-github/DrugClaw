"""
ADE Corpus - Adverse Drug Event Extraction Benchmark
Category: Drug-centric | Type: Dataset | Subcategory: Drug NLP/Text Mining
Link: https://github.com/trunghlt/AdverseDrugReaction
Paper: https://aclanthology.org/C16-1084/

The ADE Corpus v2 contains annotated medical case reports for adverse drug
event detection and drug-dose entity extraction.

Access method: Download from GitHub.
"""

import urllib.request
import os
import csv
import zipfile

REPO_ZIP = "https://github.com/trunghlt/AdverseDrugReaction/archive/refs/heads/master.zip"
OUTPUT_DIR = "ADE_Corpus"


def download_ade_corpus():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "AdverseDrugReaction-master.zip")
    print("Downloading ADE Corpus from GitHub ...")
    try:
        urllib.request.urlretrieve(REPO_ZIP, fname)
        print(f"Saved to {fname}")
        with zipfile.ZipFile(fname, "r") as zf:
            zf.extractall(OUTPUT_DIR)
        print(f"Extracted to {OUTPUT_DIR}/")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def load_ade_dataset(data_dir: str, n: int = 5):
    """
    Load ADE annotations. The dataset includes:
    - ADE-NEG.txt: sentences without ADE (negative examples)
    - DRUG-AE.rel: drug-adverse event relation pairs
    - DRUG-DOSE.rel: drug-dose relation pairs
    """
    ae_file = os.path.join(data_dir, "DRUG-AE.rel")
    if not os.path.exists(ae_file):
        # Search recursively
        for root, dirs, files in os.walk(data_dir):
            for f in files:
                if f == "DRUG-AE.rel":
                    ae_file = os.path.join(root, f)
                    break

    if not os.path.exists(ae_file):
        print(f"DRUG-AE.rel not found in {data_dir}")
        print("Available files:")
        for root, dirs, files in os.walk(data_dir):
            for f in files:
                print(f"  {os.path.join(root, f)}")
        return []

    print(f"\nFirst {n} ADE relation examples from {ae_file}:")
    examples = []
    with open(ae_file, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            # Format: PubMed_ID | text | ADE_start | ADE_end | ADE | Drug_start | Drug_end | Drug | PubMed_ID2
            parts = line.strip().split("|")
            if len(parts) >= 8:
                print(f"  PubMed: {parts[0].strip()} | Drug: {parts[7].strip()} | ADE: {parts[4].strip()}")
                examples.append({"drug": parts[7].strip(), "ade": parts[4].strip()})
    return examples


if __name__ == "__main__":
    success = download_ade_corpus()
    if success:
        extract_dir = os.path.join(OUTPUT_DIR, "AdverseDrugReaction-master")
        if not os.path.exists(extract_dir):
            extract_dir = OUTPUT_DIR
        load_ade_dataset(extract_dir)
    else:
        print("Visit https://github.com/trunghlt/AdverseDrugReaction for manual access.")
