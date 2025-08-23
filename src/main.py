from agents import Runner
from agents.health_coach import health_coach

if __name__ == "__main__":
    runner = Runner(health_coach)
    query = "I feel like giving up on my weight loss plan. Motivate me!"
    response = runner.run(query)
    print(response)
