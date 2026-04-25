"""
Skeleton Core - Strict Configuration Loader
Handles INI parsing, validation, and type safety.
"""
import configparser
import sys
from pathlib import Path
from typing import Any, Optional

from .exceptions import ConfigError


class ConfigLoader:
    """Strict configuration loader with validation."""
    
    def __init__(self, config_path: str):
        self._config_path = Path(config_path)
        self._settings: dict[str, Any] = {}
        self._load()
        self._validate()
    
    def _load(self) -> None:
        """Load and parse INI file."""
        if not self._config_path.exists():
            raise ConfigError(f"Configuration file not found: {self._config_path}")
        
        config = configparser.ConfigParser()
        config.read(self._config_path)
        
        if 'core' not in config:
            raise ConfigError("Missing [core] section in config")
        
        core = config['core']
        
        # Helper for validated integers
        def get_int(key: str, default: int, min_val: Optional[int] = None) -> int:
            try:
                val = config.getint('core', key, fallback=default)
            except ValueError:
                raise ConfigError(f"Invalid integer for '{key}': must be a number")
            
            if min_val is not None and val < min_val:
                raise ConfigError(f"Value for '{key}' must be at least {min_val}")
            return val

        # Helper for validated floats
        def get_float(key: str, default: float, min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
            try:
                val = config.getfloat('core', key, fallback=default)
            except ValueError:
                raise ConfigError(f"Invalid float for '{key}': must be a number")
            
            if min_val is not None and val < min_val:
                raise ConfigError(f"Value for '{key}' must be at least {min_val}")
            if max_val is not None and val > max_val:
                raise ConfigError(f"Value for '{key}' must be at most {max_val}")
            return val

        self._settings = {
            'name': core.get('name', 'Skeleton'),
            'version': core.get('version', '0.1.0'),
            'model_path': core.get('model_path', ''),
            'context_size': get_int('context_size', 4096, min_val=128),
            'n_threads': core.getint('n_threads', fallback=None),
            'temperature': get_float('temperature', 0.7, min_val=0.0, max_val=2.0),
            'top_p': get_float('top_p', 0.9, min_val=0.0, max_val=1.0),
            'top_k': get_int('top_k', 40, min_val=1),
            'platform': sys.platform,
        }

    def _validate(self) -> None:
        """Validate loaded settings."""
        if not self._settings['model_path']:
            raise ConfigError("'model_path' cannot be empty")

    @property
    def name(self) -> str:
        return self._settings['name']
    
    @property
    def version(self) -> str:
        return self._settings['version']
    
    @property
    def model_path(self) -> str:
        return self._settings['model_path']
    
    @property
    def context_size(self) -> int:
        return self._settings['context_size']
    
    @property
    def n_threads(self) -> Optional[int]:
        return self._settings['n_threads']
    
    @property
    def temperature(self) -> float:
        return self._settings['temperature']
    
    @property
    def top_p(self) -> float:
        return self._settings['top_p']
    
    @property
    def top_k(self) -> int:
        return self._settings['top_k']
    
    @property
    def platform(self) -> str:
        return self._settings['platform']
    
    def to_dict(self) -> dict[str, Any]:
        """Return settings as dictionary."""
        return self._settings.copy()
