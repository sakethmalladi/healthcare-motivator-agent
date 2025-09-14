def build_prompt(prev_data, current_data, user_progress: str = "neutral", custom_instruction: str = "", goal: str = "", next_action: str = "") -> str:
    """
    Builds the agent prompt including health data and motivational strategy.
    - prev_data and current_data can be dicts or plain strings.
    - user_progress can be: 'compliant', 'resistant', 'neutral'.
    - custom_instruction adds dynamic playbook guidance.
    - goal and next_action are included to focus motivation.
    """

    # Handle dict vs string
    if isinstance(prev_data, dict):
        prev_str = f"""
- Steps: {prev_data.get('steps', 0)} / {prev_data.get('goal_steps', 'N/A')}
- Calories: {prev_data.get('calories', 0)}
- Workouts: {prev_data.get('workouts', 0)}
- Weight: {prev_data.get('weight', 'N/A')} kg
"""
    else:
        prev_str = str(prev_data)

    if isinstance(current_data, dict):
        current_str = f"""
- Steps: {current_data.get('steps', 0)} / {current_data.get('goal_steps', 'N/A')}
- Calories: {current_data.get('calories', 0)}
- Workouts: {current_data.get('workouts', 0)}
- Weight: {current_data.get('weight', 'N/A')} kg
"""
    else:
        current_str = str(current_data)

    # Strategy based on progress
    if user_progress == "compliant":
        strategy = """
The user is following advice well. 
Focus on:
- Saama: gentle reasoning (why their efforts are paying off).
- Daana: reward-based encouragement (celebrate wins).
"""
    elif user_progress == "resistant":
        strategy = """
The user is struggling to follow advice. 
Use Saama, Daana, Bheda, Danda:
- Saama: logical persuasion, start small.
- Daana: highlight rewards, gains.
- Bheda: compare with their past progress.
- Danda: gentle consequence reminder (no guilt).
"""
    else:
        strategy = """
User behavior is mixed. Use Saama + Daana mainly, with a touch of Bheda.
"""

    return f"""
You are a motivational assistant. 
The user’s health journey is:

Previous Data:
{prev_str}

Current Data:
{current_str}

Goal: {goal}
Next Action: {next_action}
Progress: {user_progress}

Custom Instructions:
{custom_instruction}

Strategy:
{strategy}

Answer guidelines:
1. Provide a short, supportive motivational message.
2. Suggest 1–2 small, actionable steps.
3. Include helpful web links and YouTube resources.
4. Keep tone positive and never shaming.
"""
