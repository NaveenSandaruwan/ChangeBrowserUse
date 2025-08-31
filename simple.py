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
    # Configure browser to stay alive until explicitly closed
    profile = BrowserProfile(
        user_data_dir=r"E:\VS CODE\Agentic AI\profile",  
        profile="Default",
        chrome_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        keep_alive=True,  # Keep browser alive between tasks
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
    
    is_final_exit = False  # Flag to track if we're in final exit
    
    try:
        while True:
            task = input("Enter a task (or 'exit' to quit): ")
            if task.lower() == "exit":
                is_final_exit = True
                print("Exiting program...")
                # Ensure browser is closed only at final exit
                try:
                    # Force keep_alive to False only at final exit
                    if agent.browser_session and agent.browser_session.browser_profile:
                        agent.browser_session.browser_profile.keep_alive = False
                        print("Closing browser since this is the final exit...")
                    await agent.shutdown()
                except Exception as e:
                    print(f"Error during shutdown: {e}")
                    print("Forcing browser closure...")
                    # Last resort attempt to close browser
                    if hasattr(agent, 'browser_session') and agent.browser_session:
                        if hasattr(agent.browser_session, 'browser') and agent.browser_session.browser:
                            try:
                                await agent.browser_session.browser.close()
                                print("Browser closed forcefully.")
                            except Exception as close_e:
                                print(f"Could not close browser: {close_e}")
                break
            else:
                # For regular tasks, we want to keep the browser alive
                if agent.browser_session and agent.browser_session.browser_profile:
                    agent.browser_session.browser_profile.keep_alive = True
                # Don't force browser closure for regular tasks
                await agent.process_one_task(task, force_browser_close_on_exit=False)
    except KeyboardInterrupt:
        print("\nProgram interrupted. Shutting down...")
        is_final_exit = True
        try:
            # Force keep_alive to False on interrupt
            if agent.browser_session and agent.browser_session.browser_profile:
                agent.browser_session.browser_profile.keep_alive = False
            await agent.shutdown()
        except Exception as e:
            print(f"Error during shutdown after interrupt: {e}")
            # Try direct browser closure as last resort
            if hasattr(agent, 'browser_session') and agent.browser_session and hasattr(agent.browser_session, 'browser'):
                try:
                    await agent.browser_session.browser.close()
                except:
                    pass
    except Exception as e:
        print(f"Error in main loop: {e}")
        is_final_exit = True
        print("Attempting clean shutdown...")
        try:
            # Force keep_alive to False on error
            if agent.browser_session and agent.browser_session.browser_profile:
                agent.browser_session.browser_profile.keep_alive = False
            await agent.shutdown()
        except Exception as shutdown_e:
            print(f"Error during emergency shutdown: {shutdown_e}")
        raise
    finally:
        # Final check to ensure browser is closed if this is the final exit
        if is_final_exit and agent.browser_session and hasattr(agent.browser_session, 'browser') and agent.browser_session.browser:
            try:
                print("Final check: ensuring browser is closed...")
                await agent.browser_session.browser.close()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())





