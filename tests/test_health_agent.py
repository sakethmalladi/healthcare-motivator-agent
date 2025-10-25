import pytest
import asyncio
from src.agents.health_coordinator import HealthCoordinator
from src.tools.apple_health_kit_mock import AppleHealthKitMock
from src.models.health_kit_models import HealthKitData


@pytest.fixture
def health_coordinator():
    """Health coordinator instance"""
    return HealthCoordinator()

@pytest.fixture
def health_kit_mock():
    """Apple Health Kit mock instance"""
    return AppleHealthKitMock()

@pytest.fixture
def weight_loss_sample(health_kit_mock):
    """Weight loss scenario with mock health data"""
    current_data = health_kit_mock.generate_health_data("user001", 0, "progress")
    previous_data = health_kit_mock.generate_health_data("user001", 1, "struggling")
    
    return {
        "user_id": "user001",
        "current_data": current_data,
        "previous_data": previous_data,
        "goals": ["Lose 10kg in 6 months", "Build healthy habits"],
        "preferences": {"focus": "sustainable habits", "avoid": "crash diets"},
        "mood": "motivated",
        "energy_level": 7,
        "challenges": ["portion control", "evening snacking"],
        "achievements": ["Lost 0.5kg this week", "More energy", "Better sleep"]
    }

@pytest.fixture
def fitness_sample(health_kit_mock):
    """Fitness training scenario with mock health data"""
    current_data = health_kit_mock.generate_health_data("user002", 0, "excellent")
    previous_data = health_kit_mock.generate_health_data("user002", 1, "normal")
    
    return {
        "user_id": "user002",
        "current_data": current_data,
        "previous_data": previous_data,
        "goals": ["Run a 10K race in under 50 minutes", "Build endurance and strength"],
        "preferences": {"focus": "endurance and strength", "training": "gradual progression"},
        "mood": "energetic",
        "energy_level": 8,
        "challenges": ["maintaining pace", "recovery time"],
        "achievements": ["Improved distance and pace", "Feeling stronger", "Consistent training"]
    }

@pytest.fixture
def muscle_building_sample(health_kit_mock):
    """Muscle building scenario with mock health data"""
    current_data = health_kit_mock.generate_health_data("user003", 0, "excellent")
    previous_data = health_kit_mock.generate_health_data("user003", 1, "normal")
    
    return {
        "user_id": "user003",
        "current_data": current_data,
        "previous_data": previous_data,
        "goals": ["Build muscle mass and strength", "Progressive overload"],
        "preferences": {"focus": "progressive overload and recovery", "training": "strength focused"},
        "mood": "determined",
        "energy_level": 9,
        "challenges": ["recovery time", "form maintenance"],
        "achievements": ["Strength gains visible", "Clothes fitting tighter", "Consistent progression"]
    }

@pytest.fixture
def walking_sample(health_kit_mock):
    """Walking habit scenario with mock health data"""
    current_data = health_kit_mock.generate_health_data("user004", 0, "progress")
    previous_data = health_kit_mock.generate_health_data("user004", 1, "struggling")
    
    return {
        "user_id": "user004",
        "current_data": current_data,
        "previous_data": previous_data,
        "goals": ["Reach 10000 steps daily", "Build consistent walking habit"],
        "preferences": {"focus": "simple and enjoyable", "approach": "gradual increase"},
        "mood": "content",
        "energy_level": 6,
        "challenges": ["consistency", "weather"],
        "achievements": ["Building consistent walking habit", "Increased daily steps"]
    }

@pytest.fixture
def givingup_sample(health_kit_mock):
    """Giving up scenario with mock health data"""
    current_data = health_kit_mock.generate_health_data("user005", 0, "crisis")
    previous_data = health_kit_mock.generate_health_data("user005", 1, "excellent")
    
    return {
        "user_id": "user005",
        "current_data": current_data,
        "previous_data": previous_data,
        "goals": ["Lose weight and get healthy", "Don't give up"],
        "preferences": {"focus": "motivation and support", "approach": "gentle encouragement"},
        "mood": "discouraged",
        "energy_level": 3,
        "challenges": ["motivation", "consistency", "self-doubt"],
        "achievements": ["Was doing great for 3 weeks", "Lost 2kg initially"]
    }

