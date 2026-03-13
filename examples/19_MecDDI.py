"""
MecDDI - Drug-Drug Interaction Mechanism Annotation
Category: Drug-centric | Type: DB | Subcategory: Drug-Drug Interaction (DDI)
Link: https://mecddi.idrblab.net/download
Paper: https://pubs.acs.org/doi/10.1021/acs.jcim.2c01656

MecDDI provides mechanistic explanations for drug-drug interactions, annotating
the biological mechanisms underlying each interaction.

Access method: Download data files from the MecDDI website.
"""

import urllib.request
import os
import csv

# Download URLs from MecDDI
DOWNLOAD_URLS = {
    "DDI_data": "https://mecddi.idrblab.net/ttd/sites/default/files/mecddi_database/mecddi.csv",
}
FALLBACK_BASE = "https://mecddi.idrblab.net/download"
OUTPUT_DIR = "MecDDI"


def download_mecddi():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls_to_try = [
        "https://mecddi.idrblab.net/ttd/sites/default/files/mecddi_database/MecDDI.zip",
        "https://mecddi.idrblab.net/download/MecDDI.zip",
    ]
    for url in urls_to_try:
        fname = os.path.join(OUTPUT_DIR, "MecDDI.zip")
        print(f"Trying {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(fname, "wb") as f:
                    f.write(resp.read())
            print(f"  Saved to {fname}")
            import zipfile
            with zipfile.ZipFile(fname, "r") as zf:
                zf.extractall(OUTPUT_DIR)
            print(f"  Extracted to {OUTPUT_DIR}/")
            return True
        except Exception as e:
            print(f"  Failed: {e}")
    return False


if __name__ == "__main__":
    success = download_mecddi()
    if not success:
        print(
            "\nDirect download unavailable. Visit https://mecddi.idrblab.net/download "
            "to download MecDDI data files manually.\n"
            "The database contains drug-drug interaction mechanisms with columns:\n"
            "  - Drug1, Drug2 (interacting drug pair)\n"
            "  - Mechanism type (PK/PD)\n"
            "  - Mechanistic path (enzyme/transporter involved)\n"
            "  - Effect description"
        )
    else:
        csv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")]
        for csv_file in csv_files[:1]:
            fpath = os.path.join(OUTPUT_DIR, csv_file)
            with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                print(f"Columns: {reader.fieldnames}")
                for i, row in enumerate(reader):
                    if i >= 3:
                        break
                    print(row)
