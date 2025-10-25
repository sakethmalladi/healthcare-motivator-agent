# src/main.py

import asyncio
from src.agents import Runner
from src.agents.health_coach import health_coach

async def main():
    """Main function using your existing pattern."""
    runner = Runner(health_coach)
    query = "I feel like giving up on my weight loss plan. Motivate me!"
    response = runner.run(query)
    print(response)

if __name__ == "__main__":
    # Keep it simple like your original, but handle async properly
    runner = Runner(health_coach)
    query = "I feel like giving up on my weight loss plan. Motivate me!"
    response = runner.run(query)
    print(response)
