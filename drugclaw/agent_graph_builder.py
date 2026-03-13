"""
Graph Build Agent — extracts entity triples from retrieval context using LLM.

Replaces the rigid source/target assembly in the old _build_subgraph() with
flexible LLM-driven triple extraction.  The LLM reads the full context
(original query, retrieval results, history, entity info) and autonomously
identifies (source, relationship, target) triples to build the evidence
subgraph.

Only used in GRAPH mode.  In SIMPLE mode the retrieval text goes directly
to the Responder Agent.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .models import AgentState, Entity, Edge, EvidenceSubgraph
from .llm_client import LLMClient


class GraphBuilderAgent:
    """
    Agent that builds an EvidenceSubgraph from free-form retrieval text
    by having the LLM extract entity–relationship triples.

    This replaces the old deterministic _build_subgraph() that required
    every result to conform to the RetrievalResult schema.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------

    def get_system_prompt(self) -> str:
        return """You are the Graph Build Agent of DrugClaw — a drug-specialized agentic RAG system.

Your role is to extract entity–relationship triples from the retrieval context to build a knowledge subgraph.

Given the original query, retrieved information (from drug knowledge databases), and any previous context, you must:

1. Identify all relevant biomedical entities mentioned:
   - Drugs (drug names, brand names, generic names)
   - Genes/Proteins (gene symbols, protein names, enzymes like CYP450)
   - Diseases/Conditions (disease names, symptoms, indications)
   - Pathways (biological pathways, signaling cascades)
   - Other (cell lines, organisms, biomarkers, adverse events, etc.)

2. Extract relationships between entity pairs:
   - Drug–Target: "targets", "inhibits", "activates", "binds", "modulates"
   - Drug–Disease: "treats", "indicated_for", "contraindicated", "associated_with"
   - Drug–Drug: "interacts_with", "synergizes", "antagonizes"
   - Drug–Adverse Event: "causes", "associated_with", "reported_with"
   - Gene–Disease: "associated_with", "risk_factor", "biomarker"
   - Drug–Pathway: "modulates", "activates", "inhibits"
   - Any other relevant relationships

3. For each triple, provide:
   - source_entity: entity name
   - source_type: entity type (drug, gene, disease, pathway, adverse_event, etc.)
   - target_entity: entity name
   - target_type: entity type
   - relationship: relationship label
   - confidence: 0.0-1.0 based on evidence strength
   - evidence_text: brief text justifying this triple
   - source_db: which database/resource this came from (if identifiable)

Focus on triples that are directly relevant to answering the original query.
Be thorough but precise — extract real relationships, not speculative ones.

Return your extraction as JSON."""

    def get_extraction_prompt(
        self,
        query: str,
        retrieved_text: str,
        history_summary: str = "",
    ) -> str:
        return f"""Extract entity–relationship triples from the following retrieval context.

=== Original Query ===
{query}

=== Retrieved Information ===
{retrieved_text}

{f"=== Previous Context ==={chr(10)}{history_summary}" if history_summary else ""}

Extract all relevant entity-relationship triples.  Return JSON:
{{
    "triples": [
        {{
            "source_entity": "Imatinib",
            "source_type": "drug",
            "target_entity": "BCR-ABL",
            "target_type": "gene",
            "relationship": "inhibits",
            "confidence": 0.95,
            "evidence_text": "Imatinib is a tyrosine kinase inhibitor targeting BCR-ABL fusion protein",
            "source_db": "ChEMBL"
        }}
    ],
    "entity_summary": "Brief summary of the key entities and their roles",
    "reasoning": "Why these triples were extracted and how they relate to the query"
}}

Extract ALL relevant triples from the retrieved information.  Be thorough."""

    # ------------------------------------------------------------------
    # Main execute
    # ------------------------------------------------------------------

    def execute(self, state: AgentState) -> AgentState:
        """
        Build evidence subgraph from free-form retrieved text via LLM
        triple extraction.

        Reads state.retrieved_text and produces state.current_subgraph.
        """
        print(f"\n[Graph Build Agent] Extracting triples from retrieval context")

        retrieved_text = state.retrieved_text
        if not retrieved_text.strip():
            print("[Graph Build Agent] No retrieved text to process")
            return state

        # Build history summary from previous reasoning steps
        history_summary = self._build_history_summary(state)

        # Ask LLM to extract triples
        triples_data = self._extract_triples(
            state.original_query,
            retrieved_text,
            history_summary,
        )

        # Convert triples to EvidenceSubgraph
        subgraph = self._build_subgraph_from_triples(
            triples_data, state.current_subgraph,
        )

        state.current_subgraph = subgraph
        print(
            f"[Graph Build Agent] Built subgraph with "
            f"{subgraph.get_size()} entities, {len(subgraph.edges)} edges"
        )

        return state

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_history_summary(self, state: AgentState) -> str:
        """Build a summary of previous reasoning steps for context."""
        if not state.reasoning_steps:
            return ""
        parts = []
        for step in state.reasoning_steps[-3:]:  # Last 3 steps
            parts.append(
                f"Step {step.step_id}: "
                f"sufficiency={step.evidence_sufficiency:.2f}, "
                f"answer_preview={step.intermediate_answer[:200]}..."
            )
        return "\n".join(parts)

    def _extract_triples(
        self,
        query: str,
        retrieved_text: str,
        history_summary: str,
    ) -> Dict[str, Any]:
        """Use LLM to extract entity–relationship triples."""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self.get_extraction_prompt(
                query, retrieved_text, history_summary,
            )},
        ]
        try:
            result = self.llm.generate_json(messages, temperature=0.3)
            triples = result.get("triples", [])
            print(f"[Graph Build Agent] Extracted {len(triples)} triples")
            return result
        except Exception as exc:
            print(f"[Graph Build Agent] LLM extraction error: {exc}")
            return {"triples": [], "entity_summary": "", "reasoning": f"Error: {exc}"}

    def _build_subgraph_from_triples(
        self,
        triples_data: Dict[str, Any],
        existing_subgraph: EvidenceSubgraph,
    ) -> EvidenceSubgraph:
        """Convert extracted triples into Entity/Edge objects and merge into subgraph."""
        subgraph = existing_subgraph

        for triple in triples_data.get("triples", []):
            try:
                src_name = triple.get("source_entity", "")
                src_type = triple.get("source_type", "unknown")
                tgt_name = triple.get("target_entity", "")
                tgt_type = triple.get("target_type", "unknown")
                relationship = triple.get("relationship", "related_to")
                confidence = float(triple.get("confidence", 0.5))
                evidence_text = triple.get("evidence_text", "")
                source_db = triple.get("source_db", "unknown")

                if not src_name or not tgt_name:
                    continue

                source_entity = Entity(
                    id=f"{src_type.lower()}_{src_name.lower().replace(' ', '_')}",
                    name=src_name,
                    type=src_type.lower(),
                    attributes={
                        "source": source_db,
                        "evidence_text": evidence_text,
                    },
                )
                target_entity = Entity(
                    id=f"{tgt_type.lower()}_{tgt_name.lower().replace(' ', '_')}",
                    name=tgt_name,
                    type=tgt_type.lower(),
                    attributes={
                        "source": source_db,
                    },
                )

                edge = Edge(
                    source=source_entity,
                    target=target_entity,
                    relation_type=relationship,
                    evidence=[source_db] if source_db else [],
                    confidence=max(0.0, min(1.0, confidence)),
                    attributes={
                        "evidence_text": evidence_text,
                        "source_db": source_db,
                    },
                )
                subgraph.add_edge(edge)

            except Exception as exc:
                print(f"[Graph Build Agent] Error processing triple: {exc}")
                continue

        return subgraph
