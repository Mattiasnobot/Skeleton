"""
Skeleton AI - Core Module
A lightweight, local AI skeleton for Windows PC
"""

__version__ = "0.1.0"
__author__ = "Skeleton Project"

from .engine import SkeletonEngine
from .config_loader import ConfigLoader

__all__ = ["SkeletonEngine", "ConfigLoader"]
