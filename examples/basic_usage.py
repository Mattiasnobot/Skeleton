"""
Basic usage example for Skeleton AI
Interactive chat loop for testing the core engine.
"""

import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import SkeletonEngine, EngineError

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_chat(engine: SkeletonEngine):
    """Run interactive chat loop."""
    logger.info(f"{engine.name} v{engine.version} ready. Type 'quit' to exit.")
    print(f"\n[{engine.name} v{engine.version}] Ready! Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                logger.info("User requested exit")
                break
            
            if not user_input:
                continue
            
            response = engine.chat(user_input)
            print(f"{engine.name}: {response}\n")
            
        except EngineError as e:
            logger.error(f"Engine error during chat: {e}")
            print(f"Error: {e}\n")
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            print("\n")
            break
        except EOFError:
            logger.info("EOF received")
            print("\n")
            break


def main():
    """Main entry point."""
    engine = SkeletonEngine()
    
    try:
        # Initialize
        logger.info("Initializing engine")
        engine.initialize()
        
        # Load model
        logger.info("Loading model")
        engine.load_model()
        
        # Run chat
        run_chat(engine)
        
    except EngineError as e:
        logger.error(f"Engine error: {e}")
        print(f"Engine Error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Unexpected Error: {e}")
    finally:
        logger.info("Shutting down")
        engine.shutdown()


if __name__ == "__main__":
    main()