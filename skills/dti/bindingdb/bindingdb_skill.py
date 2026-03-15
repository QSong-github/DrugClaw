"""
BindingDBSkill — Drug-Target Binding Affinity via BindingDB REST API.

Subcategory : dti (Drug-Target Interaction)
Access mode : REST_API
Docs        : https://www.bindingdb.org/bind/BDBService.jsonp
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_BASE = "https://www.bindingdb.org/axis2/services/BDBService"


class BindingDBSkill(RAGSkill):
    """
    BindingDB binding affinity database.

    Retrieves experimentally measured binding constants (Ki, Kd, IC50)
    linking drugs/ligands to protein targets.

    Config keys
    -----------
    timeout : int  (default 20)
    """

    name = "BindingDB"
    subcategory = "dti"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "Binding affinity data"
    data_range = "Experimentally measured binding constants (Ki, Kd, IC50)"
    _implemented = True

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._timeout = int(self.config.get("timeout", 20))

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 30,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        drugs = entities.get("drug", [])
        results: List[RetrievalResult] = []

        for drug in drugs:
            if len(results) >= max_results:
                break
            results.extend(self._search_by_name(drug, max_results - len(results)))

        return results

    def _search_by_name(self, drug: str, limit: int) -> List[RetrievalResult]:
        url = (
            f"{_BASE}/getLigandsByName"
            f"?ligandname={urllib.parse.quote(drug)}"
            f"&response=json"
        )
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:
            logger.debug("BindingDB: search failed for '%s' — %s", drug, exc)
            return []

        results: List[RetrievalResult] = []
        affinities = data.get("affinities", []) or []
        for aff in affinities[:limit]:
            target = aff.get("target_name", "") or aff.get("uniprot_id", "")
            affinity_type = aff.get("affinity_type", "binding")
            value = aff.get("affinity", "")
            if not target:
                continue
            results.append(RetrievalResult(
                source_entity=drug,
                source_type="drug",
                target_entity=target,
                target_type="protein",
                relationship=f"binds_{affinity_type.lower().replace(' ', '_')}",
                weight=1.0,
                source="BindingDB",
                skill_category="dti",
                evidence_text=(
                    f"{drug} {affinity_type}={value} nM against {target}"
                    if value else f"{drug} binds {target}"
                ),
                metadata={
                    "affinity_type": affinity_type,
                    "affinity_value": value,
                    "uniprot_id": aff.get("uniprot_id", ""),
                    "pmid": aff.get("pmid", ""),
                },
            ))
        return results
