# Memory System - Quick Start Guide

## What We Built

A **structured, queryable memory system** that makes Skeleton AI learn from experience!

### Files Created
```
core/memory/
├── __init__.py           # Package exports
├── schemas.py            # Data structures (Task, Reflection)
├── storage.py            # SQLite database operations
├── retrieval.py          # Scoring & search algorithms
└── memory_manager.py     # Central interface

examples/
└── test_memory_integration.py  # Complete demo

docs/
└── MEMORY_INTEGRATION.md  # Full documentation
```

## Quick Test

```bash
python examples/test_memory_integration.py
```

Expected output:
```
✅ ALL MEMORY INTEGRATION TESTS PASSED!
```

## How to Use

### 1. Basic Setup
```python
from core.memory import MemoryManager
from core.engine import SkeletonEngine

# Create and inject memory
memory = MemoryManager(db_path="data/memory.db")
engine = SkeletonEngine(memory_manager=memory)
engine.initialize()
```

### 2. Chat with Automatic Learning
```python
# Automatically stores memories and retrieves rules
response = engine.chat("Help me organize my files")
```

### 3. Manual Memory Operations
```python
# Store a task
task_id = memory.store_task(
    goal="Organize files",
    steps="1. List\n2. Group\n3. Move",
    result="Success!",
    success=True
)

# Store learning
memory.store_reflection(
    task_id=task_id,
    insight="Grouping first is efficient",
    rule="Always group before moving"
)

# Get relevant rules
rules = memory.get_rules(context="file organization")
```

## Key Features

✅ **SQLite Storage** - Fast, queryable, persistent  
✅ **Keyword Retrieval** - Find similar past tasks  
✅ **Success Scoring** - Prioritizes what worked  
✅ **Rule Injection** - Auto-applies learned lessons  
✅ **Reflection System** - Learns from every interaction  

## What's Next?

The memory system is **production-ready**! You can now:

1. **Start using it** - Inject into your engine and chat
2. **Build experiences** - Let it learn from your interactions
3. **Monitor growth** - Check `memory.get_stats()` to see learning progress
4. **Extend later** - Add vector embeddings when you need semantic search

## Documentation

See `docs/MEMORY_INTEGRATION.md` for complete guide including:
- Architecture details
- API reference
- Best practices
- Troubleshooting
- Future enhancements

---

**Your AI now has a brain that learns!** 🧠✨
