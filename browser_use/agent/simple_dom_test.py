"""
Simple test script for DOM tree visualization feature

This script creates a minimal implementation that directly accesses 
the show_browser_state_summary method without complex setup.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path if needed
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import logging
from browser_use.browser.session import BrowserSession
from browser_use.dom.service import DomService
from browser_use.dom.views import EnhancedDOMTreeNode, NodeType

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(levelname)-8s [%(name)s] %(message)s')
logger = logging.getLogger("DOMTest")

async def get_dom_tree(browser_session):
    """Get DOM tree from browser session"""
    try:
        dom_service = DomService(browser_session)
        if browser_session.current_target_id:
            # Get DOM tree with proper target ID
            dom_tree = await dom_service.get_dom_tree(target_id=browser_session.current_target_id)
            return dom_tree
        return None
    except Exception as e:
        logger.error(f"Error getting DOM tree: {e}")
        return None

async def display_dom_structure(dom_tree):
    """Display DOM structure details"""
    if not dom_tree:
        logger.info("No DOM tree available")
        return
        
    # Count elements by type
    element_counts = {}
    text_content_by_tag = {}
    interactive_nodes = []
    
    def analyze_node(node, depth=0):
        if node.node_type == NodeType.ELEMENT_NODE:
            tag = node.node_name.lower()
            element_counts[tag] = element_counts.get(tag, 0) + 1
            
            # Track interactive elements
            if node.element_index is not None:
                interactive_nodes.append((node, depth))
            
            # Collect text content for important elements
            if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'button', 'label']:
                text = ""
                if node.children_nodes:
                    for child in node.children_nodes:
                        if child.node_type == NodeType.TEXT_NODE and child.node_value:
                            text += child.node_value.strip() + " "
                
                text = text.strip()
                if text:
                    if tag not in text_content_by_tag:
                        text_content_by_tag[tag] = []
                    text_content_by_tag[tag].append(text[:100])
        
        # Process children
        if node.children_nodes:
            for child in node.children_nodes:
                analyze_node(child, depth + 1)
                
        # Process iframe content
        if node.content_document:
            analyze_node(node.content_document, depth + 1)
            
        # Process shadow DOM
        if node.shadow_roots:
            for shadow in node.shadow_roots:
                analyze_node(shadow, depth + 1)
    
    # Analyze the entire tree
    analyze_node(dom_tree)
    
    # Display element counts
    logger.info(f"Total element types: {len(element_counts)}")
    logger.info("Most common elements:")
    for tag, count in sorted(element_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
        logger.info(f"  - {tag}: {count}")
    
    # Display heading structure if available
    headings = []
    for h_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        if h_tag in text_content_by_tag:
            for text in text_content_by_tag[h_tag]:
                headings.append((h_tag, text))
    
    if headings:
        logger.info("\nPage heading structure:")
        for h_tag, text in headings[:5]:  # Limit to first 5
            logger.info(f"  {h_tag}: {text}")
    
    # Display page content summary
    page_content = []
    for tag in ['p', 'li']:
        if tag in text_content_by_tag:
            page_content.extend(text_content_by_tag[tag])
    
    if page_content:
        logger.info("\nPage content preview:")
        for text in page_content[:3]:  # Limit to first 3
            logger.info(f"  • {text}")
    
    # Display interactive elements
    if interactive_nodes:
        logger.info(f"\nInteractive elements ({len(interactive_nodes)}):")
        for node, depth in sorted(interactive_nodes, key=lambda x: x[1])[:8]:  # Sort by depth, show first 8
            tag = node.node_name.lower()
            attrs = []
            
            for key, value in node.attributes.items():
                if key in ['id', 'class', 'role', 'type', 'name']:
                    attrs.append(f"{key}='{value}'")
                    
            attrs_text = " ".join(attrs) if attrs else ""
            
            # Get text or value
            text = ""
            if tag == 'input' and 'value' in node.attributes:
                text = f"value='{node.attributes['value']}'"
            elif node.children_nodes:
                for child in node.children_nodes:
                    if child.node_type == NodeType.TEXT_NODE and child.node_value:
                        text = child.node_value.strip()[:50]
                        break
            
            logger.info(f"  [{node.element_index}] <{tag} {attrs_text}> {text}")

async def main():
    """Test DOM tree visualization"""
    
    # Initialize browser session
    browser_session = None
    try:
        logger.info("Starting browser session...")
        browser_session = BrowserSession(headless=False)
        await browser_session.start()
        
        # Navigate to example page
        logger.info("Navigating to example.com...")
        await browser_session.cdp_client.send.Page.navigate({"url": "https://example.com"})
        
        # Wait for page to load
        logger.info("Waiting for page to load...")
        await asyncio.sleep(3)
        
        # Get DOM tree
        logger.info("Getting DOM tree...")
        dom_tree = await get_dom_tree(browser_session)
        
        # Display DOM structure
        if dom_tree:
            logger.info("✅ Successfully retrieved DOM tree")
            logger.info("=" * 50)
            logger.info("DOM STRUCTURE ANALYSIS")
            logger.info("=" * 50)
            await display_dom_structure(dom_tree)
        else:
            logger.error("❌ Failed to retrieve DOM tree")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Close browser session
        if browser_session:
            logger.info("Closing browser session...")
            await browser_session.stop()
        
        logger.info("Test complete!")

if __name__ == "__main__":
    asyncio.run(main())
