def build_prompt(prev_data: dict, current_data: dict, user_progress: str = "neutral") -> str:
    """
    Builds the agent prompt including Apple Health data and motivational strategy.
    prev_data and current_data are dictionaries serialized from HealthData.
    user_progress can be: 'compliant', 'resistant', 'neutral'.
    """

    base_prompt = f"""
You are a motivational weight-loss assistant. 
Here is the user’s Apple HealthKit data:

Previous:
- Steps: {prev_data.get('steps', 0)} / {prev_data.get('goal_steps', 'N/A')}
- Calories: {prev_data.get('calories', 0)}
- Workouts: {prev_data.get('workouts', 0)}
- Weight: {prev_data.get('weight', 'N/A')} kg

Current:
- Steps: {current_data.get('steps', 0)} / {current_data.get('goal_steps', 'N/A')}
- Calories: {current_data.get('calories', 0)}
- Workouts: {current_data.get('workouts', 0)}
- Weight: {current_data.get('weight', 'N/A')} kg
"""

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

    return base_prompt + strategy + """
Answer guidelines:
1. Suggest 1–2 small, actionable steps.
2. Keep tone positive and supportive, never shaming.
3. Offer top 3 web links and top 3 YouTube resources.
"""
