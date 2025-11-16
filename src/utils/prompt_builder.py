# src/utils/prompt_builder.py

from typing import Optional, Dict, Any, List
from datetime import datetime
from src.models.health_kit_models import HealthKitData, HealthAnalysis
from src.models.agent_models import PlanningDecision

def build_prompt(
    previous_data: str, 
    current_data: str, 
    action_taken: str, 
    next_action: str, 
    custom_instruction: str, 
    goal: str, 
    progress: str
) -> str:
    """
    Build motivation prompt for LLM (legacy function for backward compatibility).
    
    Args:
        previous_data: User's previous health metrics/data
        current_data: User's current health metrics/data  
        action_taken: Recent actions the user has taken
        next_action: Planned next actions
        custom_instruction: User's custom preferences/instructions
        goal: User's health/fitness goal
        progress: Overall progress description
        
    Returns:
        str: Formatted prompt for the health assistant
    """
    return f"""
You are a supportive health assistant.
The user has shared their health progress:

Previous Data: {previous_data}
Current Data: {current_data}
Action Taken: {action_taken}
Next Action: {next_action}
Goal: {goal}
Progress: {progress}

Instructions:
{custom_instruction}

Provide motivational advice in a short, positive tone and suggest helpful web articles and YouTube videos.
"""

def build_system_prompt() -> str:
    """
    Build system prompt for the health assistant agent.
    
    Returns:
        str: System-level instructions for the agent
    """
    return """
You are a supportive health assistant specializing in weight loss and fitness motivation.

Your role is to:
1. Analyze user's health progress data (previous vs current metrics)
2. Acknowledge their efforts and progress positively
3. Provide personalized, actionable motivation based on their goals
4. Use available tools to find relevant articles and videos when helpful
5. Keep responses concise, positive, and encouraging

Always maintain an upbeat, supportive tone and focus on progress, not perfection.
When users feel like giving up, remind them of their journey and small wins.
"""

def build_user_message(
    previous_data: str,
    current_data: str, 
    action_taken: str,
    next_action: str,
    custom_instruction: str,
    goal: str,
    progress: str
) -> str:
    """
    Build user message for Agents SDK format.
    
    Args:
        Same as build_prompt
        
    Returns:
        str: Formatted user message for agent conversation
    """
    return f"""
Here's my health progress:

Previous Data: {previous_data}
Current Data: {current_data}
Action Taken: {action_taken}
Next Action: {next_action}
Goal: {goal}
Progress: {progress}
Custom Instructions: {custom_instruction}

Please motivate me and help me stay on track!
"""

def build_motivation_context(
    goal: str,
    progress: str,
    custom_instruction: Optional[str] = None
) -> str:
    """
    Build focused context for motivation generation.
    
    Args:
        goal: User's primary health/fitness goal
        progress: Current progress description
        custom_instruction: Optional user preferences
        
    Returns:
        str: Contextual information for motivation
    """
    context = f"User Goal: {goal}\nCurrent Progress: {progress}"
    
    if custom_instruction and custom_instruction.strip():
        context += f"\nUser Preferences: {custom_instruction}"
    
    return context

def build_search_query(goal: str, query_type: str = "motivation") -> str:
    """
    Build search queries for web and YouTube searches.
    
    Args:
        goal: User's health/fitness goal
        query_type: Type of query ('motivation', 'tips', 'workouts', etc.)
        
    Returns:
        str: Optimized search query
    """
    if query_type == "motivation":
        return f"{goal} motivation tips"
    elif query_type == "fitness":
        return f"{goal} motivation fitness"
    elif query_type == "workouts":
        return f"{goal} workout routines"
    elif query_type == "nutrition":
        return f"{goal} healthy eating tips"
    else:
        return f"{goal} {query_type}"

# ========== ENHANCED CONTEXT-AWARE PROMPT BUILDING ==========

