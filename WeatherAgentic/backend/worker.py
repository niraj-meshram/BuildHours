# backend/worker.py
from agents import Runner            # or: from openai.agents import Runner
from agent import weather_agent      # 👈 IMPORTANT: no "WeatherAgentic." prefix

from .task_queue import task_queue, tasks, add_event


async def worker_loop():
    """
    Background worker that pulls tasks from the queue
    and runs the Smart Weather Agent.
    """
    while True:
        task_id, user_input = await task_queue.get()
        task = tasks[task_id]
        task.status = "running"

        try:
            agent_result = await Runner.run(
                starting_agent=weather_agent,
                input=user_input,
            )
            task.status = "done"
            task.result = agent_result.final_output
            add_event(task_id, "done", task.result, None)
        except Exception as e:
            task.status = "error"
            task.error = str(e)
            add_event(task_id, "error", None, task.error)

        task_queue.task_done()
