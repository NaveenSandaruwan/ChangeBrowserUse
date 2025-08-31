"""
Test DOM tree visualization with Agent

This module tests the DOM tree visualization feature with a real agent.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path if needed
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import logging
from browser_use import Browser, BrowserProfile, BrowserSession
from browser_use.agent.service import Agent

# Use a simple LLM for testing
class MockLLM:
    def __init__(self, model="mock"):
        self.model = model
    
    async def generate(self, *args, **kwargs):
        return {"text": "This is a mock response for testing. I'll go to example.com and look at the DOM structure.", "action": {"name": "go_to_url", "args": {"url": "https://example.com"}}}
    
    def with_structured_output(self, *args, **kwargs):
        return self

logging.basicConfig(level=logging.INFO, 
                   format='%(levelname)-8s [%(name)s] %(message)s')

async def main():
    """
    Test the DOM tree visualization with an agent.
    """
    print("Setting up browser profile...")
    profile = BrowserProfile()
    
    print("Creating browser session...")
    browser_session = await BrowserSession.create(
        profile=profile, 
        headless=False
    )
    
    print("Initializing Mock LLM...")
    llm = MockLLM()
    
    print("Creating agent...")
    agent = Agent(
        task="Go to Google and search for DOM tree visualization",
        llm=llm,
        browser_session=browser_session
    )
    
    try:
        print("Running task...")
        # Run the agent to complete the task
        await agent.process_one_task(task="Go to Google and search for DOM tree visualization")
        print("✅ Task completed. Browser session remains active.")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
    finally:
        # Clean up
        print("Shutting down...")
        print("Shutting down agent...")
        await agent.shutdown()
        print("Task complete!")

if __name__ == "__main__":
    asyncio.run(main())