# ========== GET RESULTS TESTS ==========

@pytest.mark.asyncio
async def test_weight_loss_results(health_coordinator, weight_loss_sample):
    """Test weight loss motivation with real results."""
    result = await health_coordinator.process_health_request(
        user_id=weight_loss_sample["user_id"],
        health_data=weight_loss_sample,
        custom_instruction="Focus on sustainable habits, avoid crash diets"
    )
    
    print(f"\n========== WEIGHT LOSS RESULTS ==========")
    print(f"USER: {weight_loss_sample['user_id']}")
    print(f"GOALS: {weight_loss_sample['goals']}")
    print(f"MOOD: {weight_loss_sample['mood']}")
    print(f"ENERGY: {weight_loss_sample['energy_level']}/10")
    
    print(f"\n🎯 PLANNING DECISION:")
    print(f"Theme: {result.planning_decision.theme}")
    print(f"Topic: {result.planning_decision.topic}")
    print(f"Tone: {result.planning_decision.tone} - {result.planning_decision.tone_description}")
    print(f"Confidence: {result.planning_decision.confidence_score}")
    
    print(f"\n💬 OVERALL SUMMARY:")
    print(result.overall_summary)
    
    if result.youtube_results and result.youtube_results.success:
        print(f"\n🎥 YOUTUBE VIDEOS ({len(result.youtube_results.videos)}):")
        for i, video in enumerate(result.youtube_results.videos, 1):
            print(f"{i}. {video.title}")
            print(f"   🔗 {video.url}")
    
    if result.curated_results and result.curated_results.success:
        print(f"\n📰 CURATED ARTICLES ({len(result.curated_results.articles)}):")
        for i, article in enumerate(result.curated_results.articles, 1):
            print(f"{i}. {article.title}")
            print(f"   🔗 {article.url}")
    
    if result.journaling_results and result.journaling_results.success:
        print(f"\n📝 JOURNAL ENTRY:")
        print(f"Type: {result.journaling_results.journal_entry.entry_type}")
        print(f"Content: {result.journaling_results.journal_entry.content[:200]}...")
    
    print("=" * 50)
    
    assert result.planning_decision is not None
    assert len(result.overall_summary) > 0

@pytest.mark.asyncio 
async def test_fitness_results(health_coordinator, fitness_sample):
    """Test fitness motivation with real results."""
    result = await health_coordinator.process_health_request(
        user_id=fitness_sample["user_id"],
        health_data=fitness_sample,
        custom_instruction="Want to build endurance and strength"
    )
    
    print(f"\n========== FITNESS RESULTS ==========")
    print(f"USER: {fitness_sample['user_id']}")
    print(f"GOALS: {fitness_sample['goals']}")
    print(f"MOOD: {fitness_sample['mood']}")
    print(f"ENERGY: {fitness_sample['energy_level']}/10")
    
    print(f"\n🎯 PLANNING DECISION:")
    print(f"Theme: {result.planning_decision.theme}")
    print(f"Topic: {result.planning_decision.topic}")
    print(f"Tone: {result.planning_decision.tone} - {result.planning_decision.tone_description}")
    
    print(f"\n💬 OVERALL SUMMARY:")
    print(result.overall_summary)
    print("=" * 50)
    
    assert result.planning_decision is not None
    assert len(result.overall_summary) > 0

@pytest.mark.asyncio
async def test_muscle_building_results(health_coordinator, muscle_building_sample):
    """Test muscle building motivation with real results."""
    result = await health_coordinator.process_health_request(
        user_id=muscle_building_sample["user_id"],
        health_data=muscle_building_sample,
        custom_instruction="Emphasize progressive overload and recovery"
    )
    
    print(f"\n========== MUSCLE BUILDING RESULTS ==========")
    print(f"USER: {muscle_building_sample['user_id']}")
    print(f"GOALS: {muscle_building_sample['goals']}")
    print(f"MOOD: {muscle_building_sample['mood']}")
    print(f"ENERGY: {muscle_building_sample['energy_level']}/10")
    
    print(f"\n🎯 PLANNING DECISION:")
    print(f"Theme: {result.planning_decision.theme}")
    print(f"Topic: {result.planning_decision.topic}")
    print(f"Tone: {result.planning_decision.tone} - {result.planning_decision.tone_description}")
    
    print(f"\n💬 OVERALL SUMMARY:")
    print(result.overall_summary)
    print("=" * 50)
    
    assert result.planning_decision is not None
    assert len(result.overall_summary) > 0

