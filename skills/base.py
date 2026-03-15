"""
Unified schema and abstract base classes for all DrugClaw RAG skills.

Every skill ingests a dict of entities + a free-text query and returns a list
of RetrievalResult objects.  The schema maps directly to the fields that
agent_retriever._build_subgraph() expects.

Skills are now organized by *subcategory* (matching the 68DrugResources.xlsx
Subcategory column) rather than by resource type (KG / Database / Dataset).

Subcategories
-------------
adr               Adverse Drug Reaction (ADR)
drug_combination  Drug Combination/Synergy
drug_knowledgebase Drug Knowledgebase
drug_labeling     Drug Labeling/Info
drug_mechanism    Drug Mechanism
drug_molecular_property Drug Molecular Property
drug_nlp          Drug NLP/Text Mining
drug_ontology     Drug Ontology/Terminology
drug_repurposing  Drug Repurposing
drug_review       Drug Review/Patient Report
drug_toxicity     Drug Toxicity
ddi               Drug-Drug Interaction (DDI)
dti               Drug-Target Interaction (DTI)
drug_disease      Drug–Disease Associations
pharmacogenomics  Pharmacogenomics

Access modes
------------
REST_API   HTTP REST / GraphQL endpoint (no install required)
CLI        Python package with CLI interface (preferred when available)
LOCAL_FILE Pre-downloaded local file (CSV / TSV / JSON / GraphML)
DATASET    Labelled benchmark dataset (mask during evaluation)
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Access-mode constants
# ---------------------------------------------------------------------------

class AccessMode:
    REST_API   = "REST_API"
    CLI        = "CLI"
    LOCAL_FILE = "LOCAL_FILE"
    DATASET    = "DATASET"


# ---------------------------------------------------------------------------
# Unified output schema
# ---------------------------------------------------------------------------

@dataclass
class RetrievalResult:
    """
    Canonical output record produced by every RAG skill.

    Fields used by agent_retriever._build_subgraph
    -----------------------------------------------
    source_entity  : str   – name of the source node
    source_type    : str   – entity type  (drug / gene / disease / protein / pathway / …)
    target_entity  : str   – name of the target node
    target_type    : str   – entity type of the target
    relationship   : str   – edge label (e.g. "treats", "targets", "inhibits")
    weight         : float – always 1.0; relationship exists or it does not
    source         : str   – skill/database name (used as provenance label)

    Extra context (optional, carried through to EvidenceSubgraph.metadata)
    -----------------------------------------------------------------------
    evidence_text  : free-text explanation, abstract snippet, mechanism note …
    sources        : list of provenance references — any mix of:
                       • PubMed IDs  ("PMID:12345678")
                       • URLs        ("https://www.ebi.ac.uk/chembl/…")
                       • Paper titles ("Drug Repurposing … Nature 2021")
                     Not every resource provides citations; leave empty if none.
    skill_category : subcategory string (e.g. "dti", "adr", "drug_repurposing")
    metadata       : any additional key-value pairs
    """

    # --- required core fields (mirrors _build_subgraph contract) ---
    source_entity: str
    source_type: str
    target_entity: str
    target_type: str
    relationship: str
    weight: float        # always 1.0
    source: str          # skill name used as DB provenance label

    # --- optional enrichment ---
    evidence_text: Optional[str] = None
    sources: List[str] = field(default_factory=list)   # PMIDs / URLs / titles
    skill_category: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dict (compatible with existing pipeline)."""
        d = {
            "source_entity": self.source_entity,
            "source_type": self.source_type,
            "target_entity": self.target_entity,
            "target_type": self.target_type,
            "relationship": self.relationship,
            "weight": self.weight,
            "source": self.source,
            "skill_category": self.skill_category,
        }
        if self.evidence_text is not None:
            d["evidence_text"] = self.evidence_text
        if self.sources:
            d["sources"] = self.sources
        if self.metadata:
            d.update(self.metadata)
        return d


# ---------------------------------------------------------------------------
# Abstract base skill
# ---------------------------------------------------------------------------

