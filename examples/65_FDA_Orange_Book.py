"""
FDA Orange Book - FDA-Approved Drug Products Listing
Category: Drug-centric | Type: DB | Subcategory: Drug Knowledgebase
Link: https://www.accessdata.fda.gov/scripts/cder/ob/

The FDA Orange Book lists all FDA-approved drugs with patent and exclusivity
information, therapeutic equivalence ratings, and approval details.

Access method:
  1. Direct download (ASCII files, updated monthly)
  2. openFDA API (limited Orange Book data)
  3. FDA API: https://api.fda.gov/drug/ndc.json
"""

import urllib.request
import os
import csv
import zipfile
import urllib.parse
import json

OUTPUT_DIR = "FDA_Orange_Book"

# FDA Orange Book bulk download (text files updated monthly)
ORANGE_BOOK_URL = "https://www.fda.gov/media/76860/download"
# Alternative: openFDA NDC endpoint which contains some OB data
OPENFDA_NDC_URL = "https://api.fda.gov/drug/ndc.json"


def download_orange_book():
    """Download the FDA Orange Book ASCII data files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "orange_book_data.zip")
    print("Downloading FDA Orange Book data ...")
    try:
        req = urllib.request.Request(ORANGE_BOOK_URL,
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        with zipfile.ZipFile(fname, "r") as zf:
            print(f"Contents: {zf.namelist()}")
            zf.extractall(OUTPUT_DIR)
        print(f"Extracted to {OUTPUT_DIR}/")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def search_approved_drugs(drug_name: str, limit: int = 5) -> dict:
    """Search FDA-approved drugs via openFDA NDC endpoint."""
    query = f'brand_name:"{drug_name}" OR generic_name:"{drug_name}"'
    params = urllib.parse.urlencode({
        "search": query,
        "limit": limit,
    })
    url = f"{OPENFDA_NDC_URL}?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_drug_approval_info(drug_name: str, limit: int = 3) -> dict:
    """Get drug approval information from openFDA drugsfda endpoint."""
    params = urllib.parse.urlencode({
        "search": f'openfda.brand_name:"{drug_name}"',
        "limit": limit,
    })
    url = f"https://api.fda.gov/drug/drugsfda.json?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def preview_products_file():
    """Preview the Orange Book products file if downloaded."""
    products_file = os.path.join(OUTPUT_DIR, "products.txt")
    if not os.path.exists(products_file):
        products_file = os.path.join(OUTPUT_DIR, "Products.txt")
    if not os.path.exists(products_file):
        for f in os.listdir(OUTPUT_DIR):
            if "product" in f.lower() and f.endswith(".txt"):
                products_file = os.path.join(OUTPUT_DIR, f)
                break
    if not os.path.exists(products_file):
        print("Products file not found.")
        return
    print(f"\nPreview of {products_file}:")
    with open(products_file, encoding="latin-1", errors="replace") as f:
        for i, line in enumerate(f):
            if i >= 6:
                break
            print(f"  {line.rstrip()}")


if __name__ == "__main__":
    print("=== FDA Orange Book: Download data ===")
    success = download_orange_book()
    if success:
        preview_products_file()

    print("\n=== openFDA: Search approved drugs for 'ibuprofen' ===")
    try:
        result = search_approved_drugs("ibuprofen")
        for drug in result.get("results", [])[:3]:
            brand = drug.get("brand_name", "?")
            generic = drug.get("generic_name", "?")
            applicant = drug.get("labeler_name", "?")
            print(f"  Brand: {brand} | Generic: {generic} | Applicant: {applicant}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== FDA Drug Approval Info: 'aspirin' ===")
    try:
        result = get_drug_approval_info("aspirin")
        for app in result.get("results", [])[:2]:
            app_num = app.get("application_number", "?")
            sponsor = app.get("sponsor_name", "?")
            products = app.get("products", [])
            print(f"  App#: {app_num} | Sponsor: {sponsor} | "
                  f"Products: {len(products)}")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Visit https://www.accessdata.fda.gov/scripts/cder/ob/")
