from fastapi import FastAPI
from agents import Runner
from agents.health_coach import health_coach

app = FastAPI()
runner = Runner(health_coach)

@app.get("/motivate")
def motivate(user_query: str = "Motivate me to lose weight"):
    return {"response": runner.run(user_query)}
