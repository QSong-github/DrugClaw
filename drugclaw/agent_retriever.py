"""
Retriever Agent — selects skills and delegates querying to the Code Agent.

The Retriever Agent is now focused on:
  1. Analyzing the query and selecting the best skills (via LLM or resource_filter)
  2. Extracting key entities from the query
  3. Delegating actual querying to the Code Agent
  4. Collecting results as free-form text (no forced RetrievalResult schema)

The old _build_subgraph() is replaced by the Graph Build Agent (graph mode)
or results go directly as text to the Responder Agent (simple mode).
"""
from typing import List, Dict, Any, Optional

from .models import AgentState
from .llm_client import LLMClient
from .skills.registry import SkillRegistry
from .agent_coder import CoderAgent


class RetrieverAgent:
    """
    Agent responsible for selecting skills and orchestrating retrieval.

    Uses LLM to navigate the 15-subcategory skill tree, then hands off
    to the Code Agent for actual querying.  Results come back as text.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        skill_registry: SkillRegistry,
        coder_agent: Optional[CoderAgent] = None,
    ):
        self.llm = llm_client
        self.skill_registry = skill_registry
        self.coder = coder_agent or CoderAgent(llm_client, skill_registry)

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    def get_system_prompt(self) -> str:
        """System prompt for skill selection."""
        tree_ctx = self.skill_registry.skill_tree_prompt
        return f"""You are the Retriever Agent of DrugClaw — a drug-specialized agentic RAG system covering 68 curated drug knowledge resources across 15 subcategories (DTI, ADR, DDI, drug mechanisms, pharmacogenomics, drug ontology, drug labeling, drug repurposing, drug toxicity, drug combinations, drug molecular properties, drug-disease associations, drug knowledge bases, drug reviews, and drug NLP datasets).

Your role is to:
1. Analyze the user's drug-related query
2. Navigate the 15-subcategory Skill Tree to select the most relevant resources
3. Extract key entities (drugs, genes, diseases, pathways) from the query
4. Decide which skills to query

---
{tree_ctx}
---

Each skill is marked:
  ✓ = implemented and available to call
  ○ = catalogued but not yet available (do NOT include in query_plan)

Skills also show their access mode:
  [CLI]        — Python package CLI (preferred; auto-detected if installed)
  [LOCAL_FILE] — requires pre-downloaded local data file
  [DATASET]    — benchmark dataset (mask when evaluating on it)
  (no tag)     — public REST/GraphQL API (always available)

Navigation strategy by subcategory:
- Drug targets, bioactivity, binding              → [dti]
- Side effects, pharmacovigilance                 → [adr]
- General drug info, encyclopedias, KGs           → [drug_knowledgebase]
- Mechanism of action paths                       → [drug_mechanism]
- FDA labels, prescribing info, dosing            → [drug_labeling]
- Drug codes, ATC, RxNorm, ontologies             → [drug_ontology]
- New indications, repositioning                  → [drug_repurposing]
- Variant-drug, PGx guidelines                   → [pharmacogenomics]
- Polypharmacy, drug interactions                 → [ddi]
- Hepatotoxicity, DILI, organ tox                → [drug_toxicity]
- Synergy, combination therapy                    → [drug_combination]
- QSAR, cell-line sensitivity, IC50              → [drug_molecular_property]
- Disease-drug semantic associations              → [drug_disease]
- Patient reviews, real-world effectiveness       → [drug_review]
- NLP corpora, relation extraction                → [drug_nlp]

Only select skills marked ✓ in your query_plan.
Respond with a structured plan for retrieval."""

    def get_query_planning_prompt(
        self,
        query: str,
        omics_constraints: str,
        iteration: int,
        suggested_skills: List[str],
    ) -> str:
        suggestion_str = (
            "Suggested skills (keyword-matched to your query, all ✓):\n  " +
            ", ".join(suggested_skills)
            if suggested_skills
            else "No keyword-matched suggestions — use the tree in the system prompt."
        )
        return f"""Query: {query}

Biological Constraints:
{omics_constraints}

{suggestion_str}

Current Iteration: {iteration}

Use the Skill Tree in the system prompt to navigate to the right domain, then
select the best ✓-marked skills for this query.

