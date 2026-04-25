"""
Basic usage example for Skeleton AI
Minimal template for testing the core engine
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine import SkeletonEngine, EngineError


def main():
    """Minimal template for testing Skeleton engine"""

    # Create engine instance
    engine = SkeletonEngine()

    try:
        # Initialize engine (loads config)
        print("[Skeleton v0.1.0] Initializing...")
        if not engine.initialize():
            print("Failed to initialize engine")
            return
        
        print("Initialized successfully.")
        
        # TODO: Add your own testing logic here
        # Example:
        # if engine.load_model():
        #     response = engine.generate("Hello")
        #     print(response)

    except EngineError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        engine.shutdown()


if __name__ == "__main__":
    main()
