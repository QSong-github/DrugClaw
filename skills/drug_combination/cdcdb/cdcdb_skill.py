"""
CDCDBSkill — Cancer Drug Combination Database (CDCDB).

Subcategory : drug_combination
Access mode : LOCAL_FILE

Config keys
-----------
csv_path  : str  path to CDCDB CSV/TSV file
              Expected columns: Drug1, Drug2, CancerType (or Cell), Outcome,
                                [Synergy_Score], [PMID]
delimiter : str  column delimiter (default: auto-detect from extension)
"""
from __future__ import annotations

import csv
import logging
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)


class CDCDBSkill(RAGSkill):
    """CDCDB — cancer drug combination experimental outcomes."""

    name = "CDCDB"
    subcategory = "drug_combination"
    resource_type = "Database"
    access_mode = AccessMode.LOCAL_FILE
    aim = "Cancer drug combination"
    data_range = "Cancer drug combination experimental outcomes"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._rows: List[Dict] = []
        self._drug_index: Dict[str, List[int]] = defaultdict(list)
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        path = self.config.get("csv_path", "")
        if not path or not os.path.exists(path):
            logger.warning("CDCDBSkill: file not found — set config['csv_path']")
            return
        delim = self.config.get("delimiter", "\t" if path.endswith(".tsv") else ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    d1 = (row.get("Drug1", "") or row.get("drug1", "") or
                           row.get("drug_a", "") or row.get("DrugA", "")).strip()
                    d2 = (row.get("Drug2", "") or row.get("drug2", "") or
                           row.get("drug_b", "") or row.get("DrugB", "")).strip()
                    if d1 and d2:
                        idx = len(self._rows)
                        self._rows.append(row)
                        self._drug_index[d1.lower()].append(idx)
                        self._drug_index[d2.lower()].append(idx)
            logger.info("CDCDB: loaded %d records", len(self._rows))
        except Exception as exc:
            logger.error("CDCDB: load failed — %s", exc)

    def is_available(self) -> bool:
        self._ensure_loaded()
        return bool(self._rows)

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 30,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        self._ensure_loaded()
        results: List[RetrievalResult] = []
        seen: set = set()

        for drug in entities.get("drug", []):
            for idx in self._drug_index.get(drug.lower(), []):
                if len(results) >= max_results or idx in seen:
                    continue
                seen.add(idx)
                row = self._rows[idx]
                d1 = (row.get("Drug1", "") or row.get("drug1", "") or
                       row.get("drug_a", "") or row.get("DrugA", "")).strip()
                d2 = (row.get("Drug2", "") or row.get("drug2", "") or
                       row.get("drug_b", "") or row.get("DrugB", "")).strip()
                cancer = (row.get("CancerType", "") or row.get("cancer_type", "") or
                          row.get("Cell", "") or row.get("cell_line", "")).strip()
                outcome = (row.get("Outcome", "") or row.get("Effect", "") or
                           row.get("result", "synergistic")).strip()
                results.append(RetrievalResult(
                    source_entity=d1,
                    source_type="drug",
                    target_entity=d2,
                    target_type="drug",
                    relationship=f"cancer_combination_{outcome.lower().replace(' ', '_')}",
                    weight=1.0,
                    source="CDCDB",
                    skill_category="drug_combination",
                    evidence_text=(
                        f"CDCDB: {d1} + {d2} → {outcome}"
                        + (f" in {cancer}" if cancer else "")
                    ),
                    metadata={
                        "cancer_type": cancer,
                        "outcome": outcome,
                        "pmid": row.get("PMID", ""),
                    },
                ))
        return results
