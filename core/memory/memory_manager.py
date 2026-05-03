"""Memory Manager - The brain interface for Skeleton AI."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .schemas import Task, Reflection, MemoryQuery
from .storage import MemoryStorage
from .retrieval import RetrievalSystem

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Central memory management interface for Skeleton AI.
    
    Provides methods to store tasks, retrieve similar experiences,
    and manage learned rules/reflections.
    
    Usage:
        memory = MemoryManager()
        
        # Store a completed task
        memory.store_task(
            goal="organize files by extension",
            steps="1. List files\n2. Group by extension\n3. Create folders",
            result="Successfully organized 50 files into 5 folders",
            success=True
        )
        
        # Find similar past tasks
        similar = memory.get_similar_tasks("organize files")
        
        # Store a reflection/rule learned from the task
        memory.store_reflection(
            insight="Grouping by extension is efficient",
            rule="Always group files by extension before moving"
        )
        
        # Get relevant rules before executing a task
        rules = memory.get_rules("file organization")
    """
    
    def __init__(self, db_path: str = "data/memory.db"):
        """
        Initialize memory manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.storage = MemoryStorage(db_path)
        self.retrieval = RetrievalSystem(self.storage)
        logger.info(f"MemoryManager initialized with database: {db_path}")
    
    def store_task(
        self,
        goal: str,
        steps: str,
        result: str,
        success: bool,
        timestamp: Optional[datetime] = None
    ) -> int:
        """
        Store a completed task in memory.
        
        Args:
            goal: What the task was trying to accomplish
            steps: Steps taken to complete the task
            result: Outcome of the task
            success: Whether the task succeeded
            timestamp: When the task occurred (default: now)
            
        Returns:
            Task ID for future reference
        """
        task = Task(
            goal=goal,
            steps=steps,
            result=result,
            success=success,
            timestamp=timestamp or datetime.now()
        )
        
        task_id = self.storage.store_task(task)
        logger.debug(f"Stored task {task_id}: {goal[:50]}...")
        return task_id
    
    def store_reflection(
        self,
        task_id: int,
        insight: str,
        rule: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> int:
        """
        Store a reflection or learned rule from a task.
        
        Args:
            task_id: ID of the task this reflection relates to
            insight: Key insight learned
            rule: Actionable rule extracted (optional)
            timestamp: When the reflection occurred
            
        Returns:
            Reflection ID
        """
        reflection = Reflection(
            task_id=task_id,
            insight=insight,
            rule=rule,
            timestamp=timestamp or datetime.now()
        )
        
        reflection_id = self.storage.store_reflection(reflection)
        if rule:
            logger.info(f"Stored rule {reflection_id}: {rule[:50]}...")
        else:
            logger.debug(f"Stored reflection {reflection_id}: {insight[:50]}...")
        return reflection_id
    
    def get_similar_tasks(
        self, 
        goal: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find tasks similar to the given goal.
        
        Args:
            goal: Current goal to find similarities for
            limit: Maximum number of tasks to return
            
        Returns:
            List of tasks with their scores
        """
        results = self.retrieval.find_similar_tasks(goal, limit=limit)
        
        similar_tasks = []
        for task, score in results:
            similar_tasks.append({
                "task": task,
                "score": score,
                "similarity_percent": min(100, score)
            })
        
        if similar_tasks:
            logger.debug(f"Found {len(similar_tasks)} similar tasks for: {goal[:30]}...")
        else:
            logger.debug(f"No similar tasks found for: {goal[:30]}...")
        
        return similar_tasks
    
    def get_successful_strategies(
        self, 
        keyword: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find successful strategies related to a keyword.
        
        Args:
            keyword: Topic to search for
            limit: Maximum results
            
        Returns:
            List of successful tasks with scores
        """
        results = self.retrieval.find_successful_strategies(keyword, limit=limit)
        
        strategies = []
        for task, score in results:
            strategies.append({
                "task": task,
                "score": score
            })
        
        return strategies
    
    def get_rules(self, context: Optional[str] = None, limit: int = 10) -> List[str]:
        """
        Retrieve learned rules, optionally filtered by context.
        
        Args:
            context: Current context to filter relevant rules
            limit: Maximum number of rules to return
            
        Returns:
            List of rule strings
        """
        rules = self.retrieval.get_relevant_rules(context or "", limit=limit)
        logger.debug(f"Retrieved {len(rules)} rules" + (f" for context: {context[:30]}..." if context else ""))
        return rules
    
    def get_recent_tasks(self, limit: int = 10) -> List[Task]:
        """
        Get most recent tasks regardless of success.
        
        Args:
            limit: Number of tasks to retrieve
            
        Returns:
            List of recent tasks
        """
        return self.storage.get_recent_tasks(limit)
    
    def analyze_and_store(
        self,
        goal: str,
        steps: str,
        result: str,
        success: bool,
        auto_generate_reflection: bool = True
    ) -> Dict[str, Any]:
        """
        Store a task and optionally auto-generate reflection.
        
        This is a convenience method that combines task storage
        with automatic reflection generation.
        
        Args:
            goal: Task goal
            steps: Steps taken
            result: Task outcome
            success: Whether it succeeded
            auto_generate_reflection: If True, creates basic reflection
            
        Returns:
            Dictionary with task_id and reflection_id (if generated)
        """
        # Store the task
        task_id = self.store_task(goal, steps, result, success)
        
        result_data = {"task_id": task_id}
        
        # Auto-generate basic reflection
        if auto_generate_reflection:
            insight = f"Task {'succeeded' if success else 'failed'}: {goal}"
            rule = None
            
            # Generate simple rule based on outcome
            if success:
                rule = f"When {goal.lower()}, use similar approach"
            else:
                rule = f"Avoid previous approach when {goal.lower()}"
            
            reflection_id = self.store_reflection(task_id, insight, rule)
            result_data["reflection_id"] = reflection_id
        
        return result_data
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics.
        
        Returns:
            Dictionary with memory stats
        """
        stats = self.storage.get_stats()
        logger.debug(f"Memory stats: {stats}")
        return stats
    
    def clear_memory(self, confirm: bool = False):
        """
        Clear all memories (use with caution).
        
        Args:
            confirm: Must be True to proceed
        """
        if not confirm:
            logger.warning("Clear memory called without confirmation")
            return
        
        logger.warning("Clearing all memory data")
        # Reinitialize database
        self.storage._init_database()
        logger.info("Memory cleared")
