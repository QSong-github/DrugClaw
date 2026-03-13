"""
RxListSkill — RxList Drug Descriptions (stub).

Subcategory : drug_labeling
Access mode : REST_API

RxList provides drug monographs but does not offer a public REST API.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)


class RxListSkill(RAGSkill):
    """RxList drug monographs (interface stub — no public API)."""

    name = "RxList Drug Descriptions"
    subcategory = "drug_labeling"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "Drug monographs"
    data_range = "Clinical drug descriptions including mechanism and dosing"

    def is_available(self) -> bool:
        return False

    def retrieve(self, entities, query="", max_results=30, **kwargs) -> List[RetrievalResult]:
        logger.debug("RxList: no public API — skill unavailable")
        return []
