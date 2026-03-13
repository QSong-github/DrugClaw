"""
AskAPatientSkill — AskAPatient Drug Experience Reports.

Subcategory : drug_review
Access mode : DATASET (local CSV)
Source      : https://www.askapatient.com / Kaggle mirror

AskAPatient contains patient-reported drug experiences including side effects,
effectiveness, and satisfaction.  No public REST API; use local dataset.

Config keys
-----------
csv_path  : str  path to askapatient CSV file
              Expected columns: drug (or Drug), condition (or Condition),
                                sideeffects (or SideEffects, side_effects),
                                effectiveness (or Effectiveness), rating
delimiter : str  column delimiter (default: ",")
"""
from __future__ import annotations

import csv
import logging
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ...base import DatasetRAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)


class AskAPatientSkill(DatasetRAGSkill):
    """AskAPatient — patient-reported drug experiences."""

    name = "askapatient"
    subcategory = "drug_review"
    resource_type = "Dataset"
    access_mode = AccessMode.DATASET
    aim = "Patient experience reports"
    data_range = "Patient-reported drug experiences from AskAPatient.com"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._rows: List[Dict] = []
        self._drug_index: Dict[str, List[int]] = defaultdict(list)

    def _load(self) -> None:
        path = self.config.get("csv_path", "")
        if not path or not os.path.exists(path):
            logger.warning(
                "AskAPatientSkill: file not found. "
                "Set config['csv_path'] to the AskAPatient dataset CSV."
            )
            return
        delim = self.config.get("delimiter", ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    drug = (row.get("drug", "") or row.get("Drug", "") or
                            row.get("drug_name", "")).strip()
                    if drug:
                        idx = len(self._rows)
                        self._rows.append(row)
                        self._drug_index[drug.lower()].append(idx)
            logger.info("AskAPatient: loaded %d records", len(self._rows))
        except Exception as exc:
            logger.error("AskAPatient: load failed — %s", exc)

    def is_available(self) -> bool:
        self._ensure_loaded()
        return bool(self._rows)

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 10,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        self._ensure_loaded()
        results: List[RetrievalResult] = []

        for drug in entities.get("drug", []):
            for idx in self._drug_index.get(drug.lower(), []):
                if len(results) >= max_results:
                    break
                row = self._rows[idx]
                drug_name = (row.get("drug", "") or row.get("Drug", "")).strip()
                condition = (row.get("condition", "") or row.get("Condition", "")).strip()
                side_fx = (row.get("sideeffects", "") or row.get("SideEffects", "") or
                           row.get("side_effects", ""))[:200].strip()
                rating = row.get("rating", "") or row.get("Rating", "")
                results.append(RetrievalResult(
                    source_entity=drug_name,
                    source_type="drug",
                    target_entity=condition or "general",
                    target_type="condition",
                    relationship="patient_experience",
                    weight=1.0,
                    source="askapatient",
                    skill_category="drug_review",
                    evidence_text=f"AskAPatient: {drug_name}"
                                  + (f" for {condition}" if condition else "")
                                  + (f" (rating={rating})" if rating else "")
                                  + (f" side effects: {side_fx}" if side_fx else ""),
                    metadata={"rating": rating, "condition": condition},
                ))
        return results

    def get_all_pairs(self) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        return [
            {"drug": (r.get("drug", "") or r.get("Drug", "")).strip(),
             "disease": (r.get("condition", "") or r.get("Condition", "")).strip(),
             "label": r.get("rating", "")}
            for r in self._rows
        ]
