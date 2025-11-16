🌤️ WeatherAgentic – Background Task Queue LLM Agent

Autonomous Weather Agent using OpenAI Agents SDK, Task Queue, and Async Workers

This project demonstrates a production-grade agentic architecture using:

OpenAI Agents SDK

Background task queue (asyncio.Queue)

Dedicated agent worker(s)

FastAPI backend

CLI frontend

Tool calling (weather + clothing advice)

Event-based communication (/events endpoint)

It is a real-world pattern for deploying LLM-based microservices or agent workers at scale (similar to Celery, Sidekiq, AWS SQS workers, etc.).

Architecture Overview
🧠 High-Level Flow
User → CLI Frontend → Backend API → Task Queue → Worker → Agent → Tools → Worker → Events → Frontend → User

🧩 Components
Component	Location	Description
Frontend	chat_loop.py	Sends user queries → polls events → prints final result
Backend API	backend/api.py	Receives tasks → enqueues work → exposes /tasks and /events
Task Queue	backend/task_queue.py	In-memory queue + task store + event store
Worker	backend/worker.py	Background loop that processes tasks using the Agent SDK
Agent	agent.py	Smart weather agent with instructions + tools
Tools	tools.py	Weather API tool + clothing recommendation tool
Logging	logging_config.py	Centralized logging for tracing every step

Detailed Architecture (Diagram)

flowchart LR
    subgraph UserSide[User Side]
        CLI[chat_loop.py\nCLI Frontend]
    end

    subgraph Backend[FastAPI Backend]
        API[backend/api.py\nPOST /tasks\nGET /events]
        QUEUE[backend/task_queue.py\nasyncio.Queue + tasks + events]
        WORKER[backend/worker.py\nworker_loop()]
    end

    subgraph AgentLayer[Agent Layer]
        AGENT[agent.py\nweather_agent]
        TOOLS[tools.py\nget_weather\nrecommend_clothing]
    end

    EXTAPI[(wttr.in\nWeather API)]

    CLI -->|"POST /tasks\n(input)"| API
    API -->|"enqueue"| QUEUE
    WORKER -->|"await get()"| QUEUE
    WORKER -->|"Runner.run()"| AGENT
    AGENT -->|"tool call"| TOOLS
    TOOLS -->|"HTTP GET"| EXTAPI
    EXTAPI -->|"JSON"| TOOLS
    TOOLS -->|"string"| AGENT
    AGENT -->|"final_output"| WORKER
    WORKER -->|"add_event()"| QUEUE
    CLI <--|"GET /events"| API

Smart Weather Agent
Tools:
🔧 get_weather(city: str)

Real-time weather from wttr.in

Returns temperature, humidity, condition, feels-like temperature

🧥 recommend_clothing(temp_c, condition, activity)

Suggests clothing based on:

Temperature (°C)

Condition (rain, snow, clear, etc.)

Optional activity (walk, run, hike)

Agent Behavior:

When user asks about weather → call get_weather

When user asks about clothing → call get_weather → then recommend_clothing

Produces a clean, helpful answer

Project Structure

WeatherAgentic/
├── agent.py                # Smart weather agent
├── tools.py                # Tools exposed to agent
├── chat_loop.py            # CLI frontend
├── logging_config.py       # Central logging
├── requirements.txt
│
└── backend/
    ├── __init__.py
    ├── api.py              # FastAPI server
    ├── models.py           # TaskRequest, TaskStatus, TaskEvent
    ├── task_queue.py       # Queue + task/event stores
    └── worker.py           # Background worker loop

🖥️ Running the System
▶️ Step 1 — Start the backend
cd WeatherAgentic
uvicorn backend.api:app --reload


You should see:

Uvicorn running on http://127.0.0.1:8000
Backend startup: launching worker loop


Keep this window open.

▶️ Step 2 — Start the frontend CLI (new terminal)

cd WeatherAgentic
.\.venv\Scripts\activate
python chat_loop.py

You: SLC
(submitted task_id=ab12cd...)
Assistant:
Weather in Salt Lake City:
- Condition: Clear
- Temperature: 12°C
- Feels like: 10°C
- Humidity: 61%

You: What should I wear?
(submitted task_id=ff41b2...)
Assistant:
It will be around 12°C and clear.
A light jacket or sweater is recommended for an evening walk.
