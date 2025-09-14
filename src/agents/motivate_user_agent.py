# src/agents/motivate_user_agent.py

import os
import time
from openai import OpenAI
from src.utils.prompt_builder import build_prompt
from src.models.health_models import MotivationRequest, MotivationResponse
from src.tools.search_web import search_web
from src.tools.search_youtube import search_youtube

class MotivateUserAgent:
    def __init__(self, client=None, assistant_id: str = None):
        self.client = client or OpenAI()
        self.assistant_id = assistant_id or os.getenv("MOTIVATE_AGENT_ID")
        self.use_sdk = self.assistant_id is not None   # toggle mode

    async def run(self, request: MotivationRequest) -> MotivationResponse:
        if self.use_sdk:
            return await self._run_via_sdk(request)
        else:
            return await self._run_local(request)

    async def _run_local(self, request: MotivationRequest) -> MotivationResponse:
        # Build dynamic prompt
        instruction_text = build_prompt(
            prev_data=request.previous_data,
            current_data=request.current_data,
            user_progress=request.progress,
            custom_instruction=request.custom_instruction,
            goal=request.goal,
            next_action=request.next_action
        )

        # Call LLM locally
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": instruction_text},
                {"role": "user", "content": f"My goal is {request.goal}. Next action: {request.next_action}. Please motivate me."}
            ]
        )

        message = response.choices[0].message.content.strip() if response.choices else ""
        if not message:
            message = f"You're making steady progress toward {request.goal}. Next step: {request.next_action}."

        # Tools
        search_query = f"{request.goal} {request.next_action} motivation"
        web_results = search_web(search_query, max_results=3)

        yt_query = f"{request.goal} {request.next_action} tips"
        yt_raw = search_youtube(yt_query)[:3]
        youtube_videos = [{"title": v.split(" - ")[0], "url": v.split(" - ")[1]} for v in yt_raw]

        return MotivationResponse(
            prompt=message,
            web_results=web_results,
            youtube_videos=youtube_videos
        )

    async def _run_via_sdk(self, request: MotivationRequest) -> MotivationResponse:
        """
        Run via registered OpenAI Assistant (Agents SDK).
        Requires MOTIVATE_AGENT_ID in env or passed into constructor.
        """
        # Create thread
        thread = self.client.beta.threads.create()

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id,
            instructions=f"Previous: {request.previous_data}, Current: {request.current_data}, "
                         f"Action Taken: {request.action_taken}, Next Action: {request.next_action}, "
                         f"Goal: {request.goal}, Progress: {request.progress}. "
                         f"Custom: {request.custom_instruction}"
        )

        # Poll until complete
        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                text_blocks = [m.content[0].text.value for m in messages.data if m.role == "assistant"]
                full_message = "\n".join(text_blocks) if text_blocks else "Stay motivated!"
                # In SDK mode, you only get text (tools are handled server-side)
                return MotivationResponse(prompt=full_message, web_results=[], youtube_videos=[])
            elif run_status.status in ["failed", "cancelled"]:
                return MotivationResponse(prompt="Agent run failed.", web_results=[], youtube_videos=[])
            time.sleep(1)
