"""
Tool registry - Hard-coded tool mapping (Phase 1).
No dynamic loading yet.
"""

from typing import Any, Dict, Optional
from .base import BaseTool, ToolResult, ToolError


class ToolRegistry:
    """
    Hard-coded tool registry.
    
    Phase 1 implementation: Simple dictionary mapping.
    Future phases can add dynamic loading, permissions checking, etc.
    """
    
    def __init__(self, sandbox_root: str):
        """
        Initialize registry with tools.
        
        Args:
            sandbox_root: Root directory for sandboxed file operations.
        """
        self.sandbox_root = sandbox_root
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """Register the initial set of tools."""
        # Import here to avoid circular imports
        from .file_tools import ListFilesTool, ReadFileTool
        
        # Register tools with sandbox root
        self._tools["list_files"] = ListFilesTool(self.sandbox_root)
        self._tools["read_file"] = ReadFileTool(self.sandbox_root)
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def execute(self, name: str, args: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool by name with given arguments.
        
        Args:
            name: Tool name from registry.
            args: Arguments to pass to tool.
            
        Returns:
            ToolResult with execution outcome.
            
        Raises:
            ToolError: If tool not found or execution fails.
        """
        tool = self.get(name)
        if tool is None:
            return ToolResult.fail(f"Unknown tool: {name}")
        
        try:
            # Validate args first
            if not tool.validate_args(args):
                return ToolResult.fail("Invalid arguments for tool")
            
            # Execute tool
            result = tool.execute(args)
            return result
            
        except ToolError as e:
            return ToolResult.fail(str(e), output=None)
        except Exception as e:
            return ToolResult.fail(f"Tool execution error: {str(e)}")
    
    def list_tools(self) -> Dict[str, str]:
        """List all registered tools with descriptions."""
        return {name: tool.description for name, tool in self._tools.items()}
    
    def __contains__(self, name: str) -> bool:
        """Check if tool exists in registry."""
        return name in self._tools
    
    def __repr__(self) -> str:
        return f"<ToolRegistry: {len(self._tools)} tools>"
