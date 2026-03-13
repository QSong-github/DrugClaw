"""RepurposingHubSkill — Broad Institute Drug Repurposing Hub."""
from ...base import RAGSkill, RetrievalResult, AccessMode
import csv, logging, os
from collections import defaultdict
from typing import Any, Dict, List, Optional
logger = logging.getLogger(__name__)

class RepurposingHubSkill(RAGSkill):
    name = "Drug Repurposing Hub"; subcategory = "drug_repurposing"; resource_type = "Database"
    access_mode = AccessMode.LOCAL_FILE; aim = "Repurposing screening library"
    data_range = "Broad-spectrum repurposing library with mechanism annotations"
    def __init__(self, config=None):
        super().__init__(config); self._rows=[]; self._drug_index=defaultdict(list); self._loaded=False
    def _ensure_loaded(self):
        if self._loaded: return
        self._loaded = True
        path = self.config.get("csv_path","")
        if not path or not os.path.exists(path): logger.warning("RepurposingHub: set config['csv_path']"); return
        try:
            with open(path, newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    drug = (row.get("name","") or row.get("pert_iname","")).strip()
                    if drug: idx=len(self._rows); self._rows.append(row); self._drug_index[drug.lower()].append(idx)
        except Exception as e: logger.error("RepurposingHub load failed: %s", e)
    def is_available(self): self._ensure_loaded(); return bool(self._rows)
    def retrieve(self, entities, query="", max_results=30, **kwargs):
        self._ensure_loaded(); results=[]
        for drug in entities.get("drug",[]):
            for row in self._drug_index.get(drug.lower(),[]):
                if len(results)>=max_results: break
                r=self._rows[row]; target=r.get("target",""); moa=r.get("moa","")
                if target: results.append(RetrievalResult(drug,"drug",target,"protein","repurposing_target",1.0,"Drug Repurposing Hub","drug_repurposing",f"RepurposingHub: {drug} → {target} [{moa}]"))
        return results