Provide your plan in JSON format:
{{
    "key_entities": {{
        "drugs": ["drug1", "drug2"],
        "genes": ["gene1", "gene2"],
        "diseases": ["disease1"],
        "pathways": ["pathway1"],
        "other": []
    }},
    "highly_related_entities": {{
        "drugs": ["related_drug1"],
        "genes": ["related_gene1"],
        "diseases": ["related_disease1"],
        "pathways": [],
        "other": []
    }},
    "selected_skills": ["ChEMBL", "DGIdb"],
    "reasoning": "Explanation of which skill-tree domain you used and why these skills were selected"
}}"""

    # ------------------------------------------------------------------
    # Main execute
    # ------------------------------------------------------------------

    def execute(self, state: AgentState) -> AgentState:
        """
        Execute retrieval step:
          1. Plan (LLM selects skills + extracts entities)
          2. Delegate to Code Agent for actual querying
          3. Store results as text in state.retrieved_text
        """
        print(f"\n[Retriever Agent] Iteration {state.iteration}")
        resource_filter = getattr(state, "resource_filter", [])
        if resource_filter:
            print(f"[Retriever Agent] resource_filter={resource_filter}")

        # Prepare omics constraints string
        omics_str = self._format_omics_constraints(state.omics_constraints)

        if resource_filter:
            query_plan = self._get_query_plan_filtered(
                state.original_query, omics_str, state.iteration, resource_filter,
            )
        else:
            query_plan = self._get_query_plan(
                state.original_query, omics_str, state.iteration,
            )

        # Extract info from the plan
        key_entities = query_plan.get("key_entities", {})
        selected_skills = query_plan.get("selected_skills", [])

        # Backward compat: also check query_plan list for skill names
        if not selected_skills:
            selected_skills = [
                step.get("database", "")
                for step in query_plan.get("query_plan", [])
                if step.get("database")
            ]

        print(f"[Retriever Agent] Selected skills: {selected_skills}")
        print(f"[Retriever Agent] Key entities: {key_entities}")

        # Normalize entities for Code Agent
        entities: Dict[str, List[str]] = {}
        for etype in ("drugs", "genes", "diseases", "pathways", "other"):
            vals = key_entities.get(etype, [])
            if isinstance(vals, str):
                vals = [vals]
            if vals:
                # Map plural to singular for consistency
                singular = etype.rstrip("s") if etype != "other" else "other"
                entities[singular] = vals

        # Delegate to Code Agent
        coder_result = self.coder.generate_and_execute(
            skill_names=selected_skills,
            entities=entities,
            query=state.original_query,
        )

        # Build a combined context string with query + entities + results
        context_parts = [
            f"Query: {state.original_query}",
            f"Key Entities: {key_entities}",
            f"Skills Used: {selected_skills}",
            "",
            coder_result["text"],
        ]

        # Include history if available
        if state.reasoning_steps:
            last_step = state.reasoning_steps[-1]
            context_parts.insert(
                3,
                f"Previous iteration answer (preview): "
                f"{last_step.intermediate_answer[:300]}...",
            )

        retrieved_text = "\n".join(context_parts)

        # Update state
        state.current_query_entities = key_entities
        state.retrieved_text = retrieved_text
        state.code_agent_code = "\n---\n".join(
            f"# Skill: {name}\n{info.get('code', '')}"
            for name, info in coder_result.get("per_skill", {}).items()
        )

        # Also populate retrieved_content for backward compat (flat list)
        # Parse from coder results if needed
        state.retrieved_content = self._text_to_retrieved_content(
            coder_result, selected_skills,
        )

        print(f"[Retriever Agent] Retrieved {len(retrieved_text)} chars of text")
        print(f"[Retriever Agent] {len(state.retrieved_content)} backward-compat records")

        return state

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _format_omics_constraints(self, constraints) -> str:
        if constraints is None:
            return "No specific biological constraints provided."
        parts = []
        if constraints.gene_sets:
            parts.append(f"Genes: {', '.join(constraints.gene_sets[:10])}")
        if constraints.pathway_sets:
            parts.append(f"Pathways: {', '.join(constraints.pathway_sets[:10])}")
        if constraints.disease_terms:
            parts.append(f"Diseases: {', '.join(constraints.disease_terms)}")
        if constraints.tissue_types:
            parts.append(f"Tissues: {', '.join(constraints.tissue_types)}")
        return "\n".join(parts) if parts else "No specific constraints."

    def _get_query_plan(
        self, query: str, omics_str: str, iteration: int,
    ) -> Dict[str, Any]:
        """Use LLM to select skills and extract entities."""
        suggested = self.skill_registry.get_skills_for_query(query)

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self.get_query_planning_prompt(
                query, omics_str, iteration, suggested_skills=suggested,
            )},
        ]
        try:
            return self.llm.generate_json(messages)
        except Exception as e:
            print(f"[Retriever Agent] Error generating plan: {e}")
            return {
                "key_entities": {"drugs": [], "genes": [], "diseases": [], "pathways": []},
                "selected_skills": suggested[:3],
                "reasoning": "Fallback plan due to LLM error",
            }

    def _get_query_plan_filtered(
        self, query: str, omics_str: str, iteration: int,
        resource_filter: List[str],
    ) -> Dict[str, Any]:
        """Build a plan forcing the specified skills (skip LLM skill selection)."""
        entity_prompt = f"""Extract drug/gene/disease/pathway entities from this query for retrieval.
Query: {query}
Biological Constraints: {omics_str}

Respond in JSON:
{{
  "drugs": ["drugA"],
  "genes": ["geneA"],
  "diseases": ["diseaseA"],
  "pathways": [],
  "other": []
}}"""
        try:
            entities = self.llm.generate_json([{"role": "user", "content": entity_prompt}])
        except Exception:
            entities = {"drugs": [], "genes": [], "diseases": [], "pathways": []}

        return {
            "key_entities": entities,
            "selected_skills": resource_filter,
            "reasoning": f"resource_filter active: using {resource_filter}",
        }

    @staticmethod
    def _text_to_retrieved_content(
        coder_result: Dict[str, Any],
        skill_names: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Convert coder output to backward-compatible retrieved_content list.
        Each entry is a minimal dict with source + text.
        """
        records = []
        for skill_name in skill_names:
            info = coder_result.get("per_skill", {}).get(skill_name, {})
            output = info.get("output", "").strip()
            if output:
                records.append({
                    "source": skill_name,
                    "source_entity": "",
                    "source_type": "",
                    "target_entity": "",
                    "target_type": "",
                    "relationship": "",
                    "weight": 1.0,
                    "evidence_text": output[:2000],
                    "skill_category": "",
                })
        return records
