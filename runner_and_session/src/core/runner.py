from google.adk.runners import Runner
from google.genai import types  # Assuming types is exposed at the root or specific module

async def run_chat_loop(runner: Runner, user_id: str, session_id: str, app_name: str):
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        print("Agent: ", end="", flush=True)
        
        # 1. Strictly construct the expected types.Content object
        message_content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )
        
        # 2. Call run_async matching the signature exactly
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message_content,
            # state_delta={"temp_current_city": "Mysore"} # Example of injecting context mid-flight
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    print("Final response:", event.content.parts[0].text)
                
        print("\n")