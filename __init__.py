"""
DrugClaw RAG Skills Package - 68 LLM-Friendly Drug Resources + WebSearch
=========================================================================
Organized by 15 subcategories (from 68DrugResources.xlsx) plus a web_search
skill that wraps DuckDuckGo (free) + PubMed E-utilities (free).

Access modes: REST_API | CLI | LOCAL_FILE | DATASET
CLI-capable: ChEMBL (chembl_webresource_client), ChEBI (libchebipy), KEGG Drug (bioservices)
"""
from .base import RAGSkill, DatasetRAGSkill, RetrievalResult, AccessMode
from .registry import SkillRegistry
from .skill_tree import SkillTree, SkillNode, Subcategory

SubDomain = Subcategory  # legacy alias
Domain = Subcategory     # legacy alias

from .dti import (ChEMBLSkill, BindingDBSkill, DGIdbSkill, OpenTargetsSkill,
    TTDSkill, STITCHSkill, TarKGSkill, PROMISCUOUSSkill, GDKDSkill, DTCSkill)
from .adr import (FAERSSkill, SIDERSkill, nSIDESSkill, VigiAccessSkill, ADReCSSkill)
from .drug_knowledgebase import (UniD3Skill, DrugBankSkill, IUPHARSkill, DrugCentralSkill,
    DrugsComSkill, PharmKGSkill, WHOEssentialMedicinesSkill, FDAOrangeBookSkill, CPICSkill)
from .drug_mechanism import DrugMechDBSkill
from .drug_labeling import (OpenFDASkill, DailyMedSkill, RxListSkill, MedlinePlusSkill)
from .drug_ontology import (RxNormSkill, ATCSkill, NDFRTSkill, ChEBISkill)
from .drug_repurposing import (RepoDBSkill, DRKGSkill, OREGANOSkill, RepurposingHubSkill,
    DrugRepoBankSkill, RepurposeDrugsSkill, DrugRepurposingOnlineSkill, CancerDRSkill, EKDRDSkill)
from .pharmacogenomics import PharmGKBSkill
from .ddi import (MecDDISkill, DDInterSkill, KEGGDrugSkill)
from .drug_toxicity import (UniToxSkill, LiverToxSkill, DILIrankSkill, DILISkill)
from .drug_combination import (DrugCombDBSkill, CDCDBSkill, DrugCombSkill, DCDBSkill)
from .drug_molecular_property import GDSCSkill
from .drug_disease import SemaTyPSkill
from .drug_review import (WebMDReviewsSkill, AskAPatientSkill, DrugsComReviewsSkill)
from .drug_nlp import (DrugEHRQASkill, DDICorpusSkill, DrugProtSkill, ADECorpusSkill,
    N2C22018Skill, CADECSkill, PsyTARSkill, TAC2017ADRSkill, PHEESkill)
from .web_search import WebSearchSkill


