"""
Skill Tree for DrugClaw RAG retrieval.

Organises all 68 LLM-friendly resources from 68DrugResources.xlsx into a
15-subcategory tree so the RetrieverAgent can navigate to the right skills
without scanning a flat list.

Tree layout (15 subcategories as top-level nodes → leaf skill nodes)
-------------------------------------------------------------------
 1. Drug-Target Interaction (DTI)       dti
 2. Adverse Drug Reaction (ADR)         adr
 3. Drug Knowledgebase                  drug_knowledgebase
 4. Drug Mechanism                      drug_mechanism
 5. Drug Labeling/Info                  drug_labeling
 6. Drug Ontology/Terminology           drug_ontology
 7. Drug Repurposing                    drug_repurposing
 8. Pharmacogenomics                    pharmacogenomics
 9. Drug-Drug Interaction (DDI)         ddi
10. Drug Toxicity                       drug_toxicity
11. Drug Combination/Synergy            drug_combination
12. Drug Molecular Property             drug_molecular_property
13. Drug–Disease Associations           drug_disease
14. Drug Review/Patient Report          drug_review
15. Drug NLP/Text Mining                drug_nlp

Each leaf node carries:
  name         — resource name (= RAGSkill.name)
  aim          — one-line purpose
  data_range   — coverage note
  access_mode  — REST_API | CLI | LOCAL_FILE | DATASET
  implemented  — True if the skill class exists and is registered
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SkillNode:
    name: str
    aim: str
    data_range: str
    access_mode: str = "REST_API"    # REST_API | CLI | LOCAL_FILE | DATASET
    implemented: bool = False        # set True when registered in SkillRegistry

    def to_prompt_line(self, indent: int = 4) -> str:
        marker = "✓" if self.implemented else "○"
        mode_tag = f"[{self.access_mode}]" if self.access_mode != "REST_API" else ""
        return (
            f"{' ' * indent}{marker} {self.name}{' ' + mode_tag if mode_tag else ''}"
            f" — {self.aim}"
        )


@dataclass
class Subcategory:
    key: str            # e.g. "dti"
    name: str           # e.g. "Drug-Target Interaction (DTI)"
    description: str
    skills: List[SkillNode] = field(default_factory=list)

    def to_prompt_block(self, implemented_only: bool = False) -> str:
        lines = [f"[{self.key}] {self.name} — {self.description}"]
        for node in self.skills:
            if implemented_only and not node.implemented:
                continue
            lines.append(node.to_prompt_line())
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Legacy aliases (kept for backward compatibility with SkillRegistry)
# ---------------------------------------------------------------------------
SubDomain = Subcategory
Domain = Subcategory


@dataclass
class _LegacyDomain:
    """Thin wrapper so SkillRegistry.skill_tree.domains still works."""
    name: str
    description: str
    subdomains: List[Subcategory] = field(default_factory=list)

    @property
    def all_skills(self) -> List[SkillNode]:
        return [n for sd in self.subdomains for n in sd.skills]


# ---------------------------------------------------------------------------
# Skill Tree
# ---------------------------------------------------------------------------

class SkillTree:
    """
    15-subcategory skill tree covering all 68 LLM-friendly drug resources.

    The tree is used by:
      - SkillRegistry.skill_tree_prompt   → full tree for the system prompt
      - SkillRegistry.skill_tree_compact  → compact one-liner per skill
      - SkillRegistry.get_skills_for_query → keyword-based skill pre-selection
    """

    def __init__(self) -> None:
        self.subcategories: List[Subcategory] = _build_subcategories()

        # Legacy compatibility: expose .domains with a flat wrapper so the
        # existing registry.get_skills_for_query() loop still works.
        self.domains: List[_LegacyDomain] = [
            _LegacyDomain(
                name=sc.name,
                description=sc.description,
                subdomains=[sc],   # one subdomain == the subcategory itself
            )
            for sc in self.subcategories
        ]

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def all_skill_nodes(self) -> List[SkillNode]:
        return [n for sc in self.subcategories for n in sc.skills]

    def get_subcategory(self, key: str) -> Optional[Subcategory]:
        for sc in self.subcategories:
            if sc.key == key:
                return sc
        return None

    def get_node(self, name: str) -> Optional[SkillNode]:
        for node in self.all_skill_nodes():
            if node.name == name:
                return node
        return None

    # ------------------------------------------------------------------
    # Prompt rendering
    # ------------------------------------------------------------------

    def to_prompt_context(self, implemented_only: bool = False) -> str:
        """
        Full skill tree formatted for the RetrieverAgent system prompt.

        ✓  = implemented skill (callable)
        ○  = catalogued but not yet implemented
        """
        header = (
            "=== DrugClaw Skill Tree (68 LLM-Friendly Drug Resources) ===\n"
            "15 subcategories — navigate to the right one for your query.\n"
            "✓ = implemented & available   ○ = catalogued, not yet callable\n"
        )
        blocks = [
            sc.to_prompt_block(implemented_only=implemented_only)
            for sc in self.subcategories
        ]
        return header + "\n\n".join(blocks)

    def to_compact_prompt(self) -> str:
        """One-liner per implemented skill: name → subcategory → aim."""
        lines: List[str] = []
        for sc in self.subcategories:
            for node in sc.skills:
                if node.implemented:
                    lines.append(
                        f"  {node.name:40s} [{sc.key:25s}] {node.aim}"
                    )
        return (
            "Implemented skills (name → subcategory → aim):\n"
            + ("\n".join(lines) if lines else "  (none)")
        )

    # ------------------------------------------------------------------
    # Two-stage LLM selection prompts
    # ------------------------------------------------------------------

    def stage1_subcategory_prompt(self) -> str:
        """
        Stage 1 prompt: list all 15 subcategories with one-line descriptions
        so the LLM can select the most relevant subcategory key.

        Returns a compact string; does NOT include skill names to save tokens.
        """
        lines = [
            "Select the most relevant subcategory key for the query.\n"
            "Subcategories:\n"
        ]
        for i, sc in enumerate(self.subcategories, 1):
            lines.append(f"  {i:2d}. [{sc.key}] {sc.name} — {sc.description}")
        lines.append(
            "\nReply with the subcategory key only, e.g.: dti"
        )
        return "\n".join(lines)

    def stage2_skill_prompt(self, subcategory_key: str) -> str:
        """
        Stage 2 prompt: given a subcategory key, list only the skill names
        and their one-line aims within that subcategory.

        Minimal token footprint — no data_range or access_mode details.
        """
        sc = self.get_subcategory(subcategory_key)
        if sc is None:
            return f"Unknown subcategory: {subcategory_key}"
        lines = [
            f"Subcategory: [{sc.key}] {sc.name}\n"
            f"Select one or more skills for the query.\n"
        ]
        for node in sc.skills:
            marker = "✓" if node.implemented else "○"
            lines.append(f"  {marker} {node.name} — {node.aim}")
        lines.append(
            "\nReply with skill name(s) separated by commas, e.g.: ChEMBL, DGIdb"
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tree data — all 68 resources from 68DrugResources.xlsx
# ---------------------------------------------------------------------------

def _build_subcategories() -> List[Subcategory]:
    return [

        # ------------------------------------------------------------------ #
        #  1. Drug-Target Interaction (DTI)                                   #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="dti",
            name="Drug-Target Interaction (DTI)",
            description=(
                "Binding affinities, bioactivity, target databases; "
                "use for mechanism-of-action and target discovery queries."
            ),
            skills=[
                SkillNode(
                    "ChEMBL", "Bioactivity reasoning",
                    "Drug–target IC50/Ki/EC50 across 14 000+ targets",
                    access_mode="CLI",   # chembl_webresource_client
                ),
                SkillNode(
                    "Open Targets Platform", "Drug-target evidence",
                    "Curated + machine-learning drug-target evidence scores",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "DGIdb", "Drug–gene interactions",
                    "Curated drug–gene interaction database (NCI, ClinVar, etc.)",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "TTD", "Therapeutic target database",
                    "Approved/clinical/experimental targets with drug linkages",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "BindingDB", "Binding affinity data",
                    "Experimentally measured binding constants (Ki, Kd, IC50)",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "TarKG", "Target knowledge graph",
                    "Drug-target KG linking targets to diseases via pathways",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "STITCH", "Drug–protein interactions",
                    "Chemical–protein interaction network (STRING extension)",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "PROMISCUOUS 2.0", "Drug polypharmacology",
                    "Drug–protein interaction profiles for polypharmacology",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "GDKD", "Genomics-drug knowledge",
                    "Genomics-Drug Knowledge Database from Synapse",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "DTC", "Drug target commons",
                    "Community-curated drug-target bioactivity database",
                    access_mode="LOCAL_FILE",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        #  2. Adverse Drug Reaction (ADR)                                     #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="adr",
            name="Adverse Drug Reaction (ADR)",
            description=(
                "Post-market safety signals, side effects, adverse events; "
                "use for safety profiling and pharmacovigilance queries."
            ),
            skills=[
                SkillNode(
                    "FAERS", "Post-market drug safety surveillance",
                    "FDA spontaneous adverse event reports (all marketed drugs)",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "SIDER", "Side effect resource",
                    "Drug–side-effect associations from package inserts",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "nSIDES", "Adverse drug effects (broad)",
                    "Off-label and on-label adverse effects via NLP on EHRs",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "VigiAccess", "WHO pharmacovigilance",
                    "WHO global adverse reaction database (VigiBase summary)",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "ADReCS", "ADR classification system",
                    "Hierarchical adverse drug reaction classification",
                    access_mode="REST_API",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        #  3. Drug Knowledgebase                                              #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_knowledgebase",
            name="Drug Knowledgebase",
            description=(
                "Comprehensive drug information encyclopedias and KGs; "
                "use as primary sources for drug properties, mechanisms, and indications."
            ),
            skills=[
                SkillNode(
                    "UniD3", "Drug discovery knowledge graph",
                    "Multi-KG + drug-disease datasets from 150 000+ PubMed articles",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "DrugBank", "Comprehensive drug reference",
                    "Drug structures, pharmacology, targets, interactions",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "IUPHAR/BPS Guide to Pharmacology", "Pharmacology reference",
                    "Expert-curated targets, drugs, and pharmacological data",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "DrugCentral", "Drug information resource",
                    "FDA-approved drug information, indications, targets",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "Drugs.com", "Consumer drug information",
                    "Drug monographs, interactions, and patient education",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "PharmKG", "Pharmaceutical knowledge graph",
                    "Multi-relational drug KG (drug-gene-disease-pathway)",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "WHO Essential Medicines List", "Essential medicines",
                    "WHO list of essential medicines with therapeutic category",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "FDA Orange Book", "Approved drug products",
                    "FDA-approved drugs with bioequivalence and patent info",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "CPIC", "Clinical pharmacogenomics",
                    "CPIC guidelines linking genes/variants to drug dosing",
                    access_mode="REST_API",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        #  4. Drug Mechanism                                                  #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_mechanism",
            name="Drug Mechanism",
            description=(
                "Curated mechanism-of-action paths and biological mechanism graphs; "
                "use to explain how a drug exerts its therapeutic effect."
            ),
            skills=[
                SkillNode(
                    "DRUGMECHDB", "Drug mechanism-of-action paths",
                    "Curated MoA paths linking drugs to diseases via biological graphs",
                    access_mode="REST_API",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        #  5. Drug Labeling/Info                                              #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_labeling",
            name="Drug Labeling/Info",
            description=(
                "Official drug labels, prescribing information, and monographs; "
                "use for dosing, contraindications, and regulatory information."
            ),
            skills=[
                SkillNode(
                    "openFDA Human Drug", "FDA drug label search",
                    "Structured FDA drug labels (adverse events, dosing, warnings)",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "DailyMed", "Official drug labels (NIH)",
                    "FDA-approved drug labeling from NIH DailyMed",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "RxList Drug Descriptions", "Drug monographs",
                    "Clinical drug descriptions including mechanism and dosing",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "MedlinePlus Drug Info", "Patient drug information",
                    "NIH MedlinePlus drug information for patients and clinicians",
                    access_mode="REST_API",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        #  6. Drug Ontology/Terminology                                       #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_ontology",
            name="Drug Ontology/Terminology",
            description=(
                "Standardized drug terminologies, ontologies, and classification systems; "
                "use for drug normalization, coding, and hierarchical classification."
            ),
            skills=[
                SkillNode(
                    "RxNorm", "Drug name normalization",
                    "NLM normalized drug names linking to NDC, RxCUI, and clinical concepts",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "ATC/DDD", "WHO drug classification",
                    "Anatomical Therapeutic Chemical classification + daily doses",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "NDF-RT", "National drug file taxonomy",
                    "VA National Drug File ontology of drug classes and roles",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "ChEBI", "Chemical entity ontology",
                    "Ontology of chemical entities with biological roles",
                    access_mode="CLI",   # libchebipy
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        #  7. Drug Repurposing                                                #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_repurposing",
            name="Drug Repurposing",
            description=(
                "Drug repositioning datasets, screening libraries, and repurposing KGs; "
                "use for identifying new indications for approved drugs."
            ),
            skills=[
                SkillNode(
                    "RepoDB", "Drug repositioning outcomes",
                    "Labelled drug-disease repositioning pairs from clinical trials",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "OREGANO", "Drug repurposing candidates",
                    "Drug repurposing predictions with clinical evidence",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "DRKG", "Drug repurposing KG",
                    "Multi-relational KG integrating DrugBank, Hetionet, STRING, etc.",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "Drug Repurposing Hub", "Repurposing screening library",
                    "Broad-spectrum repurposing library with mechanism annotations",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "DrugRepoBank", "Repurposing repository",
                    "Curated drug repurposing data with clinical trial evidence",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "RepurposeDrugs", "Repurposing portal",
                    "Open drug repurposing portal with disease-drug associations",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "DrugRepurposing Online", "Repurposing predictions",
                    "Computational drug repurposing predictions database",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "CancerDR", "Cancer drug resistance",
                    "Drug resistance mutations and cancer drug sensitivity",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "EK-DRD", "Expert knowledge drug repurposing",
                    "Expert knowledge-based drug repurposing database",
                    access_mode="REST_API",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        #  8. Pharmacogenomics                                                #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="pharmacogenomics",
            name="Pharmacogenomics",
            description=(
                "Variant-drug relationships, PGx guidelines, and clinical pharmacogenomics; "
                "use for precision medicine and variant-based drug response queries."
            ),
            skills=[
                SkillNode(
                    "PharmGKB", "Pharmacogenomics knowledge base",
                    "Curated PGx knowledge: variant-drug-outcome annotations",
                    access_mode="REST_API",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        #  9. Drug-Drug Interaction (DDI)                                     #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="ddi",
            name="Drug-Drug Interaction (DDI)",
            description=(
                "Drug-drug interaction databases with mechanisms; "
                "use for polypharmacy safety and interaction mechanism queries."
            ),
            skills=[
                SkillNode(
                    "MecDDI", "Mechanistic DDI database",
                    "DDI database with mechanistic explanations",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "DDInter", "DDI interaction database",
                    "Comprehensive DDI database with clinical evidence",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "KEGG Drug", "KEGG drug interactions",
                    "Drug-drug interactions from KEGG with pathway context",
                    access_mode="CLI",   # bioservices
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        # 10. Drug Toxicity                                                   #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_toxicity",
            name="Drug Toxicity",
            description=(
                "Hepatotoxicity, organ toxicity, and high-throughput tox datasets; "
                "use for safety assessment and DILI prediction queries."
            ),
            skills=[
                SkillNode(
                    "UniTox", "Drug toxicity database",
                    "Large-scale drug toxicity database from clinical notes",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "LiverTox", "Drug-induced liver injury",
                    "NCBI LiverTox clinical descriptions of DILI by drug",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "DILIrank", "DILI severity ranking",
                    "FDA DILI severity ranking (most-DILI-concern to no-DILI-concern)",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "DILI", "DILI benchmark dataset",
                    "Drug-induced liver injury benchmark dataset (Xu et al.)",
                    access_mode="LOCAL_FILE",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        # 11. Drug Combination/Synergy                                        #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_combination",
            name="Drug Combination/Synergy",
            description=(
                "Drug synergy and combination datasets; "
                "use for combination therapy and synergy prediction queries."
            ),
            skills=[
                SkillNode(
                    "DrugCombDB", "Drug combination database",
                    "Human/animal drug combination synergy/antagonism records",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "CDCDB", "Cancer drug combination",
                    "Cancer drug combination experimental outcomes",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "DrugComb", "Drug combination screening",
                    "Drug combination screening data across cancer cell lines",
                    access_mode="LOCAL_FILE",
                ),
                SkillNode(
                    "DCDB", "Drug combination reference",
                    "Drug Combination Database with efficacy information",
                    access_mode="LOCAL_FILE",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        # 12. Drug Molecular Property                                         #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_molecular_property",
            name="Drug Molecular Property",
            description=(
                "Drug sensitivity, molecular descriptors, and physicochemical properties; "
                "use for QSAR, ADMET, and structure-activity relationship queries."
            ),
            skills=[
                SkillNode(
                    "GDSC", "Genomics of drug sensitivity in cancer",
                    "Drug sensitivity (IC50) profiles across 1000+ cancer cell lines",
                    access_mode="LOCAL_FILE",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        # 13. Drug–Disease Associations                                       #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_disease",
            name="Drug–Disease Associations",
            description=(
                "Semantic drug-disease association databases and KGs; "
                "use for indication discovery and disease-drug linkage queries."
            ),
            skills=[
                SkillNode(
                    "SemaTyP", "Semantic drug-disease KG",
                    "Drug-disease KG built from semantic types in biomedical literature",
                    access_mode="LOCAL_FILE",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        # 14. Drug Review/Patient Report                                      #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_review",
            name="Drug Review/Patient Report",
            description=(
                "Patient-reported drug reviews and sentiment datasets; "
                "use for patient experience, adherence, and real-world effectiveness queries."
            ),
            skills=[
                SkillNode(
                    "WebMD Drug Reviews", "Patient drug reviews (WebMD)",
                    "362 000+ patient drug reviews from WebMD",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "askapatient", "Patient experience reports",
                    "Patient-reported drug experiences from AskAPatient.com",
                    access_mode="REST_API",
                ),
                SkillNode(
                    "Drug Reviews (Drugs.com)", "Drug reviews dataset",
                    "UCI/Drugs.com drug reviews with patient ratings",
                    access_mode="DATASET",
                ),
            ],
        ),

        # ------------------------------------------------------------------ #
        # 15. Drug NLP/Text Mining                                            #
        # ------------------------------------------------------------------ #
        Subcategory(
            key="drug_nlp",
            name="Drug NLP/Text Mining",
            description=(
                "Annotated NLP corpora for drug information extraction; "
                "use as training/evaluation data for drug NER, RE, and event extraction."
            ),
            skills=[
                SkillNode(
                    "DrugEHRQA", "Drug QA over EHR",
                    "Question-answering dataset over structured/unstructured EHRs",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "DDI Corpus 2013", "DDI extraction corpus",
                    "Annotated DDI extraction corpus from drug labels/MEDLINE",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "DrugProt", "Drug-protein relation corpus",
                    "BioCreative VII drug-protein relation extraction corpus",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "ADE Corpus", "Adverse drug event corpus",
                    "Annotated adverse drug event corpus from case reports",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "n2c2 2018 Track 2", "Clinical NLP ADE corpus",
                    "n2c2 2018 adverse drug event extraction from EHRs",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "CADEC", "Clinical ADE corpus",
                    "CSIRO annotated drug side-effect corpus from social media",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "PsyTAR", "Psychiatric drug ADE corpus",
                    "Annotated psychiatric drug adverse events from patient forums",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "TAC 2017 ADR", "TAC ADR extraction corpus",
                    "TAC 2017 adverse drug reaction extraction from labels",
                    access_mode="DATASET",
                ),
                SkillNode(
                    "PHEE", "Pharmacovigilance event corpus",
                    "Pharmacovigilance event extraction corpus (EMNLP 2022)",
                    access_mode="DATASET",
                ),
            ],
        ),
    ]
