"""
Simple DOM tree visualization test

This is a simplified test that doesn't require LLM authentication.
"""

import asyncio
import logging
from pathlib import Path

from browser_use.browser.session import BrowserSession
from browser_use.agent.dom_tree_visualizer import DOMTreeVisualizer

logging.basicConfig(level=logging.INFO,
                   format='%(levelname)-8s [%(name)s] %(message)s')

async def test_dom_visualizer():
    """Test the DOM tree visualizer with a browser session."""
    
    # Create a browser session
    session = BrowserSession(headless=False)
    await session.start()
    
    try:
        # Navigate to a test page
        await session.goto("https://example.com")
        
        # Create the visualizer
        visualizer = DOMTreeVisualizer(session)
        
        # Get and print DOM tree
        dom_tree = await visualizer.get_current_dom_tree()
        
        if dom_tree:
            print("\nDOM Tree structure:")
            tree_output = visualizer.print_dom_tree(dom_tree, max_depth=3, include_details=False)
            for line in tree_output:
                print(line)
            
            # Get interactive elements
            interactive_elements = []
            
            def find_interactive_nodes(node):
                if node.element_index is not None:
                    interactive_elements.append(node)
                
                if node.children_nodes:
                    for child in node.children_nodes:
                        find_interactive_nodes(child)
                        
                if node.content_document:
                    find_interactive_nodes(node.content_document)
                    
                if node.shadow_roots:
                    for shadow in node.shadow_roots:
                        find_interactive_nodes(shadow)
                        
            find_interactive_nodes(dom_tree)
            
            # Print info about interactive elements
            print(f"\nFound {len(interactive_elements)} interactive elements:")
            for i, node in enumerate(interactive_elements[:10]):  # Limit to 10
                elem_type = node.node_name.lower()
                elem_attrs = []
                
                for key, value in node.attributes.items():
                    if key in ['id', 'class', 'role', 'type', 'name']:
                        elem_attrs.append(f"{key}='{value}'")
                        
                attrs_text = " ".join(elem_attrs) if elem_attrs else ""
                print(f"  {i+1}. <{elem_type} {attrs_text} [idx:{node.element_index}]>")
        else:
            print("No DOM tree available")
            
    finally:
        # Close the browser session
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_dom_visualizer())
