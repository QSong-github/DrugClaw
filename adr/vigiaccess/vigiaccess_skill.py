"""
VigiAccessSkill — WHO VigiAccess Pharmacovigilance (stub).

Subcategory : adr (Adverse Drug Reaction)
Access mode : REST_API

VigiAccess provides access to the WHO global pharmacovigilance database
(VigiBase). Their web API has rate limits and CAPTCHA; this skill
provides a stub with the interface defined.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)


class VigiAccessSkill(RAGSkill):
    """WHO VigiAccess pharmacovigilance database (interface stub)."""

    name = "VigiAccess"
    subcategory = "adr"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "WHO pharmacovigilance"
    data_range = "WHO global adverse reaction database (VigiBase summary)"

    def is_available(self) -> bool:
        return False

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 30,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        logger.debug("VigiAccess: no public API — skill unavailable")
        return []
