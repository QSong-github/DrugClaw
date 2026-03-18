"""RepurposingHubSkill — Broad Institute Drug Repurposing Hub."""
# --- CLI entry-point (inserted before relative imports) -------------------
import sys as _sys, os as _os
if __name__ == "__main__" and len(_sys.argv) > 1:
    _skill_dir = _os.path.dirname(_os.path.abspath(__file__))
    if _skill_dir not in _sys.path:
        _sys.path.insert(0, _skill_dir)
    _entities = _sys.argv[1:]
    try:
        import example as _ex

        for _e in _entities:
            _hits = _ex.search(_e)
            print(_ex.summarize(_hits, _e))
    except Exception as _exc:
        print(f"Error: {_exc}", _sys.stderr)
        _sys.exit(1)
    _sys.exit(0)
# --------------------------------------------------------------------------
from ...base import RAGSkill, RetrievalResult, AccessMode
import csv, logging, os
from collections import defaultdict
from typing import Any, Dict, List, Optional
logger = logging.getLogger(__name__)

class RepurposingHubSkill(RAGSkill):
    name = "Drug Repurposing Hub"; subcategory = "drug_repurposing"; resource_type = "Database"
    access_mode = AccessMode.LOCAL_FILE; aim = "Repurposing screening library"
    data_range = "Broad-spectrum repurposing library with mechanism annotations"
    _implemented = True
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
                phase = r.get("clinical_phase", "") or r.get("phase", "")
                if target:
                    results.append(RetrievalResult(
                        source_entity=drug,
                        source_type="drug",
                        target_entity=target,
                        target_type="protein",
                        relationship="repurposing_target",
                        weight=1.0,
                        source="Drug Repurposing Hub",
                        evidence_text=f"RepurposingHub: {drug} → {target} [{moa}]",
                        skill_category="drug_repurposing",
                        metadata={
                            "moa": moa,
                            "clinical_phase": phase,
                        },
                    ))
        return results
