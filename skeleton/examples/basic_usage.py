"""
Basic usage example for Skeleton AI
Demonstrates the core engine functionality
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine import SkeletonEngine, EngineError


def main():
    """Demonstrate basic Skeleton engine usage"""
    
    print("=" * 50)
    print("Skeleton AI - Basic Usage Example")
    print("=" * 50)
    
    # Create engine instance
    engine = SkeletonEngine()
    
    try:
        # Step 1: Initialize engine (loads config)
        print("\n[1] Initializing engine...")
        if not engine.initialize():
            print("Failed to initialize engine")
            return
        
        # Show status
        print(f"\nEngine Status: {engine.status}")
        
        # Step 2: Load model
        print("\n[2] Loading model...")
        try:
            if not engine.load_model():
                print("Failed to load model")
                print("Note: This is expected if you haven't downloaded the model yet.")
                print("Download mistral-7b-instruct-v0.2.Q4_0.gguf to the models folder")
                return
        except EngineError as e:
            print(f"Model loading error: {e}")
            print("Note: This is expected if you haven't downloaded the model yet.")
            return
        
        # Step 3: Generate text
        print("\n[3] Testing generation...")
        prompt = "What is artificial intelligence?"
        print(f"Prompt: {prompt}")
        
        try:
            response = engine.generate(prompt, max_tokens=50)
            print(f"Response: {response}")
        except EngineError as e:
            print(f"Generation error: {e}")
        
        # Step 4: Chat mode
        print("\n[4] Testing chat mode...")
        try:
            response = engine.chat("Hello, who are you?")
            print(f"Response: {response}")
        except EngineError as e:
            print(f"Chat error: {e}")
        
        # Step 5: Streaming generation
        print("\n[5] Testing streaming generation...")
        try:
            print("Streaming: ", end="", flush=True)
            for token in engine.generate_stream("Count from 1 to 5", max_tokens=20):
                print(token, end="", flush=True)
            print()  # New line
        except EngineError as e:
            print(f"Stream error: {e}")
        
    except EngineError as e:
        print(f"\nEngine Error: {e}")
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
    finally:
        # Step 6: Cleanup
        print("\n[6] Shutting down...")
        engine.shutdown()
        print("\nExample complete!")


if __name__ == "__main__":
    main()
