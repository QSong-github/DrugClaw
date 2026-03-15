"""
CDCDB - Cancer Drug Combination Database
Category: Drug-centric | Type: DB | Subcategory: Drug Combination/Synergy
Link: https://icc.ise.bgu.ac.il/medical_ai/CDCDB/
Paper: https://www.nature.com/articles/s41597-022-01360-z

CDCDB collects clinically relevant cancer drug combination therapies from
literature, providing combination pairs, cancer types, and clinical evidence.

Access method: Download CSV file directly from the website.
"""

import urllib.request
import os
import csv

OUTPUT_DIR = "CDCDB"
# Direct download link from the paper/website
DOWNLOAD_URL = "https://icc.ise.bgu.ac.il/medical_ai/CDCDB/static/CDCDB.csv"
FALLBACK_URL = (
    "https://raw.githubusercontent.com/ICCBGU/CDCDB/main/CDCDB.csv"
)


def download_cdcdb():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "CDCDB.csv")
    for url in [DOWNLOAD_URL, FALLBACK_URL]:
        print(f"Trying: {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(output_file, "wb") as f:
                    f.write(resp.read())
            print(f"  Saved to {output_file}")
            return output_file
        except Exception as e:
            print(f"  Failed: {e}")
    return None


def preview_cdcdb(fpath: str, n: int = 5):
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return
    with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        print(f"Columns: {reader.fieldnames}")
        for i, row in enumerate(reader):
            if i >= n:
                break
            print(f"  Drug1: {row.get('drug1_name', row.get('Drug1', '?'))} | "
                  f"Drug2: {row.get('drug2_name', row.get('Drug2', '?'))} | "
                  f"Cancer: {row.get('cancer_type', row.get('Cancer', '?'))}")


if __name__ == "__main__":
    fpath = download_cdcdb()
    if fpath:
        preview_cdcdb(fpath)
    else:
        print(
            "\nDownload unavailable. Visit https://icc.ise.bgu.ac.il/medical_ai/CDCDB/ "
            "to access CDCDB.\n"
            "The database contains clinically tested cancer drug combinations:\n"
            "  Drug1, Drug2, Cancer type, Clinical evidence, Outcome"
        )
