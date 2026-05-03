"""
Skeleton Core - Main Engine
Handles model loading, inference with strict resource management.
Windows-focused implementation.

Note: This engine is NOT thread-safe. Use separate instances per thread
or implement external synchronization for multi-threaded access.
"""

import sys
import gc
import re
import logging
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
from .exceptions import EngineError

logger = logging.getLogger(__name__)


class SkeletonEngine:
    """
    Main engine for Skeleton AI - handles model inference.
    
    Design principles:
    - Explicit initialization and shutdown
    - No automatic model loading
    - Guaranteed resource cleanup
    - Windows-native path handling
    """
    
    # Class-level constant for default stop tokens
    DEFAULT_STOP_TOKENS: List[str] = ["[INST]", "[/INST]", "</s>", "User:", "Human:"]
    
    # Maximum prompt length to prevent injection attacks
    MAX_PROMPT_LENGTH: int = 16384
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None, config_path: str = "config/settings.ini"):
        """
        Initialize engine instance.
        
        Args:
            config_loader: Optional ConfigLoader instance for dependency injection.
                          If not provided, will be created from config_path.
            config_path: Path to configuration file (relative or absolute).
                        Only used if config_loader is not provided.
        """
        self._config_path = Path(config_path)
        self._config_loader: Optional[ConfigLoader] = config_loader
        self._model: Optional[Llama] = None
        self._is_initialized = False
        self._is_model_loaded = False
        
        # Windows-specific: Default stop tokens for common models
        self._default_stop_tokens: List[str] = self.DEFAULT_STOP_TOKENS.copy()
    
    def initialize(self) -> bool:
        """
        Initialize the engine by loading and validating configuration.
        
        Returns:
            True if initialization successful.
            
        Raises:
            EngineError: If configuration validation fails.
        """
        try:
            # Use injected config_loader or create one
            if self._config_loader is None:
                # Resolve config path relative to project root if not absolute
                if not self._config_path.is_absolute():
                    project_root = Path(__file__).parent.parent
                    self._config_path = project_root / self._config_path
                
                self._config_loader = ConfigLoader(str(self._config_path))
            
            # Platform check at runtime
            if sys.platform != "win32":
                logger.warning(f"Running on {sys.platform}, but Skeleton is optimized for Windows.")
            
            self._is_initialized = True
            return True
            
        except FileNotFoundError as e:
            logger.error(f"Configuration file not found: {e}")
            raise EngineError(f"Configuration file not found: {e}") from e
        except ConfigError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise EngineError(f"Configuration validation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {e}")
            raise EngineError(f"Unexpected error during initialization: {e}") from e
    
    @property
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self._is_initialized
    
    @property
    def is_model_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_model_loaded
    
    @staticmethod
    def _sanitize_prompt(prompt: str) -> str:
        """
        Sanitize prompt to prevent injection attacks and ensure safe processing.
        
        Args:
            prompt: Raw user input prompt.
            
        Returns:
            Sanitized prompt string.
            
        Raises:
            EngineError: If prompt is empty or exceeds maximum length.
        """
        if not prompt:
            raise EngineError("Prompt cannot be empty")
        
        # Check prompt length to prevent buffer overflow attacks
        if len(prompt) > SkeletonEngine.MAX_PROMPT_LENGTH:
            raise EngineError(
                f"Prompt exceeds maximum length of {SkeletonEngine.MAX_PROMPT_LENGTH} characters"
            )
        
        # Remove potentially dangerous control characters (except newlines and tabs)
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', prompt)
        
        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()
        
        if not sanitized:
            raise EngineError("Prompt cannot be empty after sanitization")
        
        return sanitized
    
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
            logger.error(f"Model file not found at {model_file}")
            raise EngineError(f"Model file not found at {model_file}")
        
        try:
            if self._config_loader is None:
                raise EngineError("Config loader not available")
            
            logger.info(f"Loading model from {model_file}")
            self._model = Llama(
                model_path=str(model_file),
                n_ctx=self._config_loader.context_size,
                n_threads=self._config_loader.n_threads,
                verbose=False
            )
            
            self._is_model_loaded = True
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise EngineError(f"Failed to load model: {e}") from e
    
    def _get_generation_params(
        self,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_tokens: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Consolidate generation parameter logic.
        
        Args:
            max_tokens: Override for max tokens.
            temperature: Override for temperature.
            top_p: Override for top_p.
            top_k: Override for top_k.
            stop_tokens: Override for stop tokens.
            
        Returns:
            Dictionary of generation parameters.
        """
        if self._config_loader is None:
            raise EngineError("Config loader not available")
        
        return {
            'max_tokens': max_tokens if max_tokens is not None else 512,
            'temperature': temperature if temperature is not None else self._config_loader.temperature,
            'top_p': top_p if top_p is not None else self._config_loader.top_p,
            'top_k': top_k if top_k is not None else self._config_loader.top_k,
            'stop_tokens': stop_tokens if stop_tokens is not None else self._default_stop_tokens.copy(),
        }
    
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
        
        # Sanitize prompt for security
        sanitized_prompt = self._sanitize_prompt(prompt)
        
        # Get consolidated parameters
        params = self._get_generation_params(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop_tokens=stop_tokens
        )
        
        try:
            logger.debug(f"Generating response with params: {params}")
            output = self._model(
                sanitized_prompt,
                max_tokens=params['max_tokens'],
                temperature=params['temperature'],
                top_p=params['top_p'],
                top_k=params['top_k'],
                stop=params['stop_tokens'],
                echo=False
            )
            
            if output and 'choices' in output and len(output['choices']) > 0:
                result = output['choices'][0]['text'].strip()
                logger.debug(f"Generated {len(result)} characters")
                return result
            else:
                logger.warning("Model returned empty output")
                return ""
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
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
        
        # Sanitize prompt for security
        sanitized_prompt = self._sanitize_prompt(prompt)
        
        # Get consolidated parameters
        params = self._get_generation_params(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop_tokens=stop_tokens
        )
        
        try:
            logger.debug(f"Streaming with params: {params}")
            stream = self._model(
                sanitized_prompt,
                max_tokens=params['max_tokens'],
                temperature=params['temperature'],
                top_p=params['top_p'],
                top_k=params['top_k'],
                stop=params['stop_tokens'],
                echo=False,
                stream=True
            )
            
            if stream:
                token_count = 0
                for output in stream:
                    if output and 'choices' in output and len(output['choices']) > 0:
                        token = output['choices'][0]['text']
                        token_count += 1
                        yield token
                logger.debug(f"Streamed {token_count} tokens")
                        
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise EngineError(f"Streaming generation failed: {e}") from e
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Handle a chat message with proper Mistral formatting.
        
        Args:
            message: User message.
            system_prompt: Optional system instruction. If None, uses personality-based default.
            
        Returns:
            Model response.
            
        Raises:
            EngineError: If generation fails.
        """
        if system_prompt is None:
            # Use personality-driven system prompt from config
            if self._config_loader and hasattr(self._config_loader, 'personality_description'):
                system_prompt = self._config_loader.personality_description
            else:
                system_prompt = "You are Skeleton, a helpful AI assistant."
        
        # Sanitize both system prompt and message
        sanitized_message = self._sanitize_prompt(message)
        sanitized_system = self._sanitize_prompt(system_prompt)
        
        # Format for Mistral Instruct model (no leading <s>)
        formatted_prompt = f"[INST] {sanitized_system}\n\n{sanitized_message} [/INST]"
        
        logger.info(f"Chat request with message length: {len(sanitized_message)}")
        return self.generate(formatted_prompt)
    
    def unload_model(self) -> None:
        """Unload the model from memory and perform cleanup."""
        if self._model is not None:
            try:
                logger.info("Unloading model from memory")
                del self._model
                self._model = None
            except Exception as e:
                logger.warning(f"Error during model deletion: {e}")
        
        # Make garbage collection configurable - only collect if needed
        gc.collect()
        
        # Windows-specific: Try to free memory
        if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'kernel32'):
            try:
                ctypes.windll.kernel32.SetProcessWorkingSetSize(
                    ctypes.c_void_p(-1),
                    ctypes.c_size_t(0),
                    ctypes.c_size_t(0)
                )
                logger.debug("Freed Windows working set memory")
            except Exception as e:
                logger.debug(f"Could not free Windows working set: {e}")
        else:
            logger.debug("Non-Windows platform, skipping working set optimization")
        
        self._is_model_loaded = False
        logger.info("Model unloaded successfully")
    
    def shutdown(self) -> None:
        """Perform complete engine shutdown with guaranteed cleanup."""
        logger.info("Shutting down engine")
        self.unload_model()
        
        self._config_loader = None
        self._is_initialized = False
        
        gc.collect()
        logger.info("Engine shutdown complete")
    
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