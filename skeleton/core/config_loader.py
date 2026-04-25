"""
Configuration loader for Skeleton AI
Handles loading and parsing of configuration settings
"""

import configparser
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Load and manage configuration settings"""
    
    def __init__(self, config_path: str = "config/settings.ini"):
        self.config_path = Path(config_path)
        self.config = configparser.ConfigParser()
        self._settings: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        self.config.read(self.config_path)
        
        # Parse paths
        self._settings['model_path'] = self.config.get('paths', 'model_path')
        
        # Parse model settings
        self._settings['context_size'] = self.config.getint('model', 'context_size')
        self._settings['max_tokens'] = self.config.getint('model', 'max_tokens')
        self._settings['temperature'] = self.config.getfloat('model', 'temperature')
        self._settings['top_p'] = self.config.getfloat('model', 'top_p')
        self._settings['top_k'] = self.config.getint('model', 'top_k')
        
        # Parse system settings
        self._settings['name'] = self.config.get('system', 'name')
        self._settings['version'] = self.config.get('system', 'version')
        self._settings['platform'] = self.config.get('system', 'platform')
        
        return self._settings
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value"""
        return self._settings.get(key, default)
    
    @property
    def model_path(self) -> str:
        return self._settings.get('model_path', '')
    
    @property
    def context_size(self) -> int:
        return self._settings.get('context_size', 4096)
    
    @property
    def max_tokens(self) -> int:
        return self._settings.get('max_tokens', 512)
    
    @property
    def temperature(self) -> float:
        return self._settings.get('temperature', 0.7)
    
    @property
    def top_p(self) -> float:
        return self._settings.get('top_p', 0.9)
    
    @property
    def top_k(self) -> int:
        return self._settings.get('top_k', 40)
