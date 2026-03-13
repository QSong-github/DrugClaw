"""
DGIdb - Drug-Gene Interaction Database
Category: Drug-centric | Type: DB | Subcategory: Drug-Target Interaction (DTI)
Link: https://www.dgidb.org/
Paper: https://www.nature.com/articles/nmeth.2689

DGIdb curates drug-gene interaction data and gene druggability information
from 40+ databases and literature.

API docs: https://dgidb.org/api
GraphQL endpoint: https://dgidb.org/api/graphql
No API key required.
"""

import urllib.request
import json


GRAPHQL_URL = "https://dgidb.org/api/graphql"


def run_query(query: str, variables: dict = None) -> dict:
    payload = {"query": query, "variables": variables or {}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL, data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def get_gene_interactions(gene_name: str) -> dict:
    """Get drug interactions for a specific gene."""
    query = """
    query GeneInteractions($name: String!) {
      genes(names: [$name]) {
        nodes {
          name
          interactions {
            drug { name conceptId }
            interactionTypes { type directionality }
            sources { sourceDbName }
          }
        }
      }
    }
    """
    return run_query(query, {"name": gene_name})


def get_drug_interactions(drug_name: str) -> dict:
    """Get gene interactions for a specific drug."""
    query = """
    query DrugInteractions($name: String!) {
      drugs(names: [$name]) {
        nodes {
          name
          conceptId
          interactions {
            gene { name }
            interactionTypes { type directionality }
          }
        }
      }
    }
    """
    return run_query(query, {"name": drug_name})


def get_druggable_genes(category: str = "CLINICALLY ACTIONABLE", limit: int = 5) -> dict:
    """Get genes with druggability annotations."""
    query = """
    query DruggableGenes($category: String!, $first: Int!) {
      geneCategories(name: $category) {
        nodes {
          name
          genes(first: $first) {
            nodes { name }
          }
        }
      }
    }
    """
    return run_query(query, {"category": category, "first": limit})


if __name__ == "__main__":
    print("=== DGIdb: Drug interactions for gene EGFR ===")
    result = get_gene_interactions("EGFR")
    nodes = result.get("data", {}).get("genes", {}).get("nodes", [])
    for node in nodes[:1]:
        print(f"  Gene: {node['name']}")
        for inter in node.get("interactions", [])[:5]:
            drug = inter.get("drug", {}).get("name")
            itype = [t.get("type") for t in inter.get("interactionTypes", [])]
            print(f"    Drug: {drug} | Types: {itype}")

    print("\n=== DGIdb: Gene targets for drug 'imatinib' ===")
    result = get_drug_interactions("imatinib")
    nodes = result.get("data", {}).get("drugs", {}).get("nodes", [])
    for node in nodes[:1]:
        print(f"  Drug: {node['name']} ({node.get('conceptId')})")
        for inter in node.get("interactions", [])[:5]:
            gene = inter.get("gene", {}).get("name")
            itype = [t.get("type") for t in inter.get("interactionTypes", [])]
            print(f"    Gene: {gene} | Types: {itype}")
