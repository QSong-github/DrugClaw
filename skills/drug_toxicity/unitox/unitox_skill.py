"""UniToxSkill — Drug Toxicity Database (local/Zenodo)."""
from __future__ import annotations
import csv, logging, os
from collections import defaultdict
from typing import Any, Dict, List, Optional
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
logger = logging.getLogger(__name__)

class UniToxSkill(RAGSkill):
    name = "UniTox"; subcategory = "drug_toxicity"; resource_type = "Dataset"
    access_mode = AccessMode.LOCAL_FILE; aim = "Drug toxicity database"
    data_range = "Large-scale drug toxicity database from clinical notes"
    _implemented = True
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
                organ = row.get("organ_system","") or row.get("system","")
                evidence = f"UniTox: {drug} → {tox or 'toxicity'}"
                if organ:
                    evidence += f" [{organ}]"
                results.append(RetrievalResult(
                    source_entity=drug,
                    source_type="drug",
                    target_entity=tox or "toxicity",
                    target_type="toxicity",
                    relationship="has_toxicity",
                    weight=1.0,
                    source="UniTox",
                    evidence_text=evidence,
                    skill_category="drug_toxicity",
                    metadata={
                        "organ_system": organ,
                        "source_label": row.get("label", ""),
                    },
                ))
        return results
