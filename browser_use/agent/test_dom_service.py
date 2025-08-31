"""
Test agent DOM visualization methods

This script focuses on testing the agent's ability to visualize DOM tree
after a task completes.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path if needed
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from browser_use.agent.dom_tree_visualizer import DOMTreeVisualizer
from browser_use.agent.service import Agent
from browser_use.browser.session import BrowserSession
from browser_use.dom.service import DomService

async def main():
    """Test DOM tree visualization methods"""
    
    print("Initializing DOM Tree Visualizer...")
    
    # Create browser session manually
    browser_session = BrowserSession(headless=False)
    await browser_session.start()
    
    # Navigate to a test page
    await browser_session.navigate(url="https://example.com")
    
    try:
        # Create a DOM service directly
        dom_service = DomService(browser_session)
        
        # Get the DOM tree using the method we're fixing
        print("Fetching DOM tree...")
        dom_tree = await dom_service.get_dom_tree(target_id=browser_session.current_target_id)
        
        if dom_tree:
            print(f"✅ Successfully retrieved DOM tree with {len(dom_tree.children_nodes or [])} top-level nodes")
            
            # Print basic info about the tree
            print(f"Root node: {dom_tree.node_name}")
            if dom_tree.children_nodes:
                print("Top-level nodes:")
                for i, child in enumerate(dom_tree.children_nodes[:5]):  # Limit to 5
                    print(f"  {i+1}. {child.node_name}")
                
            # Test the visualizer
            visualizer = DOMTreeVisualizer(browser_session)
            tree_lines = visualizer.print_dom_tree(dom_tree, max_depth=2, include_details=False)
            print("\nDOM Tree Sample (first 10 lines):")
            for line in tree_lines[:10]:
                print(line)
        else:
            print("❌ Failed to retrieve DOM tree")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        await browser_session.stop()
        print("Browser session closed")

if __name__ == "__main__":
    asyncio.run(main())