class RAGSkill(ABC):
    """
    Abstract base class that every RAG skill must implement.

    Subclasses must define:
      - name          : unique string identifier (e.g. "ChEMBL", "DGIdb")
      - subcategory   : one of the 15 subcategory keys (e.g. "dti", "adr")
      - resource_type : 'KG' | 'Database' | 'Dataset'  (kept for compat)
      - access_mode   : AccessMode constant
      - aim           : short purpose string from the survey
      - data_range    : coverage description
      - retrieve()    : the actual retrieval logic
    """

    name: str = "UnnamedSkill"
    subcategory: str = "unknown"          # 15-category system
    resource_type: str = "unknown"        # KG / Database / Dataset  (legacy)
    access_mode: str = AccessMode.REST_API
    aim: str = ""
    data_range: str = ""
    _implemented: bool = False            # True only for skills with working example code

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config: Dict[str, Any] = config or {}

    @abstractmethod
    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 50,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        """
        Main retrieval entry-point.

        Parameters
        ----------
        entities    : dict mapping entity_type -> list[entity_name]
                      e.g. {"drug": ["aspirin"], "gene": ["TP53"]}
        query       : optional free-text query for semantic retrieval
        max_results : upper bound on number of results to return

        Returns
        -------
        List of RetrievalResult objects with weight=1.0 for each found triplet.
        """

    def is_available(self) -> bool:
        """Return True if the skill can be used right now.

        Only implemented skills (with working example code + SKILL.md) are available.
        """
        return self._implemented

    def get_example_path(self) -> Optional[str]:
        """Return path to the example.py in this skill's directory, or None."""
        import inspect
        skill_dir = os.path.dirname(inspect.getfile(type(self)))
        example_path = os.path.join(skill_dir, "example.py")
        if os.path.exists(example_path):
            return example_path
        return None

    def get_skill_md_path(self) -> Optional[str]:
        """Return path to the SKILL.md in this skill's directory, or None."""
        import inspect
        skill_dir = os.path.dirname(inspect.getfile(type(self)))
        md_path = os.path.join(skill_dir, "SKILL.md")
        if os.path.exists(md_path):
            return md_path
        return None

    def get_example_code(self) -> str:
        """Read and return the example.py code for this skill."""
        path = self.get_example_path()
        if path:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return f"# No example code available for {self.name}"

    def get_skill_md(self) -> str:
        """Read and return the SKILL.md description for this skill."""
        path = self.get_skill_md_path()
        if path:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return f"No skill description available for {self.name}"

    def get_description(self) -> str:
        """Human-readable description used in LLM prompts."""
        return (
            f"{self.name} [{self.subcategory}] — aim: {self.aim} — "
            f"covers: {self.data_range}"
        )

    # ---- helpers ----------------------------------------------------------

    @staticmethod
    def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

    def _retry(self, fn, retries: int = 3, delay: float = 1.0):
        """Simple retry wrapper for network calls."""
        last_exc: Optional[Exception] = None
        for attempt in range(retries):
            try:
                return fn()
            except Exception as exc:
                last_exc = exc
                time.sleep(delay * (2 ** attempt))
        raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# CLI-capable skill mixin
# ---------------------------------------------------------------------------

class CLISkillMixin:
    """
    Mixin for skills that can use a CLI tool (Python package with CLI interface)
    in preference to raw REST calls.

    Inspired by OpenClaw Medical Skills' approach of preferring installed
    CLI/Python-package tools over raw HTTP when available.

    Subclasses should:
      1. Set cli_package_name = "package_name"  (pip install name)
      2. Implement _cli_search(entities, query) -> List[RetrievalResult]
      3. Call self._try_cli_or_rest(entities, query) in retrieve()

    The mixin checks if the package is importable; if so, uses the CLI path;
    otherwise falls back to the REST path (_rest_search).
    """

    cli_package_name: str = ""
    _cli_checked: Optional[bool] = None

    def _cli_available(self) -> bool:
        if self._cli_checked is None:
            if not self.cli_package_name:
                self._cli_checked = False
            else:
                import importlib
                try:
                    importlib.import_module(self.cli_package_name.replace("-", "_"))
                    self._cli_checked = True
                    logger.debug(
                        "%s: CLI package '%s' available",
                        getattr(self, "name", "skill"),
                        self.cli_package_name,
                    )
                except ImportError:
                    self._cli_checked = False
                    logger.debug(
                        "%s: CLI package '%s' not found, using REST",
                        getattr(self, "name", "skill"),
                        self.cli_package_name,
                    )
        return self._cli_checked  # type: ignore[return-value]

    def _try_cli_or_rest(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 50,
    ) -> List[RetrievalResult]:
        """Dispatch to CLI or REST depending on availability."""
        if self._cli_available():
            try:
                return self._cli_search(entities, query, max_results)  # type: ignore[attr-defined]
            except Exception as exc:
                logger.warning(
                    "%s: CLI search failed (%s), falling back to REST",
                    getattr(self, "name", "skill"),
                    exc,
                )
        return self._rest_search(entities, query, max_results)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Dataset skill base class
# ---------------------------------------------------------------------------

class DatasetRAGSkill(RAGSkill):
    """
    Base class for benchmark dataset skills.

    Dataset skills are RAG sources like any other skill.  The key difference
    is that they contain *labelled* drug–disease (or drug–AE) pairs which can
    serve as both:

      1. Evidence during inference  — register the skill normally.
      2. Held-out evaluation pairs  — simply do NOT register this skill in
         the SkillRegistry when benchmarking on it.  The system must then
         reason purely from the other registered skills.

    ``get_all_pairs()`` enumerates every labelled record, which is useful for
    setting up evaluation loops (e.g. iterating over drug–disease pairs and
    calling the pipeline for each).
    """

    resource_type: str = "Dataset"
    access_mode: str = AccessMode.DATASET

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._loaded = False

    @abstractmethod
    def get_all_pairs(self) -> List[Dict[str, Any]]:
        """
        Return every labelled pair in the dataset as a list of dicts.

        Each dict must have at minimum:
          drug     : str   drug common name
          disease  : str   disease / indication / adverse event name
          label    : str   outcome label (e.g. "Approved", "positive")
        """

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        """Override to populate data from files / network."""