def build_default_registry(config) -> SkillRegistry:
    """Build a SkillRegistry pre-loaded with all 68 skills from config."""
    sc = getattr(config, "SKILL_CONFIGS", {})
    registry = SkillRegistry()

    # DTI
    registry.register(ChEMBLSkill(sc.get("ChEMBL", {})))
    registry.register(BindingDBSkill(sc.get("BindingDB", {})))
    registry.register(DGIdbSkill(sc.get("DGIdb", {})))
    registry.register(OpenTargetsSkill(sc.get("Open Targets Platform", {})))
    registry.register(TTDSkill(sc.get("TTD", {})))
    registry.register(STITCHSkill(sc.get("STITCH", {})))
    registry.register(TarKGSkill(sc.get("TarKG", {})))
    registry.register(PROMISCUOUSSkill(sc.get("PROMISCUOUS 2.0", {})))
    registry.register(GDKDSkill(sc.get("GDKD", {})))
    registry.register(DTCSkill(sc.get("DTC", {})))

    # ADR
    registry.register(FAERSSkill(sc.get("FAERS", {})))
    registry.register(SIDERSkill(sc.get("SIDER", {})))
    registry.register(nSIDESSkill(sc.get("nSIDES", {})))
    registry.register(VigiAccessSkill(sc.get("VigiAccess", {})))
    registry.register(ADReCSSkill(sc.get("ADReCS", {})))

    # Drug Knowledgebase
    registry.register(UniD3Skill({
        "graphml_paths": getattr(config, "KG_ENDPOINTS", {}).get("unid3", {}),
        **sc.get("UniD3", {}),
    }))
    registry.register(DrugBankSkill(sc.get("DrugBank", {})))
    registry.register(IUPHARSkill(sc.get("IUPHAR/BPS Guide to Pharmacology", {})))
    registry.register(DrugCentralSkill(sc.get("DrugCentral", {})))
    registry.register(DrugsComSkill(sc.get("Drugs.com", {})))
    registry.register(PharmKGSkill(sc.get("PharmKG", {})))
    registry.register(WHOEssentialMedicinesSkill(sc.get("WHO Essential Medicines List", {})))
    registry.register(FDAOrangeBookSkill(sc.get("FDA Orange Book", {})))
    registry.register(CPICSkill(sc.get("CPIC", {})))

    # Drug Mechanism
    registry.register(DrugMechDBSkill(sc.get("DRUGMECHDB", {})))

    # Drug Labeling
    registry.register(OpenFDASkill(sc.get("openFDA Human Drug", {})))
    registry.register(DailyMedSkill(sc.get("DailyMed", {})))
    registry.register(RxListSkill(sc.get("RxList Drug Descriptions", {})))
    registry.register(MedlinePlusSkill(sc.get("MedlinePlus Drug Info", {})))

    # Drug Ontology
    registry.register(RxNormSkill(sc.get("RxNorm", {})))
    registry.register(ATCSkill(sc.get("ATC/DDD", {})))
    registry.register(NDFRTSkill(sc.get("NDF-RT", {})))
    registry.register(ChEBISkill(sc.get("ChEBI", {})))

    # Drug Repurposing
    registry.register(RepoDBSkill(sc.get("RepoDB", {})))
    registry.register(DRKGSkill(sc.get("DRKG", {})))
    registry.register(OREGANOSkill(sc.get("OREGANO", {})))
    registry.register(RepurposingHubSkill(sc.get("Drug Repurposing Hub", {})))
    registry.register(DrugRepoBankSkill(sc.get("DrugRepoBank", {})))
    registry.register(RepurposeDrugsSkill(sc.get("RepurposeDrugs", {})))
    registry.register(DrugRepurposingOnlineSkill(sc.get("DrugRepurposing Online", {})))
    registry.register(CancerDRSkill(sc.get("CancerDR", {})))
    registry.register(EKDRDSkill(sc.get("EK-DRD", {})))

    # Pharmacogenomics
    registry.register(PharmGKBSkill(sc.get("PharmGKB", {})))

    # DDI
    registry.register(MecDDISkill(sc.get("MecDDI", {})))
    registry.register(DDInterSkill(sc.get("DDInter", {})))
    registry.register(KEGGDrugSkill(sc.get("KEGG Drug", {})))

    # Drug Toxicity
    registry.register(UniToxSkill(sc.get("UniTox", {})))
    registry.register(LiverToxSkill(sc.get("LiverTox", {})))
    registry.register(DILIrankSkill(sc.get("DILIrank", {})))
    registry.register(DILISkill(sc.get("DILI", {})))

    # Drug Combination
    registry.register(DrugCombDBSkill(sc.get("DrugCombDB", {})))
    registry.register(CDCDBSkill(sc.get("CDCDB", {})))
    registry.register(DrugCombSkill(sc.get("DrugComb", {})))
    registry.register(DCDBSkill(sc.get("DCDB", {})))

    # Drug Molecular Property
    registry.register(GDSCSkill(sc.get("GDSC", {})))

    # Drug Disease
    registry.register(SemaTyPSkill(sc.get("SemaTyP", {})))

    # Drug Review
    registry.register(WebMDReviewsSkill(sc.get("WebMD Drug Reviews", {})))
    registry.register(AskAPatientSkill(sc.get("askapatient", {})))
    registry.register(DrugsComReviewsSkill(sc.get("Drug Reviews (Drugs.com)", {})))

    # Drug NLP
    registry.register(DrugEHRQASkill(sc.get("DrugEHRQA", {})))
    registry.register(DDICorpusSkill(sc.get("DDI Corpus 2013", {})))
    registry.register(DrugProtSkill(sc.get("DrugProt", {})))
    registry.register(ADECorpusSkill(sc.get("ADE Corpus", {})))
    registry.register(N2C22018Skill(sc.get("n2c2 2018 Track 2", {})))
    registry.register(CADECSkill(sc.get("CADEC", {})))
    registry.register(PsyTARSkill(sc.get("PsyTAR", {})))
    registry.register(TAC2017ADRSkill(sc.get("TAC 2017 ADR", {})))
    registry.register(PHEESkill(sc.get("PHEE", {})))

    # Web Search (free, always-on)
    registry.register(WebSearchSkill(sc.get("WebSearch", {})))

    return registry
