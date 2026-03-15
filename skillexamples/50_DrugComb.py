"""
DrugComb - Drug Combination Response Data for Cancer
Category: Drug-centric | Type: DB | Subcategory: Drug Combination/Synergy
Link: https://zenodo.org/records/11102665
Paper: https://academic.oup.com/nar/article/47/W1/W43/5486743

DrugComb is an open-access portal for drug combination response data in cancer
cell lines, integrating data from multiple large-scale screens with harmonized
synergy scores across multiple models.

Access method: Download from Zenodo.
"""

import urllib.request
import os
import csv
import zipfile

OUTPUT_DIR = "DrugComb"
ZENODO_BASE = "https://zenodo.org/records/11102665/files"


def download_drugcomb(file_name: str = "drugcomb_data_v1.5.csv"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    url = f"{ZENODO_BASE}/{file_name}?download=1"
    fname = os.path.join(OUTPUT_DIR, file_name)
    print(f"Downloading DrugComb from Zenodo: {file_name} ...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(fname, "wb") as f:
                # Stream to handle large file
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


def list_zenodo_files():
    """List available files in the DrugComb Zenodo record."""
    url = "https://zenodo.org/api/records/11102665"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        files = data.get("files", [])
        print("Available files in DrugComb Zenodo record:")
        for f in files:
            print(f"  {f.get('key')} ({f.get('size', 0) // 1024} KB)")
        return files
    except Exception as e:
        print(f"Failed to list files: {e}")
        return []


def preview_drugcomb(fpath: str, n: int = 5):
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return
    with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        print(f"Columns: {reader.fieldnames}")
        print(f"\nFirst {n} entries:")
        for i, row in enumerate(reader):
            if i >= n:
                break
            d1 = row.get("drug_row", "?")
            d2 = row.get("drug_col", "?")
            cell = row.get("cell_line_name", "?")
            synergy = row.get("synergy_zip", "?")
            print(f"  {d1} + {d2} | Cell: {cell} | Synergy (ZIP): {synergy}")


if __name__ == "__main__":
    import json

    print("=== DrugComb: Available Zenodo files ===")
    files = list_zenodo_files()

    if files:
        # Download the smallest/main data file
        small_file = sorted(files, key=lambda x: x.get("size", float("inf")))[0]
        fname = download_drugcomb(small_file.get("key", "drugcomb_data_v1.5.csv"))
        if fname:
            preview_drugcomb(fname)
    else:
        # Try direct download
        fname = download_drugcomb("drugcomb_data_v1.5.csv")
        if fname:
            preview_drugcomb(fname)
        else:
            print("\nVisit https://zenodo.org/records/11102665 to download DrugComb.")