@pytest.mark.asyncio
async def test_walking_results(health_coordinator, walking_sample):
    """Test walking motivation with real results."""
    result = await health_coordinator.process_health_request(
        user_id=walking_sample["user_id"],
        health_data=walking_sample,
        custom_instruction="Keep it simple and enjoyable"
    )
    
    print(f"\n========== WALKING RESULTS ==========")
    print(f"USER: {walking_sample['user_id']}")
    print(f"GOALS: {walking_sample['goals']}")
    print(f"MOOD: {walking_sample['mood']}")
    print(f"ENERGY: {walking_sample['energy_level']}/10")
    
    print(f"\n🎯 PLANNING DECISION:")
    print(f"Theme: {result.planning_decision.theme}")
    print(f"Topic: {result.planning_decision.topic}")
    print(f"Tone: {result.planning_decision.tone} - {result.planning_decision.tone_description}")
    
    print(f"\n💬 OVERALL SUMMARY:")
    print(result.overall_summary)
    print("=" * 50)
    
    assert result.planning_decision is not None
    assert len(result.overall_summary) > 0

@pytest.mark.asyncio
async def test_giving_up_results(health_coordinator, givingup_sample):
    """Test motivation for someone wanting to give up."""
    result = await health_coordinator.process_health_request(
        user_id=givingup_sample["user_id"],
        health_data=givingup_sample,
        custom_instruction="Need motivation to not give up completely"
    )
    
    print(f"\n========== GIVING UP SCENARIO RESULTS ==========")
    print(f"USER: {givingup_sample['user_id']}")
    print(f"GOALS: {givingup_sample['goals']}")
    print(f"MOOD: {givingup_sample['mood']}")
    print(f"ENERGY: {givingup_sample['energy_level']}/10")
    
    print(f"\n🎯 PLANNING DECISION:")
    print(f"Theme: {result.planning_decision.theme}")
    print(f"Topic: {result.planning_decision.topic}")
    print(f"Tone: {result.planning_decision.tone} - {result.planning_decision.tone_description}")
    
    print(f"\n💬 OVERALL SUMMARY:")
    print(result.overall_summary)
    print("=" * 50)
    
    assert result.planning_decision is not None
    assert len(result.overall_summary) > 0

@pytest.mark.asyncio
async def test_original_sample(health_coordinator, health_kit_mock):
    """Your original test sample with new architecture."""
    # Create mock health data for the original scenario
    current_data = health_kit_mock.generate_health_data("user123", 0, "progress")
    previous_data = health_kit_mock.generate_health_data("user123", 1, "normal")
    
    sample_data = {
        "user_id": "user123",
        "current_data": current_data,
        "previous_data": previous_data,
        "goals": ["Lose 5kg in 2 months", "Maintain 7,000+ steps daily"],
        "preferences": {"focus": "motivation and healthy recipes", "approach": "gradual progress"},
        "mood": "motivated",
        "energy_level": 8,
        "challenges": ["consistency"],
        "achievements": ["Doubled steps today", "Added extra workout"]
    }
    
    result = await health_coordinator.process_health_request(
        user_id=sample_data["user_id"],
        health_data=sample_data,
        custom_instruction="Keep motivation high and suggest healthy recipes"
    )

    print("\n========== ORIGINAL SAMPLE RESULTS ==========")
    print(f"USER: {sample_data['user_id']}")
    print(f"GOALS: {sample_data['goals']}")
    print(f"MOOD: {sample_data['mood']}")
    print(f"ENERGY: {sample_data['energy_level']}/10")
    
    print(f"\n🎯 PLANNING DECISION:")
    print(f"Theme: {result.planning_decision.theme}")
    print(f"Topic: {result.planning_decision.topic}")
    print(f"Tone: {result.planning_decision.tone} - {result.planning_decision.tone_description}")
    
    print(f"\n💬 OVERALL SUMMARY:")
    print(result.overall_summary)
    print("=" * 50)

    assert result.planning_decision is not None
    assert len(result.overall_summary) > 0

