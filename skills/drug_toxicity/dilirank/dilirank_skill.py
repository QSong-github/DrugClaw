"""DILIrankSkill — FDA DILIrank Dataset (local)."""
from __future__ import annotations
import csv, logging, os
from collections import defaultdict
from typing import Any, Dict, List, Optional
from ...base import RAGSkill, RetrievalResult, AccessMode
logger = logging.getLogger(__name__)

class DILIrankSkill(RAGSkill):
    name = "DILIrank"; subcategory = "drug_toxicity"; resource_type = "Dataset"
    access_mode = AccessMode.LOCAL_FILE; aim = "DILI severity ranking"
    data_range = "FDA DILI severity ranking (most-DILI-concern to no-DILI-concern)"
    def __init__(self, config=None):
        super().__init__(config); self._drug_index=defaultdict(list); self._rows=[]; self._loaded=False
    def _ensure_loaded(self):
        if self._loaded: return
        self._loaded = True
        path = self.config.get("csv_path","")
        if not path or not os.path.exists(path): logger.warning("DILIrankSkill: set config['csv_path']"); return
        try:
            with open(path, newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    drug = (row.get("Drug Name","") or row.get("drug","")).strip()
                    if drug: idx=len(self._rows); self._rows.append(row); self._drug_index[drug.lower()].append(idx)
        except Exception as e: logger.error("DILIrank load failed: %s", e)
    def is_available(self): self._ensure_loaded(); return bool(self._rows)
    def retrieve(self, entities, query="", max_results=30, **kwargs):
        self._ensure_loaded(); results=[]
        for drug in entities.get("drug",[]):
            for idx in self._drug_index.get(drug.lower(),[]):
                if len(results)>=max_results: break
                row=self._rows[idx]; rank=row.get("vDILIConcern","") or row.get("DILI Concern","")
                results.append(RetrievalResult(drug,"drug",rank or "DILI","dili_concern","has_dili_concern",1.0,"DILIrank","drug_toxicity",f"DILIrank: {drug} → {rank}",metadata={"rank":rank}))
        return results
