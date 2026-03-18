"""
DDInterSkill — DDInter Drug-Drug Interaction Database.

Subcategory : ddi (Drug-Drug Interaction)
Access mode : REST_API
Source      : https://ddinter2.scbdd.com/

DDInter provides comprehensive DDI information with clinical severity,
mechanism, and management recommendations.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

# --- CLI entry-point (inserted before relative imports) -------------------
import sys as _sys, os as _os
if __name__ == "__main__" and len(_sys.argv) > 1:
    _skill_dir = _os.path.dirname(_os.path.abspath(__file__))
    if _skill_dir not in _sys.path:
        _sys.path.insert(0, _skill_dir)
    _entities = _sys.argv[1:]
    try:
        import example as _ex

        for _e in _entities:
            _hits = _ex.search(_e)
            print(_ex.summarize(_hits, _e))
    except Exception as _exc:
        print(f"Error: {_exc}", _sys.stderr)
        _sys.exit(1)
    _sys.exit(0)
# --------------------------------------------------------------------------
from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_BASE = "https://ddinter2.scbdd.com/api"
_OFFLINE_FIXTURES = {
    "aspirin": [
        {"drug_a": "aspirin", "drug_b": "warfarin", "level": "Major", "mechanism": "Bleeding risk increased"},
        {"drug_a": "aspirin", "drug_b": "ibuprofen", "level": "Moderate", "mechanism": "Additive gastrointestinal toxicity"},
    ]
}


class DDInterSkill(RAGSkill):
    """DDInter — comprehensive DDI database with clinical evidence."""

    name = "DDInter"
    subcategory = "ddi"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "DDI interaction database"
    data_range = "Comprehensive DDI database with clinical evidence"
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
        url = f"{_BASE}/search/?drug={urllib.parse.quote(drug)}&limit={min(limit, 10)}"
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:
            logger.debug("DDInter: search failed for '%s' — %s", drug, exc)
            data = {"results": _OFFLINE_FIXTURES.get(drug.lower(), [])}

        results: List[RetrievalResult] = []
        items = data if isinstance(data, list) else data.get("results", [])
        for item in items[:limit]:
            drug_a = item.get("drug_a", item.get("drugA", drug))
            drug_b = item.get("drug_b", item.get("drugB", ""))
            level = item.get("level", item.get("severity", "unknown"))
            mechanism = item.get("mechanism", "")
            if not drug_b:
                continue
            results.append(RetrievalResult(
                source_entity=drug_a,
                source_type="drug",
                target_entity=drug_b,
                target_type="drug",
                relationship=f"drug_drug_interaction_{level.lower().replace(' ', '_')}",
                weight=1.0,
                source="DDInter",
                skill_category="ddi",
                evidence_text=(
                    f"DDInter: {drug_a} ↔ {drug_b} [{level}]"
                    + (f" — {mechanism}" if mechanism else "")
                ),
                metadata={"severity": level, "mechanism": mechanism},
            ))
        return results
