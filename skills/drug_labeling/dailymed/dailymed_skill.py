"""
DailyMedSkill — NIH DailyMed Official Drug Labels.

Subcategory : drug_labeling
Access mode : REST_API
Docs        : https://dailymed.nlm.nih.gov/dailymed/webservices-help/v2/

DailyMed provides the most comprehensive, up-to-date, and publicly available
source of FDA-approved drug labeling.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_BASE = "https://dailymed.nlm.nih.gov/dailymed/services/v2"


class DailyMedSkill(RAGSkill):
    """DailyMed official FDA-approved drug labels (NIH)."""

    name = "DailyMed"
    subcategory = "drug_labeling"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "Official drug labels (NIH)"
    data_range = "FDA-approved drug labeling from NIH DailyMed"
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
            results.extend(self._search(drug, max_results - len(results)))
        return results

    def _search(self, drug: str, limit: int) -> List[RetrievalResult]:
        url = (
            f"{_BASE}/spls.json"
            f"?drug_name={urllib.parse.quote(drug)}&pagesize={min(limit, 5)}"
        )
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:
            logger.debug("DailyMed: search failed for '%s' — %s", drug, exc)
            return []

        results: List[RetrievalResult] = []
        for item in data.get("data", [])[:limit]:
            title = item.get("title", drug)
            set_id = item.get("setid", "")
            results.append(RetrievalResult(
                source_entity=drug,
                source_type="drug",
                target_entity=title,
                target_type="drug_label",
                relationship="has_official_label",
                weight=1.0,
                source="DailyMed",
                skill_category="drug_labeling",
                evidence_text=f"DailyMed label: {title}",
                sources=[f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={set_id}"],
                metadata={"set_id": set_id, "published": item.get("published", "")},
            ))
        return results