def build_health_context_prompt(health_data: Dict[str, Any], planning_decision: PlanningDecision) -> str:
    """
    Build context-aware prompt based on health data and planning decision.
    
    Args:
        health_data: Complete health data including current/previous metrics
        planning_decision: AI planning decision with theme, topic, tone
        
    Returns:
        str: Contextualized prompt for agents
    """
    current_data = health_data.get("current_data")
    previous_data = health_data.get("previous_data")
    goals = health_data.get("goals", [])
    mood = health_data.get("mood", "neutral")
    energy_level = health_data.get("energy_level", 5)
    challenges = health_data.get("challenges", [])
    achievements = health_data.get("achievements", [])
    
    # Extract key metrics from health data
    health_metrics = _extract_health_metrics(current_data, previous_data)
    
    # Build context based on planning decision
    context = f"""
HEALTH CONTEXT ANALYSIS:
{_build_health_summary(health_metrics)}

PLANNING DECISION:
- Theme: {planning_decision.theme}
- Topic: {planning_decision.topic}
- Tone: {planning_decision.tone} - {planning_decision.tone_description}
- Characteristics: {', '.join(planning_decision.tone_characteristics)}

USER STATE:
- Goals: {', '.join(goals)}
- Mood: {mood} (Energy: {energy_level}/10)
- Challenges: {', '.join(challenges) if challenges else 'None'}
- Achievements: {', '.join(achievements) if achievements else 'None'}

CONTEXTUAL GUIDANCE:
{_build_contextual_guidance(planning_decision, health_metrics, mood, energy_level)}
"""
    
    return context.strip()

def build_agent_specific_prompt(agent_type: str, health_data: Dict[str, Any], 
                               planning_decision: PlanningDecision, custom_instruction: str = "") -> str:
    """
    Build agent-specific prompts based on planning decision and health context.
    
    Args:
        agent_type: Type of agent ('youtube', 'curated', 'web', 'journaling')
        health_data: Complete health data
        planning_decision: AI planning decision
        custom_instruction: User's custom instructions
        
    Returns:
        str: Agent-specific prompt
    """
    base_context = build_health_context_prompt(health_data, planning_decision)
    
    if agent_type == "youtube":
        return _build_youtube_prompt(base_context, planning_decision, custom_instruction)
    elif agent_type == "curated":
        return _build_curated_prompt(base_context, planning_decision, custom_instruction)
    elif agent_type == "web":
        return _build_web_prompt(base_context, planning_decision, custom_instruction)
    elif agent_type == "journaling":
        return _build_journaling_prompt(base_context, planning_decision, custom_instruction)
    else:
        return base_context

def build_planning_prompt(health_data: Dict[str, Any], user_goals: List[str], 
                         user_preferences: Dict[str, Any] = None,
                         topic_hint: str = "",
                         must_address_challenges: List[str] = None) -> str:
    """
    Build comprehensive prompt for the planning agent.
    
    Args:
        health_data: Complete health data
        user_goals: User's health goals
        user_preferences: User's preferences and constraints
        
    Returns:
        str: Planning-specific prompt
    """
    current_data = health_data.get("current_data")
    previous_data = health_data.get("previous_data")
    mood = health_data.get("mood", "neutral")
    energy_level = health_data.get("energy_level", 5)
    challenges = health_data.get("challenges", [])
    achievements = health_data.get("achievements", [])
    
    health_metrics = _extract_health_metrics(current_data, previous_data)
    
    must_address_challenges = must_address_challenges or []
    topic_hint_clause = f"Topic hint (derived heuristically): {topic_hint}" if topic_hint else "Topic hint: None"
    challenge_clause = ", ".join(must_address_challenges) if must_address_challenges else "None"
    return f"""
HEALTH DATA ANALYSIS:
{_build_health_summary(health_metrics)}

USER PROFILE:
- Goals: {', '.join(user_goals)}
- Mood: {mood} (Energy Level: {energy_level}/10)
- Current Challenges: {', '.join(challenges) if challenges else 'None identified'}
- Recent Achievements: {', '.join(achievements) if achievements else 'None reported'}
- Preferences: {user_preferences or 'No specific preferences'}
 - {topic_hint_clause}
 - Challenges to explicitly address in reasoning: {challenge_clause}

Please analyze the health data and determine the most appropriate planning decisions. Return your response in the following JSON format:

{{
    "theme": "<Motivation Needed|Progress Celebration|Struggle Support|Goal Adjustment|Habit Building|Crisis Intervention>",
    "topic": "<Workout Plan|Meal Plan|Health Habits>",
    "tone": "<Sama|Dana|Dhanda|Bedha>",
    "timing": {{
        "immediate": <boolean>,
        "frequency": "<daily|twice_daily|weekly>"
    }},
    "reasoning": "<detailed explanation of your decisions>",
    "confidence": <float between 0 and 1>
}}

IMPORTANT:
- Analyze the health data comprehensively
- Consider the user's emotional state, progress level, and specific needs
- Choose ONE topic. If diet/snacking/calories/meal/recipe related, prefer 'Meal Plan'.
- If endurance/workout/strength/run/pacing related, prefer 'Workout Plan'.
- If sleep/stress/routine/consistency related, prefer 'Health Habits'.
- If a Topic hint is present above, you MUST set the topic exactly to that hint unless it is clearly wrong.
- Provide clear reasoning for all decisions and explicitly address: {challenge_clause}
- Return ONLY valid JSON without any additional text or markdown formatting
"""
# ========== HELPER FUNCTIONS ==========

