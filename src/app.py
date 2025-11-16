# src/app.py

from fastapi import FastAPI
from src.agents import Runner
from src.agents.health_coach import health_coach

app = FastAPI(title="Healthcare Motivator Agent", version="1.0.0")
runner = Runner(health_coach)

@app.get("/")
def root():
    return {"message": "Healthcare Motivator Agent with OpenAI Agents SDK"}

@app.get("/motivate")
def motivate(user_query: str = "Motivate me to lose weight"):
    """Your existing endpoint structure - now powered by Agents SDK."""
    response = runner.run(user_query)
    return {"response": response}

@app.post("/motivate")
def motivate_post(request: dict):
    """Enhanced endpoint for detailed motivation requests."""
    user_query = request.get("query", "Motivate me to lose weight")
    response = runner.run(user_query)
    return {"response": response}
