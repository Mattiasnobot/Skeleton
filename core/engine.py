"""
Skeleton Core - Main Engine
Handles model loading, inference with strict resource management.
Windows-focused implementation.
"""

import sys
import gc
from typing import Optional, Generator, Dict, Any, List
from pathlib import Path
import ctypes

# Import llama-cpp-python for GGUF model support
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

from .config_loader import ConfigLoader, ConfigError


class EngineError(Exception):
    """Raised when engine operations fail."""
    pass


class SkeletonEngine:
    """
    Main engine for Skeleton AI - handles model inference.
    
    Design principles:
    - Explicit initialization and shutdown
    - No automatic model loading
    - Guaranteed resource cleanup
    - Windows-native path handling
    """
    
    def __init__(self, config_path: str = "config/settings.ini"):
        """
        Initialize engine instance.
        
        Args:
            config_path: Path to configuration file (relative or absolute).
        """
        self._config_path = Path(config_path)
        self._config_loader: Optional[ConfigLoader] = None
        self._model: Optional[Llama] = None
        self._is_initialized = False
        self._is_model_loaded = False
        
        # Windows-specific: Default stop tokens for common models
        self._default_stop_tokens: List[str] = ["[INST]", "[/INST]", "</s>", "User:", "Human:"]
    
    def initialize(self) -> bool:
        """
        Initialize the engine by loading and validating configuration.
        
        Returns:
            True if initialization successful.
            
        Raises:
            EngineError: If configuration validation fails.
        """
        try:
            # Resolve config path relative to project root if not absolute
            if not self._config_path.is_absolute():
                project_root = Path(__file__).parent.parent
                self._config_path = project_root / self._config_path
            
            self._config_loader = ConfigLoader(str(self._config_path))
            
            # Platform check at runtime
            if sys.platform != "win32":
                print(f"Warning: Running on {sys.platform}, but Skeleton is optimized for Windows.")
            
            self._is_initialized = True
            return True
            
        except FileNotFoundError as e:
            raise EngineError(f"Configuration file not found: {e}") from e
        except ConfigError as e:
            raise EngineError(f"Configuration validation failed: {e}") from e
        except Exception as e:
            raise EngineError(f"Unexpected error during initialization: {e}") from e
    
    @property
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self._is_initialized
    
    @property
    def is_model_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_model_loaded
    
    @property
    def name(self) -> str:
        """Get engine name."""
        if self._config_loader:
            return self._config_loader.name
        return "Skeleton"
    
    @property
    def version(self) -> str:
        """Get engine version."""
        if self._config_loader:
            return self._config_loader.version
        return "0.1.0"
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load the GGUF model into memory.
        
        Args:
            model_path: Optional override for model path from config.
            
        Returns:
            True if model loaded successfully.
            
        Raises:
            EngineError: If engine not initialized or model loading fails.
        """
        if not self._is_initialized:
            raise EngineError("Engine not initialized. Call initialize() first.")
        
        if not LLAMA_CPP_AVAILABLE:
            raise EngineError("llama-cpp-python is not installed.")
        
        if self._is_model_loaded:
            return True
        
        # Determine model path
        path_str = model_path
        if path_str is None:
            if self._config_loader is None:
                raise EngineError("Config loader not available")
            path_str = self._config_loader.model_path
        
        # Clean path
        path_str = path_str.strip('"').strip("'")
        
        # Resolve path
        model_file = Path(path_str)
        if not model_file.is_absolute():
            project_root = Path(__file__).parent.parent
            model_file = project_root / model_file
        
        model_file = model_file.resolve()
        
        if not model_file.exists():
            raise EngineError(f"Model file not found at {model_file}")
        
        try:
            if self._config_loader is None:
                raise EngineError("Config loader not available")
            
            self._model = Llama(
                model_path=str(model_file),
                n_ctx=self._config_loader.context_size,
                n_threads=self._config_loader.n_threads,
                verbose=False
            )
            
            self._is_model_loaded = True
            return True
            
        except Exception as e:
            raise EngineError(f"Failed to load model: {e}") from e
    
    def generate(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_tokens: Optional[List[str]] = None
    ) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: Input prompt text.
            max_tokens: Override for max tokens to generate.
            temperature: Override for temperature.
            top_p: Override for top_p sampling.
            top_k: Override for top_k sampling.
            stop_tokens: Override for stop tokens.
            
        Returns:
            Generated text response.
            
        Raises:
            EngineError: If model not loaded or generation fails.
        """
        if not self._is_model_loaded:
            raise EngineError("Model not loaded. Call load_model() first.")
        
        if self._model is None:
            raise EngineError("Model instance is None")
        
        if self._config_loader is None:
            raise EngineError("Config loader not available")
        
        # Use overrides or config values
        tokens = max_tokens if max_tokens is not None else 512
        temp = temperature if temperature is not None else self._config_loader.temperature
        p_val = top_p if top_p is not None else self._config_loader.top_p
        k_val = top_k if top_k is not None else self._config_loader.top_k
        stops = stop_tokens if stop_tokens is not None else self._default_stop_tokens
        
        try:
            output = self._model(
                prompt,
                max_tokens=tokens,
                temperature=temp,
                top_p=p_val,
                top_k=k_val,
                stop=stops,
                echo=False
            )
            
            if output and 'choices' in output and len(output['choices']) > 0:
                return output['choices'][0]['text'].strip()
            else:
                return ""
                
        except Exception as e:
            raise EngineError(f"Generation failed: {e}") from e
    
    def generate_stream(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_tokens: Optional[List[str]] = None
    ) -> Generator[str, None, None]:
        """
        Stream generation output token by token.
        
        Args:
            prompt: Input prompt text.
            max_tokens: Override for max tokens to generate.
            temperature: Override for temperature.
            top_p: Override for top_p sampling.
            top_k: Override for top_k sampling.
            stop_tokens: Override for stop tokens.
            
        Yields:
            Generated tokens one at a time.
            
        Raises:
            EngineError: If model not loaded or generation fails.
        """
        if not self._is_model_loaded:
            raise EngineError("Model not loaded. Call load_model() first.")
        
        if self._model is None:
            raise EngineError("Model instance is None")
        
        if self._config_loader is None:
            raise EngineError("Config loader not available")
        
        # Use overrides or config values
        tokens = max_tokens if max_tokens is not None else 512
        temp = temperature if temperature is not None else self._config_loader.temperature
        p_val = top_p if top_p is not None else self._config_loader.top_p
        k_val = top_k if top_k is not None else self._config_loader.top_k
        stops = stop_tokens if stop_tokens is not None else self._default_stop_tokens
        
        try:
            stream = self._model(
                prompt,
                max_tokens=tokens,
                temperature=temp,
                top_p=p_val,
                top_k=k_val,
                stop=stops,
                echo=False,
                stream=True
            )
            
            if stream:
                for output in stream:
                    if output and 'choices' in output and len(output['choices']) > 0:
                        token = output['choices'][0]['text']
                        yield token
                        
        except Exception as e:
            raise EngineError(f"Streaming generation failed: {e}") from e
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Handle a chat message with proper Mistral formatting.
        
        Args:
            message: User message.
            system_prompt: Optional system instruction.
            
        Returns:
            Model response.
            
        Raises:
            EngineError: If generation fails.
        """
        if system_prompt is None:
            system_prompt = "You are Skeleton, a helpful AI assistant."
        
        # Format for Mistral Instruct model (no leading <s>)
        formatted_prompt = f"[INST] {system_prompt}\n\n{message} [/INST]"
        
        return self.generate(formatted_prompt)
    
    def unload_model(self) -> None:
        """Unload the model from memory and perform cleanup."""
        if self._model is not None:
            try:
                del self._model
                self._model = None
            except Exception:
                pass
        
        gc.collect()
        
        # Windows-specific: Try to free memory
        if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'kernel32'):
            try:
                ctypes.windll.kernel32.SetProcessWorkingSetSize(
                    ctypes.c_void_p(-1),
                    ctypes.c_size_t(0),
                    ctypes.c_size_t(0)
                )
            except Exception:
                pass
        
        self._is_model_loaded = False
    
    def shutdown(self) -> None:
        """Perform complete engine shutdown with guaranteed cleanup."""
        self.unload_model()
        
        self._config_loader = None
        self._is_initialized = False
        
        gc.collect()
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            'initialized': self._is_initialized,
            'model_loaded': self._is_model_loaded,
            'config_path': str(self._config_path) if self._config_path else None,
            'model_path': self._config_loader.model_path if self._config_loader else None,
            'platform': sys.platform,
            'name': self.name,
            'version': self.version
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with guaranteed cleanup."""
        self.shutdown()
        return False