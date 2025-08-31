"""
DOM Tree Visualizer for Agent

This module provides functionality to visualize the DOM element tree and element details
after a process_one_task function completes successfully.
"""

import asyncio
from typing import Optional, List, Dict, Any

from browser_use.dom.views import EnhancedDOMTreeNode, NodeType
from browser_use.dom.service import DomService
from browser_use.browser.session import BrowserSession
from browser_use.observability import observe_debug

class DOMTreeVisualizer:
    """
    A class to visualize the DOM tree and element details for agent usage
    """

    def __init__(self, browser_session: BrowserSession = None):
        """
        Initialize the DOM Tree Visualizer.
        
        Args:
            browser_session: The browser session used to fetch DOM information
        """
        self.browser_session = browser_session
        self.dom_service = None
        
    async def initialize(self, browser_session: BrowserSession = None) -> None:
        """
        Initialize DOM service if not already initialized.
        
        Args:
            browser_session: The browser session to use if not already provided
        """
        if browser_session:
            self.browser_session = browser_session
        
        if not self.browser_session:
            raise ValueError("Browser session is required")
            
        self.dom_service = DomService(self.browser_session)
    
    async def get_current_dom_tree(self) -> Optional[EnhancedDOMTreeNode]:
        """
        Get the current DOM tree from the browser session.
        
        Returns:
            EnhancedDOMTreeNode: The root node of the DOM tree
        """
        if not self.dom_service:
            await self.initialize()
            
        try:
            # Get the DOM tree from the DOM service using the correct method
            dom_tree = await self.dom_service.get_dom_tree(target_id=self.browser_session.current_target_id)
            return dom_tree
        except Exception as e:
            print(f"Error getting DOM tree: {e}")
            return None
    
    @observe_debug
    def print_dom_tree(self, node: EnhancedDOMTreeNode, depth: int = 0, max_depth: int = 10, 
                       include_details: bool = True, output_list: List[str] = None) -> List[str]:
        """
        Print the DOM tree in a hierarchical format.
        
        Args:
            node: The current DOM node
            depth: Current depth in the tree
            max_depth: Maximum depth to traverse
            include_details: Whether to include element details
            output_list: List to collect output strings
            
        Returns:
            List[str]: The output strings
        """
        if output_list is None:
            output_list = []
        
        if depth > max_depth:
            output_list.append(f"{' ' * (depth * 2)}... (max depth reached)")
            return output_list
            
        # Skip non-element nodes unless they're text nodes with content
        if node.node_type != NodeType.ELEMENT_NODE:
            if node.node_type == NodeType.TEXT_NODE and node.node_value.strip():
                output_list.append(f"{' ' * (depth * 2)}#TEXT: {node.node_value.strip()[:50]}")
            return output_list
        
        # Print node information
        element_info = f"{' ' * (depth * 2)}<{node.node_name.lower()}"
        
        # Add key attributes
        attrs = []
        for key, value in node.attributes.items():
            if key in ['id', 'class', 'role', 'type', 'name']:
                attrs.append(f"{key}='{value}'")
                
        if attrs:
            element_info += f" {' '.join(attrs)}"
        
        # Add interactive index if available
        if node.element_index is not None:
            element_info += f" [idx:{node.element_index}]"
            
        element_info += ">"
        output_list.append(element_info)
        
        # Print element details if requested
        if include_details and depth <= max_depth - 1:
            self._print_element_details(node, depth + 1, output_list)
        
        # Print children recursively
        if node.children_nodes:
            for child in node.children_nodes:
                self.print_dom_tree(child, depth + 1, max_depth, include_details, output_list)
        
        # Print iframe content documents if available
        if node.content_document:
            output_list.append(f"{' ' * ((depth + 1) * 2)}[iframe content]:")
            self.print_dom_tree(node.content_document, depth + 2, max_depth, include_details, output_list)
        
        # Print shadow roots if available
        if node.shadow_roots:
            for shadow_root in node.shadow_roots:
                output_list.append(f"{' ' * ((depth + 1) * 2)}[shadow-root]:")
                self.print_dom_tree(shadow_root, depth + 2, max_depth, include_details, output_list)
        
        # Print closing tag for elements
        if node.node_type == NodeType.ELEMENT_NODE:
            output_list.append(f"{' ' * (depth * 2)}</{node.node_name.lower()}>")
            
        return output_list
    
    def _print_element_details(self, node: EnhancedDOMTreeNode, depth: int, output_list: List[str]) -> None:
        """
        Print details about a DOM element.
        
        Args:
            node: The DOM node
            depth: Current depth in the tree
            output_list: List to collect output strings
        """
        prefix = ' ' * (depth * 2)
        
        # Print visibility and scrollability
        if node.is_visible is not None:
            output_list.append(f"{prefix}Visible: {node.is_visible}")
        if node.is_scrollable is not None:
            output_list.append(f"{prefix}Scrollable: {node.is_scrollable}")
            
        # Print position if available
        if node.absolute_position:
            pos = node.absolute_position
            output_list.append(f"{prefix}Position: x={pos.x:.1f}, y={pos.y:.1f}, width={pos.width:.1f}, height={pos.height:.1f}")
            
        # Print accessibility info if available
        if node.ax_node:
            ax = node.ax_node
            if ax.role:
                output_list.append(f"{prefix}AX Role: {ax.role}")
            if ax.name:
                output_list.append(f"{prefix}AX Name: {ax.name}")
            if ax.properties:
                for prop in ax.properties:
                    if prop.value is not None:
                        output_list.append(f"{prefix}AX {prop.name}: {prop.value}")
                        
        # Print snapshot info if available
        if node.snapshot_node:
            snap = node.snapshot_node
            if snap.is_clickable:
                output_list.append(f"{prefix}Clickable: {snap.is_clickable}")
            if snap.cursor_style:
                output_list.append(f"{prefix}Cursor: {snap.cursor_style}")
    
    @observe_debug
    def summarize_dom_tree(self, node: EnhancedDOMTreeNode) -> Dict[str, Any]:
        """
        Create a summary of the DOM tree.
        
        Args:
            node: The root DOM node
            
        Returns:
            Dict: Summary information about the DOM tree
        """
        summary = {
            "total_nodes": 0,
            "interactive_elements": 0,
            "visible_elements": 0,
            "form_elements": 0,
            "links": 0,
            "buttons": 0,
            "depth": 0
        }
        
        def traverse(node, depth):
            # Update summary statistics
            summary["total_nodes"] += 1
            summary["depth"] = max(summary["depth"], depth)
            
            if node.node_type == NodeType.ELEMENT_NODE:
                if node.is_visible:
                    summary["visible_elements"] += 1
                    
                if node.element_index is not None:
                    summary["interactive_elements"] += 1
                    
                if node.node_name.lower() == 'a':
                    summary["links"] += 1
                    
                if node.node_name.lower() == 'button':
                    summary["buttons"] += 1
                    
                if node.node_name.lower() in ['input', 'select', 'textarea']:
                    summary["form_elements"] += 1
                
                # Traverse child nodes
                if node.children_nodes:
                    for child in node.children_nodes:
                        traverse(child, depth + 1)
                        
                # Traverse iframe content document
                if node.content_document:
                    traverse(node.content_document, depth + 1)
                    
                # Traverse shadow roots
                if node.shadow_roots:
                    for shadow_root in node.shadow_roots:
                        traverse(shadow_root, depth + 1)
                    
        traverse(node, 0)
        return summary
        
    def _get_element_type_distribution(self, node: EnhancedDOMTreeNode) -> Dict[str, int]:
        """
        Get distribution of element types in the DOM tree.
        
        Args:
            node: The root DOM node
            
        Returns:
            Dict: Mapping of element types to counts
        """
        element_types = {}
        
        def traverse(node):
            if node.node_type == NodeType.ELEMENT_NODE:
                element_name = node.node_name.lower()
                element_types[element_name] = element_types.get(element_name, 0) + 1
                
                # Traverse child nodes
                if node.children_nodes:
                    for child in node.children_nodes:
                        traverse(child)
                        
                # Traverse iframe content document
                if node.content_document:
                    traverse(node.content_document)
                    
                # Traverse shadow roots
                if node.shadow_roots:
                    for shadow_root in node.shadow_roots:
                        traverse(shadow_root)
        
        traverse(node)
        return element_types
    
    def _get_interactive_elements(self, node: EnhancedDOMTreeNode) -> List[EnhancedDOMTreeNode]:
        """
        Get all interactive elements in the DOM tree.
        
        Args:
            node: The root DOM node
            
        Returns:
            List: List of interactive DOM nodes
        """
        interactive_elements = []
        
        def traverse(node):
            if node.node_type == NodeType.ELEMENT_NODE:
                # Check if element is interactive
                if node.element_index is not None:
                    interactive_elements.append(node)
                
                # Traverse child nodes
                if node.children_nodes:
                    for child in node.children_nodes:
                        traverse(child)
                        
                # Traverse iframe content document
                if node.content_document:
                    traverse(node.content_document)
                    
                # Traverse shadow roots
                if node.shadow_roots:
                    for shadow_root in node.shadow_roots:
                        traverse(shadow_root)
        
        traverse(node)
        return interactive_elements
    
    def _get_element_text(self, node: EnhancedDOMTreeNode) -> str:
        """
        Extract text content from an element.
        
        Args:
            node: The DOM node
            
        Returns:
            str: Text content of the element
        """
        text_parts = []
        
        def extract_text(node):
            if node.node_type == NodeType.TEXT_NODE and node.node_value.strip():
                text_parts.append(node.node_value.strip())
            elif node.node_type == NodeType.ELEMENT_NODE and node.children_nodes:
                for child in node.children_nodes:
                    extract_text(child)
        
        extract_text(node)
        return " ".join(text_parts)

    @observe_debug
    async def print_dom_after_task(self, max_depth: int = 5, include_details: bool = True) -> None:
        """
        Print the DOM tree after a task completes.
        
        Args:
            max_depth: Maximum depth to display
            include_details: Whether to include element details
        """
        dom_tree = await self.get_current_dom_tree()
        
        if not dom_tree:
            print("No DOM tree available")
            return
        
        import logging
        logger = logging.getLogger('Agent')
            
        logger.info("\n" + "="*80)
        logger.info("DOM TREE AFTER TASK COMPLETION")
        logger.info("="*80)
        
        # Print tree summary
        summary = self.summarize_dom_tree(dom_tree)
        logger.info(f"Summary: {summary['total_nodes']} nodes, {summary['interactive_elements']} interactive elements")
        logger.info(f"Depth: {summary['depth']}, Visible: {summary['visible_elements']}, Links: {summary['links']}, Buttons: {summary['buttons']}, Forms: {summary['form_elements']}")
        
        # Print element types breakdown
        element_types = self._get_element_type_distribution(dom_tree)
        logger.info("Element types breakdown:")
        for elem_type, count in sorted(element_types.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {elem_type}: {count}")
        
        logger.info("-"*80)
        logger.info("DOM TREE STRUCTURE:")
        
        # Print tree with limited depth for main output
        display_depth = min(max_depth, 3)  # Start with a smaller depth for overview
        output_lines = self.print_dom_tree(dom_tree, max_depth=display_depth, include_details=False)
        for line in output_lines:
            logger.info(line)
        
        # Print interactive elements with more details
        logger.info("-"*80)
        logger.info("INTERACTIVE ELEMENTS DETAILS:")
        interactive_elements = self._get_interactive_elements(dom_tree)
        if interactive_elements:
            for i, elem in enumerate(interactive_elements[:20]):  # Limit to first 20 elements
                elem_info = []
                elem_info.append(f"[{i+1}] <{elem.node_name.lower()}")
                
                # Add important attributes
                attrs = []
                for key, value in elem.attributes.items():
                    if key in ['id', 'class', 'role', 'type', 'name', 'href', 'placeholder', 'value']:
                        attrs.append(f"{key}='{value}'")
                
                if attrs:
                    elem_info.append(f" {' '.join(attrs)}")
                
                # Add element index
                if elem.element_index is not None:
                    elem_info.append(f" [idx:{elem.element_index}]")
                
                elem_info.append(">")
                logger.info("".join(elem_info))
                
                # Print text content if available
                text_content = self._get_element_text(elem)
                if text_content:
                    logger.info(f"    Text: \"{text_content[:100]}\"")
                
                # Print position if available
                if elem.absolute_position:
                    pos = elem.absolute_position
                    logger.info(f"    Position: x={pos.x:.1f}, y={pos.y:.1f}, width={pos.width:.1f}, height={pos.height:.1f}")
                
                # Print if clickable
                if elem.snapshot_node and elem.snapshot_node.is_clickable:
                    logger.info(f"    Clickable: {elem.snapshot_node.is_clickable}")
            
            if len(interactive_elements) > 20:
                logger.info(f"... and {len(interactive_elements) - 20} more interactive elements")
        else:
            logger.info("No interactive elements found")
        
        logger.info("="*80)


# Function to use in the Agent's process_one_task method
async def visualize_dom_after_task(browser_session) -> None:
    """
    Visualize the DOM tree after a task completes.
    This function can be called from within process_one_task.
    
    Args:
        browser_session: The browser session to use
    """
    visualizer = DOMTreeVisualizer(browser_session)
    await visualizer.print_dom_after_task(max_depth=5, include_details=True)
