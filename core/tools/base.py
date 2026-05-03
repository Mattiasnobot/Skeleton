"""
Base tool classes and types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path


@dataclass
class ToolResult:
    """Structured result from tool execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def ok(cls, output: Any, **metadata) -> 'ToolResult':
        """Create successful result."""
        return cls(success=True, output=output, metadata=metadata)
    
    @classmethod
    def fail(cls, error: str, output: Any = None) -> 'ToolResult':
        """Create failed result."""
        return cls(success=False, output=output, error=error)


class ToolError(Exception):
    """Exception raised by tools during execution."""
    pass


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    Every tool must:
    - Accept structured args (dict)
    - Return structured output (ToolResult)
    - Declare required permissions
    """
    
    name: str = "base_tool"
    description: str = "Base tool class"
    required_permissions: List[str] = field(default_factory=list)
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with given arguments.
        
        Args:
            args: Dictionary of tool-specific arguments.
            
        Returns:
            ToolResult with success status and output/error.
        """
        pass
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """
        Validate that required arguments are present.
        
        Override in subclasses for more complex validation.
        """
        return True
    
    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"
