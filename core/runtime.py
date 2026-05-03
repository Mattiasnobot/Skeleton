"""
Runtime - Main execution loop for Skeleton.

Phase 1: Core loop MVP
- Continuous execution
- Tool-based action system
- Simple intent parsing
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .tools import ToolRegistry, ToolResult


logger = logging.getLogger(__name__)


class Runtime:
    """
    Main runtime loop for Skeleton.
    
    Executes user intents through tools with sandboxing.
    """
    
    def __init__(self, sandbox_root: str):
        """
        Initialize runtime.
        
        Args:
            sandbox_root: Root directory for all sandboxed operations.
        """
        self.sandbox_root = Path(sandbox_root).resolve()
        self.tool_registry = ToolRegistry(self.sandbox_root)
        self._running = False
        
        # Ensure sandbox root exists
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Runtime initialized with sandbox: {self.sandbox_root}")
    
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input into structured intent.
        
        Phase 1: Simple JSON parsing or hardcoded format.
        Future phases: LLM-based parsing.
        
        Args:
            user_input: Raw user input string.
            
        Returns:
            Intent dict with 'tool' and 'args' keys.
        """
        user_input = user_input.strip()
        
        # Try JSON format first
        if user_input.startswith('{'):
            try:
                intent = json.loads(user_input)
                if 'tool' not in intent:
                    return {'tool': 'unknown', 'args': {}, 'error': 'Missing "tool" key'}
                return intent
            except json.JSONDecodeError as e:
                return {'tool': 'unknown', 'args': {}, 'error': f'Invalid JSON: {str(e)}'}
        
        # Simple command parsing for common patterns
        # Format: "list_files /path" or "read_file /path"
        parts = user_input.split(maxsplit=1)
        if len(parts) >= 1:
            tool_name = parts[0]
            path_arg = parts[1] if len(parts) > 1 else str(self.sandbox_root)
            
            if tool_name in ['list_files', 'read_file']:
                return {
                    'tool': tool_name,
                    'args': {'path': path_arg}
                }
        
        # Unknown format
        return {
            'tool': 'unknown',
            'args': {},
            'error': 'Could not parse intent. Use JSON or "tool_name path" format.'
        }
    
    def execute_intent(self, intent: Dict[str, Any]) -> ToolResult:
        """
        Execute a parsed intent.
        
        Args:
            intent: Parsed intent dict with 'tool' and 'args'.
            
        Returns:
            ToolResult from execution.
        """
        tool_name = intent.get('tool', 'unknown')
        args = intent.get('args', {})
        
        # Check for parse errors
        if 'error' in intent:
            return ToolResult.fail(intent['error'])
        
        logger.info(f"Executing tool: {tool_name} with args: {args}")
        
        # Execute through registry
        result = self.tool_registry.execute(tool_name, args)
        
        if result.success:
            logger.debug(f"Tool execution successful: {tool_name}")
        else:
            logger.warning(f"Tool execution failed: {tool_name} - {result.error}")
        
        return result
    
    def run_interactive(self) -> None:
        """
        Run interactive loop.
        
        Phase 1: Simple REPL with tool execution.
        """
        self._running = True
        
        print(f"\n🦴 Skeleton Runtime v0.1.0")
        print(f"Sandbox: {self.sandbox_root}")
        print(f"Available tools: {', '.join(self.tool_registry.list_tools().keys())}")
        print(f"Type 'quit' to exit, 'tools' to list tools\n")
        
        while self._running:
            try:
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ('quit', 'exit', 'q'):
                    print("Shutting down...")
                    break
                
                if user_input.lower() == 'tools':
                    print("\nAvailable tools:")
                    for name, desc in self.tool_registry.list_tools().items():
                        print(f"  {name}: {desc}")
                    print()
                    continue
                
                # Parse and execute
                intent = self.parse_intent(user_input)
                result = self.execute_intent(intent)
                
                # Display result
                if result.success:
                    print(f"✓ Success:")
                    if isinstance(result.output, (list, dict)):
                        print(json.dumps(result.output, indent=2))
                    else:
                        print(result.output)
                    if result.metadata:
                        print(f"[Metadata: {result.metadata}]")
                else:
                    print(f"✗ Error: {result.error}")
                
                print()
                
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'quit' to exit.\n")
            except EOFError:
                print("\nEOF received. Shutting down...")
                break
            except Exception as e:
                logger.exception(f"Unexpected error in runtime loop: {e}")
                print(f"Unexpected error: {e}\n")
        
        self._running = False
        logger.info("Runtime shutdown complete")
    
    def run_once(self, user_input: str) -> ToolResult:
        """
        Execute a single input (for testing/programmatic use).
        
        Args:
            user_input: User input string.
            
        Returns:
            ToolResult from execution.
        """
        intent = self.parse_intent(user_input)
        return self.execute_intent(intent)
    
    @property
    def is_running(self) -> bool:
        """Check if runtime is active."""
        return self._running
