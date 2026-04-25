"""
Basic usage example for Skeleton AI
Interactive chat loop for testing the core engine.
"""

from skeleton.core.engine import SkeletonEngine, EngineError


def run_chat(engine: SkeletonEngine):
    """Run interactive chat loop."""
    print(f"\n[{engine.name} v{engine.version}] Ready! Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                break
            
            if not user_input:
                continue
            
            response = engine.chat(user_input)
            print(f"{engine.name}: {response}\n")
            
        except EngineError as e:
            print(f"Error: {e}\n")
        except KeyboardInterrupt:
            print("\n")
            break
        except EOFError:
            print("\n")
            break


def main():
    """Main entry point."""
    engine = SkeletonEngine()
    
    try:
        # Initialize
        engine.initialize()
        
        # Load model
        engine.load_model()
        
        # Run chat
        run_chat(engine)
        
    except EngineError as e:
        print(f"Engine Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        engine.shutdown()


if __name__ == "__main__":
    main()
