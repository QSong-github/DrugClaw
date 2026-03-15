"""
RepurposeDrugs - Drug Repurposing Opportunities Database
Category: Drug-centric | Type: DB | Subcategory: Drug Repurposing
Link: https://repurposedrugs.org/
Paper: https://academic.oup.com/bib/article/25/4/bbae328/7709763

RepurposeDrugs.org is a curated portal documenting drug repurposing
opportunities with supporting evidence from trials and literature.

Access method: Download from the website or via direct data files.
"""

import urllib.request
import urllib.parse
import os
import csv

BASE_URL = "https://repurposedrugs.org"
OUTPUT_DIR = "RepurposeDrugs"


def search_repurposed_drugs(drug_name: str = "", disease: str = "") -> str:
    """
    Query RepurposeDrugs.org search endpoint.
    Returns raw HTML/JSON response.
    """
    params = {}
    if drug_name:
        params["drug"] = drug_name
    if disease:
        params["disease"] = disease
    query_str = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/search?{query_str}" if query_str else f"{BASE_URL}/"
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def download_dataset():
    """Download RepurposeDrugs dataset."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Try common download paths
    urls = [
        f"{BASE_URL}/download/repurposedrugs_data.csv",
        f"{BASE_URL}/static/data/repurposedrugs.csv",
        f"{BASE_URL}/data/download",
    ]
    for url in urls:
        fname = os.path.join(OUTPUT_DIR, "repurposedrugs.csv")
        print(f"Trying: {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read()
                with open(fname, "wb") as f:
                    f.write(content)
            print(f"  Saved to {fname}")
            return fname
        except Exception as e:
            print(f"  Failed: {e}")
    return None


if __name__ == "__main__":
    print("=== RepurposeDrugs: Homepage check ===")
    try:
        content = search_repurposed_drugs()
        print(f"Page loaded ({len(content)} bytes).")
        if "repurpos" in content.lower():
            print("Confirmed: RepurposeDrugs content detected.")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== Attempting dataset download ===")
    fpath = download_dataset()
    if fpath and os.path.exists(fpath):
        with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i >= 5:
                    break
                print(f"  {row}")
    else:
        print(
            "\nVisit https://repurposedrugs.org/ to access the database.\n"
            "The database includes:\n"
            "  - Original drug indication\n"
            "  - New repurposing indication\n"
            "  - Clinical phase, evidence level, references"
        )
