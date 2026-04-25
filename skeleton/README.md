# Skeleton AI

A lightweight, local AI skeleton built for Windows PC, designed to run fully local models like Mistral-7B-Instruct in GGUF format.

## Overview

Skeleton is a minimal core framework for running local LLMs on Windows. It focuses on:
- **Fully Local**: No cloud dependencies, all inference happens on your machine
- **Lightweight**: Minimal dependencies and clean architecture
- **Windows-First**: Optimized for Windows PC (cross-platform support planned later)
- **GGUF Support**: Uses llama-cpp-python for efficient GGUF model inference
- **Solid Core**: Strict validation, explicit lifecycle management, guaranteed cleanup

## Project Structure

```
skeleton/
├── __init__.py          # Main package entry point
├── core/
│   ├── __init__.py      # Core module exports
│   ├── engine.py        # Main inference engine with resource management
│   └── config_loader.py # Strict configuration validation
├── config/
│   └── settings.ini     # Configuration file
├── models/              # Place your GGUF models here
├── examples/
│   └── basic_usage.py   # Example usage script
└── requirements.txt     # Python dependencies
```

## Installation

### Prerequisites

1. **Python 3.8+** installed on Windows
2. **Visual C++ Build Tools** (for compiling llama-cpp-python)
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Steps

1. Clone or download this repository

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download a GGUF model:
   - Get `mistral-7b-instruct-v0.2.Q4_0.gguf` from HuggingFace
   - Place it in the `models/` folder

4. Run the example:
   ```bash
   python examples/basic_usage.py
   ```

## Usage

### Basic Example

```python
from skeleton.core import SkeletonEngine, EngineError

# Initialize engine
engine = SkeletonEngine()

try:
    engine.initialize()
    
    # Load model
    engine.load_model()
    
    # Chat
    response = engine.chat("Hello, how are you?")
    print(response)
    
    # Or stream responses
    for token in engine.generate_stream("Tell me a story"):
        print(token, end="", flush=True)
        
finally:
    # Always shutdown to release resources
    engine.shutdown()
```

### Using Context Manager (Recommended)

```python
from skeleton.core import SkeletonEngine

with SkeletonEngine() as engine:
    engine.initialize()
    engine.load_model()
    response = engine.chat("What is AI?")
    print(response)
# Automatically cleans up resources
```

### Configuration

Edit `config/settings.ini` to customize:
- Model path
- Context size
- Max tokens
- Temperature and sampling parameters

## Features

### Core Engine (`SkeletonEngine`)

**Lifecycle Management:**
- `initialize()` - Load and validate configuration (raises `EngineError` if invalid)
- `load_model()` - Load GGUF model into memory
- `shutdown()` - Complete cleanup with resource release
- `unload_model()` - Free model from memory without full shutdown

**Properties:**
- `is_initialized` - Check if engine is initialized
- `is_model_loaded` - Check if model is loaded
- `status` - Get current engine status dict

**Generation:**
- `generate(prompt, ...)` - Generate text from prompt with optional overrides
- `generate_stream(prompt, ...)` - Stream generation token by token
- `chat(message, system_prompt)` - Chat with proper Mistral formatting

All generation methods support runtime overrides for:
- `max_tokens`
- `temperature`
- `top_p`
- `top_k`
- `stop_tokens`

### Configuration (`ConfigLoader`)

**Strict Validation:**
- All required keys must be present
- Value ranges are validated (e.g., temperature 0.0-2.0, top_p 0.0-1.0)
- Platform enforcement (Windows only for now)
- Clear error messages on validation failure

**Properties (require `.load()` first):**
- `model_path`, `context_size`, `max_tokens`
- `temperature`, `top_p`, `top_k`
- `name`, `version`, `platform`

### Error Handling

Two custom exceptions for clear error handling:
- `ConfigError` - Configuration validation failures
- `EngineError` - Engine operation failures

```python
from skeleton.core import SkeletonEngine, EngineError, ConfigError

try:
    engine = SkeletonEngine()
    engine.initialize()
    engine.load_model()
except ConfigError as e:
    print(f"Config problem: {e}")
except EngineError as e:
    print(f"Engine problem: {e}")
finally:
    engine.shutdown()
```

## Model Support

Currently optimized for:
- **Mistral-7B-Instruct-v0.2** (Q4_0 quantization recommended)
- Other GGUF models should work with proper prompt formatting

Download models from:
- [TheBloke on HuggingFace](https://huggingface.co/TheBloke)

## Windows-Specific Notes

### GPU Acceleration (Optional)
For CUDA support on NVIDIA GPUs:
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

Adjust the CUDA version (cu121) based on your installation.

### Memory Requirements
- Q4_0 quantization: ~4GB RAM for 7B model
- Recommended: 8GB+ RAM for comfortable usage

### Resource Cleanup
The engine includes Windows-specific memory cleanup:
- Explicit `SetProcessWorkingSetSize` calls to release memory
- Guaranteed cleanup via context manager or explicit `shutdown()`
- Prevents resource locks that require system restart

## Design Principles

This is a **solid skeleton** - the core foundation before adding features:

1. **Explicit Lifecycle**: No auto-loading, explicit `initialize()` and `shutdown()`
2. **Strict Validation**: Fail fast with clear errors if config is wrong
3. **Resource Safety**: Guaranteed cleanup, especially important on Windows
4. **Type Safety**: Full type hints for IDE support and error prevention
5. **Windows-Native**: Uses `pathlib.Path` everywhere for proper path handling
6. **No Magic**: What you see is what you get - no hidden behavior

## Roadmap

**Core (Current Phase):**
- [x] Strict configuration validation
- [x] Explicit lifecycle management
- [x] Windows-native path handling
- [x] Guaranteed resource cleanup
- [x] Type hints throughout
- [x] Custom exception types
- [x] Context manager support

**Next (When Core is Stable):**
- [ ] Conversation history management
- [ ] Session management
- [ ] Logging system
- [ ] Performance optimizations
- [ ] Cross-platform support
- [ ] Plugin/skills system

## License

MIT License - Feel free to use and modify

## Contributing

This is a personal project, but suggestions are welcome!

---

**Skeleton AI** - Building the bones of something great 🦴
