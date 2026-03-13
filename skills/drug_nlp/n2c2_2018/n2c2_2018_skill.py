"""
N2C22018Skill — n2c2 2018 Track 2: Adverse Drug Events.

Subcategory : drug_nlp
Access mode : DATASET (local files, access requires DUA from n2c2)
Source      : https://n2c2.dbmi.hms.harvard.edu/
Paper       : Henry et al. (2020), JAMIA

n2c2 2018 Track 2 contains clinical notes annotated for adverse drug events,
drug-reason relations, and drug attributes.

Config keys
-----------
tsv_path  : str  path to pre-parsed TSV/CSV (drug, adverse_event, sentence, label)
csv_path  : str  alternative CSV path
delimiter : str  column delimiter (default: "\t")
"""
from __future__ import annotations

import csv
import logging
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ...base import DatasetRAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)


class N2C22018Skill(DatasetRAGSkill):
    """n2c2 2018 Track 2 — adverse drug event extraction from EHRs."""

    name = "n2c2 2018 Track 2"
    subcategory = "drug_nlp"
    resource_type = "Dataset"
    access_mode = AccessMode.DATASET
    aim = "Clinical NLP ADE corpus"
    data_range = "n2c2 2018 adverse drug event extraction from EHRs"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._rows: List[Dict] = []
        self._drug_index: Dict[str, List[int]] = defaultdict(list)

    def _load(self) -> None:
        path = self.config.get("tsv_path", "") or self.config.get("csv_path", "")
        if not path or not os.path.exists(path):
            logger.warning(
                "N2C22018Skill: file not found. "
                "Access requires DUA from https://n2c2.dbmi.hms.harvard.edu/. "
                "Set config['tsv_path'] to pre-parsed TSV with columns: "
                "drug, adverse_event (or ae), label, [sentence]."
            )
            return
        delim = self.config.get("delimiter", "\t" if path.endswith(".tsv") else ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    drug = (row.get("drug", "") or row.get("Drug", "") or
                            row.get("medication", "")).strip()
                    if drug:
                        idx = len(self._rows)
                        self._rows.append(row)
                        self._drug_index[drug.lower()].append(idx)
            logger.info("n2c2 2018: loaded %d records", len(self._rows))
        except Exception as exc:
            logger.error("n2c2 2018: load failed — %s", exc)

    def is_available(self) -> bool:
        self._ensure_loaded()
        return bool(self._rows)

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 20,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        self._ensure_loaded()
        results: List[RetrievalResult] = []
        for drug in entities.get("drug", []):
            for idx in self._drug_index.get(drug.lower(), []):
                if len(results) >= max_results:
                    break
                row = self._rows[idx]
                drug_name = (row.get("drug", "") or row.get("medication", drug)).strip()
                ae = (row.get("adverse_event", "") or row.get("ae", "") or
                      row.get("ADE", "")).strip()
                label = row.get("label", "") or row.get("Label", "")
                sentence = row.get("sentence", "")[:200]
                results.append(RetrievalResult(
                    source_entity=drug_name,
                    source_type="drug",
                    target_entity=ae or "adverse_event",
                    target_type="adverse_event",
                    relationship="ehr_ade_relation",
                    weight=1.0,
                    source="n2c2 2018 Track 2",
                    skill_category="drug_nlp",
                    evidence_text=f"n2c2 2018: {drug_name} -> {ae} [{label}]" +
                                  (f" — {sentence}" if sentence else ""),
                    metadata={"label": label},
                ))
        return results

    def get_all_pairs(self) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        return [
            {"drug": (r.get("drug", "") or r.get("medication", "")).strip(),
             "disease": (r.get("adverse_event", "") or r.get("ae", "")).strip(),
             "label": r.get("label", "")}
            for r in self._rows
        ]
