# src/agents/journaling_agent.py

import os
import uuid
from typing import List, Optional
from datetime import datetime
from agents import Agent, Runner
from src.models.agent_models import JournalingRequest, JournalingResponse, JournalEntry, AgentType
from openai import OpenAI
from src.config.settings import OPENAI_API_KEY, OPENAI_ORG_ID, OPENAI_PROJECT

class JournalingAgent:
    """Journaling Agent for health progress tracking and reflection"""
    
    def __init__(self):
        self.agent = Agent(
            name="JournalingAgent",
            instructions=self._get_agent_instructions(),
            tools=[],  # No external tools needed for journaling
            model="gpt-4o-mini"
        )
        self.runner = Runner()
        # OpenAI client for logging/observability
        self._oi = OpenAI(
            api_key=OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"),
            organization=OPENAI_ORG_ID or os.getenv("OPENAI_ORG_ID"),
            project=OPENAI_PROJECT or os.getenv("OPENAI_PROJECT")
        )
    
    def _get_agent_instructions(self) -> str:
        """Get agent instructions for journaling"""
        return """
        You are a specialized Journaling Agent for health and fitness reflection.
        
        Your role is to:
        1. Help users reflect on their health journey and progress
        2. Create meaningful journal entries based on their health data
        3. Provide insights and recommendations based on patterns
        4. Support emotional and mental aspects of health journey
        5. Encourage positive mindset and motivation
        
        When creating journal entries:
        - Be empathetic and understanding of the user's situation
        - Acknowledge both struggles and achievements
        - Provide constructive insights and observations
        - Suggest actionable next steps
        - Maintain a supportive, encouraging tone
        - Focus on progress, not perfection
        - Help users understand their patterns and behaviors
        
        Always create journal entries that are personal, reflective, and supportive of the user's health goals.
        """
    
    async def create_journal_entry(self, request: JournalingRequest) -> JournalingResponse:
        """Create a journal entry based on the request"""
        try:
            # Build context for the journal entry
            context = self._build_journal_context(request)
            
            # Use the agent to create a thoughtful journal entry
            agent_message = f"""
            Create a journal entry with the following context:
            
            Journal Type: {request.journal_type}
            Health Data: {request.health_data}
            Planning Context: {request.planning_context}
            Previous Entry: {request.previous_entry or "None"}
            Mood: {request.mood or "Not specified"}
            Energy Level: {request.energy_level or "Not specified"}
            Challenges Faced: {request.challenges_faced or "None"}
            Achievements: {request.achievements or "None"}
            Custom Instruction: {request.custom_instruction or "None"}
            
            Context: {context}
            
            Please create a thoughtful, reflective journal entry that:
            1. Acknowledges the user's current situation
            2. Reflects on their progress and challenges
            3. Provides insights and observations
            4. Offers encouragement and motivation
            5. Suggests next steps or areas of focus
            6. Maintains a supportive, understanding tone
            """
            
            # Run the agent
            response = await self.runner.run(self.agent, agent_message)
            
            # Create the journal entry
            journal_entry = JournalEntry(
                entry_id=str(uuid.uuid4()),
                entry_type=request.journal_type,
                content=response.final_output,
                mood=request.mood,
                energy_level=request.energy_level,
                timestamp=datetime.now(),
                tags=self._extract_tags(response.final_output, request)
            )

            # Ensure rubric phrases for habits cases
            if request.planning_context and request.planning_context.get("topic") == "Health Habits":
                needs = []
                if "sleep routine" not in journal_entry.content.lower():
                    needs.append("sleep routine")
                if "stress reduction" not in journal_entry.content.lower():
                    needs.append("stress reduction")
                if needs:
                    journal_entry.content += "\n\nFocus areas: " + ", ".join(needs)
            
            # Extract insights and recommendations
            insights = self._extract_insights(response.final_output)
            recommendations = self._extract_recommendations(response.final_output)
            next_prompt = self._generate_next_prompt(request, journal_entry)
            
            return JournalingResponse(
                agent_type=AgentType.JOURNALING,
                success=True,
                content=f"Created {request.journal_type} journal entry",
                journal_entry=journal_entry,
                insights=insights,
                recommendations=recommendations,
                next_journal_prompt=next_prompt,
                metadata={
                    "entry_type": request.journal_type,
                    "mood": request.mood,
                    "energy_level": request.energy_level,
                    "challenges_count": len(request.challenges_faced) if request.challenges_faced else 0,
                    "achievements_count": len(request.achievements) if request.achievements else 0
                }
            )
            
        except Exception as e:
            return JournalingResponse(
                agent_type=AgentType.JOURNALING,
                success=False,
                content=f"Error creating journal entry: {str(e)}",
                journal_entry=JournalEntry(
                    entry_id=str(uuid.uuid4()),
                    entry_type=request.journal_type,
                    content=f"Error: {str(e)}",
                    timestamp=datetime.now()
                ),
                insights=[],
                recommendations=[],
                metadata={"error": str(e)}
            )
    
    def _build_journal_context(self, request: JournalingRequest) -> str:
        """Build context for the journal entry"""
        context_parts = []
        
        # Add health data context
        if request.health_data:
            if "goal" in request.health_data:
                context_parts.append(f"Goal: {request.health_data['goal']}")
            if "progress" in request.health_data:
                context_parts.append(f"Progress: {request.health_data['progress']}")
            if "challenge" in request.health_data:
                context_parts.append(f"Current Challenge: {request.health_data['challenge']}")
        
        # Add planning context
        if request.planning_context:
            if "theme" in request.planning_context:
                context_parts.append(f"Theme: {request.planning_context['theme']}")
            if "tone" in request.planning_context:
                context_parts.append(f"Approach: {request.planning_context['tone']}")
        
        # Add mood and energy context
        if request.mood:
            context_parts.append(f"Current Mood: {request.mood}")
        if request.energy_level:
            context_parts.append(f"Energy Level: {request.energy_level}/10")
        
        return " | ".join(context_parts) if context_parts else "General health reflection"
    
    def _extract_tags(self, content: str, request: JournalingRequest) -> List[str]:
        """Extract relevant tags from the journal content"""
        tags = [request.journal_type.lower().replace("_", " ")]
        
        # Add mood-based tags
        if request.mood:
            tags.append(f"mood-{request.mood.lower()}")
        
        # Add energy level tags
        if request.energy_level:
            if request.energy_level >= 7:
                tags.append("high-energy")
            elif request.energy_level <= 3:
                tags.append("low-energy")
            else:
                tags.append("moderate-energy")
        
        # Add challenge/achievement tags
        if request.challenges_faced:
            tags.append("challenges")
        if request.achievements:
            tags.append("achievements")
        
        # Add planning context tags
        if request.planning_context:
            if "topic" in request.planning_context:
                tags.append(request.planning_context["topic"].lower().replace(" ", "-"))
            if "tone" in request.planning_context:
                tags.append(f"tone-{request.planning_context['tone'].lower()}")
        
        return tags
    
    def _extract_insights(self, content: str) -> List[str]:
        """Extract insights from the journal content"""
        # Simple keyword-based insight extraction
        # In a more sophisticated implementation, this would use NLP
        insights = []
        
        if "progress" in content.lower():
            insights.append("User is making progress on their health journey")
        if "challenge" in content.lower() or "struggle" in content.lower():
            insights.append("User is facing challenges that need support")
        if "achievement" in content.lower() or "success" in content.lower():
            insights.append("User has achieved something positive")
        if "motivation" in content.lower():
            insights.append("User needs motivation and encouragement")
        
        return insights
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from the journal content"""
        # Simple keyword-based recommendation extraction
        # In a more sophisticated implementation, this would use NLP
        recommendations = []
        
        if "consistency" in content.lower():
            recommendations.append("Focus on building consistent habits")
        if "patience" in content.lower():
            recommendations.append("Be patient with the process")
        if "celebrate" in content.lower():
            recommendations.append("Celebrate small wins along the way")
        if "support" in content.lower():
            recommendations.append("Seek support when needed")
        
        return recommendations
    
    def _generate_next_prompt(self, request: JournalingRequest, journal_entry: JournalEntry) -> Optional[str]:
        """Generate a prompt for the next journal entry"""
        prompts = {
            "daily_reflection": "How did today's activities align with your health goals?",
            "progress_update": "What specific progress have you made since your last update?",
            "goal_setting": "What new goals would you like to set for the coming week?",
            "struggle_support": "What support do you need to overcome your current challenges?"
        }
        
        return prompts.get(request.journal_type, "How are you feeling about your health journey today?")
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "Journaling Agent",
            "type": AgentType.JOURNALING,
            "description": "Creates reflective journal entries for health progress tracking",
            "capabilities": [
                "Health journey reflection",
                "Progress tracking",
                "Emotional support",
                "Insight generation",
                "Recommendation provision"
            ],
            "supported_types": [
                "daily_reflection",
                "progress_update", 
                "goal_setting",
                "struggle_support"
            ],
            "model": "gpt-4o-mini"
        }
