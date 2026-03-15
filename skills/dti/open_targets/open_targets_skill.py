"""
OpenTargetsSkill — Open Targets Platform via GraphQL API.

Subcategory : dti (Drug-Target Interaction)
Access mode : REST_API (GraphQL)
Docs        : https://platform.opentargets.org/

Open Targets Platform provides evidence linking drugs to targets to diseases,
integrating genetic, genomic, and chemical data.
"""
from __future__ import annotations

import json
import logging
import urllib.request
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_GRAPHQL = "https://api.platform.opentargets.org/api/v4/graphql"


class OpenTargetsSkill(RAGSkill):
    """
    Open Targets Platform — drug-target evidence scores.

    Retrieves:
      - Drug → target associations with evidence scores
      - Target → disease associations
      - Drug mechanisms of action

    Config keys
    -----------
    timeout : int  (default 25)
    """

    name = "Open Targets Platform"
    subcategory = "dti"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "Drug-target evidence"
    data_range = "Curated + ML drug-target evidence scores"
    _implemented = True

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._timeout = int(self.config.get("timeout", 25))

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 20,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        drugs = entities.get("drug", [])
        results: List[RetrievalResult] = []

        for drug in drugs:
            if len(results) >= max_results:
                break
            results.extend(
                self._search_drug(drug, max_results - len(results))
            )

        return results

    def _search_drug(self, drug_name: str, limit: int) -> List[RetrievalResult]:
        """Search for drug and retrieve its targets via Open Targets GraphQL."""
        # Step 1: search for drug by name to get ChEMBL ID
        search_query = """
        {
          search(queryString: "%s", entityNames: ["drug"]) {
            hits {
              id
              name
              entity
            }
          }
        }
        """ % drug_name.replace('"', '')

        chembl_id = self._graphql(search_query, ["search", "hits"])
        if not chembl_id:
            return []
        drug_id = chembl_id[0].get("id", "")
        canonical_name = chembl_id[0].get("name", drug_name)
        if not drug_id:
            return []

        # Step 2: get drug's known targets (mechanisms of action)
        moa_query = """
        {
          drug(chemblId: "%s") {
            id
            name
            mechanismsOfAction {
              rows {
                actionType
                targets {
                  id
                  approvedName
                  approvedSymbol
                }
              }
            }
            linkedTargets {
              rows {
                id
                approvedName
                approvedSymbol
              }
            }
          }
        }
        """ % drug_id

        moa_data = self._graphql(moa_query, ["drug"])
        if not moa_data:
            return []
        drug_info = moa_data[0] if isinstance(moa_data, list) else moa_data

        results: List[RetrievalResult] = []

        # Mechanisms of action
        for row in (drug_info.get("mechanismsOfAction") or {}).get("rows", []):
            action_type = row.get("actionType", "targets").lower().replace(" ", "_")
            for tgt in row.get("targets", []):
                if len(results) >= limit:
                    break
                tgt_name = tgt.get("approvedName") or tgt.get("approvedSymbol", "")
                if not tgt_name:
                    continue
                results.append(RetrievalResult(
                    source_entity=canonical_name,
                    source_type="drug",
                    target_entity=tgt_name,
                    target_type="protein",
                    relationship=action_type,
                    weight=1.0,
                    source="Open Targets Platform",
                    skill_category="dti",
                    evidence_text=(
                        f"{canonical_name} {action_type} {tgt_name} "
                        f"(Open Targets MoA)"
                    ),
                    metadata={
                        "chembl_id": drug_id,
                        "target_id": tgt.get("id", ""),
                        "gene_symbol": tgt.get("approvedSymbol", ""),
                    },
                ))

        # Linked targets (broader set)
        for tgt in (drug_info.get("linkedTargets") or {}).get("rows", []):
            if len(results) >= limit:
                break
            tgt_name = tgt.get("approvedName") or tgt.get("approvedSymbol", "")
            if not tgt_name:
                continue
            # Avoid duplicates
            if any(r.target_entity == tgt_name for r in results):
                continue
            results.append(RetrievalResult(
                source_entity=canonical_name,
                source_type="drug",
                target_entity=tgt_name,
                target_type="protein",
                relationship="linked_target",
                weight=1.0,
                source="Open Targets Platform",
                skill_category="dti",
                evidence_text=f"{canonical_name} linked to target {tgt_name}",
                metadata={
                    "chembl_id": drug_id,
                    "target_id": tgt.get("id", ""),
                    "gene_symbol": tgt.get("approvedSymbol", ""),
                },
            ))

        return results

    def _graphql(self, query: str, path: List[str]):
        """Execute a GraphQL query and traverse path in the result."""
        try:
            payload = json.dumps({"query": query}).encode()
            req = urllib.request.Request(
                _GRAPHQL,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:
            logger.debug("OpenTargets: GraphQL failed — %s", exc)
            return None

        node = data.get("data", {})
        for key in path:
            if isinstance(node, dict):
                node = node.get(key)
            elif isinstance(node, list) and node:
                node = node[0].get(key) if isinstance(node[0], dict) else None
            else:
                return None
        return node
