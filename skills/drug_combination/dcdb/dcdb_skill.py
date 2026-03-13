"""
DCDBSkill — Drug Combination Database (DCDB).

Subcategory : drug_combination
Access mode : LOCAL_FILE
Source      : http://www.cls.zju.edu.cn/dcdb/

DCDB is a resource of approved drug combinations for clinical use, annotated
with therapeutic indications, component drugs, and disease targets.

Config keys
-----------
csv_path  : str  path to DCDB CSV/TSV file
              Expected columns: Drug1 (or Component1), Drug2 (or Component2),
                                Disease (or Indication), [Mechanism], [PMID]
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


class DCDBSkill(RAGSkill):
    """DCDB — Drug Combination Database with efficacy information."""

    name = "DCDB"
    subcategory = "drug_combination"
    resource_type = "Database"
    access_mode = AccessMode.LOCAL_FILE
    aim = "Drug combination reference"
    data_range = "Drug Combination Database with efficacy information"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._rows: List[Dict] = []
        self._drug_index: Dict[str, List[int]] = defaultdict(list)
        self._disease_index: Dict[str, List[int]] = defaultdict(list)
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        path = self.config.get("csv_path", "")
        if not path or not os.path.exists(path):
            logger.warning(
                "DCDBSkill: file not found. "
                "Download from http://www.cls.zju.edu.cn/dcdb/ "
                "and set config['csv_path']."
            )
            return
        delim = self.config.get("delimiter", "\t" if path.endswith(".tsv") else ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    d1 = (row.get("Drug1", "") or row.get("Component1", "") or
                           row.get("drug1", "") or row.get("drug_a", "")).strip()
                    d2 = (row.get("Drug2", "") or row.get("Component2", "") or
                           row.get("drug2", "") or row.get("drug_b", "")).strip()
                    disease = (row.get("Disease", "") or row.get("Indication", "") or
                               row.get("disease", "")).strip()
                    if d1 and d2:
                        idx = len(self._rows)
                        self._rows.append(row)
                        self._drug_index[d1.lower()].append(idx)
                        self._drug_index[d2.lower()].append(idx)
                        if disease:
                            self._disease_index[disease.lower()].append(idx)
            logger.info("DCDB: loaded %d drug combination records", len(self._rows))
        except Exception as exc:
            logger.error("DCDB: load failed — %s", exc)

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

        def _add(idxs):
            for idx in idxs:
                if len(results) >= max_results or idx in seen:
                    return
                seen.add(idx)
                row = self._rows[idx]
                d1 = (row.get("Drug1", "") or row.get("Component1", "") or
                       row.get("drug1", "") or row.get("drug_a", "")).strip()
                d2 = (row.get("Drug2", "") or row.get("Component2", "") or
                       row.get("drug2", "") or row.get("drug_b", "")).strip()
                disease = (row.get("Disease", "") or row.get("Indication", "") or
                           row.get("disease", "")).strip()
                mech = row.get("Mechanism", "") or row.get("mechanism", "")
                results.append(RetrievalResult(
                    source_entity=d1,
                    source_type="drug",
                    target_entity=d2,
                    target_type="drug",
                    relationship="approved_drug_combination",
                    weight=1.0,
                    source="DCDB",
                    skill_category="drug_combination",
                    evidence_text=(
                        f"DCDB: {d1} + {d2}"
                        + (f" for {disease}" if disease else "")
                        + (f" — {mech}" if mech else "")
                    ),
                    metadata={
                        "indication": disease,
                        "mechanism": mech,
                        "pmid": row.get("PMID", ""),
                    },
                ))

        for drug in entities.get("drug", []):
            _add(self._drug_index.get(drug.lower(), []))
        for disease in entities.get("disease", []):
            _add(self._disease_index.get(disease.lower(), []))
        return results
