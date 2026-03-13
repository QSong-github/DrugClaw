"""
Re-ranker Agent - Prunes and scores evidence paths based on semantic and structural relevance
"""
from typing import List, Dict, Any
from .models import AgentState, EvidencePath, Entity, Edge
from .llm_client import LLMClient
import math
import random
from collections import deque



class RerankerAgent:
    """
    Agent responsible for re-ranking evidence paths
    Evaluates paths based on semantic relevance and structural importance
    """
    
    def __init__(self, llm_client: LLMClient, config):
        self.llm = llm_client
        self.config = config
        self.semantic_weight = config.SEMANTIC_WEIGHT
        self.structural_weight = config.STRUCTURAL_WEIGHT
    
    def get_system_prompt(self) -> str:
        """System prompt for the re-ranker agent"""
        return """You are the Re-ranker Agent of DrugClaw — a drug-specialized agentic RAG system. You operate on evidence retrieved from 68 curated drug knowledge resources spanning drug-target interactions, adverse drug reactions, drug-drug interactions, drug mechanisms, pharmacogenomics, and more.

Your role is to:
1. Evaluate evidence paths through the drug knowledge graph
2. Score paths based on semantic relevance to the drug-related query
3. Consider structural importance (path length, node centrality, confidence scores)
4. Prune low-quality or irrelevant paths
5. Identify the most mechanistically plausible drug–target–disease connections

For each evidence path, evaluate:
- Pharmacological plausibility of the drug mechanism or interaction
- Strength and source quality of evidence (e.g., clinical vs. computational)
- Directness of the connection (shorter paths often better)
- Relevance to the specific drug, target, or disease in the query

Provide scores and reasoning for top paths."""
    
    def get_ranking_prompt(
        self,
        query: str,
        paths: List[str],
        max_paths: int = 10
    ) -> str:
        """Generate prompt for path ranking"""
        paths_str = "\n".join([f"{i+1}. {path}" for i, path in enumerate(paths[:20])])
        
        return f"""Query: {query}

Evidence Paths to Evaluate:
{paths_str}

Evaluate each path and provide:
1. Semantic relevance score (0-1): How well does this path answer the query?
2. Mechanistic plausibility (0-1): Is this a biologically plausible mechanism?
3. Evidence strength (0-1): How strong is the supporting evidence?
4. Overall reasoning: Why is this path important or not?

Return the top {max_paths} paths in JSON format:
{{
    "ranked_paths": [
        {{
            "path_id": 1,
            "semantic_score": 0.9,
            "mechanistic_score": 0.85,
            "evidence_score": 0.8,
            "overall_score": 0.85,
            "reasoning": "This path shows direct drug-target-disease mechanism..."
        }}
    ],
    "pruned_count": 5,
    "reasoning": "Overall ranking strategy explanation"
}}"""
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute re-ranking step
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state with ranked paths
        """
        print(f"\n[Re-ranker Agent] Iteration {state.iteration}")
        
        # Extract paths from current subgraph
        paths = self._extract_paths(state.current_subgraph, state.current_query_entities)
        
        if not paths:
            print("[Re-ranker Agent] No paths to rank")
            state.ranked_paths = []
            return state
        
        # Convert paths to string representation for LLM
        path_strs = [str(path) for path in paths]
        
        # Get semantic scores from LLM
        ranking_result = self._rank_paths_with_llm(
            state.original_query,
            path_strs
        )
        
        # Calculate structural scores
        structural_scores = self._calculate_structural_scores(paths)
        
        # Combine scores and update paths
        scored_paths = self._combine_scores(
            paths,
            ranking_result,
            structural_scores
        )
        
        # Sort and prune
        scored_paths.sort(key=lambda p: p.score, reverse=True)
        top_paths = scored_paths[:self.config.MAX_SUBGRAPH_SIZE]
        
        # Update state
        state.ranked_paths = top_paths
        
        # Prune subgraph to only include entities in top paths
        state.current_subgraph = self._prune_subgraph(
            state.current_subgraph,
            top_paths
        )
        
        print(f"[Re-ranker Agent] Ranked {len(paths)} paths, kept top {len(top_paths)}")
        if top_paths:
            print(f"[Re-ranker Agent] Top path score: {top_paths[0].score:.3f}")
        
        return state
    
    def _extract_paths(self, subgraph, query_entities=None) -> List[EvidencePath]:
        """
        Extract paths from the evidence subgraph using random walk with multi-layer entity matching
        
        Args:
            subgraph: The evidence subgraph containing entities and edges
            query_entities: Dictionary of entity types to entity lists, e.g.,
                        {'drugs': ['Antimicrobial'], 'genes': [], 'diseases': [], ...}
                        If None, returns empty paths.
        
        Returns:
            List of EvidencePath objects representing paths found in the graph
        """
        paths = []
        
        if query_entities is None:
            print("[Re-ranker Agent] No query entities found")
            return paths
        
        # Convert Entity objects to a dictionary for quick lookup by name
        entity_name_to_obj = {entity.name: entity for entity in subgraph.entities}
        
        # Target entities - keep as Entity objects
        target_entities = list(subgraph.entities)
        
        if not target_entities:
            print("[Re-ranker Agent] No target entities found")
            return paths
        
        # Collect all entity names from the graph for matching
        graph_entity_names = list(entity_name_to_obj.keys())
        
        # Statistics for different match types
        match_stats = {
            'exact': 0, 
            'case_insensitive': 0, 
            'normalized': 0, 
            'substring': 0, 
            'fuzzy': 0, 
            'none': 0
        }
        
        # Extract flat list of query entities for counting
        flat_query_entities = self._extract_entities_from_dict(query_entities)
        
        print(f"[Re-ranker Agent] Graph entities: {len(graph_entity_names)}")
        print(f"[Re-ranker Agent] Query entities: {len(flat_query_entities)}")
        print(f"[Re-ranker Agent] Target entities: {len(target_entities)}")
        
        # Random walk parameters (from config or defaults)
        num_walks_per_entity = getattr(self.config, 'NUM_WALKS_PER_QUERY', 10)
        max_walk_length = getattr(self.config, 'MAX_WALK_LENGTH', 5)
        walk_strategy = getattr(self.config, 'WALK_STRATEGY', 'bfs')  # 'bfs', 'dfs', or 'random'
        min_match_score = getattr(self.config, 'MIN_MATCH_SCORE', 70)  # Minimum matching score threshold
        
        # Perform walks from each query entity
        for entity_type, entities in query_entities.items():
            if not entities:  # Skip empty entity lists
                continue
                
            for query_entity in entities:
                # Multi-layer entity matching (returns matched entity NAME)
                matched_entity_name, match_type, score = self._find_entity_match(
                    query_entity, 
                    graph_entity_names
                )
                
                # Update match statistics
                match_stats[match_type] += 1
                
                # Skip if no match found or score below threshold
                if matched_entity_name is None or score < min_match_score:
                    print(f"[Re-ranker Agent] No valid match for '{query_entity}' (best: {match_type}, score: {score})")
                    continue
                
                print(f"[Re-ranker Agent] Matched '{query_entity}' -> '{matched_entity_name}' ({match_type}, score: {score})")
                
                # Convert matched entity name to Entity object
                matched_entity_obj = entity_name_to_obj.get(matched_entity_name)
                if matched_entity_obj is None:
                    print(f"[Re-ranker Agent] Warning: matched entity '{matched_entity_name}' not found in entity objects")
                    continue
                
                # Perform walk based on strategy (pass Entity objects)
                if walk_strategy == 'random':
                    # Pure random walk
                    walk_paths = self._random_walk(
                        matched_entity_obj,      # Entity object
                        target_entities,          # List of Entity objects
                        subgraph.edges,          # List of Edge objects
                        num_walks_per_entity,
                        max_walk_length
                    )
                elif walk_strategy == 'dfs':
                    # DFS-based exploration
                    walk_paths = self._dfs_walk(
                        matched_entity_obj,      # Entity object
                        target_entities,          # List of Entity objects
                        subgraph.edges,          # List of Edge objects
                        max_walk_length
                    )
                else:  # 'bfs' (default)
                    # BFS-based exploration
                    walk_paths = self._bfs_walk(
                        matched_entity_obj,      # Entity object
                        target_entities,          # List of Entity objects
                        subgraph.edges,          # List of Edge objects
                        max_walk_length
                    )
                
                print(f"[Re-ranker Agent] Found {len(walk_paths)} paths from '{query_entity}'")
                paths.extend(walk_paths)
        
        # Print matching statistics
        total_queries = sum(match_stats.values())
        matched_queries = total_queries - match_stats['none']
        print(f"[Re-ranker Agent] Match statistics: {match_stats}")
        print(f"[Re-ranker Agent] Successfully matched: {matched_queries}/{total_queries} queries")
        
        # Remove duplicate paths
        paths = self._deduplicate_paths(paths)
        print(f"[Re-ranker Agent] Extracted {len(paths)} unique paths from subgraph")
        
        return paths


    def _find_entity_match(self, query_entity, graph_entity_names):
        """
        Multi-layer entity matching strategy with progressive fallback
        
        Args:
            query_entity: The query entity string to match
            graph_entity_names: List of entity names (strings) in the knowledge graph
        
        Returns:
            tuple: (matched_entity_name, match_type, score)
                - matched_entity_name: The matched entity name from graph, or None if no match
                - match_type: Type of match ('exact', 'case_insensitive', 'normalized', 'substring', 'fuzzy', 'none')
                - score: Matching score (0-100)
        """
        # Layer 1: Exact match
        if query_entity in graph_entity_names:
            return query_entity, 'exact', 100
        
        # Layer 2: Case-insensitive match
        query_lower = query_entity.lower()
        for entity_name in graph_entity_names:
            if entity_name.lower() == query_lower:
                return entity_name, 'case_insensitive', 95
        
        # Layer 3: Normalized match (remove spaces, underscores, hyphens)
        query_normalized = query_lower.replace(' ', '').replace('_', '').replace('-', '')
        for entity_name in graph_entity_names:
            entity_normalized = entity_name.lower().replace(' ', '').replace('_', '').replace('-', '')
            if entity_normalized == query_normalized:
                return entity_name, 'normalized', 90
        
        # Layer 4: Substring match (containment relationship)
        for entity_name in graph_entity_names:
            entity_lower = entity_name.lower()
            if query_lower in entity_lower or entity_lower in query_lower:
                # Calculate overlap ratio
                overlap = min(len(query_lower), len(entity_lower)) / max(len(query_lower), len(entity_lower))
                if overlap > 0.7:  # 70% overlap threshold
                    return entity_name, 'substring', int(overlap * 100)
        
        # Layer 5: Fuzzy match using edit distance
        from difflib import SequenceMatcher
        best_match = None
        best_score = 0
        
        for entity_name in graph_entity_names:
            ratio = SequenceMatcher(None, query_lower, entity_name.lower()).ratio()
            score = int(ratio * 100)
            if score > best_score and score >= 70:  # 70 score threshold
                best_score = score
                best_match = entity_name
        
        if best_match:
            return best_match, 'fuzzy', best_score
        
        # No match found
        return None, 'none', 0


    def _extract_entities_from_dict(self, entity_dict):
        """
        Extract all entities from dictionary structure
        
        Args:
            entity_dict: Dictionary with entity types as keys and entity lists as values
                        e.g., {'drugs': ['Antimicrobial'], 'genes': [], ...}
        
        Returns:
            List of all entity strings
        """
        entities = []
        if isinstance(entity_dict, dict):
            for entity_list in entity_dict.values():
                if isinstance(entity_list, list):
                    entities.extend(entity_list)
        return entities


    def _random_walk(
        self,
        start: Entity,
        targets: List[Entity],
        edges: List[Edge],
        num_walks: int,
        max_length: int
    ) -> List[EvidencePath]:
        """
        Perform random walks from start entity
        
        Args:
            start: Starting entity
            targets: List of target entities to reach
            edges: Available edges in the graph
            num_walks: Number of random walks to perform
            max_length: Maximum length of each walk
        
        Returns:
            List of paths found
        """
        import random
        
        paths = []
        target_set = set(targets)
        
        # Build adjacency list for efficient lookup
        adj_list = {}
        for edge in edges:
            if edge.source not in adj_list:
                adj_list[edge.source] = []
            adj_list[edge.source].append((edge.target, edge))
        
        for _ in range(num_walks):
            current = start
            path_entities = [current]
            path_edges = []
            
            for step in range(max_length):
                # Check if we reached a target
                if current in target_set:
                    paths.append(EvidencePath(
                        entities=path_entities.copy(),
                        edges=path_edges.copy()
                    ))
                    break
                
                # Get neighbors
                neighbors = adj_list.get(current, [])
                if not neighbors:
                    break
                
                # Randomly select next node (can add edge weight bias here)
                next_entity, edge = random.choice(neighbors)
                
                # Avoid cycles
                if next_entity in path_entities:
                    break
                
                path_entities.append(next_entity)
                path_edges.append(edge)
                current = next_entity
            
            # Check if final node is a target
            if current in target_set and len(path_entities) > 1:
                if not any(p.entities == path_entities for p in paths):
                    paths.append(EvidencePath(
                        entities=path_entities,
                        edges=path_edges
                    ))
        
        return paths

    def _bfs_walk(
        self,
        start: Entity,
        targets: List[Entity],
        edges: List[Edge],
        max_length: int
    ) -> List[EvidencePath]:
        """
        BFS-based path exploration from start to targets
        
        Args:
            start: Starting entity
            targets: List of target entities
            edges: Available edges
            max_length: Maximum path length
        
        Returns:
            List of paths found
        """
        from collections import deque
        
        paths = []
        target_set = set(targets)
        queue = deque([(start, [start], [])])
        
        while queue:
            current, path_entities, path_edges = queue.popleft()
            
            # Check length limit
            if len(path_entities) > max_length:
                continue
            
            # Check if we reached a target
            if current in target_set and len(path_entities) > 1:
                paths.append(EvidencePath(
                    entities=path_entities,
                    edges=path_edges
                ))
                continue  # Continue searching for other paths
            
            # Explore neighbors
            for edge in edges:
                if edge.source == current:
                    next_entity = edge.target
                    # Avoid cycles
                    if next_entity not in path_entities:
                        queue.append((
                            next_entity,
                            path_entities + [next_entity],
                            path_edges + [edge]
                        ))
        
        return paths

    def _dfs_walk(
        self,
        start: Entity,
        targets: List[Entity],
        edges: List[Edge],
        max_length: int
    ) -> List[EvidencePath]:
        """
        DFS-based path exploration from start to targets
        
        Args:
            start: Starting entity
            targets: List of target entities
            edges: Available edges
            max_length: Maximum path length
        
        Returns:
            List of paths found
        """
        paths = []
        target_set = set(targets)
        
        def dfs_recursive(current, path_entities, path_edges, depth):
            # Check depth limit
            if depth > max_length:
                return
            
            # Check if we reached a target
            if current in target_set and len(path_entities) > 1:
                paths.append(EvidencePath(
                    entities=path_entities.copy(),
                    edges=path_edges.copy()
                ))
                return  # Can continue or return based on requirements
            
            # Explore neighbors
            for edge in edges:
                if edge.source == current:
                    next_entity = edge.target
                    # Avoid cycles
                    if next_entity not in path_entities:
                        path_entities.append(next_entity)
                        path_edges.append(edge)
                        
                        dfs_recursive(next_entity, path_entities, path_edges, depth + 1)
                        
                        # Backtrack
                        path_entities.pop()
                        path_edges.pop()
        
        dfs_recursive(start, [start], [], 0)
        return paths

    def _deduplicate_paths(self, paths: List[EvidencePath]) -> List[EvidencePath]:
        """Remove duplicate paths based on entity sequence"""
        seen = set()
        unique_paths = []
        
        for path in paths:
            # Create a hashable representation of the path
            entity_ids = tuple(id(e) for e in path.entities)
            
            if entity_ids not in seen:
                seen.add(entity_ids)
                unique_paths.append(path)
        
        return unique_paths
    
    def _rank_paths_with_llm(
        self,
        query: str,
        path_strs: List[str]
    ) -> Dict[str, Any]:
        """Use LLM to rank paths semantically"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self.get_ranking_prompt(query, path_strs)}
        ]
        
        try:
            ranking = self.llm.generate_json(messages, temperature=0.3)
            return ranking
        except Exception as e:
            print(f"[Re-ranker Agent] Error ranking paths: {e}")
            return {"ranked_paths": [], "pruned_count": 0, "reasoning": "Error"}
    
    def _calculate_structural_scores(self, paths: List[EvidencePath]) -> List[float]:
        """Calculate structural importance scores for paths"""
        scores = []
        
        for path in paths:
            # Factors for structural score:
            # 1. Path length (shorter is often better)
            # 2. Edge confidence (higher is better)
            # 3. Entity centrality (more connections = more important)
            
            length_score = 1.0 / (1.0 + len(path.entities))
            
            avg_confidence = sum(e.confidence for e in path.edges) / max(len(path.edges), 1)
            
            structural_score = 0.6 * length_score + 0.4 * avg_confidence
            scores.append(structural_score)
        
        return scores
    
    def _combine_scores(
        self,
        paths: List[EvidencePath],
        llm_ranking: Dict[str, Any],
        structural_scores: List[float]
    ) -> List[EvidencePath]:
        """Combine semantic and structural scores"""
        ranked_paths_data = llm_ranking.get("ranked_paths", [])
        
        # Create a mapping of path_id to semantic score
        semantic_scores = {}
        for ranked_path in ranked_paths_data:
            path_id = ranked_path.get("path_id", 0) - 1  # Convert to 0-indexed
            overall = ranked_path.get("overall_score", 0.5)
            semantic_scores[path_id] = overall
        
        # Combine scores
        for i, path in enumerate(paths):
            semantic = semantic_scores.get(i, 0.3)  # Default if not in LLM output
            structural = structural_scores[i] if i < len(structural_scores) else 0.5
            
            final_score = (
                self.semantic_weight * semantic +
                self.structural_weight * structural
            )
            path.score = final_score
        
        return paths
    
    def _prune_subgraph(self, subgraph, top_paths: List[EvidencePath]):
        """Prune subgraph to only include entities in top-ranked paths"""
        from .models import EvidenceSubgraph
        
        pruned_subgraph = EvidenceSubgraph()
        
        # Collect all entities and edges from top paths
        for path in top_paths:
            for entity in path.entities:
                pruned_subgraph.add_entity(entity)
            for edge in path.edges:
                pruned_subgraph.add_edge(edge)
        
        pruned_subgraph.paths = top_paths
        return pruned_subgraph
