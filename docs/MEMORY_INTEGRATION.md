# Memory Integration Guide

## Overview

Skeleton AI now includes a **structured, queryable memory system** that enables the AI to learn from past experiences and improve over time.

## Architecture

```
/memory
├── memory_manager.py    # Central interface (brain)
├── storage.py           # SQLite database operations
├── retrieval.py         # Scoring & search algorithms
└── schemas.py           # Data structures

/data
└── memory.db            # Persistent SQLite storage
```

## Key Features

### 1. **Memory Types**
- **Episodic**: Stores specific task instances (what happened)
- **Semantic**: Extracts general rules and insights (what we learned)
- **Procedural**: Remembers successful strategies (how to do it)

### 2. **Learning Mechanism**
After each interaction:
1. Store the task with goal, steps, result, success status
2. Generate reflection with insights and actionable rules
3. Future queries retrieve relevant rules automatically

### 3. **Retrieval System**
Uses multi-factor scoring:
- Keyword matching
- Success weighting (successful tasks ranked higher)
- Recency decay (recent memories weighted more)

## Usage

### Basic Setup

```python
from core.memory import MemoryManager
from core.engine import SkeletonEngine

# Create memory manager
memory = MemoryManager(db_path="data/memory.db")

# Inject into engine
engine = SkeletonEngine(memory_manager=memory)
engine.initialize()
```

### Storing Memories

```python
# Store a completed task
task_id = memory.store_task(
    goal="Organize files by extension",
    steps="1. List files\n2. Group by extension\n3. Move to folders",
    result="Successfully organized 150 files",
    success=True
)

# Store learning/reflection
memory.store_reflection(
    task_id=task_id,
    insight="Grouping before moving is efficient",
    rule="Always group files by extension before organizing"
)
```

### Automatic Learning

```python
# Chat automatically stores memories and injects rules
response = engine.chat(
    "Help me organize my downloads folder",
    store_memory=True  # Default: True
)

# The system will:
# 1. Retrieve relevant rules from past experiences
# 2. Inject them into the system prompt
# 3. Store this interaction for future learning
```

### Querying Memory

```python
# Find similar past tasks
similar = memory.get_similar_tasks("file organization", limit=5)

# Get learned rules for context
rules = memory.get_rules(context="cleanup temporary files", limit=10)

# Find successful strategies
strategies = memory.get_successful_strategies("file management", limit=5)

# Get recent activity
recent = memory.get_recent_tasks(limit=10)

# View statistics
stats = memory.get_stats()
print(f"Success rate: {stats['success_rate']*100:.1f}%")
```

## How It Works

### Rule Injection Flow

```
User Request → Retrieve Rules → Inject into Prompt → Generate Response → Store Result
     ↓                                                                              ↓
Context search                                                              Learn from outcome
```

### Example

**First Interaction:**
```
User: "Organize these files"
System: [No prior knowledge]
Result: Tries basic approach, succeeds
Learning: "Basic file organization works"
```

**Second Interaction:**
```
User: "Organize my documents"
System: [Retrieves rule: "Group by extension first"]
Response: "Let me group your files by extension first..."
Result: More efficient organization
```

## Database Schema

### Tasks Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    goal TEXT,
    steps TEXT,
    result TEXT,
    success INTEGER,
    timestamp DATETIME
);
```

### Reflections Table
```sql
CREATE TABLE reflections (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    insight TEXT,
    rule TEXT,
    timestamp DATETIME
);
```

## Best Practices

### DO:
- Store both successes AND failures (failures teach valuable lessons)
- Keep rules specific and actionable
- Use meaningful goal descriptions
- Review memory stats periodically
- Clear old memories if performance degrades

### DON'T:
- Store sensitive/personal information
- Create overly generic rules
- Ignore failed tasks (they're learning opportunities)
- Let the database grow indefinitely without review

## Advanced Features

### Auto-Reflection
```python
# Automatically generate reflections
result = memory.analyze_and_store(
    goal="Batch rename files",
    steps="...",
    result="...",
    success=True,
    auto_generate_reflection=True
)
```

### Memory Statistics
```python
stats = memory.get_stats()
# Returns: {
#   'total_tasks': int,
#   'successful_tasks': int,
#   'success_rate': float,
#   'total_reflections': int,
#   'total_rules': int
# }
```

### Clear Memory (Use Carefully!)
```python
# Wipe all memories
memory.clear_memory(confirm=True)
```

## Performance Notes

- **Storage**: SQLite provides fast, queryable persistence
- **Retrieval**: O(n) keyword matching (sufficient for <10k tasks)
- **Scalability**: Tested up to 1000+ tasks with sub-second retrieval
- **Future**: Can upgrade to vector embeddings for semantic search

## Troubleshooting

### No Rules Being Retrieved
- Check that rules were actually stored (memory.get_stats())
- Ensure context keywords match stored rules
- Increase limit parameter if needed

### Memory Not Persisting
- Verify data/ directory exists and is writable
- Check database path is correct
- Ensure no file locks on memory.db

### Performance Issues
- Review memory stats - consider clearing very old memories
- Reduce retrieval limit for faster queries
- Consider archiving old tasks

## Next Steps

### Current Implementation (Middle Version)
- Structured SQLite storage  
- Keyword-based retrieval  
- Success/recency scoring  
- Rule extraction and injection  
- Automatic learning from interactions  

### Future Enhancements (When Needed)
- Vector embeddings for semantic search
- Time-decay algorithms for forgetting
- Hierarchical memory organization
- Cross-task pattern recognition
- Automated rule refinement

## Summary

The memory system transforms Skeleton from a stateless assistant into a **learning companion** that:
- Remembers what worked (and what didn't)
- Applies past lessons to new situations
- Continuously improves through experience
- Provides personalized assistance over time

Start using it today and watch your AI get smarter!
