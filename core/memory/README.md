# Memory System

Skeleton AI's memory system enables persistent learning and adaptive behavior through structured storage and intelligent retrieval of past experiences.

## Architecture

```
/memory
├── memory_manager.py    # Main interface (brain)
├── storage.py           # SQLite backend
├── retrieval.py         # Scoring & search
├── schemas.py           # Data structures
└── __init__.py          # Public API
```

## Key Features

### 1. **Task Storage**
Store completed tasks with outcomes:
- Goal, steps, result
- Success/failure status
- Automatic timestamping

### 2. **Reflection System**
Learn from experiences:
- Extract insights from tasks
- Generate actionable rules
- Context-aware rule retrieval

### 3. **Intelligent Retrieval**
Find relevant past experiences using:
- Keyword matching
- Success-weighted scoring
- Recency decay (7-day half-life)
- Multi-factor relevance scoring

### 4. **Rule Injection**
Automatically enhance behavior:
- Rules injected into system prompts
- Context-aware filtering
- Improves decision-making over time

## Usage

### Basic Example

```python
from core.memory import MemoryManager

# Initialize
memory = MemoryManager(db_path="data/memory.db")

# Store a completed task
task_id = memory.store_task(
    goal="organize files by extension",
    steps="1. List files\n2. Group by extension\n3. Create folders",
    result="Organized 50 files into 5 folders",
    success=True
)

# Store a learned rule
memory.store_reflection(
    task_id=task_id,
    insight="Grouping by extension is efficient",
    rule="Always group files by extension before moving"
)

# Retrieve relevant rules before a new task
rules = memory.get_rules(context="file organization")
for rule in rules:
    print(f"Learned: {rule}")

# Find similar past tasks
similar = memory.get_similar_tasks("organize files")
for item in similar:
    print(f"Similar task: {item['task'].goal} (Score: {item['score']:.1f})")
```

### Integration with Engine

```python
from core.engine import SkeletonEngine
from core.memory import MemoryManager

# Create memory manager
memory = MemoryManager()

# Inject into engine
engine = SkeletonEngine(memory_manager=memory)
engine.initialize()
engine.load_model()

# Chat now includes learned rules
response = engine.chat("Help me organize my project files")
# Response will be influenced by past file organization experiences
```

### Auto-Learning

```python
# Store task with automatic reflection generation
result = memory.analyze_and_store(
    goal="backup documents",
    steps="1. Identify files\n2. Copy to backup\n3. Verify",
    result="Backup successful",
    success=True,
    auto_generate_reflection=True
)
# Automatically creates basic reflection and rule
```

## Scoring System

Tasks are scored based on:

| Factor | Max Points | Description |
|--------|------------|-------------|
| Keyword Match (Goal) | 40 | Exact match in goal |
| Keyword Match (Steps) | 25 | Match in steps |
| Partial Words | 10/word | Individual word matches |
| Success | 30 | Task succeeded |
| Failure | 5 | Failed tasks still valuable |
| Recency (<24h) | 30 | Very recent |
| Recency (7 days) | Decay | Linear decay over week |

**Maximum Score: 100+ points**

## Database Schema

### Tasks Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    goal TEXT NOT NULL,
    steps TEXT NOT NULL,
    result TEXT NOT NULL,
    success INTEGER NOT NULL,
    timestamp DATETIME
);
```

### Reflections Table
```sql
CREATE TABLE reflections (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    insight TEXT NOT NULL,
    rule TEXT,
    timestamp DATETIME,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

## API Reference

### MemoryManager

#### `store_task(goal, steps, result, success, timestamp)`
Store a completed task. Returns task ID.

#### `store_reflection(task_id, insight, rule, timestamp)`
Store a reflection/rule. Returns reflection ID.

#### `get_similar_tasks(goal, limit=5)`
Find similar past tasks with scores.

#### `get_successful_strategies(keyword, limit=5)`
Find only successful strategies.

#### `get_rules(context=None, limit=10)`
Get relevant rules, optionally filtered by context.

#### `get_recent_tasks(limit=10)`
Get most recent tasks regardless of success.

#### `analyze_and_store(goal, steps, result, success, auto_generate_reflection=True)`
Convenience method combining task storage with auto-reflection.

#### `get_stats()`
Return memory statistics (tasks, success rate, rules).

#### `clear_memory(confirm=False)`
⚠️ **Dangerous**: Clear all memories. Requires confirmation.

## Best Practices

### DO:
- Store both successes AND failures (failures teach valuable lessons)
- Use descriptive goals and detailed steps
- Generate specific, actionable rules
- Review memory stats periodically
- Use context-aware rule retrieval

### DON'T:
- Store sensitive information in memory
- Over-generate rules (quality over quantity)
- Ignore failed tasks (they're learning opportunities)
- Clear memory without backing up important rules

## Performance Considerations

- **SQLite**: Fast, queryable, no external dependencies
- **Indexes**: Optimized for goal/timestamp queries
- **Scoring**: Efficient keyword matching (no embeddings yet)
- **Scalability**: Handles thousands of tasks easily

## Future Enhancements

Potential upgrades (not yet implemented):

1. **Vector Embeddings**: Semantic similarity search
2. **Time-based Forgetting**: Automatic decay of old memories
3. **Memory Consolidation**: Summarize similar tasks
4. **Cross-task Learning**: Identify patterns across multiple tasks
5. **Priority Weighting**: Manually boost important memories

## Thread Safety

⚠️ **Not thread-safe**: SQLite connections are not shared across threads.
Use separate MemoryManager instances per thread or implement external synchronization.

## Example Output

```
Memory Statistics:
  - Total tasks: 47
  - Successful tasks: 39
  - Success rate: 83.0%
  - Total reflections: 52
  - Total rules: 31

Retrieved Rules for "file organization":
  1. Always group files by extension when organizing code repositories
  2. Check if temp files are locked before deletion
  3. Handle missing EXIF data gracefully when organizing images
```