def _extract_health_metrics(current_data: HealthKitData, previous_data: HealthKitData = None) -> Dict[str, Any]:
    """Extract key health metrics from health data."""
    metrics = {}
    
    if current_data:
        metrics["current"] = {
            "steps": current_data.get_daily_steps(),
            "weight": current_data.get_weight(),
            "calories_burned": current_data.get_daily_calories_burned(),
            "calories_consumed": current_data.get_daily_calories_consumed(),
            "sleep_hours": current_data.get_sleep_hours(),
            "date": current_data.date
        }
    
    if previous_data:
        metrics["previous"] = {
            "steps": previous_data.get_daily_steps(),
            "weight": previous_data.get_weight(),
            "calories_burned": previous_data.get_daily_calories_burned(),
            "calories_consumed": previous_data.get_daily_calories_consumed(),
            "sleep_hours": previous_data.get_sleep_hours(),
            "date": previous_data.date
        }
    
    return metrics

def _build_health_summary(health_metrics: Dict[str, Any]) -> str:
    """Build a summary of health metrics."""
    summary_parts = []
    
    if "current" in health_metrics:
        current = health_metrics["current"]
        summary_parts.append(f"CURRENT: Steps: {current.get('steps', 'N/A')}, Weight: {current.get('weight', 'N/A')}kg, Sleep: {current.get('sleep_hours', 'N/A')}h")
    
    if "previous" in health_metrics:
        previous = health_metrics["previous"]
        summary_parts.append(f"PREVIOUS: Steps: {previous.get('steps', 'N/A')}, Weight: {previous.get('weight', 'N/A')}kg, Sleep: {previous.get('sleep_hours', 'N/A')}h")
    
    # Add trend analysis
    if "current" in health_metrics and "previous" in health_metrics:
        trends = _analyze_trends(health_metrics["current"], health_metrics["previous"])
        if trends:
            summary_parts.append(f"TRENDS: {', '.join(trends)}")
    
    return "\n".join(summary_parts) if summary_parts else "No health data available"

def _analyze_trends(current: Dict[str, Any], previous: Dict[str, Any]) -> List[str]:
    """Analyze trends between current and previous data."""
    trends = []
    
    # Steps trend
    if current.get("steps") and previous.get("steps"):
        change = ((current["steps"] - previous["steps"]) / previous["steps"]) * 100
        if change > 10:
            trends.append("Steps increasing")
        elif change < -10:
            trends.append("Steps decreasing")
    
    # Weight trend
    if current.get("weight") and previous.get("weight"):
        change = current["weight"] - previous["weight"]
        if change < -0.5:
            trends.append("Weight decreasing")
        elif change > 0.5:
            trends.append("Weight increasing")
    
    # Sleep trend
    if current.get("sleep_hours") and previous.get("sleep_hours"):
        change = current["sleep_hours"] - previous["sleep_hours"]
        if change > 0.5:
            trends.append("Sleep improving")
        elif change < -0.5:
            trends.append("Sleep declining")
    
    return trends

