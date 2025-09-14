import time
from openai import OpenAI
from src.agents.register_motivate_agent import register_motivate_user_agent

client = OpenAI()
assistant = register_motivate_user_agent()

# Create thread for conversation
thread = client.beta.threads.create()

# Example: run agent with user context
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="User doubled their steps today, next goal 7,000+ steps tomorrow."
)

# Poll until complete
while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run_status.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for m in messages.data:
            print(m.role, ":", m.content[0].text.value)
        break
    time.sleep(1)
