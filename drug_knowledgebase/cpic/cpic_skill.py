"""
CPICSkill — Clinical Pharmacogenomics Implementation Consortium (CPIC).

Subcategory : drug_knowledgebase (Drug Knowledgebase)
Access mode : REST_API
Docs        : https://api.cpicpgx.org/

CPIC provides guidelines linking gene/variant data to drug dosing
and prescribing recommendations.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_BASE = "https://api.cpicpgx.org/v1"


class CPICSkill(RAGSkill):
    """CPIC clinical pharmacogenomics guidelines."""

    name = "CPIC"
    subcategory = "drug_knowledgebase"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "Clinical pharmacogenomics"
    data_range = "CPIC guidelines linking genes/variants to drug dosing"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._timeout = int(self.config.get("timeout", 20))

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 20,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        results: List[RetrievalResult] = []
        for drug in entities.get("drug", []):
            if len(results) >= max_results:
                break
            results.extend(self._search_drug(drug, max_results - len(results)))
        for gene in entities.get("gene", []):
            if len(results) >= max_results:
                break
            results.extend(self._search_gene(gene, max_results - len(results)))
        return results

    def _search_drug(self, drug: str, limit: int) -> List[RetrievalResult]:
        url = f"{_BASE}/drug?name={urllib.parse.quote(drug)}"
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:
            logger.debug("CPIC: drug search failed for '%s' — %s", drug, exc)
            return []

        results: List[RetrievalResult] = []
        items = data if isinstance(data, list) else data.get("data", [])
        for item in items[:limit]:
            drug_name = item.get("name", drug)
            for guideline in item.get("guidelines", []):
                genes = guideline.get("genes", [])
                for gene in genes:
                    gene_symbol = gene.get("symbol", "")
                    if not gene_symbol:
                        continue
                    results.append(RetrievalResult(
                        source_entity=drug_name,
                        source_type="drug",
                        target_entity=gene_symbol,
                        target_type="gene",
                        relationship="has_pgx_guideline",
                        weight=1.0,
                        source="CPIC",
                        skill_category="drug_knowledgebase",
                        evidence_text=(
                            f"CPIC guideline: {drug_name} dosing affected by "
                            f"{gene_symbol} variants"
                        ),
                        metadata={
                            "guideline_id": guideline.get("id", ""),
                            "url": guideline.get("url", ""),
                        },
                    ))
        return results

    def _search_gene(self, gene: str, limit: int) -> List[RetrievalResult]:
        url = f"{_BASE}/gene?symbol={urllib.parse.quote(gene)}"
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:
            logger.debug("CPIC: gene search failed for '%s' — %s", gene, exc)
            return []

        results: List[RetrievalResult] = []
        items = data if isinstance(data, list) else data.get("data", [])
        for item in items[:limit]:
            gene_symbol = item.get("symbol", gene)
            for drug in item.get("relatedDrugs", []):
                drug_name = drug.get("name", "")
                if not drug_name:
                    continue
                results.append(RetrievalResult(
                    source_entity=drug_name,
                    source_type="drug",
                    target_entity=gene_symbol,
                    target_type="gene",
                    relationship="has_pgx_guideline",
                    weight=1.0,
                    source="CPIC",
                    skill_category="drug_knowledgebase",
                    evidence_text=f"CPIC: {drug_name} dosing affected by {gene_symbol}",
                ))
        return results
