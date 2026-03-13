"""
CancerDRSkill — CancerDR: Cancer Drug Resistance Database.

Subcategory : drug_repurposing
Access mode : LOCAL_FILE
Source      : http://crdd.osdd.net/raghava/cancerdr/

CancerDR catalogs drug resistance mutations in cancer, covering 148 cancer
drugs, their targets, and resistance-causing mutations across cancer cell lines.
Useful for understanding drug resistance mechanisms and alternative therapy selection.

Config keys
-----------
csv_path  : str  path to CancerDR CSV/TSV download
              Expected columns: Drug (or drug_name), Target, Mutation,
                                CancerType (or cancer_type), [Cell_Line], [IC50]
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


class CancerDRSkill(RAGSkill):
    """CancerDR — cancer drug resistance mutations and sensitivity database."""

    name = "CancerDR"
    subcategory = "drug_repurposing"
    resource_type = "Database"
    access_mode = AccessMode.LOCAL_FILE
    aim = "Cancer drug resistance"
    data_range = "Drug resistance mutations and cancer drug sensitivity"

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
            logger.warning(
                "CancerDRSkill: file not found. "
                "Download from http://crdd.osdd.net/raghava/cancerdr/ "
                "and set config['csv_path']."
            )
            return
        delim = self.config.get("delimiter", "\t" if path.endswith(".tsv") else ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    drug = (row.get("Drug", "") or row.get("drug_name", "") or
                            row.get("drug", "") or row.get("DrugName", "")).strip()
                    if drug:
                        idx = len(self._rows)
                        self._rows.append(row)
                        self._drug_index[drug.lower()].append(idx)
            logger.info("CancerDR: loaded %d resistance records", len(self._rows))
        except Exception as exc:
            logger.error("CancerDR: load failed — %s", exc)

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
                    break
                seen.add(idx)
                row = self._rows[idx]
                drug_name = (row.get("Drug", "") or row.get("drug_name", "") or
                             row.get("drug", drug)).strip()
                target = (row.get("Target", "") or row.get("target", "")).strip()
                mutation = (row.get("Mutation", "") or row.get("mutation", "")).strip()
                cancer = (row.get("CancerType", "") or row.get("cancer_type", "") or
                          row.get("Cancer", "")).strip()
                cell_line = (row.get("Cell_Line", "") or row.get("cell_line", "")).strip()
                ic50 = row.get("IC50", "") or row.get("ic50", "")
                results.append(RetrievalResult(
                    source_entity=drug_name,
                    source_type="drug",
                    target_entity=mutation or target or "resistance",
                    target_type="mutation",
                    relationship="resistance_mutation",
                    weight=1.0,
                    source="CancerDR",
                    skill_category="drug_repurposing",
                    evidence_text=(
                        f"CancerDR: {drug_name} resistance"
                        + (f" via {mutation}" if mutation else "")
                        + (f" in {cancer}" if cancer else "")
                        + (f" (IC50={ic50})" if ic50 else "")
                    ),
                    metadata={
                        "target": target,
                        "mutation": mutation,
                        "cancer_type": cancer,
                        "cell_line": cell_line,
                        "ic50": ic50,
                    },
                ))
        return results
