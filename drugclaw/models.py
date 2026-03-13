"""
Data models and state definitions for the DrugClaw drug-specialized RAG system
"""
from typing import List, Dict, Any, Optional, Set, Tuple, TypedDict
from dataclasses import dataclass, field
from enum import Enum

class AgentType(Enum):
    """Types of agents in the system"""
    RETRIEVER = "retriever"
    CODER = "coder"
    GRAPH_BUILDER = "graph_builder"
    RERANKER = "reranker"
    RESPONDER = "responder"
    REFLECTOR = "reflector"
    WEB_SEARCH = "web_search"


class ThinkingMode(str, Enum):
    """
    Query thinking mode — controls the reasoning pipeline used.

    SIMPLE   : one-shot retrieval → LLM answer (no graph, no reflection loop).
               Fast; good for factual lookups when you know which resources to use.
    WEB_ONLY : web search only (DuckDuckGo + PubMed); no skill retrieval, no graph.
               Useful for very recent data or broad literature sweeps.
    GRAPH    : full multi-agent graph reasoning — retrieve → rerank → respond →
               reflect → (web search if needed) → finalize.
               Deepest analysis; default mode.
    """
    SIMPLE   = "simple"
    WEB_ONLY = "web_only"
    GRAPH    = "graph"

@dataclass
class Entity:
    """Represents a biological entity (drug, gene, pathway, disease, etc.)"""
    id: str
    type: str  # 'drug', 'gene', 'pathway', 'disease', 'protein', etc.
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, Entity) and self.id == other.id

@dataclass
class Edge:
    """Represents a relationship between entities"""
    source: Entity
    target: Entity
    relation_type: str  # 'targets', 'associated_with', 'regulates', etc.
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvidencePath:
    """Represents a path through the knowledge graph"""
    entities: List[Entity]
    edges: List[Edge]
    score: float = 0.0
    
    def __str__(self) -> str:
        """String representation of the evidence path"""
        path_str = " → ".join([
            f"{e.name} ({e.type})" for e in self.entities
        ])
        return f"Path: {path_str} (score: {self.score:.3f})"

@dataclass
class EvidenceSubgraph:
    """Represents the evidence subgraph G_k at iteration k"""
    entities: Set[Entity] = field(default_factory=set)
    edges: List[Edge] = field(default_factory=list)
    paths: List[EvidencePath] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_size(self) -> int:
        """Return the number of entities in the subgraph"""
        return len(self.entities)
    
    def add_entity(self, entity: Entity):
        """Add an entity to the subgraph"""
        self.entities.add(entity)
    
    def add_edge(self, edge: Edge):
        """Add an edge to the subgraph"""
        self.edges.append(edge)
        self.entities.add(edge.source)
        self.entities.add(edge.target)

@dataclass
class OmicsConstraints:
    """Biological omics constraints"""
    gene_sets: List[str] = field(default_factory=list)
    pathway_sets: List[str] = field(default_factory=list)
    disease_terms: List[str] = field(default_factory=list)
    tissue_types: List[str] = field(default_factory=list)
    additional_constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReasoningStep:
    """Represents a single iteration step in the reasoning process"""
    step_id: int
    query: str
    subgraph: EvidenceSubgraph
    intermediate_answer: str
    evidence_sufficiency: float
    reward: float
    actions_taken: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reasoning step to dictionary for serialization"""
        return {
            'step_id': self.step_id,
            'query': self.query,
            'intermediate_answer': self.intermediate_answer,
            'evidence_sufficiency': self.evidence_sufficiency,
            'reward': self.reward,
            'actions_taken': self.actions_taken,
            'subgraph_size': self.subgraph.get_size(),
            'subgraph_entities': [
                {'id': e.id, 'name': e.name, 'type': e.type} 
                for e in self.subgraph.entities
            ],
            'subgraph_edges': [
                {
                    'source': edge.source.name,
                    'target': edge.target.name,
                    'relation_type': edge.relation_type,
                    'confidence': edge.confidence
                }
                for edge in self.subgraph.edges
            ],
            'subgraph_paths': [
                {
                    'path': str(path),
                    'score': path.score,
                    'entities': [e.name for e in path.entities]
                }
                for path in self.subgraph.paths
            ],
            'metadata': self.metadata
        }

@dataclass
class AgentState:
    """Global state shared across all agents in the LangGraph"""
    # Input
    original_query: str
    omics_constraints: Optional[OmicsConstraints] = None
    # Thinking mode (simple | web_only | graph)
    thinking_mode: str = ThinkingMode.GRAPH
    # Explicit resource filter — if non-empty, only these skill names are queried
    resource_filter: List[str] = field(default_factory=list)

    # Reasoning history
    iteration: int = 0
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    
    # Current state
    current_query_entities: List[Entity] = field(default_factory=list)
    current_subgraph: EvidenceSubgraph = field(default_factory=EvidenceSubgraph)
    current_answer: str = ""
    
    # Evaluation metrics
    evidence_sufficient: bool = False
    previous_reward: float = 0.0
    current_reward: float = 0.0
    
    # Agent outputs
    retrieved_content: List[Dict[str, Any]] = field(default_factory=list)
    retrieved_text: str = ""  # Free-form string retrieval results (from code agent)
    code_agent_code: str = ""  # Code generated by the code agent (for debugging)
    ranked_paths: List[EvidencePath] = field(default_factory=list)
    reflection_feedback: str = ""
    web_search_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Control flow
    should_continue: bool = True
    max_iterations_reached: bool = False
    final_answer: str = ""
    
    def get_marginal_gain(self) -> float:
        """Calculate marginal information gain Δr_k"""
        return self.current_reward - self.previous_reward
    
    def add_reasoning_step(self, step: ReasoningStep):
        """Add a reasoning step to the history"""
        self.reasoning_steps.append(step)
        self.iteration += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            'original_query': self.original_query,
            'iteration': self.iteration,
            'current_answer': self.current_answer,
            'evidence_sufficient': self.evidence_sufficient,
            'final_answer': self.final_answer
        }


# TypedDict for LangGraph state (helps with serialization)
class AgentStateDict(TypedDict, total=False):
    """Typed dictionary version of AgentState for LangGraph"""
    original_query: str
    omics_constraints: Optional[OmicsConstraints]
    thinking_mode: str
    resource_filter: List[str]
    iteration: int
    reasoning_steps: List[ReasoningStep]
    current_subgraph: EvidenceSubgraph
    current_answer: str
    evidence_sufficient: bool
    previous_reward: float
    current_reward: float
    retrieved_content: List[Dict[str, Any]]
    retrieved_text: str
    code_agent_code: str
    ranked_paths: List[EvidencePath]
    reflection_feedback: str
    web_search_results: List[Dict[str, Any]]
    should_continue: bool
    max_iterations_reached: bool
    final_answer: str