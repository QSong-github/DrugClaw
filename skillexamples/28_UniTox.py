"""
UniTox - Unified Multi-Organ Drug Toxicity Annotation
Category: Drug-centric | Type: Dataset | Subcategory: Drug Toxicity
Link: https://zenodo.org/records/11627822
Paper: https://doi.org/10.1101/2024.06.21.24309315

UniTox uses GPT-4o to process FDA drug labels and extract toxicity summaries
and ratings across eight organ-system toxicities, with 85–96% clinician concordance.

Access method: Download from Zenodo.
"""

import urllib.request
import os
import csv

OUTPUT_DIR = "UniTox"
ZENODO_BASE = "https://zenodo.org/records/11627822/files"

# UniTox files available on Zenodo
FILES = [
    "unitox.csv",
]


def download_unitox():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for fname in FILES:
        url = f"{ZENODO_BASE}/{fname}?download=1"
        output = os.path.join(OUTPUT_DIR, fname)
        print(f"Downloading {fname} from Zenodo ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(output, "wb") as f:
                    f.write(resp.read())
            print(f"  Saved to {output}")
            return output
        except Exception as e:
            print(f"  Failed: {e}")
    return None


def preview_unitox(fpath: str, n: int = 5):
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
            drug = row.get("drug_name", row.get("Drug", "?"))
            cardio = row.get("cardiotoxicity_rating", row.get("cardiotoxicity", "?"))
            liver = row.get("hepatotoxicity_rating", row.get("hepatotoxicity", "?"))
            print(f"  Drug: {drug} | Cardio: {cardio} | Liver: {liver}")


if __name__ == "__main__":
    fpath = download_unitox()
    if fpath:
        preview_unitox(fpath)
    else:
        print(
            "\nDownload failed. Visit https://zenodo.org/records/11627822 to "
            "download UniTox manually.\n"
            "UniTox columns include:\n"
            "  - drug_name\n"
            "  - cardiotoxicity_rating (none/low/moderate/serious)\n"
            "  - hepatotoxicity_rating\n"
            "  - nephrotoxicity_rating\n"
            "  - pulmonary_toxicity_rating\n"
            "  - hematological_toxicity_rating\n"
            "  - dermatological_toxicity_rating\n"
            "  - ototoxicity_rating\n"
            "  - reproductive_toxicity_rating"
        )
