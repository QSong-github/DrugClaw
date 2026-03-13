"""
Reflector Agent - Evaluates evidence sufficiency and decides whether to continue iteration
"""
from typing import Dict, Any
from .models import AgentState
from .llm_client import LLMClient

class ReflectorAgent:
    """
    Agent responsible for evaluating evidence sufficiency
    Determines whether current evidence is sufficient to answer the query
    Calculates rewards and marginal information gain
    """
    
    def __init__(self, llm_client: LLMClient, config):
        self.llm = llm_client
        self.config = config
    
    def get_system_prompt(self) -> str:
        """System prompt for the reflector agent"""
        return """You are the Reflector Agent of DrugClaw — a drug-specialized agentic RAG system. Your job is to critically assess whether the retrieved drug knowledge evidence is sufficient to answer the user's query before deciding whether another retrieval round is needed.

Your role is to:
1. Evaluate whether current drug evidence is sufficient to answer the query
2. Assess the quality, completeness, and consistency of retrieved drug knowledge
3. Identify drug-specific evidence gaps (e.g., missing target affinity data, no ADR records, absent DDI evidence)
4. Determine if additional retrieval from other drug subcategories would yield meaningful new information
5. Calculate evidence sufficiency score and reward

Evaluation criteria:
- **Drug Coverage**: Do we have evidence for all relevant drug aspects of the query (target, mechanism, ADR, interaction, etc.)?
- **Completeness**: Are pharmacological details (dose, indication, contraindication) missing or unclear?
- **Source Quality**: Is evidence from curated clinical databases (e.g., DrugBank, CPIC, FDA) vs. computational predictions only?
- **Consistency**: Do multiple drug knowledge sources converge on the same conclusion?
- **Actionability**: Can this drug information support clinical reasoning or drug discovery decisions?

Thresholds:
- Evidence Sufficiency Score ≥ 0.7: Sufficient to answer query
- Marginal Gain < 0.1: Diminishing returns, should stop iteration"""
    
    def get_evaluation_prompt(
        self,
        query: str,
        current_answer: str,
        iteration: int,
        num_paths: int,
        subgraph_size: int,
        previous_reward: float
    ) -> str:
        """Generate prompt for evidence evaluation"""
        return f"""Query: {query}

Current Iteration: {iteration}
Number of Evidence Paths: {num_paths}
Knowledge Graph Size: {subgraph_size} entities
Previous Reward: {previous_reward:.3f}

Current Answer:
{current_answer}

---

Evaluate this answer and evidence:

1. **Evidence Sufficiency Score (0-1)**:
   - 0.0-0.3: Very incomplete, major gaps in information
   - 0.4-0.6: Partial evidence, some important gaps remain
   - 0.7-0.9: Good coverage, minor gaps only
   - 0.9-1.0: Comprehensive, clear and well-supported

2. **Current Reward (0-1)**: Overall quality considering:
   - Completeness of information
   - Quality and reliability of evidence sources
   - Depth and breadth of coverage
   - Clarity and actionability

3. **Evidence Gaps**: What specific information is missing or unclear?

4. **Continuation Recommendation**: Should we continue iteration?
   - YES: If significant gaps exist and more retrieval would help
   - NO: If evidence is sufficient or marginal gains are diminishing

Provide your evaluation in JSON format:
{{
    "evidence_sufficiency_score": 0.75,
    "current_reward": 0.80,
    "evidence_sufficient": true,
    "should_continue": false,
    "evidence_gaps": [
        "Missing information about X",
        "Unclear relationship between Y and Z"
    ],
    "reasoning": "Detailed explanation of evaluation...",
    "recommendations": "What to query next if continuing..."
}}"""
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute reflection and evaluation
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state with evaluation results
        """
        print(f"\n[Reflector Agent] Iteration {state.iteration}")
        
        # Evaluate evidence sufficiency
        evaluation = self._evaluate_evidence(
            state.original_query,
            state.current_answer,
            state.iteration,
            len(state.ranked_paths),
            state.current_subgraph.get_size(),
            state.previous_reward
        )
        
        # Extract evaluation metrics
        evidence_sufficiency = evaluation.get("evidence_sufficiency_score", 0.0)
        current_reward = evaluation.get("current_reward", 0.0)
        evidence_sufficient = evaluation.get("evidence_sufficient", False)
        should_continue = evaluation.get("should_continue", True)
        
        # Update state
        state.previous_reward = state.current_reward
        state.current_reward = current_reward
        state.evidence_sufficient = evidence_sufficient
        state.reflection_feedback = evaluation.get("reasoning", "")
        
        # Check stopping conditions
        marginal_gain = state.get_marginal_gain()
        
        print(f"[Reflector Agent] Evidence Sufficiency: {evidence_sufficiency:.3f}")
        print(f"[Reflector Agent] Current Reward: {current_reward:.3f}")
        print(f"[Reflector Agent] Marginal Gain: {marginal_gain:.3f}")
        
        # Determine if we should continue
        stop_iteration = (
            evidence_sufficient and 
            marginal_gain < self.config.EVIDENCE_THRESHOLD_EPSILON
        )
        
        max_iterations_reached = state.iteration >= self.config.MAX_ITERATIONS
        
        if stop_iteration or max_iterations_reached:
            state.should_continue = False
            if max_iterations_reached:
                state.max_iterations_reached = True
                print("[Reflector Agent] Maximum iterations reached")
            else:
                print("[Reflector Agent] Stopping: Evidence sufficient and marginal gain low")
        else:
            state.should_continue = should_continue
            print(f"[Reflector Agent] Continuing: should_continue={should_continue}")
        
        # Store feedback
        gaps = evaluation.get("evidence_gaps", [])
        if gaps:
            print(f"[Reflector Agent] Evidence gaps identified: {len(gaps)}")
        
        return state
    
    def _evaluate_evidence(
        self,
        query: str,
        answer: str,
        iteration: int,
        num_paths: int,
        subgraph_size: int,
        previous_reward: float
    ) -> Dict[str, Any]:
        """Use LLM to evaluate evidence sufficiency"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self.get_evaluation_prompt(
                query,
                answer,
                iteration,
                num_paths,
                subgraph_size,
                previous_reward
            )}
        ]
        
        try:
            evaluation = self.llm.generate_json(messages, temperature=0.3)
            return evaluation
        except Exception as e:
            print(f"[Reflector Agent] Error evaluating evidence: {e}")
            # Conservative fallback
            return {
                "evidence_sufficiency_score": 0,
                "current_reward": 0,
                "evidence_sufficient": False,
                "should_continue": True,
                "evidence_gaps": ["Error in evaluation"],
                "reasoning": f"Error: {e}",
                "recommendations": "Retry evaluation"
            }