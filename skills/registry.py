"""
SkillRegistry — central hub for all RAG skills in DrugClaw.

Skills are now organized by subcategory (15 categories from 68DrugResources.xlsx)
rather than by resource type (KG / Database / Dataset).

Backward compatibility is maintained: the existing agent_retriever still
calls get_database() / get_entity_relationships().
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from .base import RAGSkill, RetrievalResult
from .skill_tree import SkillTree

logger = logging.getLogger(__name__)


class SkillRegistry:
    """
    Maintains a catalogue of RAGSkill instances and dispatches queries.

    Usage
    -----
    registry = SkillRegistry()
    registry.register(ChEMBLSkill())

    # High-level query (returns RetrievalResult list)
    results = registry.query(
        skill_names=["ChEMBL", "DGIdb"],
        entities={"drug": ["imatinib"], "disease": ["CML"]},
        query="imatinib mechanism CML",
    )

    # Filter by subcategory
    dti_skills = registry.list_by_subcategory("dti")

    # Legacy compatibility shim
    db = registry.get_database("ChEMBL")
    rows = db.get_entity_relationships({"drug": ["imatinib"]})
    """

    def __init__(self) -> None:
        self._skills: Dict[str, RAGSkill] = {}
        self.skill_tree: SkillTree = SkillTree()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, skill: RAGSkill) -> None:
        """Register a skill instance (keyed by skill.name)."""
        self._skills[skill.name] = skill
        logger.debug(
            "Registered skill: %s [subcategory=%s, access=%s]",
            skill.name, skill.subcategory, skill.access_mode,
        )

    def unregister(self, name: str) -> None:
        """Remove a skill by name."""
        self._skills.pop(name, None)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def list_skills(self, resource_type: Optional[str] = None) -> List[str]:
        """Return names of all (optionally filtered by resource_type) registered skills."""
        if resource_type is None:
            return list(self._skills.keys())
        return [
            n for n, s in self._skills.items()
            if s.resource_type.upper() == resource_type.upper()
        ]

    def list_by_subcategory(self, subcategory: str) -> List[str]:
        """Return skill names in the given subcategory (e.g. 'dti', 'adr')."""
        return [
            n for n, s in self._skills.items()
            if s.subcategory == subcategory
        ]

    def list_by_access_mode(self, access_mode: str) -> List[str]:
        """Return skill names with the given access mode (e.g. 'CLI', 'REST_API')."""
        return [
            n for n, s in self._skills.items()
            if s.access_mode.upper() == access_mode.upper()
        ]

    def get_skill(self, name: str) -> Optional[RAGSkill]:
        return self._skills.get(name)

    @property
    def kg_database_descriptions(self) -> str:
        """Multi-line string for LLM prompts, grouped by subcategory."""
        lines = []
        by_subcat: Dict[str, List[RAGSkill]] = {}
        for skill in self._skills.values():
            by_subcat.setdefault(skill.subcategory, []).append(skill)
        for subcat in sorted(by_subcat):
            lines.append(f"\n[{subcat}]")
            for skill in by_subcat[subcat]:
                avail = "✓" if skill.is_available() else "✗ (unavailable)"
                mode = f"[{skill.access_mode}]"
                lines.append(
                    f"  - {skill.name} {mode} {avail}: {skill.get_description()}"
                )
        return "\n".join(lines) if lines else "(no skills registered)"

    @property
    def skill_tree_prompt(self) -> str:
        """Full skill tree for the RetrieverAgent system prompt (15 subcategories)."""
        registered = set(self._skills.keys())
        for node in self.skill_tree.all_skill_nodes():
            node.implemented = node.name in registered
        return self.skill_tree.to_prompt_context(implemented_only=False)

    @property
    def skill_tree_compact(self) -> str:
        """One-liner per registered skill: name → subcategory → aim."""
        registered = set(self._skills.keys())
        for node in self.skill_tree.all_skill_nodes():
            node.implemented = node.name in registered
        return self.skill_tree.to_compact_prompt()

    # ------------------------------------------------------------------
    # Two-stage LLM selection prompts
    # ------------------------------------------------------------------

    def get_subcategory_selection_prompt(self) -> str:
        """
        Stage 1 — prompt for LLM to select the most relevant subcategory.

        Returns a compact string listing all 15 subcategories with one-line
        descriptions.  The LLM should reply with the subcategory key (e.g.
        ``dti``) which is then passed to :meth:`get_skill_selection_prompt`.

        Token-efficient: does not list individual skill names.
        """
        return self.skill_tree.stage1_subcategory_prompt()

    def get_skill_selection_prompt(self, subcategory: str) -> str:
        """
        Stage 2 — prompt for LLM to select specific skill(s) within a subcategory.

        Parameters
        ----------
        subcategory : str
            Key returned by the LLM in Stage 1 (e.g. ``dti``, ``adr``).

        Returns a short prompt listing only skill names + one-line aims
        within the given subcategory.  Implemented skills are marked ✓;
        unavailable stubs are marked ○.

        The LLM should reply with one or more skill names (comma-separated).
        """
        registered = set(self._skills.keys())
        sc = self.skill_tree.get_subcategory(subcategory)
        if sc is not None:
            for node in sc.skills:
                node.implemented = node.name in registered
        return self.skill_tree.stage2_skill_prompt(subcategory)

    def get_skills_for_query(self, query: str) -> List[str]:
        """
        Use the skill tree to find registered skills most relevant to *query*.
        Returns skill names (registered & available) sorted by relevance score.
        """
        registered = set(self._skills.keys())
        for node in self.skill_tree.all_skill_nodes():
            node.implemented = node.name in registered

        q = query.lower()
        keywords = set(q.split())

        scored: Dict[str, int] = {}
        for sc in self.skill_tree.subcategories:
            sc_text = (sc.key + " " + sc.name + " " + sc.description).lower()
            for node in sc.skills:
                if node.name not in registered:
                    continue
                node_text = (
                    node.aim + " " + node.data_range + " " + sc_text
                ).lower()
                score = sum(1 for kw in keywords if kw in node_text)
                if score > 0:
                    scored[node.name] = scored.get(node.name, 0) + score

        return sorted(scored, key=lambda n: -scored[n])

    def get_skills_for_subcategory_query(
        self, subcategory: str, query: str = ""
    ) -> List[str]:
        """Return registered & available skills for a specific subcategory."""
        sc = self.skill_tree.get_subcategory(subcategory)
        if sc is None:
            return []
        registered = set(self._skills.keys())
        names = [
            node.name for node in sc.skills
            if node.name in registered
            and self._skills[node.name].is_available()
        ]
        if not query:
            return names
        q = query.lower()
        keywords = set(q.split())
        scored = {}
        for name in names:
            node = self.skill_tree.get_node(name)
            if node:
                text = (node.aim + " " + node.data_range).lower()
                scored[name] = sum(1 for kw in keywords if kw in text)
        return sorted(names, key=lambda n: -scored.get(n, 0))

    # ------------------------------------------------------------------
    # Skill descriptions & example code for Code Agent
    # ------------------------------------------------------------------

    # Mapping from skill name → example file name in the examples/ folder
    _SKILL_EXAMPLE_MAP: Dict[str, str] = {
        "UniD3": "01_UniD3.py",
        "RepoDB": "02_RepoDB.py",
        "FAERS": "03_FAERS.py",
        "DRUGMECHDB": "04_DRUGMECHDB.py",
        "openFDA Human Drug": "05_openFDA_Human_Drug.py",
        "DailyMed": "06_DailyMed.py",
        "DrugBank": "07_DrugBank.py",
        "RxNorm": "08_RxNorm.py",
        "DrugEHRQA": "09_DrugEHRQA.py",
        "WebMD Drug Reviews": "10_WebMD_Drug_Reviews.py",
        "ChEMBL": "11_ChEMBL.py",
        "Open Targets Platform": "12_Open_Targets_Platform.py",
        "IUPHAR/BPS Guide to Pharmacology": "13_IUPHAR_BPS_Guide_to_Pharmacology.py",
        "SIDER": "14_SIDER.py",
        "nSIDES": "15_nSIDES.py",
        "DGIdb": "16_DGIdb.py",
        "TTD": "17_TTD.py",
        "DrugCentral": "18_DrugCentral.py",
        "MecDDI": "19_MecDDI.py",
        "DDInter": "20_DDInter.py",
        "STITCH": "21_STITCH.py",
        "PharmGKB": "22_PharmGKB.py",
        "BindingDB": "23_BindingDB.py",
        "DRKG": "24_DRKG.py",
        "OREGANO": "25_OREGANO.py",
        "Drug Repurposing Hub": "26_Drug_Repurposing_Hub.py",
        "ATC/DDD": "27_ATC_DDD.py",
        "NDF-RT": "28_NDF_RT.py",
        "ChEBI": "29_ChEBI.py",
        "DrugCombDB": "30_DrugCombDB.py",
        "CDCDB": "31_CDCDB.py",
        "DrugComb": "32_DrugComb.py",
        "DCDB": "33_DCDB.py",
        "LiverTox": "34_LiverTox.py",
        "DILIrank": "35_DILIrank.py",
        "DILI": "36_DILI.py",
        "UniTox": "37_UniTox.py",
        "PharmKG": "38_PharmKG.py",
        "WHO Essential Medicines List": "39_WHO_Essential_Medicines_List.py",
        "FDA Orange Book": "40_FDA_Orange_Book.py",
        "CPIC": "41_CPIC.py",
        "TarKG": "42_TarKG.py",
        "PROMISCUOUS 2.0": "43_PROMISCUOUS.py",
        "GDKD": "44_GDKD.py",
        "DTC": "45_DTC.py",
        "VigiAccess": "46_VigiAccess.py",
        "ADReCS": "47_ADReCS.py",
        "DrugRepoBank": "48_DrugRepoBank.py",
        "RepurposeDrugs": "49_RepurposeDrugs.py",
        "DrugRepurposing Online": "50_DrugRepurposing_Online.py",
        "CancerDR": "51_CancerDR.py",
        "EK-DRD": "52_EK_DRD.py",
        "GDSC": "53_GDSC.py",
        "SemaTyP": "54_SemaTyP.py",
        "Drugs.com": "55_Drugs_com.py",
        "RxList Drug Descriptions": "56_RxList.py",
        "MedlinePlus Drug Info": "57_MedlinePlus.py",
        "askapatient": "58_askapatient.py",
        "Drug Reviews (Drugs.com)": "59_Drug_Reviews_Drugs_com.py",
        "DDI Corpus 2013": "60_DDI_Corpus_2013.py",
        "DrugProt": "61_DrugProt.py",
        "ADE Corpus": "62_ADE_Corpus.py",
        "n2c2 2018 Track 2": "63_n2c2_2018.py",
        "CADEC": "64_CADEC.py",
        "PsyTAR": "65_PsyTAR.py",
        "TAC 2017 ADR": "66_TAC_2017_ADR.py",
        "PHEE": "67_PHEE.py",
        "KEGG Drug": "68_KEGG_Drug.py",
        "DrugMechDB": "04_DRUGMECHDB.py",
    }

    def get_skill_description(self, name: str) -> str:
        """
        Return a human-readable description of a skill for the Code Agent.

        Includes skill name, subcategory, aim, data_range, access_mode.
        """
        skill = self._skills.get(name)
        if skill is None:
            return f"Skill '{name}' not registered."
        return (
            f"Skill: {skill.name}\n"
            f"Subcategory: {skill.subcategory}\n"
            f"Access Mode: {skill.access_mode}\n"
            f"Aim: {skill.aim}\n"
            f"Data Range: {skill.data_range}\n"
        )

    def get_skill_example_code(self, name: str) -> str:
        """
        Return the example usage code for a skill (from examples/ folder).

        Falls back to the skill's get_description() if no example file found.
        """
        example_file = self._SKILL_EXAMPLE_MAP.get(name, "")
        if example_file:
            examples_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "examples",
            )
            example_path = os.path.join(examples_dir, example_file)
            if os.path.exists(example_path):
                try:
                    with open(example_path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception:
                    pass
        # Fallback
        skill = self._skills.get(name)
        if skill is not None:
            return f"# No example file for {name}\n# {skill.get_description()}"
        return f"# No example available for {name}"

    def get_skill_info_for_coder(self, name: str) -> str:
        """
        Return combined skill description + example code for the Code Agent.
        """
        desc = self.get_skill_description(name)
        example = self.get_skill_example_code(name)
        return f"{desc}\n--- Example Code ---\n{example}"

    def get_all_skill_summaries(self) -> str:
        """
        Return a compact summary of all registered skills for the Code Agent
        to select from (name + aim + access_mode, one per line).
        """
        lines = []
        for name, skill in self._skills.items():
            if skill.is_available():
                lines.append(
                    f"- {name} [{skill.access_mode}] ({skill.subcategory}): {skill.aim}"
                )
        return "\n".join(lines) if lines else "(no skills registered)"

    # ------------------------------------------------------------------
    # Query dispatch
    # ------------------------------------------------------------------

    def query(
        self,
        skill_names: List[str],
        entities: Dict[str, List[str]],
        query: str = "",
        max_results_per_skill: int = 50,
    ) -> List[Dict[str, Any]]:
        """Call each named skill and aggregate results as plain dicts."""
        aggregated: List[Dict[str, Any]] = []
        for name in skill_names:
            skill = self._skills.get(name)
            if skill is None:
                logger.warning("Skill '%s' not registered — skipping.", name)
                continue
            if not skill.is_available():
                logger.warning("Skill '%s' unavailable — skipping.", name)
                continue
            try:
                results: List[RetrievalResult] = skill.retrieve(
                    entities=entities,
                    query=query,
                    max_results=max_results_per_skill,
                )
                aggregated.extend(r.to_dict() for r in results)
                logger.debug("Skill '%s' returned %d results.", name, len(results))
            except Exception as exc:
                logger.error("Skill '%s' raised: %s", name, exc, exc_info=True)
        return aggregated

    # ------------------------------------------------------------------
    # Legacy KGManager compatibility shim
    # ------------------------------------------------------------------

    def get_database(self, name: str) -> Optional["_LegacyDBAdapter"]:
        """Return a shim with get_entity_relationships() for legacy code paths."""
        skill = self._skills.get(name)
        if skill is None:
            return None
        return _LegacyDBAdapter(skill)


class _LegacyDBAdapter:
    """Thin wrapper giving a RAGSkill the old KGInterface surface."""

    def __init__(self, skill: RAGSkill) -> None:
        self._skill = skill

    def get_entity_relationships(
        self, entities: Dict[str, List[str]], **kwargs: Any
    ) -> List[Dict[str, Any]]:
        results = self._skill.retrieve(entities=entities, **kwargs)
        return [r.to_dict() for r in results]
