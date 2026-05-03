#!/usr/bin/env python3
"""Test script for Skeleton AI Memory System."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.memory import MemoryManager
from core.memory.schemas import Task


def test_memory_system():
    """Comprehensive test of memory functionality."""
    print("=" * 60)
    print("SKELETON AI MEMORY SYSTEM TEST")
    print("=" * 60)
    
    # Initialize memory manager
    print("\n1. Initializing Memory Manager...")
    memory = MemoryManager(db_path="data/test_memory.db")
    print("✓ Memory Manager initialized")
    
    # Test storing tasks
    print("\n2. Storing test tasks...")
    task1_id = memory.store_task(
        goal="organize files by extension",
        steps="1. List all files in directory\n2. Group files by extension\n3. Create folders for each extension\n4. Move files to appropriate folders",
        result="Successfully organized 50 files into 5 folders (txt, py, md, json, log)",
        success=True
    )
    print(f"✓ Stored task 1 (ID: {task1_id})")
    
    task2_id = memory.store_task(
        goal="clean up temporary files",
        steps="1. Find all .tmp files\n2. Check if files are in use\n3. Delete unused temp files",
        result="Deleted 23 temporary files, freed 15MB",
        success=True
    )
    print(f"✓ Stored task 2 (ID: {task2_id})")
    
    task3_id = memory.store_task(
        goal="organize images by date",
        steps="1. Read EXIF data from images\n2. Group by date taken\n3. Create date-based folders",
        result="Failed: Some images missing EXIF data",
        success=False
    )
    print(f"✓ Stored task 3 (ID: {task3_id}) - failed task")
    
    # Test storing reflections
    print("\n3. Storing reflections and rules...")
    ref1_id = memory.store_reflection(
        task_id=task1_id,
        insight="Grouping by extension is efficient for code projects",
        rule="Always group files by extension when organizing code repositories"
    )
    print(f"✓ Stored reflection 1 (ID: {ref1_id}) with rule")
    
    ref2_id = memory.store_reflection(
        task_id=task2_id,
        insight="Temporary file cleanup should verify files aren't in use",
        rule="Always check if temp files are locked before deletion"
    )
    print(f"✓ Stored reflection 2 (ID: {ref2_id}) with rule")
    
    ref3_id = memory.store_reflection(
        task_id=task3_id,
        insight="EXIF data may be missing from some images",
        rule="Handle missing EXIF data gracefully when organizing images"
    )
    print(f"✓ Stored reflection 3 (ID: {ref3_id}) with rule")
    
    # Test retrieving similar tasks
    print("\n4. Testing retrieval of similar tasks...")
    similar = memory.get_similar_tasks("organize files", limit=3)
    print(f"✓ Found {len(similar)} similar tasks for 'organize files':")
    for item in similar:
        task = item['task']
        score = item['score']
        print(f"  - Task: {task.goal[:50]}... (Score: {score:.1f})")
    
    # Test getting successful strategies
    print("\n5. Testing successful strategies retrieval...")
    strategies = memory.get_successful_strategies("organize", limit=3)
    print(f"✓ Found {len(strategies)} successful strategies for 'organize':")
    for item in strategies:
        task = item['task']
        score = item['score']
        print(f"  - Strategy: {task.goal[:50]}... (Score: {score:.1f})")
    
    # Test getting rules
    print("\n6. Testing rule retrieval...")
    rules = memory.get_rules(context="file organization", limit=5)
    print(f"✓ Retrieved {len(rules)} relevant rules:")
    for i, rule in enumerate(rules, 1):
        print(f"  {i}. {rule}")
    
    # Test getting recent tasks
    print("\n7. Testing recent tasks retrieval...")
    recent = memory.get_recent_tasks(limit=5)
    print(f"✓ Retrieved {len(recent)} recent tasks:")
    for task in recent:
        status = "✓" if task.success else "✗"
        print(f"  {status} {task.goal[:50]}...")
    
    # Test statistics
    print("\n8. Testing memory statistics...")
    stats = memory.get_stats()
    print("✓ Memory Statistics:")
    print(f"  - Total tasks: {stats['total_tasks']}")
    print(f"  - Successful tasks: {stats['successful_tasks']}")
    print(f"  - Success rate: {stats['success_rate']*100:.1f}%")
    print(f"  - Total reflections: {stats['total_reflections']}")
    print(f"  - Total rules: {stats['total_rules']}")
    
    # Test analyze_and_store convenience method
    print("\n9. Testing analyze_and_store method...")
    result = memory.analyze_and_store(
        goal="backup important documents",
        steps="1. Identify important files\n2. Copy to backup location\n3. Verify backup integrity",
        result="Backup completed successfully",
        success=True,
        auto_generate_reflection=True
    )
    print(f"✓ Stored task with auto-reflection (Task ID: {result['task_id']}, Reflection ID: {result['reflection_id']})")
    
    # Final stats
    print("\n10. Final statistics...")
    final_stats = memory.get_stats()
    print(f"✓ Final count: {final_stats['total_tasks']} tasks, {final_stats['total_rules']} rules")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        test_memory_system()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
