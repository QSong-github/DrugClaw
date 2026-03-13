"""
PROMISCUOUSSkill — PROMISCUOUS 2.0 drug polypharmacology database.

Subcategory : dti (Drug-Target Interaction)
Access mode : REST_API
Source      : https://bioinf-applied.charite.de/promiscuous2/

PROMISCUOUS 2.0 maps drug-protein interaction profiles for polypharmacology
analysis, including side effect–protein–drug triangles.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

_BASE = "https://bioinf-applied.charite.de/promiscuous2"


class PROMISCUOUSSkill(RAGSkill):
    """
    PROMISCUOUS 2.0 — drug polypharmacology and side-effect protein interactions.

    Config keys
    -----------
    timeout : int  (default 20)
    """

    name = "PROMISCUOUS 2.0"
    subcategory = "dti"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "Drug polypharmacology"
    data_range = "Drug–protein interaction profiles for polypharmacology"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._timeout = int(self.config.get("timeout", 20))

    def is_available(self) -> bool:
        # PROMISCUOUS has no public REST API; returns False until implemented
        return False

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 30,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        # PROMISCUOUS 2.0 does not expose a public REST API for programmatic access.
        # Register but mark unavailable; users can download the dataset directly.
        logger.debug("PROMISCUOUS 2.0: no public API — skill unavailable")
        return []
