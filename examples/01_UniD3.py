"""
UniD3 - Drug Discovery Knowledge Graph
Category: Drug-centric | Type: KG | Subcategory: Drug Knowledgebase
Link: https://github.com/QSong-github/UniD3

UniD3 is a multi-KG built from 150,000+ PubMed articles for drug-disease
matching, effectiveness assessment, and drug-target analysis.

Access method: Download from GitHub repository.
"""

import os
import urllib.request
import zipfile

REPO = "https://github.com/QSong-github/UniD3"
ZIP_URL = "https://github.com/QSong-github/UniD3/archive/refs/heads/main.zip"
OUTPUT_DIR = "UniD3"


def download_unid3():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    zip_path = os.path.join(OUTPUT_DIR, "UniD3-main.zip")
    print(f"Downloading UniD3 from {ZIP_URL} ...")
    urllib.request.urlretrieve(ZIP_URL, zip_path)
    print(f"Saved to {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(OUTPUT_DIR)
    print(f"Extracted to {OUTPUT_DIR}/UniD3-main/")

    extracted = os.path.join(OUTPUT_DIR, "UniD3-main")
    print("Top-level files/dirs:")
    for item in os.listdir(extracted):
        print(f"  {item}")


if __name__ == "__main__":
    download_unid3()
