"""
CancerDR - Cancer Drug Resistance Data
Category: Drug-centric | Type: DB | Subcategory: Drug Repurposing
Link: http://crdd.osdd.net/raghava/cancerdr/
Paper: https://www.nature.com/articles/srep01445

CancerDR provides pharmacological profiles of anticancer drugs against cancer
cell lines, with information on drug targets, resistance mechanisms, and cell
line characteristics.

Access method: Download from the CancerDR website.
"""

import urllib.request
import os
import csv

BASE_URL = "http://crdd.osdd.net/raghava/cancerdr"
OUTPUT_DIR = "CancerDR"


def download_cancerdr():
    """Download CancerDR data files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls_to_try = [
        f"{BASE_URL}/download.php",
        f"{BASE_URL}/data/cancerdr.zip",
        f"{BASE_URL}/data/cancerdr_data.csv",
    ]
    for url in urls_to_try:
        ext = ".zip" if url.endswith(".zip") else ".csv" if url.endswith(".csv") else ".html"
        fname = os.path.join(OUTPUT_DIR, f"cancerdr{ext}")
        print(f"Trying: {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read()
            with open(fname, "wb") as f:
                f.write(content)
            if len(content) > 5000:
                print(f"  Saved to {fname} ({len(content)} bytes)")
                if url.endswith(".zip"):
                    import zipfile
                    with zipfile.ZipFile(fname, "r") as zf:
                        zf.extractall(OUTPUT_DIR)
                return fname
            else:
                print(f"  File too small ({len(content)} bytes)")
        except Exception as e:
            print(f"  Failed: {e}")
    return None


def describe_cancerdr():
    print("=== CancerDR (Cancer Drug Resistance Database) ===")
    print("Content:")
    print("  - Pharmacological profiles of 148 anticancer drugs")
    print("  - Tested on 952 cancer cell lines (NCI-60 and others)")
    print("  - Drug target information")
    print("  - Cancer type and cell line metadata")
    print("  - Resistance/sensitivity IC50 values")
    print("\nRelated resources:")
    print("  - GDSC (60_GDSC.py): larger-scale cancer drug sensitivity")
    print("  - NCI-60 DTP: https://dtp.cancer.gov/discovery_development/nci-60/")


if __name__ == "__main__":
    describe_cancerdr()
    print()
    fpath = download_cancerdr()
    if not fpath:
        print(
            f"\nDownload failed. Visit {BASE_URL}/ to access CancerDR.\n"
            "The database can be searched by drug name, cancer type, or cell line."
        )
