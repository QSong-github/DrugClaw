"""
DrugCentralSkill — DrugCentral Drug Information Resource.

Subcategory : drug_knowledgebase (Drug Knowledgebase)
Access mode : REST_API
Docs        : https://drugcentral.org/api

DrugCentral provides FDA-approved drug information including indications,
pharmacology, targets, and drug-drug interactions.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_BASE = "https://drugcentral.org/api"


class DrugCentralSkill(RAGSkill):
    """DrugCentral — FDA-approved drug information, indications, targets."""

    name = "DrugCentral"
    subcategory = "drug_knowledgebase"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "Drug information resource"
    data_range = "FDA-approved drug information, indications, targets"
    _implemented = True

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._timeout = int(self.config.get("timeout", 20))

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 20,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        results: List[RetrievalResult] = []
        for drug in entities.get("drug", []):
            if len(results) >= max_results:
                break
            results.extend(self._search_drug(drug, max_results - len(results)))
        return results

    def _search_drug(self, name: str, limit: int) -> List[RetrievalResult]:
        url = f"{_BASE}/data?name={urllib.parse.quote(name)}"
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:
            logger.debug("DrugCentral: search failed for '%s' — %s", name, exc)
            return []

        results: List[RetrievalResult] = []
        items = data if isinstance(data, list) else data.get("data", [])
        for item in items[:limit]:
            canonical = item.get("name", name)

            # Targets
            for tgt in item.get("targets", []):
                t_name = tgt.get("gene", "") or tgt.get("name", "")
                act = tgt.get("act_value", "targets").lower()
                if t_name:
                    results.append(RetrievalResult(
                        source_entity=canonical,
                        source_type="drug",
                        target_entity=t_name,
                        target_type="protein",
                        relationship=act.replace(" ", "_"),
                        weight=1.0,
                        source="DrugCentral",
                        skill_category="drug_knowledgebase",
                        evidence_text=f"DrugCentral: {canonical} {act} {t_name}",
                        metadata={"act_type": tgt.get("act_type", "")},
                    ))

            # Indications
            for ind in item.get("indications", []):
                ind_name = ind.get("disease", "")
                if ind_name:
                    results.append(RetrievalResult(
                        source_entity=canonical,
                        source_type="drug",
                        target_entity=ind_name,
                        target_type="disease",
                        relationship="indicated_for",
                        weight=1.0,
                        source="DrugCentral",
                        skill_category="drug_knowledgebase",
                        evidence_text=f"DrugCentral: {canonical} indicated for {ind_name}",
                        metadata={"umls_cui": ind.get("umls_cui", "")},
                    ))

        return results[:limit]
