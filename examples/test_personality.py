"""
Test Skeleton's personality system
Demonstrates how the AI's character is loaded and applied.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_loader import ConfigLoader
from core.engine import SkeletonEngine


def test_personality_loading():
    """Test that personality configuration loads correctly."""
    print("=" * 60)
    print("Testing Personality Configuration Loading")
    print("=" * 60)
    
    config = ConfigLoader('config/settings.ini')
    
    print("\n✓ Personality section loaded:", bool(config.personality))
    print("\nPersonality Attributes:")
    for key, value in config.personality.items():
        print(f"  • {key}: {value[:60]}..." if len(value) > 60 else f"  • {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Generated System Prompt")
    print("=" * 60)
    print(config.personality_description)
    print()


def test_engine_integration():
    """Test that engine can access personality (without loading model)."""
    print("=" * 60)
    print("Testing Engine Integration")
    print("=" * 60)
    
    engine = SkeletonEngine()
    engine.initialize()
    
    # Verify config loader is available
    assert engine._config_loader is not None, "Config loader should be available"
    assert hasattr(engine._config_loader, 'personality_description'), "Should have personality_description"
    
    print("\n✓ Engine initialized successfully")
    print("✓ Config loader accessible")
    print("✓ Personality description method available")
    print(f"✓ Engine name: {engine.name}")
    print(f"✓ Engine version: {engine.version}")
    
    # Show what system prompt would be used
    print("\nSystem prompt that would be used in chat():")
    print("-" * 40)
    print(engine._config_loader.personality_description[:200] + "...")
    print()


def main():
    """Run all personality tests."""
    try:
        test_personality_loading()
        test_engine_integration()
        
        print("=" * 60)
        print("✅ All Personality Tests Passed!")
        print("=" * 60)
        print("\nSkeleton now has a distinct personality configured via settings.ini")
        print("The AI will embody these traits in all chat interactions.")
        print("\nNext steps:")
        print("  1. Load a model with engine.load_model()")
        print("  2. Start chatting with engine.chat('your message')")
        print("  3. Watch Skeleton respond with its unique character! 🦴")
        print()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
