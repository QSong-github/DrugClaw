"""
DrugEHRQASkill — Drug QA over EHR (DrugEHRQA).

Subcategory : drug_nlp
Access mode : DATASET (local files)
Source      : https://github.com/jayachaturvedi/DrugEHRQA
Paper       : "DrugEHRQA: A Question Answering Dataset on Structured
               and Unstructured Electronic Health Records For Drug-Related Queries" (2022)

Config keys
-----------
json_path : str  path to DrugEHRQA JSON file (questions, answers, drug entities)
csv_path  : str  alternative: path to CSV version
delimiter : str  CSV delimiter (default: ",")
"""
from __future__ import annotations

import csv
import json
import logging
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ...base import DatasetRAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)


class DrugEHRQASkill(DatasetRAGSkill):
    """DrugEHRQA — drug question answering over structured/unstructured EHRs."""

    name = "DrugEHRQA"
    subcategory = "drug_nlp"
    resource_type = "Dataset"
    access_mode = AccessMode.DATASET
    aim = "Drug QA over EHR"
    data_range = "Question-answering dataset over structured/unstructured EHRs"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._rows: List[Dict] = []
        self._drug_index: Dict[str, List[int]] = defaultdict(list)

    def _load(self) -> None:
        json_path = self.config.get("json_path", "")
        csv_path = self.config.get("csv_path", "")
        if json_path and os.path.exists(json_path):
            self._load_json(json_path)
        elif csv_path and os.path.exists(csv_path):
            self._load_csv(csv_path)
        else:
            logger.warning(
                "DrugEHRQASkill: no data file found. "
                "Download from https://github.com/jayachaturvedi/DrugEHRQA "
                "and set config['json_path'] or config['csv_path']."
            )

    def _load_json(self, path: str) -> None:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            items = data if isinstance(data, list) else data.get("data", [])
            for item in items:
                drugs = item.get("drugs", []) or item.get("entities", [])
                q = item.get("question", "") or item.get("query", "")
                a = item.get("answer", "") or item.get("response", "")
                for drug in (drugs if isinstance(drugs, list) else [drugs]):
                    if drug:
                        idx = len(self._rows)
                        self._rows.append({"drug": drug, "question": q, "answer": a})
                        self._drug_index[str(drug).lower()].append(idx)
            logger.info("DrugEHRQA: loaded %d QA records", len(self._rows))
        except Exception as exc:
            logger.error("DrugEHRQA: JSON load failed — %s", exc)

    def _load_csv(self, path: str) -> None:
        delim = self.config.get("delimiter", ",")
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                for row in csv.DictReader(fh, delimiter=delim):
                    drug = (row.get("drug", "") or row.get("Drug", "")).strip()
                    if drug:
                        idx = len(self._rows)
                        self._rows.append(row)
                        self._drug_index[drug.lower()].append(idx)
            logger.info("DrugEHRQA: loaded %d records from CSV", len(self._rows))
        except Exception as exc:
            logger.error("DrugEHRQA: CSV load failed — %s", exc)

    def is_available(self) -> bool:
        self._ensure_loaded()
        return bool(self._rows)

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 10,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        self._ensure_loaded()
        results: List[RetrievalResult] = []
        for drug in entities.get("drug", []):
            for idx in self._drug_index.get(drug.lower(), []):
                if len(results) >= max_results:
                    break
                row = self._rows[idx]
                drug_name = row.get("drug", drug)
                question = row.get("question", "")[:200]
                answer = row.get("answer", "")[:300]
                results.append(RetrievalResult(
                    source_entity=drug_name,
                    source_type="drug",
                    target_entity="EHR QA",
                    target_type="qa_record",
                    relationship="has_ehr_qa",
                    weight=1.0,
                    source="DrugEHRQA",
                    skill_category="drug_nlp",
                    evidence_text=f"DrugEHRQA: Q={question} A={answer}",
                    metadata={"question": question, "answer": answer},
                ))
        return results

    def get_all_pairs(self) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        return [{"drug": r.get("drug", ""), "disease": "", "label": "qa_pair"}
                for r in self._rows]
