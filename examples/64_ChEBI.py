"""
ChEBI - Chemical Entities of Biological Interest
Category: Drug-centric | Type: KG | Subcategory: Drug Ontology/Terminology
Link: https://www.ebi.ac.uk/chebi/
Paper: https://academic.oup.com/nar/article/54/D1/D1768/8349173

ChEBI is a freely available dictionary of molecular entities with ontological
classifications, focusing on small chemical compounds relevant to biology.

Access method: EBI REST API + OWL ontology download.
API docs: https://www.ebi.ac.uk/chebi/webServices.do
No API key required.
"""

import urllib.request
import urllib.parse
import json
import os


# ChEBI REST-style API (JSON)
CHEBI_API = "https://www.ebi.ac.uk/chebi/api/v1"
# Legacy SOAP-based API also available
CHEBI_WS = "https://www.ebi.ac.uk/webservices/chebi/2.0/webservice"


def search_chebi(query: str, max_results: int = 5) -> dict:
    """Search ChEBI by name or keyword."""
    params = urllib.parse.urlencode({
        "search": query,
        "searchCategory": "ALL",
        "maximumResults": max_results,
        "starsCategory": "ALL",
    })
    url = f"{CHEBI_API}/chebi/search?{params}"
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def get_chebi_entity(chebi_id: str) -> dict:
    """Get full information for a ChEBI entity by ID."""
    url = f"{CHEBI_API}/chebi/{chebi_id}"
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def download_chebi_owl():
    """Download the ChEBI ontology in OWL format (~200MB)."""
    os.makedirs("ChEBI", exist_ok=True)
    url = "https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.owl.gz"
    fname = "ChEBI/chebi.owl.gz"
    print(f"Downloading ChEBI OWL ontology (~200MB) ...")
    try:
        urllib.request.urlretrieve(url, fname)
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


def search_chebi_soap(query: str, max_results: int = 5) -> list:
    """
    Search ChEBI using SOAP web service (fallback if REST fails).
    Uses raw HTTP POST with minimal SOAP envelope.
    """
    soap_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:chebi="https://www.ebi.ac.uk/webservices/chebi">
  <soapenv:Body>
    <chebi:getLiteEntity>
      <chebi:search>{query}</chebi:search>
      <chebi:searchCategory>ALL</chebi:searchCategory>
      <chebi:maximumResults>{max_results}</chebi:maximumResults>
      <chebi:starsCategory>ALL</chebi:starsCategory>
    </chebi:getLiteEntity>
  </soapenv:Body>
</soapenv:Envelope>"""

    req = urllib.request.Request(
        CHEBI_WS,
        data=soap_body.encode("utf-8"),
        headers={
            "Content-Type": "text/xml; charset=UTF-8",
            "SOAPAction": "",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")


if __name__ == "__main__":
    print("=== ChEBI: Search 'aspirin' via REST API ===")
    try:
        result = search_chebi("aspirin", max_results=5)
        entities = result.get("results", []) if isinstance(result, dict) else result
        if isinstance(entities, list):
            for e in entities[:3]:
                cid = e.get("id", e.get("chebiId", ""))
                name = e.get("name", "")
                print(f"  ChEBI:{cid} - {name}")
        else:
            print(f"  Response: {str(result)[:200]}")
    except Exception as e:
        print(f"  REST API error: {e}")
        print("  Trying SOAP API ...")
        try:
            xml_result = search_chebi_soap("aspirin")
            import re
            # Extract chebiId and chebiAsciiName from XML
            ids = re.findall(r"<chebiId>(.*?)</chebiId>", xml_result)
            names = re.findall(r"<chebiAsciiName>(.*?)</chebiAsciiName>", xml_result)
            for cid, name in zip(ids[:3], names[:3]):
                print(f"  ChEBI:{cid} - {name}")
        except Exception as e2:
            print(f"  SOAP error: {e2}")

    print("\n=== ChEBI: Get entity CHEBI:15422 (adenosine triphosphate / ATP) ===")
    try:
        entity = get_chebi_entity("CHEBI:15422")
        print(f"  Name: {entity.get('name')}")
        print(f"  Formula: {entity.get('formula')}")
        print(f"  Charge: {entity.get('charge')}")
        print(f"  SMILES: {entity.get('smiles', '')[:60]}")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Visit https://www.ebi.ac.uk/chebi/ for interactive access.")
