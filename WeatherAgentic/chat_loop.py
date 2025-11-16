from agents import Runner
from agent import weather_agent
import os
import asyncio

# ============================
#   CLI CHAT LOOP
# ============================
async def chat():
    print("🌤  Weather Agent ready. Type 'exit' to quit.\n")

    while True:
        user = input("You: ").strip()
        if user.lower() in ("exit", "quit"):
            break

        result = await Runner.run(
            starting_agent=weather_agent,
            input=user
        )

        print("\nAssistant:")
        print(result.final_output)
        print()


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")
    asyncio.run(chat())