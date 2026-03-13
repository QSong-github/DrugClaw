"""
MedlinePlus Drug Info - Consumer-Oriented Drug Information
Category: Drug-centric | Type: DB | Subcategory: Drug Labeling/Info
Link: https://medlineplus.gov/druginformation.html

MedlinePlus provides plain-language, consumer-friendly drug information
maintained by the U.S. National Library of Medicine.

API docs: https://medlineplus.gov/connect/service.html
Web Service: https://wsearch.nlm.nih.gov/ws/query
No API key required.
"""

import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET


WS_BASE = "https://wsearch.nlm.nih.gov/ws/query"
MP_API_BASE = "https://connect.medlineplus.gov/service"


def search_medlineplus(query: str, count: int = 5) -> dict:
    """
    Search MedlinePlus drug information via the web service.
    Returns drug information summaries.
    """
    params = urllib.parse.urlencode({
        "db": "healthTopics",
        "term": query,
        "rettype": "brief",
        "retmax": count,
    })
    url = f"{WS_BASE}?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_drug_info_connect(drug_name: str) -> str:
    """
    Get drug information via MedlinePlus Connect API.
    Returns XML with drug information (NDC or RxCUI based).
    """
    params = urllib.parse.urlencode({
        "mainSearchCriteria.v.dn": drug_name,
        "informationRecipient": "PROV",
        "knowledgeResponseType": "application/json",
    })
    url = f"{MP_API_BASE}?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def search_drug_topics(drug_name: str) -> list:
    """Search MedlinePlus health topics for drug information."""
    params = urllib.parse.urlencode({
        "db": "healthTopics",
        "term": f"{drug_name} drug",
        "rettype": "brief",
    })
    url = f"{WS_BASE}?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    results = []
    for doc in data.get("nlmSearchResult", {}).get("list", {}).get("document", []):
        content = doc.get("content", [])
        title = next((c.get("#text") for c in content if c.get("@name") == "title"), "")
        snippet = next((c.get("#text") for c in content if c.get("@name") == "FullSummary"), "")[:200]
        url_item = next((c.get("#text") for c in content if c.get("@name") == "url"), "")
        results.append({"title": title, "snippet": snippet, "url": url_item})
    return results


if __name__ == "__main__":
    print("=== MedlinePlus: Search for 'metformin' ===")
    try:
        results = search_drug_topics("metformin")
        for r in results[:3]:
            print(f"  Title: {r['title']}")
            print(f"  URL: {r['url']}")
            print(f"  Summary: {r['snippet'][:150]}...")
            print()
    except Exception as e:
        print(f"  Error: {e}")

    print("=== MedlinePlus Connect: Drug info for 'aspirin' ===")
    try:
        result = get_drug_info_connect("aspirin")
        # Parse JSON or XML response
        try:
            data = json.loads(result)
            entries = data.get("feed", {}).get("entry", [])
            for entry in entries[:2]:
                title = entry.get("title", {}).get("_value", "")
                summary = str(entry.get("summary", {}).get("_value", ""))[:200]
                print(f"  Title: {title}")
                print(f"  Summary: {summary}...")
        except json.JSONDecodeError:
            print(f"  Response (first 300 chars): {result[:300]}")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Visit https://medlineplus.gov/druginformation.html")
