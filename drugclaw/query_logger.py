"""
Query Logger - Saves and manages query history with persistent storage
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import pickle

class QueryLogger:
    """
    Manages persistent storage of query history
    Saves queries, answers, reasoning steps, and metadata
    """
    
    def __init__(self, log_dir: str = "./query_logs"):
        """
        Initialize query logger
        
        Args:
            log_dir: Directory to store query logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON log file for easy reading
        self.json_log_file = self.log_dir / "query_history.jsonl"
        
        # Pickle file for complete objects (including subgraphs)
        self.pickle_log_dir = self.log_dir / "detailed_logs"
        self.pickle_log_dir.mkdir(exist_ok=True)
        
        # Index file for quick lookup
        self.index_file = self.log_dir / "query_index.json"
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load or create the query index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {
                'total_queries': 0,
                'queries': []
            }
            self._save_index()
    
    def _save_index(self):
        """Save the query index"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, indent=2, fp=f)
    
    def log_query(
        self,
        query: str,
        result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a query and its results
        
        Args:
            query: The original query
            result: The result dictionary from system.query()
            metadata: Optional metadata (user_id, session_id, etc.)
            
        Returns:
            query_id: Unique identifier for this query
        """
        # Generate unique query ID
        timestamp = datetime.now()
        query_id = f"query_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Prepare log entry
        log_entry = {
            'query_id': query_id,
            'timestamp': timestamp.isoformat(),
            'query': query,
            'answer': result.get('answer', ''),
            'iterations': result.get('iterations', 0),
            'evidence_graph_size': result.get('evidence_graph_size', 0),
            'final_reward': result.get('final_reward', 0.0),
            'success': result.get('success', False),
            'metadata': metadata or {}
        }
        
        # Add reasoning history summary (simplified for JSONL)
        reasoning_history = result.get('reasoning_history', [])
        log_entry['reasoning_summary'] = [
            {
                'step': step.get('step', 0),
                'reward': step.get('reward', 0.0),
                'evidence_sufficiency': step.get('evidence_sufficiency', 0.0)
            }
            for step in reasoning_history
        ]
        
        # Save to JSONL file (one JSON object per line)
        with open(self.json_log_file, 'a') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        # Save complete result with all details to pickle
        pickle_file = self.pickle_log_dir / f"{query_id}.pkl"
        with open(pickle_file, 'wb') as f:
            pickle.dump({
                'query_id': query_id,
                'timestamp': timestamp,
                'query': query,
                'full_result': result,
                'metadata': metadata,
                # 新增：保存详细的推理历史
                'detailed_reasoning_history': result.get('detailed_reasoning_history', []),
                'retrieved_content': result.get('retrieved_content', []),
                'reflection_feedback': result.get('reflection_feedback', ''),
                'web_search_results': result.get('web_search_results', [])
            }, f)
        
        # Update index
        self.index['total_queries'] += 1
        self.index['queries'].append({
            'query_id': query_id,
            'timestamp': timestamp.isoformat(),
            'query': query[:100],  # First 100 chars
            'success': result.get('success', False),
            'iterations': result.get('iterations', 0)  # 新增迭代次数到索引
        })
        self._save_index()
        
        print(f"[QueryLogger] Logged query: {query_id}")
        return query_id
    
    def get_query(self, query_id: str, detailed: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retrieve a logged query by ID
        
        Args:
            query_id: The query ID to retrieve
            detailed: If True, load from pickle with full details
            
        Returns:
            Query log entry or None if not found
        """
        if detailed:
            pickle_file = self.pickle_log_dir / f"{query_id}.pkl"
            if pickle_file.exists():
                with open(pickle_file, 'rb') as f:
                    return pickle.load(f)
            return None
        else:
            # Search in JSONL file
            if not self.json_log_file.exists():
                return None
            
            with open(self.json_log_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get('query_id') == query_id:
                        return entry
            return None
    
    def get_recent_queries(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get the N most recent queries
        
        Args:
            n: Number of recent queries to retrieve
            
        Returns:
            List of query entries
        """
        recent = self.index['queries'][-n:]
        recent.reverse()  # Most recent first
        return recent
    
    def search_queries(
        self,
        keyword: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search queries with filters
        
        Args:
            keyword: Search in query text
            start_date: Filter by start date
            end_date: Filter by end date
            success_only: Only return successful queries
            
        Returns:
            List of matching query entries
        """
        results = []
        
        if not self.json_log_file.exists():
            return results
        
        with open(self.json_log_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                
                # Apply filters
                if keyword and keyword.lower() not in entry.get('query', '').lower():
                    continue
                
                if success_only and not entry.get('success', False):
                    continue
                
                entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                if start_date and entry_time < start_date:
                    continue
                if end_date and entry_time > end_date:
                    continue
                
                results.append(entry)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about logged queries
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_queries': self.index['total_queries'],
            'successful_queries': 0,
            'failed_queries': 0,
            'avg_iterations': 0,
            'avg_reward': 0,
            'avg_graph_size': 0
        }
        
        if not self.json_log_file.exists():
            return stats
        
        total_iterations = 0
        total_reward = 0
        total_graph_size = 0
        count = 0
        
        with open(self.json_log_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                count += 1
                
                if entry.get('success', False):
                    stats['successful_queries'] += 1
                else:
                    stats['failed_queries'] += 1
                
                total_iterations += entry.get('iterations', 0)
                total_reward += entry.get('final_reward', 0)
                total_graph_size += entry.get('evidence_graph_size', 0)
        
        if count > 0:
            stats['avg_iterations'] = total_iterations / count
            stats['avg_reward'] = total_reward / count
            stats['avg_graph_size'] = total_graph_size / count
        
        return stats
    
    def export_to_csv(self, output_file: str):
        """
        Export query history to CSV
        
        Args:
            output_file: Path to output CSV file
        """
        import csv
        
        if not self.json_log_file.exists():
            print("[QueryLogger] No queries to export")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'query_id', 'timestamp', 'query', 'answer',
                'iterations', 'evidence_graph_size', 'final_reward', 'success'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            with open(self.json_log_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    # Extract only the fields we want
                    row = {k: entry.get(k, '') for k in fieldnames}
                    # Truncate answer for CSV
                    row['answer'] = row['answer'][:500] if row['answer'] else ''
                    writer.writerow(row)
        
        print(f"[QueryLogger] Exported to {output_file}")
    
    def clear_logs(self, confirm: bool = False):
        """
        Clear all query logs (use with caution!)
        
        Args:
            confirm: Must be True to actually clear
        """
        if not confirm:
            print("[QueryLogger] Set confirm=True to clear logs")
            return
        
        # Remove files
        if self.json_log_file.exists():
            self.json_log_file.unlink()
        
        # Clear pickle files
        for pkl_file in self.pickle_log_dir.glob("*.pkl"):
            pkl_file.unlink()
        
        # Reset index
        self.index = {
            'total_queries': 0,
            'queries': []
        }
        self._save_index()
        
        print("[QueryLogger] All logs cleared")

    def get_detailed_reasoning_history(self, query_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get detailed reasoning history for a specific query
        
        Args:
            query_id: The query ID
            
        Returns:
            List of detailed reasoning steps or None if not found
        """
        pickle_file = self.pickle_log_dir / f"{query_id}.pkl"
        if not pickle_file.exists():
            return None
        
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)
            return data.get('detailed_reasoning_history', [])

    def print_reasoning_trace(self, query_id: str):
        """
        Print a formatted trace of the reasoning process
        
        Args:
            query_id: The query ID
        """
        history = self.get_detailed_reasoning_history(query_id)
        if not history:
            print(f"No detailed history found for {query_id}")
            return
        
        print(f"\n{'='*80}")
        print(f"Reasoning Trace for {query_id}")
        print(f"{'='*80}\n")
        
        for step_data in history:
            print(f"Step {step_data['step_id']}:")
            print(f"  Query: {step_data['query']}")
            print(f"  Answer: {step_data['intermediate_answer'][:200]}...")
            print(f"  Reward: {step_data['reward']:.3f}")
            print(f"  Evidence Sufficiency: {step_data['evidence_sufficiency']:.3f}")
            print(f"  Subgraph Size: {step_data['subgraph_size']} entities")
            print(f"  Actions: {', '.join(step_data['actions_taken'])}")
            print(f"  Top Paths:")
            for i, path in enumerate(step_data['subgraph_paths'][:3], 1):
                print(f"    {i}. {' → '.join(path['entities'])} (score: {path['score']:.3f})")
            print()

class QuerySession:
    """
    Manages a session of related queries
    Useful for tracking conversations or research sessions
    """
    
    def __init__(self, session_id: Optional[str] = None, log_dir: str = "./query_logs"):
        """
        Initialize a query session
        
        Args:
            session_id: Optional session identifier
            log_dir: Directory for logs
        """
        self.logger = QueryLogger(log_dir)
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.queries = []
        self.start_time = datetime.now()
    
    def log_query(self, query: str, result: Dict[str, Any]) -> str:
        """
        Log a query within this session
        
        Args:
            query: The query
            result: The result
            
        Returns:
            query_id
        """
        metadata = {
            'session_id': self.session_id,
            'query_number': len(self.queries) + 1
        }
        
        query_id = self.logger.log_query(query, result, metadata)
        self.queries.append(query_id)
        return query_id
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of this session"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'duration_seconds': duration,
            'total_queries': len(self.queries),
            'query_ids': self.queries
        }