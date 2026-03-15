"""
ADReCS - Adverse Drug Reaction Classification System
Category: Drug-centric | Type: DB | Subcategory: Adverse Drug Reaction (ADR)
Link: http://bioinf.xmu.edu.cn/ADReCS
Paper: https://academic.oup.com/nar/article/43/D1/D907/2437234

ADReCS provides a hierarchical classification of adverse drug reactions and
integrates ADR information across FAERS, SIDER, and MedDRA terminology.

Access method: Download from the ADReCS website.
"""

import urllib.request
import os
import csv

BASE_URL = "http://bioinf.xmu.edu.cn/ADReCS"
OUTPUT_DIR = "ADReCS"


def download_adrecs():
    """Download ADReCS data files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls_to_try = [
        f"{BASE_URL}/download/ADReCS.zip",
        f"{BASE_URL}/download/ADReCS_data.zip",
        f"{BASE_URL}/download/ADReCS_drug_ADR.txt",
        f"{BASE_URL}/download.html",
    ]
    for url in urls_to_try:
        ext = os.path.splitext(url)[1] or ".html"
        fname = os.path.join(OUTPUT_DIR, f"ADReCS{ext}")
        print(f"Trying: {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read()
            if len(content) > 2000:
                with open(fname, "wb") as f:
                    f.write(content)
                print(f"  Saved to {fname} ({len(content)} bytes)")
                if url.endswith(".zip"):
                    import zipfile
                    with zipfile.ZipFile(fname, "r") as zf:
                        zf.extractall(OUTPUT_DIR)
                    print(f"  Extracted to {OUTPUT_DIR}/")
                return fname
            else:
                print(f"  Too small ({len(content)} bytes)")
        except Exception as e:
            print(f"  Failed: {e}")
    return None


def describe_adrecs():
    print("=== ADReCS (Adverse Drug Reaction Classification System) ===")
    print("Content:")
    print("  - 27,792 drug-ADR associations")
    print("  - Hierarchical ADR classification (4 levels)")
    print("  - Integration with MedDRA terminology")
    print("  - Sources: FAERS, SIDER, MEDLINE")
    print("\nDatabase structure:")
    print("  - drug_info: drug name, CID, synonyms")
    print("  - ADR_info: ADR name, MedDRA code, classification")
    print("  - drug_ADR: drug-ADR association with evidence")
    print("\nUse cases:")
    print("  - Drug safety profiling")
    print("  - ADR prediction model training")
    print("  - Pharmacovigilance signal detection")


if __name__ == "__main__":
    describe_adrecs()
    print()
    fpath = download_adrecs()
    if not fpath:
        print(f"\nDownload failed. Visit {BASE_URL} to access ADReCS.")
        print("The website may require clicking through a download form.")
