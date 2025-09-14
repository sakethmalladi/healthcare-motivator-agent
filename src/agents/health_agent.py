from src.models.health_models import MotivationRequest, MotivationResponse
from src.agents.motivate_user_agent import MotivateUserAgent

async def run_health_agent(request: MotivationRequest) -> MotivationResponse:
    agent = MotivateUserAgent()
    return await agent.run(request)
