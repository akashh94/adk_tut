import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from src.core.session_manager import apply_initial_state
from src.core.runner import run_chat_loop
from src.agents.answer_agent.agent import root_agent

async def main():
    # 1. Instantiate the session service
    session_service = InMemorySessionService()
    
    # 2. Instantiate the Runner, injecting the session service so it handles context internally
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="weather_assistant"
    )

    # 3. Simulate the raw payload coming from a stateless client (e.g., frontend)
    client_payload = {
        "user_id": "akash_001",
        "session_id": "session_001",
        "app_name": "weather_assistant",
        "name": "Akash",
    }

    # 4. Pre-seed the database/memory with initial state via a middleware/hook approach
    await apply_initial_state(
        session_service=session_service,
        session_id=client_payload["session_id"],
        user_id=client_payload["user_id"],
        app_name=client_payload["app_name"]
    )
    
    
    # 5. Hand execution over to the Runner using only the payload identifiers
    await run_chat_loop(
        runner=runner, 
        user_id=client_payload["user_id"],
        session_id=client_payload["session_id"],
        app_name=client_payload["app_name"]
    )

if __name__ == "__main__":
    asyncio.run(main())