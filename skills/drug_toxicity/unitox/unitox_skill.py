"""UniToxSkill — Drug Toxicity Database (local/Zenodo)."""
from __future__ import annotations
import csv, logging, os
from collections import defaultdict
from typing import Any, Dict, List, Optional
from ...base import RAGSkill, RetrievalResult, AccessMode
logger = logging.getLogger(__name__)

class UniToxSkill(RAGSkill):
    name = "UniTox"; subcategory = "drug_toxicity"; resource_type = "Dataset"
    access_mode = AccessMode.LOCAL_FILE; aim = "Drug toxicity database"
    data_range = "Large-scale drug toxicity database from clinical notes"
    def __init__(self, config=None):
        super().__init__(config); self._drug_index=defaultdict(list); self._rows=[]; self._loaded=False
    def _ensure_loaded(self):
        if self._loaded: return
        self._loaded = True
        path = self.config.get("csv_path","")
        if not path or not os.path.exists(path): logger.warning("UniToxSkill: set config['csv_path']"); return
        try:
            with open(path, newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    drug = (row.get("drug","") or row.get("Drug","")).strip()
                    if drug: idx=len(self._rows); self._rows.append(row); self._drug_index[drug.lower()].append(idx)
        except Exception as e: logger.error("UniTox load failed: %s", e)
    def is_available(self): self._ensure_loaded(); return bool(self._rows)
    def retrieve(self, entities, query="", max_results=30, **kwargs):
        self._ensure_loaded(); results=[]
        for drug in entities.get("drug",[]):
            for idx in self._drug_index.get(drug.lower(),[]):
                if len(results)>=max_results: break
                row=self._rows[idx]; tox=row.get("toxicity","") or row.get("label","")
                results.append(RetrievalResult(drug,"drug",tox or "toxicity","toxicity","has_toxicity",1.0,"UniTox","drug_toxicity",f"UniTox: {drug} → {tox}"))
        return results
