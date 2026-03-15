"""
KEGGDrugSkill — KEGG Drug Interactions.

Subcategory : ddi (Drug-Drug Interaction)
Access mode : CLI-first (bioservices), falls back to KEGG REST API.

KEGG Drug database contains drug-drug interactions with pathway context.

CLI install : pip install bioservices
REST docs   : https://www.kegg.jp/kegg/rest/keggapi.html
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, CLISkillMixin, AccessMode

logger = logging.getLogger(__name__)

_KEGG_REST = "https://rest.kegg.jp"


class KEGGDrugSkill(CLISkillMixin, RAGSkill):
    """
    KEGG Drug — drug-drug interactions with KEGG pathway context.

    Uses bioservices Python package (CLI approach) if available,
    falls back to KEGG REST API.

    Config keys
    -----------
    timeout : int  (default 20)
    """

    name = "KEGG Drug"
    subcategory = "ddi"
    resource_type = "Database"
    access_mode = AccessMode.CLI
    aim = "KEGG drug interactions"
    data_range = "Drug-drug interactions from KEGG with pathway context"
    _implemented = True
    cli_package_name = "bioservices"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        RAGSkill.__init__(self, config)
        self._timeout = int(self.config.get("timeout", 20))

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 20,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        return self._try_cli_or_rest(entities, query, max_results)

    # ------------------------------------------------------------------
    # CLI path (bioservices)
    # ------------------------------------------------------------------

    def _cli_search(self, entities, query="", max_results=20):
        from bioservices import KEGG  # type: ignore
        kegg = KEGG(verbose=False)
        results: List[RetrievalResult] = []

        for drug in entities.get("drug", []):
            if len(results) >= max_results:
                break
            try:
                # Find KEGG drug ID
                search_result = kegg.find("drug", drug)
                if not search_result or search_result == "\n":
                    continue
                lines = [l for l in search_result.strip().split("\n") if l]
                if not lines:
                    continue
                drug_id = lines[0].split("\t")[0].replace("dr:", "")
                # Get drug entry
                entry = kegg.get(f"dr:{drug_id}")
                if not entry:
                    continue
                # Parse interactions from the entry text
                in_interaction = False
                for line in str(entry).split("\n"):
                    if line.startswith("INTERACTION"):
                        in_interaction = True
                    elif in_interaction and line.startswith(" "):
                        parts = line.strip().split()
                        if parts:
                            interacting_drug = parts[0]
                            rel_desc = " ".join(parts[1:]) if len(parts) > 1 else "interacts_with"
                            results.append(RetrievalResult(
                                source_entity=drug,
                                source_type="drug",
                                target_entity=interacting_drug,
                                target_type="drug",
                                relationship="drug_drug_interaction",
                                weight=1.0,
                                source="KEGG Drug",
                                skill_category="ddi",
                                evidence_text=f"KEGG Drug: {drug} interacts with {interacting_drug}: {rel_desc}",
                                metadata={"kegg_drug_id": drug_id, "description": rel_desc, "access_via": "bioservices"},
                            ))
                    elif in_interaction and not line.startswith(" "):
                        in_interaction = False
            except Exception as exc:
                logger.debug("KEGG CLI: error for '%s' — %s", drug, exc)

        return results

    # ------------------------------------------------------------------
    # REST fallback
    # ------------------------------------------------------------------

    def _rest_search(self, entities, query="", max_results=20):
        results: List[RetrievalResult] = []
        for drug in entities.get("drug", []):
            if len(results) >= max_results:
                break
            results.extend(self._rest_find(drug, max_results - len(results)))
        return results

    def _rest_find(self, drug: str, limit: int) -> List[RetrievalResult]:
        # Search KEGG drug database
        url = f"{_KEGG_REST}/find/drug/{urllib.parse.quote(drug)}"
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                text = resp.read().decode()
        except Exception as exc:
            logger.debug("KEGG REST: find failed for '%s' — %s", drug, exc)
            return []

        lines = [l for l in text.strip().split("\n") if l]
        if not lines:
            return []

        drug_id = lines[0].split("\t")[0].replace("dr:", "")
        get_url = f"{_KEGG_REST}/get/dr:{drug_id}"
        try:
            with urllib.request.urlopen(get_url, timeout=self._timeout) as resp:
                entry = resp.read().decode()
        except Exception as exc:
            logger.debug("KEGG REST: get failed for %s — %s", drug_id, exc)
            return []

        results: List[RetrievalResult] = []
        in_interaction = False
        for line in entry.split("\n"):
            if line.startswith("INTERACTION"):
                in_interaction = True
            elif in_interaction and line.startswith(" "):
                parts = line.strip().split()
                if parts and len(results) < limit:
                    results.append(RetrievalResult(
                        source_entity=drug,
                        source_type="drug",
                        target_entity=parts[0],
                        target_type="drug",
                        relationship="drug_drug_interaction",
                        weight=1.0,
                        source="KEGG Drug",
                        skill_category="ddi",
                        evidence_text=f"KEGG Drug: {drug} → {parts[0]}",
                        metadata={"kegg_drug_id": drug_id, "access_via": "REST"},
                    ))
            elif in_interaction and not line.startswith(" "):
                in_interaction = False
        return results
