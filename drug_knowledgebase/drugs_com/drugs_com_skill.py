"""
DrugsComSkill — Drugs.com Drug Information (stub).

Subcategory : drug_knowledgebase
Access mode : REST_API

Drugs.com provides consumer drug information including monographs,
side effects, and drug interactions. No public REST API; stub.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)


class DrugsComSkill(RAGSkill):
    """Drugs.com consumer drug information (interface stub)."""

    name = "Drugs.com"
    subcategory = "drug_knowledgebase"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "Consumer drug information"
    data_range = "Drug monographs, interactions, and patient education"

    def is_available(self) -> bool:
        return False

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 30,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        logger.debug("Drugs.com: no public API — skill unavailable")
        return []
