"""
SemaTyPSkill — SemaTyP Drug-Disease Semantic Knowledge Graph.

Subcategory : drug_disease
Access mode : LOCAL_FILE
Paper       : "SemaTyP: A Knowledge Graph Based Literature Mining Method
               for Drug Discovery" (2018)

SemaTyP builds drug-disease associations using semantic type paths
extracted from biomedical literature (SemMedDB).

Config keys
-----------
csv_path  : str  path to SemaTyP triplet CSV/TSV file
              Expected columns: subject (or drug), predicate (or relation),
                                object (or disease), [score], [pmids]
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


class SemaTyPSkill(RAGSkill):
    """SemaTyP — drug-disease KG from semantic types in biomedical literature."""

    name = "SemaTyP"
    subcategory = "drug_disease"
    resource_type = "KG"
    access_mode = AccessMode.LOCAL_FILE
    aim = "Semantic drug-disease KG"
    data_range = "Drug-disease KG built from semantic types in biomedical literature"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._triplets: List[Dict] = []
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
                "SemaTyPSkill: file not found. "
                "Set config['csv_path'] to the SemaTyP triplet file."
            )
            return
        delim = self.config.get("delimiter", "\t" if path.endswith(".tsv") else ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    drug = (row.get("subject", "") or row.get("drug", "") or
                            row.get("Drug", "") or row.get("head", "")).strip()
                    disease = (row.get("object", "") or row.get("disease", "") or
                               row.get("Disease", "") or row.get("tail", "")).strip()
                    if drug and disease:
                        idx = len(self._triplets)
                        self._triplets.append(row)
                        self._drug_index[drug.lower()].append(idx)
                        self._disease_index[disease.lower()].append(idx)
            logger.info("SemaTyP: loaded %d drug-disease triplets", len(self._triplets))
        except Exception as exc:
            logger.error("SemaTyP: load failed — %s", exc)

    def is_available(self) -> bool:
        self._ensure_loaded()
        return bool(self._triplets)

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
                row = self._triplets[idx]
                drug = (row.get("subject", "") or row.get("drug", "") or
                        row.get("Drug", "") or row.get("head", "")).strip()
                disease = (row.get("object", "") or row.get("disease", "") or
                           row.get("Disease", "") or row.get("tail", "")).strip()
                rel = (row.get("predicate", "") or row.get("relation", "") or
                       row.get("Relation", "") or "drug_disease_association").strip()
                score = row.get("score", "") or row.get("confidence", "")
                pmids = row.get("pmids", "") or row.get("PMIDs", "")
                results.append(RetrievalResult(
                    source_entity=drug,
                    source_type="drug",
                    target_entity=disease,
                    target_type="disease",
                    relationship=rel.lower().replace(" ", "_"),
                    weight=1.0,
                    source="SemaTyP",
                    skill_category="drug_disease",
                    evidence_text=f"SemaTyP: {drug} {rel} {disease}"
                                  + (f" (score={score})" if score else ""),
                    sources=[f"PMID:{p.strip()}" for p in pmids.split(",") if p.strip()]
                             if pmids else [],
                    metadata={"score": score},
                ))

        for drug in entities.get("drug", []):
            _add(self._drug_index.get(drug.lower(), []))
        for disease in entities.get("disease", []):
            _add(self._disease_index.get(disease.lower(), []))
        return results
