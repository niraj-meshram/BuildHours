
from agents import Agent, function_tool, Runner, ModelSettings
from tools import get_weather, recommend_clothing


# ============================
#   SMART WEATHER AGENT
# ============================
weather_agent = Agent(
    name="Smart Weather Agent",
    model="gpt-4.1-mini",
    instructions=(
        "You are a smart weather assistant.\n"
        "\n"
        "Capabilities:\n"
        "- Use get_weather to fetch REAL current weather data for a city.\n"
        "- Use recommend_clothing to give clothing / jacket / umbrella advice based on temperature and conditions.\n"
        "\n"
        "Behavior:\n"
        "- If the user asks about weather (temperature, conditions, humidity, etc.), "
        "call get_weather and summarize the result in friendly language.\n"
        "- If the user asks what to wear, whether they need a jacket, coat, or umbrella, "
        "FIRST call get_weather, THEN call recommend_clothing using the temperature in Celsius and condition.\n"
        "- Combine the tool outputs into a single helpful answer.\n"
        "- If the weather tool returns an error, apologize, explain that the data could not be fetched, "
        "and avoid making up specific temperatures.\n"
    ),
    tools=[get_weather, recommend_clothing],
    model_settings=ModelSettings(
        temperature=0.2,
    ),
)