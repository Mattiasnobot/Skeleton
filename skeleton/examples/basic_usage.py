"""
Basic usage example for Skeleton AI
Interactive chat test for the core engine
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine import SkeletonEngine, EngineError


def main():
    """Interactive chat test for Skeleton engine"""

    # Create engine instance
    engine = SkeletonEngine()

    try:
        # Initialize engine (loads config)
        print("[Skeleton v0.1.0] Initializing...")
        if not engine.initialize():
            print("Failed to initialize engine")
            return
        
        print("[Skeleton v0.1.0] Initialized successfully")
        
        # Load model
        print("\nLoading model...")
        if not engine.load_model():
            print("Failed to load model")
            print("Make sure the model file exists in the models folder")
            return
        print("Model loaded successfully!\n")
        
        print("=" * 50)
        print("Interactive Chat Mode")
        print("Type your message and press Enter")
        print("Type 'quit', 'exit', or 'q' to stop")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Exiting chat...")
                    break
                
                if not user_input:
                    continue
                
                response = engine.chat(user_input)
                print(f"Skeleton: {response}")
                
            except EngineError as e:
                print(f"Error: {e}")
                break
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                break
        
    except EngineError as e:
        print(f"Engine Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        print("\nShutting down Skeleton engine...")
        engine.shutdown()
        print("Skeleton engine shut down complete")


if __name__ == "__main__":
    main()
