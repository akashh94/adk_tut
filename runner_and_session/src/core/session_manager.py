from google.adk.sessions import InMemorySessionService

USER_PREFIX = "user_"
TEMP_PREFIX = "temp_"

async def apply_initial_state(
    session_service: InMemorySessionService, 
    session_id: str, 
    user_id: str, 
    app_name: str
):
    """
    Creates the session with pre-filled state variables before the Runner begins execution.
    """
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