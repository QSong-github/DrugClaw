"""
Open Targets Platform - Drug-Target Association for Disease Therapy
Category: Drug-centric | Type: DB | Subcategory: Drug-Target Interaction (DTI)
Link: https://platform.opentargets.org/
Paper: https://doi.org/10.1093/nar/gkac1046

Open Targets integrates genetic, genomic, and chemical data to identify and
prioritize drug targets for human diseases.

API docs: https://api.platform.opentargets.org/api/v4/graphql/browser
GraphQL endpoint: https://api.platform.opentargets.org/api/v4/graphql
No API key required.
"""

import urllib.request
import json


GRAPHQL_URL = "https://api.platform.opentargets.org/api/v4/graphql"


def run_query(query: str, variables: dict = None) -> dict:
    payload = {"query": query, "variables": variables or {}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL, data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def get_target_info(ensembl_id: str) -> dict:
    """Get target information by Ensembl gene ID."""
    query = """
    query TargetInfo($ensemblId: String!) {
      target(ensemblId: $ensemblId) {
        id
        approvedName
        approvedSymbol
        biotype
        associatedDiseases(page: {index: 0, size: 3}) {
          rows {
            disease { name }
            score
          }
        }
      }
    }
    """
    return run_query(query, {"ensemblId": ensembl_id})


def get_drug_info(chembl_id: str) -> dict:
    """Get drug information by ChEMBL drug ID."""
    query = """
    query DrugInfo($chemblId: String!) {
      drug(chemblId: $chemblId) {
        id
        name
        drugType
        maximumClinicalTrialPhase
        indications(page: {index: 0, size: 3}) {
          rows {
            disease { name }
            maxPhaseForIndication
          }
        }
      }
    }
    """
    return run_query(query, {"chemblId": chembl_id})


def search_targets(term: str) -> dict:
    """Search for targets by name."""
    query = """
    query Search($queryString: String!) {
      search(queryString: $queryString, entityNames: ["target"], page: {index: 0, size: 5}) {
        hits {
          id
          name
          entity
        }
      }
    }
    """
    return run_query(query, {"queryString": term})


if __name__ == "__main__":
    print("=== Open Targets: EGFR (ENSG00000146648) ===")
    result = get_target_info("ENSG00000146648")
    target = result["data"]["target"]
    print(f"  Symbol: {target['approvedSymbol']}")
    print(f"  Name: {target['approvedName']}")
    print(f"  Biotype: {target['biotype']}")
    print("  Associated diseases:")
    for row in target["associatedDiseases"]["rows"]:
        print(f"    {row['disease']['name']}: score={row['score']:.3f}")

    print("\n=== Open Targets: Imatinib (CHEMBL941) ===")
    result = get_drug_info("CHEMBL941")
    drug = result["data"]["drug"]
    print(f"  Name: {drug['name']}")
    print(f"  Type: {drug['drugType']}")
    print(f"  Max trial phase: {drug['maximumClinicalTrialPhase']}")
    print("  Indications:")
    for row in drug["indications"]["rows"]:
        print(f"    {row['disease']['name']}: phase={row['maxPhaseForIndication']}")

    print("\n=== Open Targets: Search 'BRCA1' ===")
    result = search_targets("BRCA1")
    for hit in result["data"]["search"]["hits"]:
        print(f"  {hit['id']}: {hit['name']} ({hit['entity']})")
