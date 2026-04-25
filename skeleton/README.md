# Skeleton AI

A lightweight, local AI skeleton built for Windows PC, designed to run fully local models like Mistral-7B-Instruct in GGUF format.

## Overview

Skeleton is a minimal core framework for running local LLMs on Windows. It focuses on:
- **Fully Local**: No cloud dependencies, all inference happens on your machine
- **Lightweight**: Minimal dependencies and clean architecture
- **Windows-First**: Optimized for Windows PC (cross-platform support planned)
- **GGUF Support**: Uses llama-cpp-python for efficient GGUF model inference

## Project Structure

```
skeleton/
├── __init__.py          # Main package entry point
├── core/
│   ├── __init__.py      # Core module exports
│   ├── engine.py        # Main inference engine
│   └── config_loader.py # Configuration management
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
from skeleton import SkeletonEngine

# Initialize engine
engine = SkeletonEngine()
engine.initialize()

# Load model
engine.load_model()

# Chat
response = engine.chat("Hello, how are you?")
print(response)

# Or stream responses
for token in engine.generate_stream("Tell me a story"):
    print(token, end="", flush=True)

# Unload when done
engine.unload_model()
```

### Configuration

Edit `config/settings.ini` to customize:
- Model path
- Context size
- Max tokens
- Temperature and sampling parameters

## Features

### Core Engine (`SkeletonEngine`)
- `initialize()` - Load configuration
- `load_model()` - Load GGUF model into memory
- `generate(prompt)` - Generate text from prompt
- `generate_stream(prompt)` - Stream generation token by token
- `chat(message)` - Chat with proper formatting for Mistral
- `unload_model()` - Free model from memory
- `status` - Get current engine status

### Configuration (`ConfigLoader`)
- Load settings from INI file
- Access to model parameters
- Platform-specific settings

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

## Roadmap

- [x] Core engine implementation
- [x] Configuration system
- [x] GGUF model support
- [ ] Conversation history management
- [ ] Multi-model support
- [ ] Performance optimizations for Windows
- [ ] Cross-platform support
- [ ] Plugin/skills system (when core is stable)

## License

MIT License - Feel free to use and modify

## Contributing

This is a personal project, but suggestions are welcome!

---

**Skeleton AI** - Building the bones of something great 🦴
