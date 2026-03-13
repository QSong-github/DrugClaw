"""
DILISkill — DILI Drug-Induced Liver Injury Benchmark Dataset.

Subcategory : drug_toxicity
Access mode : LOCAL_FILE
Paper       : Xu et al., "Deep Learning for Drug-Induced Liver Injury" (2015)
              Available via MoleculeNet: https://moleculenet.org/datasets-1

Config keys
-----------
csv_path  : str  path to DILI CSV (columns: drug/Drug/compound_name,
                 label/Label/DILI/Y; 1=DILI-positive, 0=DILI-negative)
delimiter : str  column delimiter (default: auto-detect from extension)
"""
from __future__ import annotations

import csv
import logging
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ...base import DatasetRAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_LABEL_MAP = {
    "1": "DILI-positive", "0": "DILI-negative",
    "true": "DILI-positive", "false": "DILI-negative",
    "positive": "DILI-positive", "negative": "DILI-negative",
}


class DILISkill(DatasetRAGSkill):
    """DILI benchmark dataset — drug-induced liver injury binary labels."""

    name = "DILI"
    subcategory = "drug_toxicity"
    resource_type = "Dataset"
    access_mode = AccessMode.LOCAL_FILE
    aim = "DILI benchmark dataset"
    data_range = "Drug-induced liver injury benchmark dataset (Xu et al.)"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._rows: List[Dict] = []
        self._drug_index: Dict[str, List[int]] = defaultdict(list)

    def _load(self) -> None:
        path = self.config.get("csv_path", "")
        if not path or not os.path.exists(path):
            logger.warning(
                "DILISkill: file not found. "
                "Download from MoleculeNet (https://moleculenet.org/datasets-1) "
                "and set config['csv_path']."
            )
            return
        delim = self.config.get("delimiter", "\t" if path.endswith(".tsv") else ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    drug = (row.get("drug", "") or row.get("Drug", "") or
                            row.get("compound_name", "") or row.get("Compound", "")).strip()
                    label_raw = (row.get("label", "") or row.get("Label", "") or
                                 row.get("DILI", "") or row.get("Y", "") or
                                 row.get("activity", "")).strip()
                    if drug:
                        row["_drug"] = drug
                        row["_label"] = _LABEL_MAP.get(label_raw.lower(), label_raw)
                        idx = len(self._rows)
                        self._rows.append(row)
                        self._drug_index[drug.lower()].append(idx)
            logger.info("DILI: loaded %d drug records", len(self._rows))
        except Exception as exc:
            logger.error("DILI: load failed — %s", exc)

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
        for drug in entities.get("drug", []):
            for idx in self._drug_index.get(drug.lower(), []):
                if len(results) >= max_results:
                    break
                row = self._rows[idx]
                results.append(RetrievalResult(
                    source_entity=row["_drug"],
                    source_type="drug",
                    target_entity="drug-induced liver injury",
                    target_type="toxicity",
                    relationship="has_dili_label",
                    weight=1.0,
                    source="DILI",
                    skill_category="drug_toxicity",
                    evidence_text=f"DILI dataset: {row['_drug']} -> {row['_label']}",
                    metadata={"label": row["_label"], "smiles": row.get("smiles", "")},
                ))
        return results

    def get_all_pairs(self) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        return [
            {"drug": r["_drug"], "disease": "drug-induced liver injury", "label": r["_label"]}
            for r in self._rows
        ]
