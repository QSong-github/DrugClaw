"""
WHO Essential Medicines List - Global Essential Drug List
Category: Drug-centric | Type: DB | Subcategory: Drug Knowledgebase
Link: https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.02

The WHO Model List of Essential Medicines (EML) lists the minimum medicine
needs for a basic health-care system, organized by therapeutic category.

Access method:
  1. Download PDF from WHO website
  2. Access via WHO APIs (limited structured data)
  3. Community-maintained CSV versions on GitHub
"""

import urllib.request
import os
import csv

OUTPUT_DIR = "WHO_EML"

# WHO EML 23rd edition (2023) PDF
WHO_EML_PDF_URL = "https://www.who.int/docs/default-source/essential-medicines/2023-eml-final-web.pdf"

# Community-maintained CSV/JSON version
GITHUB_CSV_URL = "https://raw.githubusercontent.com/dolph/essential-medicines-list/master/medicines.csv"


def download_eml_pdf():
    """Download the official WHO EML PDF."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "WHO_EML_2023.pdf")
    print(f"Downloading WHO EML PDF ...")
    try:
        req = urllib.request.Request(
            WHO_EML_PDF_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


def download_community_csv():
    """Download community-maintained CSV version of the EML."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "eml_medicines.csv")
    print(f"Downloading community EML CSV ...")
    try:
        req = urllib.request.Request(GITHUB_CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


def preview_eml_csv(fpath: str, n: int = 10):
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return
    with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        print(f"Columns: {reader.fieldnames}")
        print(f"\nFirst {n} essential medicines:")
        for i, row in enumerate(reader):
            if i >= n:
                break
            name = row.get("medicine", row.get("name", row.get("Medicine", "?")))
            category = row.get("category", row.get("Category", "?"))
            print(f"  {name} | Category: {category}")


if __name__ == "__main__":
    print("=== WHO Essential Medicines List ===")
    print("23rd edition (2023)")
    print("~500 medicines organized across therapeutic categories\n")

    fpath = download_community_csv()
    if fpath:
        preview_eml_csv(fpath)
    else:
        print("Trying PDF download ...")
        pdf = download_eml_pdf()
        if pdf:
            print(f"PDF downloaded: {pdf}")
            print("To parse the PDF: pip install pdfplumber")
        else:
            print(
                "\nDownload failed. Access the WHO EML at:\n"
                "  https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.02\n"
                "Or search the online database:\n"
                "  https://list.essentialmedicines.org/"
            )
