"""
DTCSkill — Drug Target Commons (DTC) 2.0.

Subcategory : dti (Drug-Target Interaction)
Access mode : LOCAL_FILE (CSV download from drugtargetcommons.fimm.fi)
Download    : https://drugtargetcommons.fimm.fi/static/Excell_files/DTC_data.csv

DTC is a community-curated open resource for drug-target bioactivity data.
"""
from __future__ import annotations

import csv
import logging
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)


class DTCSkill(RAGSkill):
    """Drug Target Commons — community-curated drug-target bioactivity."""

    name = "DTC"
    subcategory = "dti"
    resource_type = "Database"
    access_mode = AccessMode.LOCAL_FILE
    aim = "Drug target commons"
    data_range = "Community-curated drug-target bioactivity database"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._drug_index: Dict[str, List[Dict]] = defaultdict(list)
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        path = self.config.get("csv_path", "")
        if not path or not os.path.exists(path):
            logger.warning("DTCSkill: file not found — set config['csv_path']")
            return
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh):
                    drug = row.get("compound_name", "") or row.get("drug_name", "")
                    if drug:
                        self._drug_index[drug.lower()].append(row)
            logger.info("DTC: loaded %d drugs", len(self._drug_index))
        except Exception as exc:
            logger.error("DTC: load failed — %s", exc)

    def is_available(self) -> bool:
        self._ensure_loaded()
        return bool(self._drug_index)

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 30,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        self._ensure_loaded()
        results: List[RetrievalResult] = []

        for drug in entities.get("drug", []):
            for row in self._drug_index.get(drug.lower(), []):
                if len(results) >= max_results:
                    break
                target = row.get("gene_name", "") or row.get("target_name", "")
                if not target:
                    continue
                act_type = row.get("standard_type", "bioactivity")
                act_val = row.get("standard_value", "")
                results.append(RetrievalResult(
                    source_entity=drug,
                    source_type="drug",
                    target_entity=target,
                    target_type="protein",
                    relationship=f"has_{act_type.lower()}_activity",
                    weight=1.0,
                    source="DTC",
                    skill_category="dti",
                    evidence_text=f"DTC: {drug} {act_type}={act_val} against {target}",
                    metadata={
                        "standard_type": act_type,
                        "standard_value": act_val,
                        "uniprot": row.get("wildtype_or_mutant_acc", ""),
                    },
                ))
        return results
