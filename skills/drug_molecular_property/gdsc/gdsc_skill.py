"""
GDSCSkill — Genomics of Drug Sensitivity in Cancer (GDSC).

Subcategory : drug_molecular_property
Access mode : LOCAL_FILE
Download    : https://www.cancerrxgene.org/downloads/bulk_download
Paper       : Yang et al., Nucleic Acids Research, 2013

GDSC provides drug sensitivity (IC50) profiles across 1000+ cancer cell lines,
linking drug response to genomic features.

Config keys
-----------
csv_path  : str  path to GDSC CSV file (e.g. GDSC2_fitted_dose_response.csv)
              Expected columns: DRUG_NAME, CELL_LINE_NAME, LN_IC50 (or IC50),
                                [AUC], [RMSE], [TCGA_DESC], [DRUG_TARGETS]
delimiter : str  column delimiter (default: auto-detect from extension)
"""
from __future__ import annotations

import csv
import logging
import os
from collections import defaultdict
from math import exp
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)


class GDSCSkill(RAGSkill):
    """GDSC — drug sensitivity (IC50) profiles across cancer cell lines."""

    name = "GDSC"
    subcategory = "drug_molecular_property"
    resource_type = "Dataset"
    access_mode = AccessMode.LOCAL_FILE
    aim = "Genomics of drug sensitivity in cancer"
    data_range = "Drug sensitivity (IC50) profiles across 1000+ cancer cell lines"

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
                "GDSCSkill: file not found. "
                "Download from https://www.cancerrxgene.org/downloads/bulk_download "
                "and set config['csv_path']."
            )
            return
        delim = self.config.get("delimiter", "\t" if path.endswith(".tsv") else ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    drug = (row.get("DRUG_NAME", "") or row.get("drug_name", "") or
                            row.get("Drug", "")).strip()
                    if drug:
                        idx = len(self._rows)
                        self._rows.append(row)
                        self._drug_index[drug.lower()].append(idx)
            logger.info("GDSC: loaded %d drug-cell sensitivity records", len(self._rows))
        except Exception as exc:
            logger.error("GDSC: load failed — %s", exc)

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
                drug_name = (row.get("DRUG_NAME", "") or row.get("drug_name", "") or
                             row.get("Drug", drug)).strip()
                cell_line = (row.get("CELL_LINE_NAME", "") or row.get("cell_line_name", "") or
                             row.get("CellLine", "")).strip()
                # Convert LN_IC50 to IC50 µM if available
                ln_ic50 = row.get("LN_IC50", "") or row.get("ln_ic50", "")
                ic50_raw = row.get("IC50", "") or row.get("ic50", "")
                if ln_ic50:
                    try:
                        ic50_val = f"{exp(float(ln_ic50)):.3f} µM"
                    except ValueError:
                        ic50_val = ln_ic50
                else:
                    ic50_val = ic50_raw
                auc = row.get("AUC", "") or row.get("auc", "")
                targets = row.get("DRUG_TARGETS", "") or row.get("drug_targets", "")
                cancer_type = row.get("TCGA_DESC", "") or row.get("cancer_type", "")

                results.append(RetrievalResult(
                    source_entity=drug_name,
                    source_type="drug",
                    target_entity=cell_line or "cancer_cell_line",
                    target_type="cell_line",
                    relationship="has_ic50_sensitivity",
                    weight=1.0,
                    source="GDSC",
                    skill_category="drug_molecular_property",
                    evidence_text=(
                        f"GDSC: {drug_name} IC50={ic50_val} in {cell_line}"
                        + (f" ({cancer_type})" if cancer_type else "")
                        + (f" [targets: {targets}]" if targets else "")
                    ),
                    metadata={
                        "ic50": ic50_val,
                        "auc": auc,
                        "cell_line": cell_line,
                        "cancer_type": cancer_type,
                        "drug_targets": targets,
                    },
                ))
        return results
