"""
OpenFDASkill — FDA Drug Labels via openFDA REST API.

Subcategory : drug_labeling (Drug Labeling/Info)
Access mode : REST_API
Docs        : https://open.fda.gov/apis/drug/label/

Searches FDA drug labels for adverse reactions, indications, warnings,
and mechanism-of-action data.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_BASE = "https://api.fda.gov/drug/label.json"
_FIELDS = [
    ("adverse_reactions", "has_adverse_reaction"),
    ("indications_and_usage", "indicated_for"),
    ("warnings", "has_warning"),
    ("mechanism_of_action", "has_mechanism"),
    ("drug_interactions", "interacts_with"),
]


class OpenFDASkill(RAGSkill):
    """openFDA Human Drug label search."""

    name = "openFDA Human Drug"
    subcategory = "drug_labeling"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "FDA drug label search"
    data_range = "Structured FDA drug labels (adverse events, dosing, warnings)"
    _implemented = True

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._api_key = self.config.get("api_key", "")
        self._timeout = int(self.config.get("timeout", 15))

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
            results.extend(self._search_label(drug, max_results - len(results)))
        return results

    def _search_label(self, drug: str, limit: int) -> List[RetrievalResult]:
        params = {
            "search": f'openfda.brand_name:"{drug}"+openfda.generic_name:"{drug}"',
            "limit": min(limit, 5),
        }
        if self._api_key:
            params["api_key"] = self._api_key
        url = _BASE + "?" + urllib.parse.urlencode(params)

        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:
            logger.debug("OpenFDA: label search failed for '%s' — %s", drug, exc)
            return []

        results: List[RetrievalResult] = []
        for label in data.get("results", [])[:limit]:
            brand_name = label.get("openfda", {}).get("brand_name", [drug])[0]
            for field, relationship in _FIELDS:
                text_list = label.get(field, [])
                if not text_list:
                    continue
                text = text_list[0][:500] if isinstance(text_list, list) else str(text_list)[:500]
                results.append(RetrievalResult(
                    source_entity=brand_name,
                    source_type="drug",
                    target_entity=field.replace("_", " "),
                    target_type="label_section",
                    relationship=relationship,
                    weight=1.0,
                    source="openFDA Human Drug",
                    skill_category="drug_labeling",
                    evidence_text=text,
                    metadata={"field": field},
                ))
        return results
