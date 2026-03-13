"""
Drugs.com - Consumer Drug Information and Interactions
Category: Drug-centric | Type: DB | Subcategory: Drug Knowledgebase
Link: https://www.drugs.com/

Drugs.com provides a comprehensive consumer drug information database with
drug descriptions, side effects, interactions, dosage guidelines, and reviews.

Access method: Web scraping (terms of service permitting) or structured URL patterns.
Note: Drugs.com does not offer a public API. For structured drug info, use
openFDA (05_openFDA_Human_Drug.py) or DrugBank (07_DrugBank.py).
"""

import urllib.request
import urllib.parse
import re
import html


BASE_URL = "https://www.drugs.com"


def get_drug_info_page(drug_name: str) -> str:
    """Fetch the Drugs.com drug information page for a given drug."""
    # Drugs.com uses lowercase hyphenated drug names
    slug = drug_name.lower().replace(" ", "-")
    url = f"{BASE_URL}/{slug}.html"
    print(f"GET {url}")
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; research)"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_drug_details(html_content: str) -> dict:
    """Extract key drug information from the HTML page."""
    details = {}

    # Extract title
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html_content, re.IGNORECASE | re.DOTALL)
    if title_match:
        details["title"] = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()

    # Extract description/uses
    uses_match = re.search(
        r"<h2[^>]*>.*?Uses.*?</h2>\s*(.*?)<h2",
        html_content, re.IGNORECASE | re.DOTALL
    )
    if uses_match:
        text = html.unescape(re.sub(r"<[^>]+>", " ", uses_match.group(1))).strip()
        details["uses"] = " ".join(text.split())[:300]

    return details


def check_drug_interactions(drugs: list) -> str:
    """
    Check drug interactions via Drugs.com interaction checker.
    Returns the URL for interactive checking.
    """
    params = urllib.parse.urlencode({"q[]": drugs}, doseq=True)
    url = f"{BASE_URL}/interactions-check.php?{params}"
    return url


if __name__ == "__main__":
    drug = "aspirin"
    print(f"=== Drugs.com: Information for '{drug}' ===")
    try:
        content = get_drug_info_page(drug)
        details = extract_drug_details(content)
        for k, v in details.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Visit {BASE_URL}/{drug}.html for drug information.")

    print("\n=== Drug Interaction Check URL ===")
    url = check_drug_interactions(["aspirin", "warfarin"])
    print(f"  {url}")
    print("  Visit this URL to check interactions interactively.")
