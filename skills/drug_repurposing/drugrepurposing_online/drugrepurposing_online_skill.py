"""
DrugRepurposingOnlineSkill — Drug Repurposing Hub / Online Database.

Subcategory : drug_repurposing
Access mode : LOCAL_FILE
Source      : https://www.drrepurp.com/
              (Drug Repurposing Hub, Broad Institute)
Download    : https://clue.io/repurposing-app

The Drug Repurposing Hub (Broad Institute) catalogs approved and
investigational drugs with their disease indications and mechanism classes
for systematic repurposing analysis.

Config keys
-----------
csv_path  : str  path to Drug Repurposing Hub CSV/TSV
              Expected columns: pert_iname (drug), disease_area, indication,
                                clinical_phase, moa (mechanism of action), target
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


class DrugRepurposingOnlineSkill(RAGSkill):
    """Drug Repurposing Hub — Broad Institute computational repurposing predictions."""

    name = "DrugRepurposing Online"
    subcategory = "drug_repurposing"
    resource_type = "Database"
    access_mode = AccessMode.LOCAL_FILE
    aim = "Repurposing predictions"
    data_range = "Computational drug repurposing predictions database"

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
                "DrugRepurposingOnlineSkill: file not found. "
                "Download Drug Repurposing Hub from https://clue.io/repurposing-app "
                "and set config['csv_path']."
            )
            return
        delim = self.config.get("delimiter", "\t" if path.endswith(".tsv") else ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    drug = (row.get("pert_iname", "") or row.get("drug", "") or
                            row.get("Drug", "") or row.get("compound", "")).strip()
                    disease = (row.get("indication", "") or row.get("disease_area", "") or
                               row.get("disease", "") or row.get("Disease", "")).strip()
                    if drug:
                        idx = len(self._rows)
                        self._rows.append(row)
                        self._drug_index[drug.lower()].append(idx)
                        if disease:
                            self._disease_index[disease.lower()].append(idx)
            logger.info("DrugRepurposingOnline: loaded %d records", len(self._rows))
        except Exception as exc:
            logger.error("DrugRepurposingOnline: load failed — %s", exc)

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
                drug = (row.get("pert_iname", "") or row.get("drug", "") or
                        row.get("Drug", "")).strip()
                disease = (row.get("indication", "") or row.get("disease_area", "") or
                           row.get("disease", "")).strip()
                moa = row.get("moa", "") or row.get("mechanism_of_action", "")
                target = row.get("target", "") or row.get("Target", "")
                phase = row.get("clinical_phase", "") or row.get("phase", "")
                results.append(RetrievalResult(
                    source_entity=drug,
                    source_type="drug",
                    target_entity=disease or "unknown",
                    target_type="disease",
                    relationship="repurposed_for",
                    weight=1.0,
                    source="DrugRepurposing Online",
                    skill_category="drug_repurposing",
                    evidence_text=(
                        f"DrugRepurposingHub: {drug}"
                        + (f" → {disease}" if disease else "")
                        + (f" [{phase}]" if phase else "")
                        + (f" MoA: {moa}" if moa else "")
                    ),
                    metadata={
                        "moa": moa,
                        "target": target,
                        "clinical_phase": phase,
                        "indication": disease,
                    },
                ))

        for drug in entities.get("drug", []):
            _add(self._drug_index.get(drug.lower(), []))
        for disease in entities.get("disease", []):
            _add(self._disease_index.get(disease.lower(), []))
        return results