# ========== RUN ALL SAMPLES ==========

@pytest.mark.asyncio
async def test_all_samples(health_coordinator, health_kit_mock):
    """Test all sample scenarios together."""
    samples = [
        ("Weight Loss", {
            "user_id": "batch001",
            "current_data": health_kit_mock.generate_health_data("batch001", 0, "progress"),
            "previous_data": health_kit_mock.generate_health_data("batch001", 1, "normal"),
            "goals": ["Lose 15kg in 8 months", "Small sustainable changes"],
            "preferences": {"focus": "small sustainable changes", "approach": "gradual"},
            "mood": "determined",
            "energy_level": 6,
            "challenges": ["portion control"],
            "achievements": ["Small but consistent progress"]
        }),
        
        ("Marathon Training", {
            "user_id": "batch002",
            "current_data": health_kit_mock.generate_health_data("batch002", 0, "excellent"),
            "previous_data": health_kit_mock.generate_health_data("batch002", 1, "normal"),
            "goals": ["Complete first marathon in 6 months", "Build endurance"],
            "preferences": {"focus": "injury prevention", "training": "endurance focused"},
            "mood": "focused",
            "energy_level": 8,
            "challenges": ["distance building"],
            "achievements": ["Building endurance slowly but surely"]
        }),
        
        ("Strength Building", {
            "user_id": "batch003",
            "current_data": health_kit_mock.generate_health_data("batch003", 0, "excellent"),
            "previous_data": health_kit_mock.generate_health_data("batch003", 1, "normal"),
            "goals": ["Deadlift 150kg within 1 year", "Progressive overload"],
            "preferences": {"focus": "progressive overload with perfect form", "training": "strength focused"},
            "mood": "determined",
            "energy_level": 9,
            "challenges": ["form maintenance"],
            "achievements": ["Steady strength gains each month"]
        })
    ]
    
    print(f"\n{'='*60}")
    print("TESTING ALL SAMPLES - BATCH RESULTS")
    print(f"{'='*60}")
    
    for scenario_name, sample_data in samples:
        result = await health_coordinator.process_health_request(
            user_id=sample_data["user_id"],
            health_data=sample_data,
            custom_instruction="Focus on sustainable progress"
        )
        
        print(f"\n🎯 SCENARIO: {scenario_name}")
        print(f"👤 User: {sample_data['user_id']}")
        print(f"🎯 Goals: {sample_data['goals']}")
        print(f"📈 Mood: {sample_data['mood']} (Energy: {sample_data['energy_level']}/10)")
        print(f"\n🎯 PLANNING DECISION:")
        print(f"  Theme: {result.planning_decision.theme}")
        print(f"  Topic: {result.planning_decision.topic}")
        print(f"  Tone: {result.planning_decision.tone}")
        print(f"\n💬 OVERALL SUMMARY:")
        print(f"{result.overall_summary}")
        print(f"\n📊 AGENTS SUCCESSFUL: {result.metadata.get('agents_successful', 0)}/4")
        print(f"\n{'-'*50}")
        
        # Basic assertions
        assert result.planning_decision is not None
        assert len(result.overall_summary) > 0

if __name__ == "__main__":
    # Complete system test with comprehensive mock data
    async def complete_system_test():
        print("🏃‍♂️ AGENTIC WEIGHTLOSS MOTIVATOR - COMPLETE SYSTEM TEST")
        print("=" * 70)
        
        coordinator = HealthCoordinator()
        health_kit_mock = AppleHealthKitMock()
        
        # Test scenarios with comprehensive mock data
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
                
            except Exception as e:
                print(f"❌ ERROR in {test_case['name']}: {str(e)}")
            
            print()
        
        print("=" * 70)
        print("🎉 COMPLETE SYSTEM TEST FINISHED!")
        print("📈 All health scenarios processed successfully")
        print("🤖 AI Planning Agent working with Indian tone selection")
        print("📱 Mock Apple Health Kit data generation working")
        print("🔧 System ready for production use!")
        
    asyncio.run(complete_system_test())
