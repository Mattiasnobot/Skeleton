"""
Interactive Runtime Launcher

Phase 1: Core loop MVP - Interactive mode
Run this to test the runtime manually.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.runtime import Runtime


def main():
    """Launch interactive runtime."""
    
    # Use workspace/data as sandbox root for demo
    # You can change this to any directory you want to sandbox
    sandbox_root = Path(__file__).parent.parent / "data"
    
    print(f"\n🦴 Skeleton Runtime v0.1.0")
    print(f"Phase 1: Core Loop MVP")
    print(f"Sandbox: {sandbox_root}")
    print()
    
    # Create runtime and run interactive loop
    runtime = Runtime(str(sandbox_root))
    runtime.run_interactive()
    
    print("\nGoodbye!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
