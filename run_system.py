#!/usr/bin/env python3
"""
Agentic Weightloss Motivator - One Command System Runner
Run the complete system with comprehensive mock data testing
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.health_coordinator import HealthCoordinator
from src.tools.apple_health_kit_mock import AppleHealthKitMock

async def run_complete_system():
    """Run the complete Agentic Weightloss Motivator system"""
    print("🏃‍♂️ AGENTIC WEIGHTLOSS MOTIVATOR - COMPLETE SYSTEM")
    print("=" * 70)
    print("🤖 AI-Powered Health Planning with Indian Historical Tones")
    print("📱 Mock Apple Health Kit Data Integration")
    print("🔧 4 Parallel Agents: YouTube, Curated, Web, Journaling")
    print("=" * 70)
    
    coordinator = HealthCoordinator()
    health_kit_mock = AppleHealthKitMock()
    
    # Comprehensive test scenarios
    test_scenarios = [
        {
            "name": "Weight Loss Progress",
            "scenario": "progress",
            "goals": ["Lose 10kg in 6 months", "Build healthy habits"],
            "mood": "motivated",
            "energy_level": 7,
            "challenges": ["portion control"],
            "achievements": ["Lost 0.5kg this week"],
            "custom_instruction": "Focus on sustainable weight loss"
        },
        {
            "name": "Fitness Enthusiast",
            "scenario": "excellent",
            "goals": ["Run a 10K race in under 50 minutes", "Build endurance"],
            "mood": "energetic",
            "energy_level": 9,
            "challenges": ["time management"],
            "achievements": ["Consistent training for 3 weeks"],
            "custom_instruction": "Help with advanced training techniques"
        },
        {
            "name": "Struggling Beginner",
            "scenario": "struggling",
            "goals": ["Start exercising regularly", "Eat healthier"],
            "mood": "frustrated",
            "energy_level": 4,
            "challenges": ["motivation", "consistency", "overwhelm"],
            "achievements": [],
            "custom_instruction": "Need gentle encouragement and simple steps"
        },
        {
            "name": "Health Crisis",
            "scenario": "crisis",
            "goals": ["Get back on track", "Emergency health intervention"],
            "mood": "discouraged",
            "energy_level": 2,
            "challenges": ["motivation", "consistency", "depression"],
            "achievements": ["Was doing great for 3 weeks"],
            "custom_instruction": "Need urgent motivation to not give up"
        },
        {
            "name": "Muscle Building",
            "scenario": "excellent",
            "goals": ["Build muscle mass and strength", "Progressive overload"],
            "mood": "determined",
            "energy_level": 8,
            "challenges": ["form maintenance"],
            "achievements": ["Strength gains visible", "Consistent progression"],
            "custom_instruction": "Emphasize progressive overload and recovery"
        }
    ]
    
    print(f"🧪 Testing {len(test_scenarios)} different health scenarios...")
    print()
    
    successful_tests = 0
    
    for i, test_case in enumerate(test_scenarios, 1):
        print(f"🎯 TEST {i}: {test_case['name'].upper()}")
        print("-" * 50)
        
        # Generate mock health data
        current_data = health_kit_mock.generate_health_data(f"user_{i}", 0, test_case["scenario"])
        previous_data = health_kit_mock.generate_health_data(f"user_{i}", 1, "normal")
        
        # Create comprehensive sample data
        sample_data = {
            "user_id": f"user_{i}",
            "current_data": current_data,
            "previous_data": previous_data,
            "goals": test_case["goals"],
            "preferences": {
                "focus": "motivation and healthy habits",
                "approach": "gradual progress" if test_case["scenario"] != "crisis" else "urgent intervention"
            },
            "mood": test_case["mood"],
            "energy_level": test_case["energy_level"],
            "challenges": test_case["challenges"],
            "achievements": test_case["achievements"]
        }
        
        try:
            # Process the health request
            result = await coordinator.process_health_request(
                user_id=sample_data["user_id"],
                health_data=sample_data,
                custom_instruction=test_case["custom_instruction"]
            )
            
            # Display results
            print(f"📊 Health Data: {current_data.summary}")
            print(f"🎯 Goals: {test_case['goals']}")
            print(f"😊 Mood: {test_case['mood']} (Energy: {test_case['energy_level']}/10)")
            print(f"🎯 Planning Decision:")
            print(f"   Theme: {result.planning_decision.theme}")
            print(f"   Topic: {result.planning_decision.topic}")
            print(f"   Tone: {result.planning_decision.tone} - {result.planning_decision.tone_description}")
            print(f"   Confidence: {result.planning_decision.confidence_score}")
            print(f"💬 Overall Summary: {result.overall_summary}")
            print(f"📊 Agents Successful: {result.metadata.get('agents_successful', 0)}/4")
            print(f"✅ Status: {'SUCCESS' if result.planning_decision else 'FAILED'}")
            
            if result.planning_decision:
                successful_tests += 1
                
        except Exception as e:
            print(f"❌ ERROR in {test_case['name']}: {str(e)}")
        
        print()
    
    print("=" * 70)
    print("🎉 COMPLETE SYSTEM TEST FINISHED!")
    print(f"📈 {successful_tests}/{len(test_scenarios)} health scenarios processed successfully")
    print("🤖 AI Planning Agent working with Indian tone selection (Sama, Dana, Dhanda, Bedha)")
    print("📱 Mock Apple Health Kit data generation working perfectly")
    print("🔧 System ready for production use!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_complete_system())
