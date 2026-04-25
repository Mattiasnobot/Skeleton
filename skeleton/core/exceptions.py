"""Custom exceptions for the Skeleton AI engine."""


class SkeletonError(Exception):
    """Base exception for all Skeleton errors."""
    pass


class ConfigError(SkeletonError):
    """Raised when configuration validation fails."""
    pass


class EngineError(SkeletonError):
    """Raised when the engine encounters a runtime error."""
    pass