def _build_contextual_guidance(planning_decision: PlanningDecision, health_metrics: Dict[str, Any], 
                              mood: str, energy_level: int) -> str:
    """Build contextual guidance based on planning decision."""
    guidance_parts = []
    
    # Tone-based guidance
    tone = planning_decision.tone
    if tone == "Sama":
        guidance_parts.append("Approach: Gentle, compassionate, patient - focus on encouragement and small steps")
    elif tone == "Dana":
        guidance_parts.append("Approach: Generous, supportive, educational - celebrate progress and provide knowledge")
    elif tone == "Dhanda":
        guidance_parts.append("Approach: Firm, direct, challenging - hold accountable and push for results")
    elif tone == "Bedha":
        guidance_parts.append("Approach: Strategic, analytical, systematic - focus on optimization and planning")
    
    # Topic-based guidance
    topic = planning_decision.topic
    if topic == "Workout Plan":
        guidance_parts.append("Focus: Exercise routines, fitness activities, physical training")
    elif topic == "Meal Plan":
        guidance_parts.append("Focus: Nutrition, diet planning, healthy eating habits")
    elif topic == "Health Habits":
        guidance_parts.append("Focus: Lifestyle changes, daily routines, wellness practices")
    
    # Mood and energy guidance
    if mood in ["discouraged", "frustrated", "overwhelmed"]:
        guidance_parts.append("User State: Needs extra support and encouragement")
    elif mood in ["motivated", "energetic", "confident"]:
        guidance_parts.append("User State: Ready for challenges and new goals")
    
    if energy_level < 4:
        guidance_parts.append("Energy: Low - focus on gentle, manageable activities")
    elif energy_level > 7:
        guidance_parts.append("Energy: High - can handle more challenging activities")
    
    return " | ".join(guidance_parts)

def _build_youtube_prompt(base_context: str, planning_decision: PlanningDecision, custom_instruction: str) -> str:
    """Build YouTube-specific prompt."""
    return f"""
{base_context}

YOUTUBE SEARCH AGENT INSTRUCTIONS:
- Search for fitness and health videos that match the {planning_decision.topic}
- Use {planning_decision.tone} approach: {planning_decision.tone_description}
- Focus on videos that align with the user's current mood and energy level
- Prioritize educational, motivational content
- Consider video duration based on user's available time

Custom Instruction: {custom_instruction}
"""

def _build_curated_prompt(base_context: str, planning_decision: PlanningDecision, custom_instruction: str) -> str:
    """Build curated search-specific prompt."""
    return f"""
{base_context}

CURATED SEARCH AGENT INSTRUCTIONS:
- Find high-quality, evidence-based articles on {planning_decision.topic}
- Use {planning_decision.tone} approach: {planning_decision.tone_description}
- Focus on trusted medical and fitness sources
- Prioritize content that matches the user's current health situation
- Look for actionable, educational information

Custom Instruction: {custom_instruction}
"""

def _build_web_prompt(base_context: str, planning_decision: PlanningDecision, custom_instruction: str) -> str:
    """Build web search-specific prompt."""
    return f"""
{base_context}

WEB SEARCH AGENT INSTRUCTIONS:
- Search for general health information and community content on {planning_decision.topic}
- Use {planning_decision.tone} approach: {planning_decision.tone_description}
- Include diverse perspectives and real-world experiences
- Look for recent trends and community discussions
- Focus on practical, actionable information

Custom Instruction: {custom_instruction}
"""

def _build_journaling_prompt(base_context: str, planning_decision: PlanningDecision, custom_instruction: str) -> str:
    """Build journaling-specific prompt."""
    return f"""
{base_context}

JOURNALING AGENT INSTRUCTIONS:
- Create a reflective journal entry based on the {planning_decision.topic}
- Use {planning_decision.tone} approach: {planning_decision.tone_description}
- Acknowledge the user's current situation and progress
- Provide insights and encouragement
- Suggest next steps and areas of focus
- Maintain a supportive, understanding tone

Custom Instruction: {custom_instruction}
"""
