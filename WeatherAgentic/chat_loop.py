# chat_loop.py
import time
import requests

BACKEND_URL = "http://127.0.0.1:8000"


def chat():
    print("🌤  Weather Agent (Background Task Queue). Type 'exit' to quit.\n")

    while True:
        user = input("You: ").strip()
        if user.lower() in ("exit", "quit"):
            break

        # 1) Create task
        resp = requests.post(
            f"{BACKEND_URL}/tasks",
            json={"input": user},
            timeout=10,
        )
        resp.raise_for_status()
        task_id = resp.json()["task_id"]
        print(f"(submitted task_id={task_id})")

        # 2) Poll /events until we see an event for this task_id
        result = None
        error = None

        while True:
            ev_resp = requests.get(f"{BACKEND_URL}/events", timeout=10)
            ev_resp.raise_for_status()
            events = ev_resp.json()  # list of {event_id, task_id, status, ...}

            found = False
            for ev in events:
                if ev["task_id"] == task_id:
                    found = True
                    if ev["status"] == "done":
                        result = ev["result"]
                    else:
                        error = ev["error"]
                    break

            if found:
                break

            # No relevant event yet → wait a bit and poll again
            time.sleep(0.5)

        print("\nAssistant:")
        if error:
            print("Error:", error)
        else:
            print(result)
        print()


if __name__ == "__main__":
    chat()
