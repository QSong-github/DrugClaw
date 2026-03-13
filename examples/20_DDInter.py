"""
DDInter - Drug-Drug Interaction Database
Category: Drug-centric | Type: DB | Subcategory: Drug-Drug Interaction (DDI)
Link: https://ddinter2.scbdd.com/server/search/
Paper: https://academic.oup.com/nar/article/53/D1/D1356/7740584

DDInter is a comprehensive DDI database providing interaction severity,
mechanisms, and clinical management recommendations.

Access method: Web interface query via the DDInter2 REST API.
"""

import urllib.request
import urllib.parse
import json


BASE_URL = "https://ddinter2.scbdd.com"


def search_ddi_by_drug(drug_name: str) -> dict:
    """
    Search for DDIs involving a specific drug name.
    Returns interaction records from the DDInter2 search endpoint.
    """
    params = urllib.parse.urlencode({"drugname": drug_name, "format": "json"})
    url = f"{BASE_URL}/server/search/?{params}"
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read()
        return json.loads(content)


def download_ddi_dataset():
    """
    Download the DDInter full dataset.
    The database is available for download from the website.
    """
    import os
    os.makedirs("DDInter", exist_ok=True)
    download_url = "https://ddinter2.scbdd.com/static/file/DDInter2_database.xlsx"
    output = "DDInter/DDInter2_database.xlsx"
    print(f"Downloading DDInter2 dataset ...")
    try:
        req = urllib.request.Request(download_url,
                                     headers={"User-Agent": "Mozilla/5.0"})
        urllib.request.urlretrieve(download_url, output)
        print(f"Saved to {output}")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


if __name__ == "__main__":
    print("=== DDInter: Search for 'aspirin' ===")
    try:
        result = search_ddi_by_drug("aspirin")
        items = result if isinstance(result, list) else result.get("results", [])
        print(f"Found {len(items)} interactions")
        for item in items[:5]:
            print(f"  Drug1: {item.get('drug1_name')} | "
                  f"Drug2: {item.get('drug2_name')} | "
                  f"Level: {item.get('level')}")
    except Exception as e:
        print(f"API query failed: {e}")

    print("\n=== Downloading DDInter2 dataset ===")
    success = download_ddi_dataset()
    if not success:
        print("Visit https://ddinter2.scbdd.com/server/search/ for manual access.")
