"""
DrugClaw RAG Skills Package - 68 LLM-Friendly Drug Resources + WebSearch
=========================================================================
Organized by 15 subcategories (from 68DrugResources.xlsx) plus a web_search
skill that wraps DuckDuckGo (free) + PubMed E-utilities (free).

Access modes: REST_API | CLI | LOCAL_FILE | DATASET
CLI-capable: ChEMBL (chembl_webresource_client), ChEBI (libchebipy), KEGG Drug (bioservices)

Implemented skills (25): those with working example.py + SKILL.md in their directory.
Stub skills (43): interface only, not yet implemented — kept for future development.
"""
from .base import RAGSkill, DatasetRAGSkill, RetrievalResult, AccessMode
from .registry import SkillRegistry
from .skill_tree import SkillTree, SkillNode, Subcategory

SubDomain = Subcategory  # legacy alias
Domain = Subcategory     # legacy alias

# --- Implemented skills (25) — have example.py + SKILL.md ---
from .dti import (ChEMBLSkill, BindingDBSkill, DGIdbSkill, OpenTargetsSkill,
    TTDSkill, STITCHSkill)
from .adr import (FAERSSkill, SIDERSkill)
from .drug_knowledgebase import (UniD3Skill, DrugBankSkill, IUPHARSkill,
    DrugCentralSkill, CPICSkill)
from .drug_mechanism import DrugMechDBSkill
from .drug_labeling import (OpenFDASkill, DailyMedSkill, MedlinePlusSkill)
from .drug_ontology import (RxNormSkill, ChEBISkill)
from .drug_repurposing import RepoDBSkill
from .pharmacogenomics import PharmGKBSkill
from .ddi import (MecDDISkill, DDInterSkill, KEGGDrugSkill)
from .drug_review import WebMDReviewsSkill
from .web_search import WebSearchSkill

# --- Stub skills (43) — interface preserved, not registered ---
from .dti import (TarKGSkill, PROMISCUOUSSkill, GDKDSkill, DTCSkill)
from .adr import (nSIDESSkill, VigiAccessSkill, ADReCSSkill)
from .drug_knowledgebase import (DrugsComSkill, PharmKGSkill,
    WHOEssentialMedicinesSkill, FDAOrangeBookSkill)
from .drug_labeling import RxListSkill
from .drug_ontology import (ATCSkill, NDFRTSkill)
from .drug_repurposing import (DRKGSkill, OREGANOSkill, RepurposingHubSkill,
    DrugRepoBankSkill, RepurposeDrugsSkill, DrugRepurposingOnlineSkill,
    CancerDRSkill, EKDRDSkill)
from .drug_toxicity import (UniToxSkill, LiverToxSkill, DILIrankSkill, DILISkill)
from .drug_combination import (DrugCombDBSkill, CDCDBSkill, DrugCombSkill, DCDBSkill)
from .drug_molecular_property import GDSCSkill
from .drug_disease import SemaTyPSkill
from .drug_review import (AskAPatientSkill, DrugsComReviewsSkill)
from .drug_nlp import (DrugEHRQASkill, DDICorpusSkill, DrugProtSkill, ADECorpusSkill,
    N2C22018Skill, CADECSkill, PsyTARSkill, TAC2017ADRSkill, PHEESkill)


def build_default_registry(config) -> SkillRegistry:
    """
    Build a SkillRegistry pre-loaded with implemented skills only.

    Only the 25 skills that have working example.py + SKILL.md are registered.
    Stub skills (43) are NOT registered — their interfaces remain importable
    for future development.
    """
    sc = getattr(config, "SKILL_CONFIGS", {})
    registry = SkillRegistry()

    # ── DTI (6 implemented) ──────────────────────────────────────────
    registry.register(ChEMBLSkill(sc.get("ChEMBL", {})))
    registry.register(BindingDBSkill(sc.get("BindingDB", {})))
    registry.register(DGIdbSkill(sc.get("DGIdb", {})))
    registry.register(OpenTargetsSkill(sc.get("Open Targets Platform", {})))
    registry.register(TTDSkill(sc.get("TTD", {})))
    registry.register(STITCHSkill(sc.get("STITCH", {})))

    # ── ADR (2 implemented) ──────────────────────────────────────────
    registry.register(FAERSSkill(sc.get("FAERS", {})))
    registry.register(SIDERSkill(sc.get("SIDER", {})))

    # ── Drug Knowledgebase (5 implemented) ───────────────────────────
    registry.register(UniD3Skill({
        "graphml_paths": getattr(config, "KG_ENDPOINTS", {}).get("unid3", {}),
        **sc.get("UniD3", {}),
    }))
    registry.register(DrugBankSkill(sc.get("DrugBank", {})))
    registry.register(IUPHARSkill(sc.get("IUPHAR/BPS Guide to Pharmacology", {})))
    registry.register(DrugCentralSkill(sc.get("DrugCentral", {})))
    registry.register(CPICSkill(sc.get("CPIC", {})))

    # ── Drug Mechanism (1 implemented) ───────────────────────────────
    registry.register(DrugMechDBSkill(sc.get("DRUGMECHDB", {})))

    # ── Drug Labeling (3 implemented) ────────────────────────────────
    registry.register(OpenFDASkill(sc.get("openFDA Human Drug", {})))
    registry.register(DailyMedSkill(sc.get("DailyMed", {})))
    registry.register(MedlinePlusSkill(sc.get("MedlinePlus Drug Info", {})))

    # ── Drug Ontology (2 implemented) ────────────────────────────────
    registry.register(RxNormSkill(sc.get("RxNorm", {})))
    registry.register(ChEBISkill(sc.get("ChEBI", {})))

    # ── Drug Repurposing (1 implemented) ─────────────────────────────
    registry.register(RepoDBSkill(sc.get("RepoDB", {})))

    # ── Pharmacogenomics (1 implemented) ─────────────────────────────
    registry.register(PharmGKBSkill(sc.get("PharmGKB", {})))

    # ── DDI (3 implemented) ──────────────────────────────────────────
    registry.register(MecDDISkill(sc.get("MecDDI", {})))
    registry.register(DDInterSkill(sc.get("DDInter", {})))
    registry.register(KEGGDrugSkill(sc.get("KEGG Drug", {})))

    # ── Drug Review (1 implemented) ──────────────────────────────────
    registry.register(WebMDReviewsSkill(sc.get("WebMD Drug Reviews", {})))

    # ── Web Search (always-on) ───────────────────────────────────────
    registry.register(WebSearchSkill(sc.get("WebSearch", {})))

    return registry
