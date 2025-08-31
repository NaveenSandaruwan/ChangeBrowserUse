from browser_use import Agent, ChatGoogle, BrowserProfile, BrowserSession ,browser
from dotenv import load_dotenv

# Read GOOGLE_API_KEY into env
load_dotenv()

# Create a browser profile


# Start a browser session using the browser_profile argument


# Initialize the model
llm = ChatGoogle(model='gemini-2.0-flash')

# Create agent with the model


import asyncio

load_dotenv()


async def main():
    profile = BrowserProfile(
    user_data_dir=r"E:\VS CODE\Agentic AI\profile",  
    profile="Default",
    chrome_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    keep_alive=True,
    enable_default_extensions=True
)
    browser = BrowserSession(
    browser_profile=profile
     )
    agent = Agent(
    task="Go to geeks for geeks data structures and algorithms",
    llm=llm,
    browser=browser
            )
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())





