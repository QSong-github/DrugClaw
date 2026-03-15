"""
LiverTox - Drug-Induced Liver Injury Information
Category: Drug-centric | Type: DB | Subcategory: Drug Toxicity
Link: https://www.ncbi.nlm.nih.gov/books/NBK547852/

LiverTox is an NLM/NIH resource providing detailed, referenced information on
diagnosis, cause, frequency, patterns, and management of drug-induced liver injury.

Access method:
  1. NCBI Bookshelf API (public REST)
  2. NCBI E-utilities for full-text search
"""

import urllib.request
import urllib.parse
import json

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
LIVERTOX_BOOK_ID = "NBK548937"  # LiverTox main NBK ID


def search_livertox(drug_name: str) -> dict:
    """
    Search LiverTox via NCBI E-utilities.
    Returns book sections related to a specific drug.
    """
    # Search in bookshelf
    params = urllib.parse.urlencode({
        "db": "books",
        "term": f"{drug_name}[tiab] AND LiverTox[book]",
        "retmax": 5,
        "retmode": "json",
    })
    url = f"{NCBI_BASE}/esearch.fcgi?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    return data


def fetch_livertox_summary(uid: str) -> dict:
    """Fetch the summary for a specific LiverTox book section."""
    params = urllib.parse.urlencode({
        "db": "books",
        "id": uid,
        "retmode": "json",
    })
    url = f"{NCBI_BASE}/esummary.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_livertox_article_text(pmcid: str = None, uid: str = None) -> str:
    """
    Retrieve LiverTox text via NCBI efetch.
    Can use PMC article IDs or book UIDs.
    """
    if uid:
        params = urllib.parse.urlencode({
            "db": "books",
            "id": uid,
            "retmode": "text",
            "rettype": "abstract",
        })
        url = f"{NCBI_BASE}/efetch.fcgi?{params}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    return ""


if __name__ == "__main__":
    print("=== LiverTox: Search for 'acetaminophen' ===")
    result = search_livertox("acetaminophen")
    id_list = result.get("esearchresult", {}).get("idlist", [])
    count = result.get("esearchresult", {}).get("count", 0)
    print(f"Found {count} records | IDs: {id_list[:5]}")

    if id_list:
        uid = id_list[0]
        print(f"\n=== Summary for UID={uid} ===")
        summary = fetch_livertox_summary(uid)
        doc = summary.get("result", {}).get(str(uid), {})
        print(f"  Title: {doc.get('title')}")
        print(f"  Source: {doc.get('source')}")
        print(f"  PubDate: {doc.get('pubdate')}")

    print("\n=== LiverTox: Search for 'methotrexate' ===")
    result2 = search_livertox("methotrexate")
    id_list2 = result2.get("esearchresult", {}).get("idlist", [])
    print(f"Found {len(id_list2)} records: {id_list2}")
    print("\nFull database: https://www.ncbi.nlm.nih.gov/books/NBK547852/")
