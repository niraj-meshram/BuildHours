from typing import Literal
import requests
from agents import function_tool

# ============================
#   TOOL DEFINITION
# ============================

@function_tool
def get_weather(city: str, units: Literal["metric", "imperial"] = "metric") -> str:
    """
    Fetch weather for a city using wttr.in (no API key needed).

    Args:
        city: e.g. "Salt Lake City"
        units: metric -> °C, imperial -> °F
    """
    try:
        resp = requests.get(f"https://wttr.in/{city}", params={"format": "j1"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data["current_condition"][0]
        desc = current["weatherDesc"][0]["value"]

        temp_c = float(current["temp_C"])
        feels_c = float(current["FeelsLikeC"])
        temp_f = float(current["temp_F"])
        feels_f = float(current["FeelsLikeF"])

        if units == "metric":
            temp = f"{temp_c}°C"
            feels = f"{feels_c}°C"
        else:
            temp = f"{temp_f}°F"
            feels = f"{feels_f}°F"

        return (
            f"Weather in {city}:\n"
            f"- Condition: {desc}\n"
            f"- Temperature: {temp}\n"
            f"- Feels like: {feels}\n"
            f"- Humidity: {current['humidity']}%"
        )

    except Exception as e:
        return f"Failed to fetch weather for {city}. Error: {str(e)}"