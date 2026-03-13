"""
DrugEHRQA - Drug QA Dataset on Electronic Health Records
Category: Drug-centric | Type: Dataset | Subcategory: Drug NLP/Text Mining
Link: https://github.com/jayetri/DrugEHRQA-A-Question-Answering-Dataset-on-Structured-and-Unstructured-Electronic-Health-Records
Paper: https://aclanthology.org/2022.lrec-1.117/

A QA dataset on structured and unstructured EHR data focused on drug-related
queries. Supports evaluating NLP models on clinical drug information extraction.

Note: Underlying MIMIC-III data requires PhysioNet credentialed access.
The GitHub repository contains the code and anonymized sample data.

Access method: Download from GitHub repository.
"""

import os
import urllib.request
import zipfile

ZIP_URL = "https://github.com/jayetri/DrugEHRQA-A-Question-Answering-Dataset-on-Structured-and-Unstructured-Electronic-Health-Records/archive/refs/heads/main.zip"
OUTPUT_DIR = "DrugEHRQA"


def download_drugehqa():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    zip_path = os.path.join(OUTPUT_DIR, "DrugEHRQA-main.zip")
    print("Downloading DrugEHRQA repository ...")
    urllib.request.urlretrieve(ZIP_URL, zip_path)
    print(f"Saved to {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(OUTPUT_DIR)
    print(f"Extracted to {OUTPUT_DIR}/")
    extracted_dir = [d for d in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, d))][0]
    print(f"Top-level contents of {extracted_dir}:")
    for item in os.listdir(os.path.join(OUTPUT_DIR, extracted_dir)):
        print(f"  {item}")


if __name__ == "__main__":
    download_drugehqa()
    print(
        "\nNote: Full dataset requires MIMIC-III access from PhysioNet "
        "(https://physionet.org/content/mimiciii/)"
    )
