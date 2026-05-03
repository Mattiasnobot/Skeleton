"""
File system tools with sandbox protection.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

from .base import BaseTool, ToolResult


class ListFilesTool(BaseTool):
    """List files in a directory within the sandbox."""
    
    name = "list_files"
    description = "List files and directories in a given path"
    required_permissions = ["READ"]
    
    def __init__(self, sandbox_root: str):
        """Initialize with sandbox root for path validation."""
        self.sandbox_root = Path(sandbox_root).resolve()
    
    def _validate_path(self, path: str) -> bool:
        """Ensure path is within sandbox."""
        try:
            resolved = Path(path).resolve()
            # Check if resolved path starts with sandbox root
            return str(resolved).startswith(str(self.sandbox_root))
        except Exception:
            return False
    
    def execute(self, args: Dict[str, Any]) -> ToolResult:
        """
        List files in directory.
        
        Args:
            args: {"path": "directory path"}
        """
        path_str = args.get("path", str(self.sandbox_root))
        
        # Validate path is within sandbox
        if not self._validate_path(path_str):
            return ToolResult.fail(f"Path outside sandbox: {path_str}")
        
        path = Path(path_str)
        
        if not path.exists():
            return ToolResult.fail(f"Path does not exist: {path_str}")
        
        if not path.is_dir():
            return ToolResult.fail(f"Not a directory: {path_str}")
        
        try:
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item),
                })
            
            return ToolResult.ok(
                output=items,
                count=len(items),
                directory=str(path)
            )
        except PermissionError:
            return ToolResult.fail(f"Permission denied: {path_str}")
        except Exception as e:
            return ToolResult.fail(f"Error listing directory: {str(e)}")


class ReadFileTool(BaseTool):
    """Read file contents within the sandbox."""
    
    name = "read_file"
    description = "Read contents of a text file"
    required_permissions = ["READ"]
    
    def __init__(self, sandbox_root: str):
        """Initialize with sandbox root for path validation."""
        self.sandbox_root = Path(sandbox_root).resolve()
    
    def _validate_path(self, path: str) -> bool:
        """Ensure path is within sandbox."""
        try:
            resolved = Path(path).resolve()
            return str(resolved).startswith(str(self.sandbox_root))
        except Exception:
            return False
    
    def execute(self, args: Dict[str, Any]) -> ToolResult:
        """
        Read file contents.
        
        Args:
            args: {"path": "file path"}
        """
        path_str = args.get("path")
        
        if not path_str:
            return ToolResult.fail("Missing required argument: path")
        
        # Validate path is within sandbox
        if not self._validate_path(path_str):
            return ToolResult.fail(f"Path outside sandbox: {path_str}")
        
        path = Path(path_str)
        
        if not path.exists():
            return ToolResult.fail(f"File does not exist: {path_str}")
        
        if not path.is_file():
            return ToolResult.fail(f"Not a file: {path_str}")
        
        try:
            content = path.read_text(encoding='utf-8')
            return ToolResult.ok(
                output=content,
                lines=len(content.splitlines()),
                size=len(content),
                file=str(path)
            )
        except UnicodeDecodeError:
            return ToolResult.fail(f"Cannot read binary file: {path_str}")
        except PermissionError:
            return ToolResult.fail(f"Permission denied: {path_str}")
        except Exception as e:
            return ToolResult.fail(f"Error reading file: {str(e)}")
