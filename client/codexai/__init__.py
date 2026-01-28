# Create this folder: client/codexai/
from .resolver import CodexResolver

# Public API
_resolver = CodexResolver()
resolve = _resolver.resolve

__all__ = ["CodexResolver", "resolve"]