"""
DCDB - Drug Combination Database
Category: Drug-centric | Type: DB | Subcategory: Drug Combination/Synergy
Link: http://www.cls.zju.edu.cn/dcdb/
Paper: https://academic.oup.com/database/article/doi/10.1093/database/bau124/2635579

DCDB provides information on approved and investigational drug combinations,
including combination rationale, component drugs, targets, and relevant diseases.

Note: The DCDB website may have limited availability. This script attempts to
download data from the website and provides an alternative data source.

Access method: Direct download from the DCDB website.
"""

import urllib.request
import os
import csv

OUTPUT_DIR = "DCDB"
BASE_URL = "http://www.cls.zju.edu.cn/dcdb"

# Alternative: Published supplemental tables from the DCDB paper
SUPPLEMENT_URL = "https://academic.oup.com/database/article/doi/10.1093/database/bau124/2635579"


def download_dcdb_data():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls_to_try = [
        f"{BASE_URL}/download/DCDB_combination.csv",
        f"{BASE_URL}/download/dcdb.csv",
        f"{BASE_URL}/download/DCDB.zip",
    ]
    for url in urls_to_try:
        fname = os.path.join(OUTPUT_DIR, os.path.basename(url))
        print(f"Trying: {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(fname, "wb") as f:
                    f.write(resp.read())
            size = os.path.getsize(fname)
            if size > 1000:
                print(f"  Saved to {fname} ({size} bytes)")
                return fname
            else:
                print(f"  File too small ({size} bytes), skipping")
                os.remove(fname)
        except Exception as e:
            print(f"  Failed: {e}")
    return None


def describe_dcdb():
    print("=== DCDB (Drug Combination Database) ===")
    print("Content:")
    print("  - 1,363 drug combinations (approved + investigational)")
    print("  - Drug pair information: names, structures, targets")
    print("  - Disease indication for each combination")
    print("  - Combination rationale and mechanism")
    print("  - Clinical status and references")
    print("\nFields:")
    print("  - Combination_ID, Drug1, Drug2")
    print("  - Disease, Combination_Mechanism")
    print("  - Drug1_Target, Drug2_Target")
    print("  - Reference (PMID or FDA label)")


if __name__ == "__main__":
    describe_dcdb()
    print()
    fpath = download_dcdb_data()
    if fpath:
        ext = os.path.splitext(fpath)[1]
        if ext == ".csv":
            with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                print(f"\nColumns: {reader.fieldnames}")
                for i, row in enumerate(reader):
                    if i >= 5:
                        break
                    print(f"  {row}")
    else:
        print(f"\nDownload failed. Visit {BASE_URL}/ to access DCDB.")
