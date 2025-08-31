"""
Browser Use Agent Module

This module provides the agent interface for browser automation and control.
"""

from .service import Agent
# Import dom_tree_visualizer module
from .dom_tree_visualizer import DOMTreeVisualizer, visualize_dom_after_task

__all__ = ["Agent", "DOMTreeVisualizer", "visualize_dom_after_task"]
