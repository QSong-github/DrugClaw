"""
DrugRepoBank - Drug Repurposing Evidence Compilation
Category: Drug-centric | Type: DB | Subcategory: Drug Repurposing
Link: https://awi.cuhk.edu.cn/DrugRepoBank/php/index.php
Paper: https://academic.oup.com/database/article/doi/10.1093/database/baae051/7712639

DrugRepoBank collects and curates drug repurposing candidates and evidence from
experimental, computational, and clinical sources.

Access method: Web interface and direct data downloads from the website.
"""

import urllib.request
import urllib.parse
import os
import json

BASE_URL = "https://awi.cuhk.edu.cn/DrugRepoBank"
OUTPUT_DIR = "DrugRepoBank"


def search_repurposing_candidates(drug_name: str) -> dict:
    """
    Search DrugRepoBank for repurposing candidates involving a specific drug.
    Uses the web search API endpoint.
    """
    params = urllib.parse.urlencode({"keyword": drug_name, "type": "drug"})
    url = f"{BASE_URL}/php/search.php?{params}"
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/html",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode("utf-8", errors="replace")
    return content


def download_database():
    """Attempt to download the DrugRepoBank full dataset."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    download_url = f"{BASE_URL}/php/download.php"
    output = os.path.join(OUTPUT_DIR, "DrugRepoBank.xlsx")
    print(f"Downloading DrugRepoBank dataset ...")
    try:
        req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(output, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {output}")
        return output
    except Exception as e:
        print(f"Download failed: {e}")
        return None


if __name__ == "__main__":
    print("=== DrugRepoBank: Search for 'metformin' ===")
    try:
        result = search_repurposing_candidates("metformin")
        print(f"Response (first 300 chars): {result[:300]}")
    except Exception as e:
        print(f"Search failed: {e}")

    print("\n=== Attempting database download ===")
    fpath = download_database()
    if not fpath:
        print(
            "\nVisit https://awi.cuhk.edu.cn/DrugRepoBank/php/index.php to access DrugRepoBank.\n"
            "The database contains:\n"
            "  - Drug name, SMILES, DrugBank ID\n"
            "  - Disease (new indication)\n"
            "  - Evidence type (experimental/computational/clinical)\n"
            "  - Source reference"
        )
