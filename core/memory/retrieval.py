"""Memory retrieval system with scoring for Skeleton AI."""
from typing import List, Tuple
from datetime import datetime, timedelta

from .schemas import Task, MemoryQuery
from .storage import MemoryStorage


class RetrievalSystem:
    """Handles intelligent retrieval of memories with scoring."""
    
    def __init__(self, storage: MemoryStorage):
        """Initialize with storage backend."""
        self.storage = storage
    
    def calculate_task_score(
        self, 
        task: Task, 
        query: MemoryQuery,
        current_time: datetime = None
    ) -> float:
        """
        Calculate relevance score for a task.
        
        Scoring factors:
        - Keyword match strength
        - Success weight (successful tasks scored higher)
        - Recency (newer tasks scored higher)
        """
        if current_time is None:
            current_time = datetime.now()
        
        score = 0.0
        
        # Keyword matching (0-40 points)
        if query.keyword:
            keyword_lower = query.keyword.lower()
            goal_lower = task.goal.lower()
            steps_lower = task.steps.lower()
            
            # Exact match in goal: 40 points
            if keyword_lower in goal_lower:
                score += 40
            # Match in steps: 25 points
            elif keyword_lower in steps_lower:
                score += 25
            
            # Partial word matches: 10 points each
            words = keyword_lower.split()
            for word in words:
                if len(word) > 2:
                    if word in goal_lower or word in steps_lower:
                        score += 10
        
        # Success weight (0-30 points)
        if task.success:
            score += 30
        else:
            # Failed tasks still have some value for learning
            score += 5
        
        # Recency score (0-30 points)
        # Tasks from last 24 hours get full points, decaying over 7 days
        time_diff = current_time - task.timestamp
        if time_diff < timedelta(hours=24):
            score += 30
        elif time_diff < timedelta(days=7):
            decay_factor = 1 - (time_diff.days / 7)
            score += 30 * decay_factor
        
        return score
    
    def search(
        self, 
        query: MemoryQuery
    ) -> List[Tuple[Task, float]]:
        """
        Search for tasks matching query with scores.
        
        Returns list of (task, score) tuples sorted by score descending.
        """
        tasks = []
        
        # Get candidate tasks
        if query.keyword:
            tasks.extend(self.storage.get_similar_tasks(query.keyword, limit=query.limit * 2))
        else:
            tasks.extend(self.storage.get_recent_tasks(limit=query.limit * 2))
        
        # Score and filter tasks
        scored_tasks = []
        for task in tasks:
            score = self.calculate_task_score(task, query)
            
            # Filter by minimum success score
            if query.min_success_score > 0 and not task.success:
                continue
            
            if score >= query.min_success_score * 100:  # Convert to 0-100 scale
                scored_tasks.append((task, score))
        
        # Sort by score descending
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return scored_tasks[:query.limit]
    
    def find_similar_tasks(
        self, 
        goal: str, 
        limit: int = 5
    ) -> List[Tuple[Task, float]]:
        """Find tasks similar to the given goal."""
        query = MemoryQuery(keyword=goal, limit=limit)
        return self.search(query)
    
    def find_successful_strategies(
        self, 
        keyword: str, 
        limit: int = 5
    ) -> List[Tuple[Task, float]]:
        """Find successful tasks related to keyword."""
        query = MemoryQuery(
            keyword=keyword,
            min_success_score=0.5,
            limit=limit
        )
        return self.search(query)
    
    def get_relevant_rules(self, context: str, limit: int = 10) -> List[str]:
        """
        Get rules relevant to current context.
        
        For now, returns all rules. Later can be enhanced with
        keyword matching on context.
        """
        all_rules = self.storage.get_all_rules(limit=50)
        
        # Simple keyword-based filtering
        if context:
            context_lower = context.lower()
            relevant_rules = []
            
            for rule in all_rules:
                rule_lower = rule.lower()
                # Check if any word from context appears in rule
                words = context_lower.split()
                for word in words:
                    if len(word) > 3 and word in rule_lower:
                        relevant_rules.append(rule)
                        break
            
            if relevant_rules:
                return relevant_rules[:limit]
        
        return all_rules[:limit]
