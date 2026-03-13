"""
GDSC/GDSC2 - Genomics of Drug Sensitivity in Cancer
Category: Drug-centric | Type: Dataset | Subcategory: Drug Molecular Property
Link: https://www.cancerrxgene.org/
Paper: https://academic.oup.com/nar/article/41/D1/D955/1059448

GDSC contains pharmacological profiles for ~500 drugs tested in ~1,000 cancer
cell lines with matched genomic data, enabling biomarker discovery.

Access method: Direct download from cancerrxgene.org.
"""

import urllib.request
import os
import csv
import zipfile

OUTPUT_DIR = "GDSC"

# GDSC2 drug sensitivity data (latest)
GDSC2_URL = "https://cog.sanger.ac.uk/cancerrxgene/GDSC_data_8.5/GDSC2_fitted_dose_response_27Oct23.xlsx"
GDSC1_URL = "https://cog.sanger.ac.uk/cancerrxgene/GDSC_data_8.5/GDSC1_fitted_dose_response_27Oct23.xlsx"
# Drug list
DRUG_LIST_URL = "https://www.cancerrxgene.org/downloads/drug_data?drug_id=&drug_name=&putative_gene_target=&pathway_name=&export=csv"


def download_gdsc_drug_list():
    """Download the GDSC drug information list."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    url = "https://cog.sanger.ac.uk/cancerrxgene/GDSC_data_8.5/screened_compunds_rel_8.5.csv"
    fname = os.path.join(OUTPUT_DIR, "GDSC_drug_list.csv")
    print(f"Downloading GDSC drug list ...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


def download_gdsc2_data():
    """Download GDSC2 fitted drug response data (XLSX, ~50MB)."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "GDSC2_fitted_dose_response.xlsx")
    print(f"Downloading GDSC2 dose-response data (~50MB) ...")
    try:
        req = urllib.request.Request(GDSC2_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(fname, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 512)
                    if not chunk:
                        break
                    f.write(chunk)
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


def preview_drug_list(fpath: str, n: int = 10):
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return
    with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        print(f"Columns: {reader.fieldnames}")
        print(f"\nFirst {n} drugs in GDSC:")
        for i, row in enumerate(reader):
            if i >= n:
                break
            name = row.get("DRUG_NAME", row.get("Name", "?"))
            target = row.get("TARGET", row.get("Gene Target", "?"))
            pathway = row.get("PATHWAY_NAME", row.get("Pathway", "?"))
            print(f"  {name} | Target: {target} | Pathway: {pathway}")


if __name__ == "__main__":
    fpath = download_gdsc_drug_list()
    if fpath:
        preview_drug_list(fpath)
    else:
        print("Drug list download failed.")

    print("\n=== GDSC2 Data Download (large file) ===")
    user_input = input("Download GDSC2 dose-response data (~50MB)? [y/N]: ").strip().lower()
    if user_input == "y":
        download_gdsc2_data()
    else:
        print(f"Skipped. Download manually from:\n  {GDSC2_URL}")
        print("Or visit https://www.cancerrxgene.org/downloads/bulk_download")
