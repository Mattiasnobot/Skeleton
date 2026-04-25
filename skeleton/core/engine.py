"""
Core engine for Skeleton AI
Manages model loading, inference, and conversation handling
"""

import sys
from typing import Optional, Generator, Dict, Any
from pathlib import Path

# Import llama-cpp-python for GGUF model support
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    print("Warning: llama-cpp-python not installed. Install with: pip install llama-cpp-python")

from .config_loader import ConfigLoader


class SkeletonEngine:
    """Main engine for Skeleton AI - handles model inference"""
    
    def __init__(self, config_path: str = "config/settings.ini"):
        self.config_loader = ConfigLoader(config_path)
        self.config: Dict[str, Any] = {}
        self.model: Optional[Llama] = None
        self.is_loaded = False
        
    def initialize(self) -> bool:
        """Initialize the engine by loading configuration"""
        try:
            self.config = self.config_loader.load()
            print(f"[{self.config['name']} v{self.config['version']}] Initialized")
            return True
        except Exception as e:
            print(f"Error initializing engine: {e}")
            return False
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Load the GGUF model into memory"""
        if not LLAMA_CPP_AVAILABLE:
            print("Error: llama-cpp-python is not installed")
            return False
        
        if not self.config:
            if not self.initialize():
                return False
        
        path = model_path or self.config_loader.model_path
        
        # Clean path (remove quotes if present from config)
        path = path.strip('"').strip("'")
        
        # Resolve path relative to project root
        model_file = Path(path)
        if not model_file.is_absolute():
            model_file = Path(__file__).parent.parent / model_file
        
        if not model_file.exists():
            print(f"Error: Model file not found at {model_file}")
            print("Please download mistral-7b-instruct-v0.2.Q4_0.gguf and place it in the models folder")
            return False
        
        try:
            print(f"Loading model: {model_file.name}...")
            self.model = Llama(
                model_path=str(model_file),
                n_ctx=self.config_loader.context_size,
                n_threads=None,  # Auto-detect
                verbose=False
            )
            self.is_loaded = True
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate a response from the model"""
        if not self.is_loaded:
            return "Error: Model not loaded. Call load_model() first."
        
        tokens = max_tokens or self.config_loader.max_tokens
        
        try:
            output = self.model(
                prompt,
                max_tokens=tokens,
                temperature=self.config_loader.temperature,
                top_p=self.config_loader.top_p,
                top_k=self.config_loader.top_k,
                stop=["User:", "Human:"],
                echo=False
            )
            return output['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error during generation: {e}"
    
    def generate_stream(self, prompt: str, max_tokens: Optional[int] = None) -> Generator[str, None, None]:
        """Stream generation output token by token"""
        if not self.is_loaded:
            yield "Error: Model not loaded."
            return
        
        tokens = max_tokens or self.config_loader.max_tokens
        
        try:
            stream = self.model(
                prompt,
                max_tokens=tokens,
                temperature=self.config_loader.temperature,
                top_p=self.config_loader.top_p,
                top_k=self.config_loader.top_k,
                stop=["User:", "Human:"],
                echo=False,
                stream=True
            )
            
            for output in stream:
                token = output['choices'][0]['text']
                yield token
                
        except Exception as e:
            yield f"Error: {e}"
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Handle a chat message with proper formatting"""
        if system_prompt is None:
            system_prompt = "You are Skeleton, a helpful AI assistant."
        
        # Format for Mistral Instruct model
        formatted_prompt = (
            f"<s>[INST] {system_prompt}\n\n{message} [/INST]"
        )
        
        return self.generate(formatted_prompt)
    
    def unload_model(self):
        """Unload the model from memory"""
        if self.model:
            del self.model
            self.model = None
            self.is_loaded = False
            print("Model unloaded")
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return {
            'initialized': bool(self.config),
            'model_loaded': self.is_loaded,
            'model_path': self.config_loader.model_path if self.config else None,
            'platform': self.config.get('platform', 'unknown') if self.config else None,
            'version': self.config.get('version', 'unknown') if self.config else None
        }
