import os

from google.adk.agents import Agent

from dotenv import load_dotenv
load_dotenv()

root_agent = Agent(
    model=os.environ.get('AGENT_MODEL', ''),
    name='answer_agent',
    description='A helpful assistant for user questions.',
    instruction='''Answer user questions to the best of your knowledge
    You might have to answer questions about the user, their interests, and preferences.
    You can access the same for user {user_name} in the session state.

    and the data information is:
    {user_favorite_sport} is the user's favorite sport.
    
    '''
)