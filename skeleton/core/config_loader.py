"""
Configuration loader for Skeleton AI
Handles loading and parsing of configuration settings with strict validation
Windows-focused implementation
"""

import configparser
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigError(Exception):
    """Raised when configuration validation fails"""
    pass


class ConfigLoader:
    """Load and manage configuration settings with strict validation"""
    
    # Required configuration keys
    REQUIRED_PATH_KEYS = ['model_path']
    REQUIRED_MODEL_KEYS = ['context_size', 'max_tokens', 'temperature', 'top_p', 'top_k']
    REQUIRED_SYSTEM_KEYS = ['name', 'version', 'platform']
    
    def __init__(self, config_path: str = "config/settings.ini"):
        self.config_path = Path(config_path)
        self.config = configparser.ConfigParser()
        self._settings: Dict[str, Any] = {}
        self._is_loaded = False
    
    def load(self) -> Dict[str, Any]:
        """Load and validate configuration from file
        
        Raises:
            ConfigError: If required keys are missing or values are invalid
            FileNotFoundError: If config file doesn't exist
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path.resolve()}")
        
        # Read config file
        read_files = self.config.read(self.config_path)
        if not read_files:
            raise ConfigError(f"Failed to read configuration file: {self.config_path}")
        
        # Validate sections exist
        required_sections = ['paths', 'model', 'system']
        for section in required_sections:
            if section not in self.config:
                raise ConfigError(f"Missing required section: [{section}]")
        
        # Validate and parse paths
        for key in self.REQUIRED_PATH_KEYS:
            if not self.config.has_option('paths', key):
                raise ConfigError(f"Missing required path setting: paths.{key}")
            value = self.config.get('paths', key).strip().strip('"').strip("'")
            if not value:
                raise ConfigError(f"Empty value for paths.{key}")
            self._settings['model_path'] = value
        
        # Validate and parse model settings
        try:
            self._settings['context_size'] = self.config.getint('model', 'context_size')
            if self._settings['context_size'] <= 0:
                raise ConfigError("context_size must be positive")
        except ValueError as e:
            raise ConfigError(f"Invalid context_size: must be an integer") from e
        
        try:
            self._settings['max_tokens'] = self.config.getint('model', 'max_tokens')
            if self._settings['max_tokens'] <= 0:
                raise ConfigError("max_tokens must be positive")
        except ValueError as e:
            raise ConfigError(f"Invalid max_tokens: must be an integer") from e
        
        try:
            self._settings['temperature'] = self.config.getfloat('model', 'temperature')
            if not (0.0 <= self._settings['temperature'] <= 2.0):
                raise ConfigError("temperature must be between 0.0 and 2.0")
        except ValueError as e:
            raise ConfigError(f"Invalid temperature: must be a float") from e
        
        try:
            self._settings['top_p'] = self.config.getfloat('model', 'top_p')
            if not (0.0 <= self._settings['top_p'] <= 1.0):
                raise ConfigError("top_p must be between 0.0 and 1.0")
        except ValueError as e:
            raise ConfigError(f"Invalid top_p: must be a float") from e
        
        try:
            self._settings['top_k'] = self.config.getint('model', 'top_k')
            if self._settings['top_k'] <= 0:
                raise ConfigError("top_k must be positive")
        except ValueError as e:
            raise ConfigError(f"Invalid top_k: must be an integer") from e
        
        # Validate and parse system settings
        for key in self.REQUIRED_SYSTEM_KEYS:
            if not self.config.has_option('system', key):
                raise ConfigError(f"Missing required system setting: system.{key}")
            value = self.config.get('system', key).strip()
            if not value:
                raise ConfigError(f"Empty value for system.{key}")
            self._settings[key] = value
        
        # Enforce Windows platform for now
        if self._settings['platform'].lower() != 'windows':
            raise ConfigError(f"Only 'windows' platform is supported. Found: {self._settings['platform']}")
        
        self._is_loaded = True
        return self._settings.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self._settings.get(key, default)
    
    @property
    def is_loaded(self) -> bool:
        """Check if configuration has been loaded"""
        return self._is_loaded
    
    @property
    def model_path(self) -> str:
        """Get model path"""
        if not self._is_loaded:
            raise ConfigError("Configuration not loaded. Call load() first.")
        return self._settings.get('model_path', '')
    
    @property
    def context_size(self) -> int:
        """Get context size"""
        if not self._is_loaded:
            raise ConfigError("Configuration not loaded. Call load() first.")
        return self._settings.get('context_size', 4096)
    
    @property
    def max_tokens(self) -> int:
        """Get max tokens"""
        if not self._is_loaded:
            raise ConfigError("Configuration not loaded. Call load() first.")
        return self._settings.get('max_tokens', 512)
    
    @property
    def temperature(self) -> float:
        """Get temperature"""
        if not self._is_loaded:
            raise ConfigError("Configuration not loaded. Call load() first.")
        return self._settings.get('temperature', 0.7)
    
    @property
    def top_p(self) -> float:
        """Get top_p"""
        if not self._is_loaded:
            raise ConfigError("Configuration not loaded. Call load() first.")
        return self._settings.get('top_p', 0.9)
    
    @property
    def top_k(self) -> int:
        """Get top_k"""
        if not self._is_loaded:
            raise ConfigError("Configuration not loaded. Call load() first.")
        return self._settings.get('top_k', 40)
    
    @property
    def name(self) -> str:
        """Get system name"""
        if not self._is_loaded:
            raise ConfigError("Configuration not loaded. Call load() first.")
        return self._settings.get('name', 'Skeleton')
    
    @property
    def version(self) -> str:
        """Get system version"""
        if not self._is_loaded:
            raise ConfigError("Configuration not loaded. Call load() first.")
        return self._settings.get('version', '0.0.0')
