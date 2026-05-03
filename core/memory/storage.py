"""SQLite storage backend for Skeleton AI memory system."""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from .schemas import Task, Reflection


class MemoryStorage:
    """SQLite-based storage for task and reflection memories."""
    
    def __init__(self, db_path: str = "data/memory.db"):
        """Initialize storage with database path."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal TEXT NOT NULL,
                    steps TEXT NOT NULL,
                    result TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Reflections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reflections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    insight TEXT NOT NULL,
                    rule TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)
            
            # Indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_goal 
                ON tasks(goal)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_success 
                ON tasks(success)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_timestamp 
                ON tasks(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_reflections_task_id 
                ON reflections(task_id)
            """)
    
    def store_task(self, task: Task) -> int:
        """Store a task and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (goal, steps, result, success, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                task.goal,
                task.steps,
                task.result,
                1 if task.success else 0,
                task.timestamp.isoformat()
            ))
            return cursor.lastrowid
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row:
                return Task(
                    id=row["id"],
                    goal=row["goal"],
                    steps=row["steps"],
                    result=row["result"],
                    success=bool(row["success"]),
                    timestamp=datetime.fromisoformat(row["timestamp"])
                )
            return None
    
    def get_similar_tasks(self, keyword: str, limit: int = 10) -> List[Task]:
        """Find tasks matching a keyword in goal or steps."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{keyword}%"
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE goal LIKE ? OR steps LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (search_pattern, search_pattern, limit))
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append(Task(
                    id=row["id"],
                    goal=row["goal"],
                    steps=row["steps"],
                    result=row["result"],
                    success=bool(row["success"]),
                    timestamp=datetime.fromisoformat(row["timestamp"])
                ))
            return tasks
    
    def get_successful_tasks(self, limit: int = 10) -> List[Task]:
        """Retrieve recently successful tasks."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE success = 1
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append(Task(
                    id=row["id"],
                    goal=row["goal"],
                    steps=row["steps"],
                    result=row["result"],
                    success=True,
                    timestamp=datetime.fromisoformat(row["timestamp"])
                ))
            return tasks
    
    def store_reflection(self, reflection: Reflection) -> int:
        """Store a reflection and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reflections (task_id, insight, rule, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                reflection.task_id,
                reflection.insight,
                reflection.rule,
                reflection.timestamp.isoformat()
            ))
            return cursor.lastrowid
    
    def get_reflections_for_task(self, task_id: int) -> List[Reflection]:
        """Get all reflections for a specific task."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reflections 
                WHERE task_id = ?
                ORDER BY timestamp DESC
            """, (task_id,))
            
            reflections = []
            for row in cursor.fetchall():
                reflections.append(Reflection(
                    id=row["id"],
                    task_id=row["task_id"],
                    insight=row["insight"],
                    rule=row["rule"],
                    timestamp=datetime.fromisoformat(row["timestamp"])
                ))
            return reflections
    
    def get_all_rules(self, limit: int = 50) -> List[str]:
        """Retrieve all stored rules from reflections."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rule FROM reflections 
                WHERE rule IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [row["rule"] for row in cursor.fetchall() if row["rule"]]
    
    def get_recent_tasks(self, limit: int = 20) -> List[Task]:
        """Get most recent tasks regardless of success."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks 
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append(Task(
                    id=row["id"],
                    goal=row["goal"],
                    steps=row["steps"],
                    result=row["result"],
                    success=bool(row["success"]),
                    timestamp=datetime.fromisoformat(row["timestamp"])
                ))
            return tasks
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE success = 1")
            successful_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reflections")
            total_reflections = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reflections WHERE rule IS NOT NULL")
            total_rules = cursor.fetchone()[0]
            
            return {
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
                "total_reflections": total_reflections,
                "total_rules": total_rules
            }
