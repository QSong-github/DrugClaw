"""
MedlinePlusSkill — NLM MedlinePlus Drug Information.

Subcategory : drug_labeling
Access mode : REST_API
Docs        : https://medlineplus.gov/druginformation.html
              https://wsearch.nlm.nih.gov/ws/query?db=healthTopics

NLM MedlinePlus provides consumer health information about drugs,
diseases, and medical conditions.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://wsearch.nlm.nih.gov/ws/query"


class MedlinePlusSkill(RAGSkill):
    """NIH MedlinePlus drug information for patients and clinicians."""

    name = "MedlinePlus Drug Info"
    subcategory = "drug_labeling"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "Patient drug information"
    data_range = "NIH MedlinePlus drug information for patients and clinicians"
    _implemented = True

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._timeout = int(self.config.get("timeout", 20))

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 10,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        results: List[RetrievalResult] = []
        for drug in entities.get("drug", []):
            if len(results) >= max_results:
                break
            results.extend(self._search(drug, max_results - len(results)))
        return results

    def _search(self, drug: str, limit: int) -> List[RetrievalResult]:
        params = {
            "db": "healthTopics",
            "term": f'"{drug}" drug',
            "retmax": min(limit, 5),
            "rettype": "topic",
        }
        url = _SEARCH_URL + "?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                content = resp.read().decode()
        except Exception as exc:
            logger.debug("MedlinePlus: search failed for '%s' — %s", drug, exc)
            return []

        results: List[RetrievalResult] = []
        try:
            root = ET.fromstring(content)
            for doc in root.iter("document"):
                url_attr = doc.get("url", "")
                title = ""
                snippet = ""
                for content_elem in doc.iter("content"):
                    name = content_elem.get("name", "")
                    if name == "title":
                        title = content_elem.text or ""
                    elif name == "snippet":
                        snippet = (content_elem.text or "")[:300]
                if title:
                    results.append(RetrievalResult(
                        source_entity=drug,
                        source_type="drug",
                        target_entity=title,
                        target_type="health_topic",
                        relationship="has_health_topic",
                        weight=1.0,
                        source="MedlinePlus Drug Info",
                        skill_category="drug_labeling",
                        evidence_text=snippet or title,
                        sources=[url_attr] if url_attr else [],
                    ))
        except ET.ParseError:
            pass
        return results[:limit]
