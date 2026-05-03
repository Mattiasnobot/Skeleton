"""
Test script for Phase 1: Core Runtime Loop

Tests:
1. Runtime initialization
2. Tool execution (list_files, read_file)
3. Sandbox protection
4. Intent parsing
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.runtime import Runtime
from core.tools import ToolResult


def test_runtime_init():
    """Test runtime initialization."""
    print("Test 1: Runtime Initialization")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = Runtime(tmpdir)
        
        assert runtime.sandbox_root == Path(tmpdir).resolve()
        assert runtime.tool_registry is not None
        assert 'list_files' in runtime.tool_registry
        assert 'read_file' in runtime.tool_registry
        
        print(f"  ✓ Runtime initialized with sandbox: {runtime.sandbox_root}")
        print(f"  ✓ Tools registered: {list(runtime.tool_registry.list_tools().keys())}")
    
    print("  PASSED\n")


def test_list_files():
    """Test list_files tool."""
    print("Test 2: List Files Tool")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_dir = Path(tmpdir) / "test_subdir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        
        runtime = Runtime(tmpdir)
        
        # Test via run_once
        result = runtime.run_once(f"list_files {test_dir}")
        
        assert result.success, f"Expected success, got error: {result.error}"
        assert isinstance(result.output, list)
        assert len(result.output) == 2
        
        print(f"  ✓ Listed {len(result.output)} files")
        print(f"  ✓ Output: {result.output}")
    
    print("  PASSED\n")


def test_read_file():
    """Test read_file tool."""
    print("Test 3: Read File Tool")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "test.txt"
        test_content = "Hello, Skeleton!"
        test_file.write_text(test_content)
        
        runtime = Runtime(tmpdir)
        
        # Test via run_once
        result = runtime.run_once(f"read_file {test_file}")
        
        assert result.success, f"Expected success, got error: {result.error}"
        assert result.output == test_content
        assert result.metadata.get('lines') == 1
        
        print(f"  ✓ Read file content: {result.output}")
        print(f"  ✓ Metadata: {result.metadata}")
    
    print("  PASSED\n")


def test_sandbox_protection():
    """Test that sandbox blocks access outside root."""
    print("Test 4: Sandbox Protection")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = Runtime(tmpdir)
        
        # Try to access outside sandbox
        result = runtime.run_once("list_files /etc")
        
        assert not result.success, "Should have blocked access outside sandbox"
        assert "outside sandbox" in result.error.lower()
        
        print(f"  ✓ Blocked access to /etc: {result.error}")
    
    print("  PASSED\n")


def test_json_intent():
    """Test JSON intent parsing."""
    print("Test 5: JSON Intent Parsing")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = Runtime(tmpdir)
        
        # Create test file
        test_file = Path(tmpdir) / "json_test.txt"
        test_file.write_text("JSON test content")
        
        # Test JSON format
        json_input = json.dumps({
            "tool": "read_file",
            "args": {"path": str(test_file)}
        })
        
        result = runtime.run_once(json_input)
        
        assert result.success, f"Expected success, got error: {result.error}"
        assert result.output == "JSON test content"
        
        print(f"  ✓ Parsed JSON intent successfully")
        print(f"  ✓ Result: {result.output[:30]}...")
    
    print("  PASSED\n")


def test_unknown_tool():
    """Test handling of unknown tools."""
    print("Test 6: Unknown Tool Handling")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = Runtime(tmpdir)
        
        result = runtime.run_once("unknown_tool arg1")
        
        assert not result.success
        assert "Unknown tool" in result.error or "Could not parse" in result.error
        
        print(f"  ✓ Handled unknown tool: {result.error}")
    
    print("  PASSED\n")


def main():
    """Run all tests."""
    print("=" * 50)
    print("PHASE 1: CORE RUNTIME LOOP TESTS")
    print("=" * 50)
    print()
    
    try:
        test_runtime_init()
        test_list_files()
        test_read_file()
        test_sandbox_protection()
        test_json_intent()
        test_unknown_tool()
        
        print("=" * 50)
        print("ALL TESTS PASSED ✓")
        print("=" * 50)
        print()
        print("Phase 1 Complete:")
        print("  ✓ Runtime loop exists and runs")
        print("  ✓ 2 tools implemented (list_files, read_file)")
        print("  ✓ Hard-coded tool registry working")
        print("  ✓ Simple intent parsing (JSON + command)")
        print("  ✓ Sandbox protection active")
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
