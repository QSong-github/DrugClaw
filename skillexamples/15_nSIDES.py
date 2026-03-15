"""
nSIDES - EHR-Derived Drug Side Effects
Category: Drug-centric | Type: DB | Subcategory: Adverse Drug Reaction (ADR)
Link: https://nsides.io/
Paper: https://www.science.org/doi/10.1126/scitranslmed.3003377

nSIDES provides drug side effects and polypharmacy adverse events mined from
electronic health records using statistical disproportionality methods.

API: https://nsides.io/api/v1
"""

import urllib.request
import urllib.parse
import json
from typing import Union


BASE_URL = "https://nsides.io/api/v1"


# ── core helpers ────────────────────────────────────────────

def _get(url: str, timeout: int = 15) -> dict | list:
    """GET JSON from URL."""
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read())


def _rows(data) -> list[dict]:
    """Normalise API response → list[dict]."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("results", data.get("data", []))
    return []


# ── public API ──────────────────────────────────────────────

def search_concept(name: str) -> list[dict]:
    """Search OMOP concepts by name.

    Returns list of dicts with keys: concept_id, concept_name, domain_id, …
    """
    params = urllib.parse.urlencode({"q": name})
    return _rows(_get(f"{BASE_URL}/concepts?{params}"))


def get_drug_outcomes(drug_concept_id: int, limit: int = 10) -> list[dict]:
    """Get adverse outcomes for a drug (OMOP concept ID).

    Returns list of dicts with keys: outcome_concept_id,
    outcome_concept_name, prr (proportional reporting ratio), …
    """
    params = urllib.parse.urlencode({"drug": drug_concept_id, "limit": limit})
    return _rows(_get(f"{BASE_URL}/drug/{drug_concept_id}/outcomes?{params}"))


def get_outcome_drugs(outcome_concept_id: int, limit: int = 10) -> list[dict]:
    """Get drugs linked to a specific adverse outcome (OMOP concept ID).

    Returns list of dicts with keys: drug_concept_id, drug_concept_name, prr, …
    """
    params = urllib.parse.urlencode({"limit": limit})
    return _rows(_get(f"{BASE_URL}/outcome/{outcome_concept_id}/drugs?{params}"))


# ── batch / convenience ────────────────────────────────────

def query(entity: str, limit: int = 10) -> dict:
    """Query a single drug name → concept info + top adverse outcomes.

    Returns {"entity", "concepts": [...], "outcomes": {...concept_id: [...]}}
    """
    concepts = search_concept(entity)
    outcomes = {}
    for c in concepts:
        cid = c.get("concept_id")
        domain = (c.get("domain_id") or "").lower()
        if cid and domain in ("drug", "ingredient", ""):
            try:
                outcomes[cid] = get_drug_outcomes(int(cid), limit=limit)
            except Exception:
                outcomes[cid] = []
    return {"entity": entity, "concepts": concepts, "outcomes": outcomes}


def query_batch(entities: list[str], limit: int = 10) -> list[dict]:
    """Query a list of drug names → list of query() results."""
    return [query(e, limit=limit) for e in entities]


def summarize(result: dict) -> str:
    """Compact text summary from a single query() result."""
    lines = [f"Entity: {result['entity']}"]
    for c in result.get("concepts", []):
        cid = c.get("concept_id", "?")
        cname = c.get("concept_name", "?")
        lines.append(f"  Concept {cid}: {cname}")
        outs = result.get("outcomes", {}).get(cid, [])
        if outs:
            for o in outs[:5]:
                name = o.get("outcome_concept_name", o.get("concept_name", "?"))
                prr = o.get("prr", "")
                extra = f" (PRR={prr})" if prr else ""
                lines.append(f"    - {name}{extra}")
        else:
            lines.append("    (no outcomes)")
    if not result.get("concepts"):
        lines.append("  (no concepts found)")
    return "\n".join(lines)


# ── usage example ──────────────────────────────────────────

if __name__ == "__main__":
    # --- single entity ---
    print("=== Single query: aspirin ===")
    try:
        res = query("aspirin", limit=5)
        print(summarize(res))
    except Exception as e:
        print(f"  Error: {e}")

    # --- batch query ---
    print("\n=== Batch query: [ibuprofen, metformin] ===")
    try:
        results = query_batch(["ibuprofen", "metformin"], limit=3)
        for r in results:
            print(summarize(r))
            print()
    except Exception as e:
        print(f"  Error: {e}")