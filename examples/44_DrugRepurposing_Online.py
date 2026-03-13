"""
DrugRepurposing Online - Drug Repurposing Resource Aggregation
Category: Drug-centric | Type: DB | Subcategory: Drug Repurposing
Link: https://drugrepurposing.info/

DrugRepurposing.info aggregates computational and experimental drug repurposing
results from multiple sources with a searchable interface.

Access method: Web interface only — no public API available.
"""

import urllib.request
import urllib.parse
import re


BASE_URL = "https://drugrepurposing.info"


def get_homepage():
    """Fetch and confirm connectivity to DrugRepurposing.info."""
    req = urllib.request.Request(
        BASE_URL, headers={"User-Agent": "Mozilla/5.0 (compatible; research)"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    return html


def search_drug(drug_name: str) -> str:
    """
    Search for a drug on DrugRepurposing.info.
    Returns the raw HTML response.
    """
    params = urllib.parse.urlencode({"q": drug_name})
    url = f"{BASE_URL}/search?{params}"
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


if __name__ == "__main__":
    print("=== DrugRepurposing.info: Checking connectivity ===")
    try:
        html = get_homepage()
        print(f"Homepage loaded ({len(html)} bytes).")
        if "repurpos" in html.lower():
            print("Confirmed: Drug repurposing content detected.")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== Search for 'aspirin' ===")
    try:
        result = search_drug("aspirin")
        # Extract any meaningful text (simple approach)
        text = re.sub(r"<[^>]+>", " ", result)
        text = re.sub(r"\s+", " ", text).strip()
        print(f"Response snippet: {text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Visit {BASE_URL} to search the database interactively.")

    print("\nNote: DrugRepurposing.info is a web-only resource.")
    print("For programmatic access to drug repurposing data, consider:")
    print("  - Drug Repurposing Hub (29_Drug_Repurposing_Hub.py) - has downloadable data")
    print("  - RepoDB (02_RepoDB.py) - has downloadable CSV")
    print("  - DrugRepoBank (42_DrugRepoBank.py)")
