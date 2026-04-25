"""
Example usage of Skeleton AI
Demonstrates basic initialization and chat functionality
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SkeletonEngine


def main():
    """Run example demonstration"""
    print("=" * 50)
    print("Skeleton AI - Example Usage")
    print("=" * 50)
    
    # Initialize the engine
    engine = SkeletonEngine()
    
    if not engine.initialize():
        print("Failed to initialize engine")
        return
    
    # Show status
    print("\nEngine Status:")
    status = engine.status
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Try to load model (will fail if model file doesn't exist)
    print("\nAttempting to load model...")
    if engine.load_model():
        print("\nModel loaded! You can now chat.")
        print("Type 'quit' to exit\n")
        
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input:
                print("Skeleton: ", end="", flush=True)
                response = engine.chat(user_input)
                print(response)
                print()
        
        engine.unload_model()
    else:
        print("\nModel not loaded. To use Skeleton AI:")
        print("1. Download mistral-7b-instruct-v0.2.Q4_0.gguf")
        print("2. Place it in the models/ folder")
        print("3. Run this example again")
    
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
