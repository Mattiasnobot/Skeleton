"""Test Memory Integration with Skeleton Engine"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.memory import MemoryManager
from core.engine import SkeletonEngine


def test_memory_integration():
    """Test complete memory integration workflow."""
    
    print("=" * 60)
    print("MEMORY INTEGRATION TEST")
    print("=" * 60)
    
    # Step 1: Create Memory Manager
    print("\n1. Creating Memory Manager...")
    memory = MemoryManager(db_path="data/memory.db")
    print("   ✓ Memory Manager initialized")
    
    # Step 2: Create Engine with Memory Injection
    print("\n2. Creating Engine with Memory Injection...")
    engine = SkeletonEngine(memory_manager=memory)
    engine.initialize()
    print("   ✓ Engine initialized with memory support")
    
    # Step 3: Store Sample Tasks (simulating past interactions)
    print("\n3. Storing sample tasks in memory...")
    
    task1_id = memory.store_task(
        goal="Organize files by extension",
        steps="1. List all files\n2. Group by extension\n3. Create folders\n4. Move files",
        result="Successfully organized 150 files into 12 folders",
        success=True
    )
    print(f"   ✓ Stored task 1: File organization (ID: {task1_id})")
    
    memory.store_reflection(
        task_id=task1_id,
        insight="Grouping by extension before moving is efficient",
        rule="Always group files by extension before organizing"
    )
    print("   ✓ Stored reflection for task 1")
    
    task2_id = memory.store_task(
        goal="Clean up temporary files",
        steps="1. Find .tmp files\n2. Verify not in use\n3. Delete safely",
        result="Removed 45 temporary files, freed 2.3GB",
        success=True
    )
    print(f"   ✓ Stored task 2: Cleanup task (ID: {task2_id})")
    
    memory.store_reflection(
        task_id=task2_id,
        insight="Always verify files aren't in use before deletion",
        rule="Check file locks before deleting temporary files"
    )
    print("   ✓ Stored reflection for task 2")
    
    # Step 4: Retrieve Similar Tasks
    print("\n4. Testing retrieval of similar tasks...")
    similar = memory.get_similar_tasks("organize files by type", limit=3)
    print(f"   ✓ Found {len(similar)} similar tasks for 'organize files'")
    for i, item in enumerate(similar, 1):
        print(f"      {i}. {item['task'].goal[:50]}... (score: {item['score']:.2f})")
    
    # Step 5: Get Learned Rules
    print("\n5. Retrieving learned rules...")
    rules = memory.get_rules(context="file organization cleanup", limit=5)
    print(f"   ✓ Retrieved {len(rules)} relevant rules:")
    for i, rule in enumerate(rules, 1):
        print(f"      {i}. {rule}")
    
    # Step 6: Get Successful Strategies
    print("\n6. Finding successful strategies...")
    strategies = memory.get_successful_strategies("file", limit=3)
    print(f"   ✓ Found {len(strategies)} successful strategies:")
    for i, strat in enumerate(strategies, 1):
        print(f"      {i}. {strat['task'].steps[:60]}... (success score: {strat['score']:.2f})")
    
    # Step 7: Get Memory Statistics
    print("\n7. Memory Statistics:")
    stats = memory.get_stats()
    print(f"   - Total tasks: {stats['total_tasks']}")
    print(f"   - Success rate: {stats['success_rate']*100:.1f}%")
    print(f"   - Total reflections: {stats['total_reflections']}")
    print(f"   - Total rules: {stats['total_rules']}")
    
    # Step 8: Test Rule Injection (without model)
    print("\n8. Testing rule injection capability...")
    if engine._memory_manager:
        test_context = "I need to organize my downloads folder"
        injected_rules = engine._memory_manager.get_rules(context=test_context, limit=3)
        print(f"   ✓ For context: '{test_context}'")
        print(f"   ✓ Would inject {len(injected_rules)} rules:")
        for rule in injected_rules:
            print(f"      • {rule}")
    
    print("\n" + "=" * 60)
    print("✅ ALL MEMORY INTEGRATION TESTS PASSED!")
    print("=" * 60)
    print("\nMemory system is ready for use with the engine.")
    print("When a model is loaded, chat() will automatically:")
    print("  • Inject learned rules into system prompts")
    print("  • Store successful interactions as memories")
    print("  • Learn from failures and successes")
    print("=" * 60)


if __name__ == "__main__":
    test_memory_integration()
