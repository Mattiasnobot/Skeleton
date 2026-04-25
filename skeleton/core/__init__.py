"""
Skeleton AI - Core Module
A lightweight, local AI skeleton for Windows PC
"""

__version__ = "0.1.0"
__author__ = "Skeleton Project"

from .engine import SkeletonEngine, EngineError
from .config_loader import ConfigLoader, ConfigError

__all__ = ["SkeletonEngine", "EngineError", "ConfigLoader", "ConfigError"]
