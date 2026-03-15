"""
DrugCombDB - Drug Combination Synergy Data
Category: Drug-centric | Type: DB | Subcategory: Drug Combination/Synergy
Link: http://drugcombdb.denglab.org/
Paper: https://academic.oup.com/nar/article/48/D1/D871/5609522

DrugCombDB is a comprehensive database of drug combinations, collecting
experimental synergy data from NCI-ALMANAC and literature.

Access method: Download data files from the DrugCombDB website.
"""

import urllib.request
import os
import csv

OUTPUT_DIR = "DrugCombDB"

# Download links from DrugCombDB
DOWNLOAD_URLS = [
    "http://drugcombdb.denglab.org/static/download/drug_comb_data_ver3.3.tar.gz",
    "http://drugcombdb.denglab.org/static/download/drug_comb_data.tar.gz",
]


def download_drugcombdb():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for url in DOWNLOAD_URLS:
        fname = os.path.join(OUTPUT_DIR, os.path.basename(url))
        print(f"Trying: {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(fname, "wb") as f:
                    f.write(resp.read())
            print(f"  Saved to {fname}")
            import tarfile
            with tarfile.open(fname, "r:gz") as tf:
                tf.extractall(OUTPUT_DIR)
            print(f"  Extracted to {OUTPUT_DIR}/")
            return True
        except Exception as e:
            print(f"  Failed: {e}")
    return False


def preview_data(n: int = 5):
    """Preview downloaded CSV data."""
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for fname in files:
            if fname.endswith(".csv"):
                fpath = os.path.join(root, fname)
                print(f"\nPreview of {fpath}:")
                with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
                    reader = csv.DictReader(f)
                    print(f"  Columns: {reader.fieldnames}")
                    for i, row in enumerate(reader):
                        if i >= n:
                            break
                        print(f"  {row}")
                return


if __name__ == "__main__":
    success = download_drugcombdb()
    if success:
        preview_data()
    else:
        print(
            "\nDownload failed. Visit http://drugcombdb.denglab.org/ to "
            "download DrugCombDB data manually.\n"
            "The database contains columns:\n"
            "  Drug1, Drug2, Cell_line, Synergy_score, Source, ..."
        )
