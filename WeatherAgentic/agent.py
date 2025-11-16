
from agents import Agent, function_tool, Runner, ModelSettings
from tools import get_weather


weather_agent = Agent(
    name="Weather Assistant",
    model="gpt-4.1-mini",
    instructions=(
        "You are a helpful weather assistant.\n"
        "- When the user asks about current weather or temperature for a city, "
        "ALWAYS call the `get_weather` tool instead of guessing.\n"
        "- If the user doesn't specify units, default to metric.\n"
    ),
    tools=[get_weather],
    model_settings=ModelSettings(
        temperature=0.2,
    ),
)
