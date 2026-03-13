"""
Main LangGraph orchestration for DrugClaw — Drug-Specialized Agentic RAG System.

Three thinking modes are supported, selectable per-query:

  GRAPH    (default) — full multi-agent graph reasoning:
                       retrieve → graph_build → rerank → respond → reflect → [web_search] → finalize
  SIMPLE             — one-shot retrieval + direct LLM synthesis (no graph, no loop):
                       retrieve → simple_respond → finalize
  WEB_ONLY           — live web search only, no structured skill retrieval:
                       web_search_direct → finalize

Agent architecture:
  RetrieverAgent   — selects skills, delegates to CoderAgent
  CoderAgent       — writes and executes Python code to query skills
  GraphBuilderAgent— LLM-driven triple extraction (replaces rigid _build_subgraph)
  RerankerAgent    — path scoring and pruning
  ResponderAgent   — answer synthesis
  ReflectorAgent   — evidence sufficiency evaluation
  WebSearchAgent   — PubMed + ClinicalTrials supplementation

Additional query parameters:
  resource_filter : List[str]  — if non-empty, only query the named skills
                                 (bypasses LLM skill selection in the retriever)
  omics_constraints : OmicsConstraints — biological constraints (all modes)
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional

from langgraph.graph import StateGraph, END

from .models import AgentState, OmicsConstraints, ReasoningStep, ThinkingMode
from .config import Config
from .llm_client import LLMClient
from .skills import build_default_registry, WebSearchSkill
from .skills.registry import SkillRegistry
from .agent_coder import CoderAgent
from .agent_retriever import RetrieverAgent
from .agent_graph_builder import GraphBuilderAgent
from .agent_reranker import RerankerAgent
from .agent_responder import ResponderAgent
from .agent_reflector import ReflectorAgent
from .agent_websearch import WebSearchAgent
from .query_logger import QueryLogger, QuerySession


class DrugClawSystem:
    """
    Main orchestration system for drug-specialised agentic RAG.
    Uses LangGraph to manage the multi-agent workflow.

    The RAG retrieval layer is powered by a SkillRegistry that aggregates
    results from 68 curated drug knowledge sources (+ WebSearchSkill) across
    15 subcategories.  Retrieval is now handled by a Code Agent that writes
    custom query code per skill, and graph construction is done by an LLM-driven
    Graph Build Agent.
    """

    def __init__(
        self,
        config: Config,
        enable_logging: bool = True,
        log_dir: str = "./query_logs",
        skill_registry: Optional[SkillRegistry] = None,
    ):
        self.config = config

        # Query logger
        self.enable_logging = enable_logging
        self.logger = QueryLogger(log_dir) if enable_logging else None

        # LLM
        self.llm_client = LLMClient(config)

        # Skill registry (68 drug resources + WebSearchSkill)
        self.skill_registry = (
            skill_registry if skill_registry is not None
            else build_default_registry(self.config)
        )
        # Backward-compat alias
        self.kg_manager = self.skill_registry

        # Grab the WebSearchSkill instance for injection into WebSearchAgent
        _web_skill = self.skill_registry.get_skill("WebSearch")

        # Agents
        self.coder = CoderAgent(self.llm_client, self.skill_registry)
        self.retriever = RetrieverAgent(
            self.llm_client, self.skill_registry, coder_agent=self.coder,
        )
        self.graph_builder = GraphBuilderAgent(self.llm_client)
        self.reranker = RerankerAgent(self.llm_client, config)
        self.responder = ResponderAgent(self.llm_client)
        self.reflector = ReflectorAgent(self.llm_client, config)
        self.web_search = WebSearchAgent(
            self.llm_client,
            web_search_skill=_web_skill,
        )

        # Build LangGraph workflow (handles all 3 modes via conditional routing)
        self.workflow = self._build_workflow()

    # ------------------------------------------------------------------
    # LangGraph workflow
    # ------------------------------------------------------------------

    def _build_workflow(self) -> StateGraph:
        """
        Build a single StateGraph that routes between the three thinking modes.

        Graph topology:
          entry_router ──(mode=graph|simple)──► retrieve
                       ──(mode=web_only)──────► web_search_direct

          retrieve ──(graph)──► graph_build ──► rerank ──► respond ──► reflect
                   ──(simple)──► simple_respond ──► finalize

          reflect ──(continue)──► web_search ──► retrieve   (graph loop)
                  ──(finalize)──► finalize

          web_search_direct ──► finalize
          finalize ──► END
        """
        wf = StateGraph(AgentState)

        wf.add_node("entry_router",       self._entry_router_node)
        wf.add_node("retrieve",           self._retrieve_node)
        wf.add_node("graph_build",        self._graph_build_node)
        wf.add_node("rerank",             self._rerank_node)
        wf.add_node("respond",            self._respond_node)
        wf.add_node("reflect",            self._reflect_node)
        wf.add_node("web_search",         self._web_search_node)
        wf.add_node("simple_respond",     self._simple_respond_node)
        wf.add_node("web_search_direct",  self._web_search_direct_node)
        wf.add_node("finalize",           self._finalize_node)

        wf.set_entry_point("entry_router")

        # entry_router → mode dispatch
        wf.add_conditional_edges(
            "entry_router",
            self._route_by_mode,
            {"retrieve": "retrieve", "web_search_direct": "web_search_direct"},
        )

        # retrieve → next step depends on mode
        wf.add_conditional_edges(
            "retrieve",
            self._after_retrieve,
            {"graph_build": "graph_build", "simple_respond": "simple_respond"},
        )

        # graph mode pipeline: graph_build → rerank → respond → reflect
        wf.add_edge("graph_build", "rerank")
        wf.add_edge("rerank",     "respond")
        wf.add_edge("respond",    "reflect")
        wf.add_conditional_edges(
            "reflect",
            self._should_continue,
            {"continue": "web_search", "finalize": "finalize"},
        )
        wf.add_edge("web_search", "retrieve")

        # simple / web_only termination
        wf.add_edge("simple_respond",    "finalize")
        wf.add_edge("web_search_direct", "finalize")
        wf.add_edge("finalize",          END)

        return wf.compile()

    # ------------------------------------------------------------------
    # Routing helpers (conditional edge functions)
    # ------------------------------------------------------------------

    def _route_by_mode(self, state: AgentState) -> str:
        mode = getattr(state, "thinking_mode", ThinkingMode.GRAPH)
        if str(mode) == ThinkingMode.WEB_ONLY:
            return "web_search_direct"
        return "retrieve"

    def _after_retrieve(self, state: AgentState) -> str:
        mode = getattr(state, "thinking_mode", ThinkingMode.GRAPH)
        if str(mode) == ThinkingMode.SIMPLE:
            return "simple_respond"
        return "graph_build"

    def _should_continue(self, state: AgentState) -> str:
        if state.should_continue and not state.max_iterations_reached:
            return "continue"
        return "finalize"

    # ------------------------------------------------------------------
    # Node wrappers
    # ------------------------------------------------------------------

    def _entry_router_node(self, state: AgentState) -> AgentState:
        """Passthrough — routing happens in the conditional edge above."""
        mode = getattr(state, "thinking_mode", ThinkingMode.GRAPH)
        rf   = getattr(state, "resource_filter", [])
        print(f"\n[DrugClaw] mode={mode}"
              + (f"  resource_filter={rf}" if rf else ""))
        return state

    def _retrieve_node(self, state: AgentState) -> AgentState:
        return self.retriever.execute(state)

    def _graph_build_node(self, state: AgentState) -> AgentState:
        """Graph mode: LLM extracts entity triples from retrieval text."""
        return self.graph_builder.execute(state)

    def _rerank_node(self, state: AgentState) -> AgentState:
        return self.reranker.execute(state)

    def _respond_node(self, state: AgentState) -> AgentState:
        return self.responder.execute(state)

    def _reflect_node(self, state: AgentState) -> AgentState:
        state = self.reflector.execute(state)
        step = ReasoningStep(
            step_id=state.iteration,
            query=state.original_query,
            subgraph=state.current_subgraph,
            intermediate_answer=state.current_answer,
            evidence_sufficiency=state.current_reward,
            reward=state.current_reward,
            actions_taken=["retrieve", "graph_build", "rerank", "respond", "reflect"],
        )
        state.add_reasoning_step(step)
        return state

    def _web_search_node(self, state: AgentState) -> AgentState:
        """Graph-mode web search (triggered by reflector when evidence is lacking)."""
        return self.web_search.execute(state)

    def _simple_respond_node(self, state: AgentState) -> AgentState:
        """Simple-mode: synthesize retrieved text directly."""
        return self.responder.execute_simple(state)

    def _web_search_direct_node(self, state: AgentState) -> AgentState:
        """WEB_ONLY mode: search the original query without prior retrieval."""
        return self.web_search.execute_direct(state)

    def _finalize_node(self, state: AgentState) -> AgentState:
        print("\n[DrugClaw] Finalizing answer...")
        state.final_answer = state.current_answer
        return state

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(
        self,
        query: str,
        omics_constraints: Optional[OmicsConstraints] = None,
        thinking_mode: str = ThinkingMode.GRAPH,
        resource_filter: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a drug-related query.

        Parameters
        ----------
        query            : Natural language question.
        omics_constraints: Optional biological constraints (gene sets, pathways, …).
        thinking_mode    : One of ThinkingMode.GRAPH (default), .SIMPLE, .WEB_ONLY.
        resource_filter  : Optional list of skill names to restrict retrieval
                           (e.g. ["ChEMBL", "DGIdb"]).  When provided, the LLM
                           skill-selection step is bypassed.
        metadata         : Arbitrary metadata to log alongside the query.

        Returns
        -------
        dict with keys: query, answer, mode, iterations, evidence_graph_size,
                        final_reward, reasoning_history, retrieved_content,
                        web_search_results, success, [query_id]
        """
        print(f"\n{'='*80}")
        print(f"QUERY [{thinking_mode}]: {query}")
        if resource_filter:
            print(f"RESOURCE FILTER: {resource_filter}")
        print(f"{'='*80}\n")

        initial_state = AgentState(
            original_query=query,
            omics_constraints=omics_constraints,
            thinking_mode=str(thinking_mode),
            resource_filter=resource_filter or [],
        )

        try:
            final = self.workflow.invoke(initial_state)

            final_answer    = final.get("final_answer", final.get("current_answer", ""))
            iteration       = final.get("iteration", 0)
            current_reward  = final.get("current_reward", 0.0)
            reasoning_steps = final.get("reasoning_steps", [])
            subgraph        = final.get("current_subgraph")
            subgraph_size   = subgraph.get_size() if subgraph and hasattr(subgraph, "get_size") else 0

            print(f"\n{'='*80}\nFINAL ANSWER\n{'='*80}\n")
            print(final_answer)

            result = {
                "query":              query,
                "answer":             final_answer,
                "mode":               thinking_mode,
                "resource_filter":    resource_filter or [],
                "iterations":         iteration,
                "evidence_graph_size": subgraph_size,
                "final_reward":       current_reward,
                "reasoning_history":  [
                    {
                        "step": s.step_id,
                        "answer": s.intermediate_answer,
                        "reward": s.reward,
                        "evidence_sufficiency": s.evidence_sufficiency,
                    }
                    for s in reasoning_steps
                ],
                "retrieved_content":  final.get("retrieved_content", []),
                "retrieved_text":     final.get("retrieved_text", ""),
                "reflection_feedback": final.get("reflection_feedback", ""),
                "web_search_results": final.get("web_search_results", []),
                "success":            True,
            }

            if self.enable_logging and self.logger:
                result["query_id"] = self.logger.log_query(query, result, metadata)

            return result

        except Exception as exc:
            import traceback
            print(f"\n[DrugClaw] Error: {exc}")
            traceback.print_exc()
            return {
                "query":   query,
                "answer":  f"Error: {exc}",
                "mode":    thinking_mode,
                "success": False,
            }

    # ------------------------------------------------------------------
    # Logging helpers (unchanged API)
    # ------------------------------------------------------------------

    def get_query_history(self, n: int = 10) -> List[Dict[str, Any]]:
        if not self.logger:
            return []
        return self.logger.get_recent_queries(n)

    def get_query_by_id(self, query_id: str, detailed: bool = False):
        if not self.logger:
            return None
        return self.logger.get_query(query_id, detailed)

    def search_queries(self, keyword: str) -> List[Dict[str, Any]]:
        if not self.logger:
            return []
        return self.logger.search_queries(keyword=keyword)

    def get_statistics(self) -> Dict[str, Any]:
        if not self.logger:
            return {}
        return self.logger.get_statistics()

    def visualize_workflow(self, output_path: str = "workflow.png"):
        try:
            png_data = self.workflow.get_graph().draw_mermaid_png()
            with open(output_path, "wb") as fh:
                fh.write(png_data)
            print(f"Workflow saved to {output_path}")
        except Exception as exc:
            print(f"Cannot generate visualization: {exc}")
