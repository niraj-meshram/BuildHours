from typing import Literal, Optional
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


# ============================
#   TOOL 2: CLOTHING ADVICE
# ============================
@function_tool
def recommend_clothing(
    temp_c: float,
    condition: str,
    activity: Optional[str] = None,
) -> str:
    """
    Recommend what to wear based on temperature, condition, and optional activity.
    """

    # Simple rules – you can tweak as you like
    advice_parts = []

    if temp_c <= 0:
        advice_parts.append("It's very cold. Wear a heavy winter coat, gloves, and a warm hat.")
    elif temp_c <= 10:
        advice_parts.append("It's chilly. A warm jacket or coat is recommended.")
    elif temp_c <= 18:
        advice_parts.append("Mild weather. A light jacket or sweater should be enough.")
    elif temp_c <= 25:
        advice_parts.append("Comfortable temperature. Light clothing like t-shirt and jeans is fine.")
    else:
        advice_parts.append("It's quite warm. Wear light, breathable clothing and stay hydrated.")

    cond_lower = condition.lower()
    if "rain" in cond_lower or "shower" in cond_lower or "drizzle" in cond_lower:
        advice_parts.append("It might rain, so carry an umbrella or raincoat.")
    if "snow" in cond_lower:
        advice_parts.append("Snowy conditions – wear waterproof boots and warm layers.")
    if "sunny" in cond_lower or "clear" in cond_lower:
        advice_parts.append("It looks sunny; sunglasses and sunscreen could be helpful.")

    if activity:
        activity_lower = activity.lower()
        if "walk" in activity_lower or "hike" in activity_lower:
            advice_parts.append("Choose comfortable walking shoes.")
        if "run" in activity_lower or "jog" in activity_lower:
            advice_parts.append("Wear breathable sportswear suitable for the temperature.")

    return " ".join(advice_parts)
