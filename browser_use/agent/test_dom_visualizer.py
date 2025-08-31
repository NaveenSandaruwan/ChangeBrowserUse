"""
Test module for DOM Tree Visualizer

This module provides a simple way to test the DOM tree visualizer
without modifying the Agent's process_one_task method.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path if needed
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from browser_use.agent.dom_tree_visualizer import DOMTreeVisualizer
from browser_use.browser.session import BrowserSession

async def test_dom_tree_visualizer():
    """
    Test the DOM tree visualizer with a browser session.
    """
    # Create a browser session
    session = await BrowserSession.create(headless=False)
    
    try:
        # Navigate to a test page
        await session.goto("https://www.google.com/search?q=g&udm=14")
        
        # Wait for the page to load
        await asyncio.sleep(2)
        
        # Create and initialize the visualizer
        visualizer = DOMTreeVisualizer(session)
        
        # Print the DOM tree
        await visualizer.print_dom_after_task(max_depth=5, include_details=True)
        
    finally:
        # Close the browser session
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_dom_tree_visualizer())
