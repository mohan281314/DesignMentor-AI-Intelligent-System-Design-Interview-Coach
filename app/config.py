"""
Backward-compatibility shim.
The canonical config now lives in app.core.config.
All existing code that does `from app.config import get_settings` keeps working.
"""

from app.core.config import Settings, get_settings  # noqa: F401

__all__ = ["Settings", "get_settings"]
