"""Memory schemas for Skeleton AI."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Task:
    """Represents a completed task with its outcome."""
    goal: str
    steps: str
    result: str
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "goal": self.goal,
            "steps": self.steps,
            "result": self.result,
            "success": 1 if self.success else 0,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Reflection:
    """Represents an insight or rule learned from a task."""
    task_id: int
    insight: str
    rule: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "insight": self.insight,
            "rule": self.rule,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class MemoryQuery:
    """Represents a query for retrieving memories."""
    keyword: Optional[str] = None
    min_success_score: float = 0.0
    limit: int = 10
    include_reflections: bool = True
