# Google ADK Implementation Context

## Overview
This document serves as the architectural and operational context for the Google Agent Development Kit (ADK) implementation. It captures the verified patterns, directory structures, and critical execution rules established for running a session-managed conversational agent.

## Directory Structure
The project follows a standard Python package structure. Execution must always occur from the root directory to maintain module resolution.

```text
root/
├── .env
├── requirements.txt
└── src/
    ├── __init__.py
    ├── main.py
    ├── core/
    │   ├── config.py
    │   ├── runner.py
    │   └── session_manager.py
    ├── agents/
    │   └── answer_agent/
    │       └── agent.py
    └── tools/
	
1. Session Management (src/core/session_manager.py)
Session state must be explicitly seeded before the Runner executes if the session does not already exist. The create_session method injects variables into the RAM database.

from google.adk.sessions import InMemorySessionService

USER_PREFIX = "user_"
TEMP_PREFIX = "temp_"

async def apply_initial_state(session_service: InMemorySessionService, session_id: str, user_id: str, app_name: str):
    """Creates the session with pre-filled state variables."""
    initial_state = {
        f"{USER_PREFIX}name": "Akash",
        f"{USER_PREFIX}favorite_sport": "Cricket",
        f"{TEMP_PREFIX}current_city": "Bengaluru"
    }
    
    await session_service.create_session(
        session_id=session_id,
        user_id=user_id,
        app_name=app_name,
        state=initial_state
    )
	
2. Agent Definition (src/agents/answer_agent/agent.py)
Critical Rule: Variables wrapped in {} within the agent's instructions must exactly match the keys evaluated in the session state (e.g., {user_name}, not {name}). Failure to match results in a KeyError.

from google.adk.engine import Agent

instructions = """
You are a helpful assistant.
The user's name is {user_name}.
Their favorite sport is {user_favorite_sport}.
Their current city context for this session is {temp_current_city}.
"""

root_agent = Agent(
    name="WeatherAssistant",
    model="gemini-2.5-flash",
    instructions=instructions
)

3. Runner & Event Loop (src/core/runner.py)
The Runner must be imported from google.adk.runners. When handling the run_async event loop, strict type-checking must be applied to satisfy static analyzers like Pylance. The user input must be wrapped in a types.Content object.
from google.adk.runners import Runner
from google.adk import types

async def run_chat_loop(runner: Runner, user_id: str, session_id: str, app_name: str):
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        print("Agent: ", end="", flush=True)
        
        message_content = types.Content(role="user", parts=[types.Part(text=user_input)])
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message_content
        ):
            if event.is_final_response():
                content = event.content
                if content is not None:
                    parts = content.parts
                    if parts is not None:
                        final_text = "".join(p.text for p in parts if getattr(p, 'text', None))
                        print(final_text)
                
        print("\n")
		
4. Main Entry Point (src/main.py)
When passing an agent directly to the Runner (without a full app object), the app_name parameter is mandatory to define the session namespace.

import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from src.core.session_manager import apply_initial_state
from src.core.runner import run_chat_loop
from src.agents.answer_agent.agent import root_agent

async def main():
    session_service = InMemorySessionService()
    
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="weather_assistant" # Mandatory when using agent directly
    )

    client_payload = {
        "user_id": "akash_001",
        "session_id": "session_001",
        "app_name": "weather_assistant"
    }

    await apply_initial_state(
        session_service=session_service,
        session_id=client_payload["session_id"],
        user_id=client_payload["user_id"],
        app_name=client_payload["app_name"]
    )
    
    await run_chat_loop(
        runner=runner, 
        user_id=client_payload["user_id"],
        session_id=client_payload["session_id"],
        app_name=client_payload["app_name"]
    )

if __name__ == "__main__":
    asyncio.run(main())
	
5. Execution Protocol
To execute the application, run the module from the root directory. Do not use relative dots or the .py extension in the module name.

Correct Command:python -m src.main