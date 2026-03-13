"""
PROMISCUOUS 2.0 - Drug Polypharmacology Network
Category: Drug-centric | Type: DB | Subcategory: Drug-Target Interaction (DTI)
Link: https://bioinf-applied.charite.de/promiscuous2/index.php
Paper: https://academic.oup.com/nar/article/49/D1/D1373/5983618

PROMISCUOUS 2.0 integrates drug-protein interactions and PPI networks to
analyze drug polypharmacology and off-target effects.

Access method: Web interface with download functionality.
"""

import urllib.request
import urllib.parse
import os
import json

BASE_URL = "https://bioinf-applied.charite.de/promiscuous2"
OUTPUT_DIR = "PROMISCUOUS2"


def search_drug(drug_name: str) -> str:
    """Search PROMISCUOUS 2.0 for a drug by name."""
    params = urllib.parse.urlencode({
        "search_term": drug_name,
        "search_type": "drug",
    })
    url = f"{BASE_URL}/search.php?{params}"
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def download_dataset():
    """Download PROMISCUOUS 2.0 interaction dataset."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls = [
        f"{BASE_URL}/download/promiscuous2_interactions.csv",
        f"{BASE_URL}/download/promiscuous2_data.zip",
    ]
    for url in urls:
        fname = os.path.join(OUTPUT_DIR, os.path.basename(url))
        print(f"Trying: {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(fname, "wb") as f:
                    f.write(resp.read())
            print(f"  Saved to {fname}")
            return fname
        except Exception as e:
            print(f"  Failed: {e}")
    return None


if __name__ == "__main__":
    print("=== PROMISCUOUS 2.0: Search 'ibuprofen' ===")
    try:
        result = search_drug("ibuprofen")
        print(f"Response ({len(result)} bytes).")
        if "promiscuous" in result.lower() or "drug" in result.lower():
            print("Page loaded successfully.")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== Attempting dataset download ===")
    fpath = download_dataset()
    if not fpath:
        print(
            "\nVisit https://bioinf-applied.charite.de/promiscuous2/index.php\n"
            "PROMISCUOUS 2.0 contains:\n"
            "  - Drug-protein interactions (from ChEMBL, DrugBank, SIDER, STITCH)\n"
            "  - Protein-protein interactions (from STRING)\n"
            "  - Drug similarity networks\n"
            "  - Off-target prediction networks"
        )
