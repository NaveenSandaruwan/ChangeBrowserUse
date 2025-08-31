"""
Browser Use Agent Module

This module provides the agent interface for browser automation and control.
"""

from .service import BrowserAgent
from . import dom_tree

__all__ = ["BrowserAgent", "dom_tree"]
