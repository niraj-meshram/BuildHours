from agents import Agent
from utils import run_demo_loop


agent = Agent(
    name="Assistant",
    model="o3",
)

run_demo_loop(agent)