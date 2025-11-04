# Agentic Weightloss Motivator

A comprehensive AI-powered health coaching system that provides personalized health advice, motivation, web articles, YouTube videos, and journaling support using OpenAI GPT models and multi-agent architecture.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Usage](#usage)
8. [Running Tests](#running-tests)
9. [Running Evaluations](#running-evaluations)
10. [API Documentation](#api-documentation)
11. [Project Structure](#project-structure)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)

## 🎯 Overview

The Agentic Weightloss Motivator is an intelligent health assistant that uses a multi-agent system to provide personalized health guidance. The system coordinates multiple specialized agents that work together to:

- Analyze health data and determine appropriate intervention strategies
- Search for relevant health content (articles, videos)
- Create personalized journal entries
- Provide motivation based on user's current health state

The system uses Indian historical philosophical approaches (Sama, Dana, Dhanda, Bedha) to determine the appropriate tone and style of guidance.

## ✨ Features

### Core Capabilities
- **Health Data Analysis**: Analyzes steps, calories, weight, sleep, and workout data
- **Intelligent Planning**: Determines themes, topics, tones, and timing based on health scores
- **Multi-Agent Coordination**: Orchestrates 4 parallel agents:
  - **Planning Agent**: Analyzes health data and creates strategic plans
  - **YouTube Search Agent**: Finds relevant fitness and health videos
  - **Curated Search Agent**: Searches for high-quality health articles from trusted sources
  - **Web Search Agent**: Finds general health information and community content
  - **Journaling Agent**: Creates personalized reflective journal entries

### Key Features
- API-free DuckDuckGo search for health articles
- API-free YouTube search for fitness motivation videos
- Mock Apple Health Kit integration for testing
- Comprehensive evaluation framework
- FastAPI web interface
- Indian historical tone selection (Sama, Dana, Dhanda, Bedha)

## 🏗️ Architecture

The system uses a coordinator pattern where:

1. **Health Coordinator** receives health requests
2. **Planning Agent** analyzes data and creates a plan (theme, topic, tone, timing)
3. **Four agents run in parallel**:
   - YouTube Search Agent
   - Curated Search Agent
   - Web Search Agent
   - Journaling Agent
4. **Coordinator aggregates** all responses into a unified result

```
User Request
    ↓
Health Coordinator
    ↓
Planning Agent (analyzes health data)
    ↓
┌─────────────┬──────────────┬─────────────┬─────────────┐
│   YouTube   │   Curated    │    Web      │ Journaling  │
│   Agent     │   Agent       │   Agent     │   Agent     │
└─────────────┴──────────────┴─────────────┴─────────────┘
    ↓
Coordinated Response
```

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
1. **Python 3.11 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Git** (if cloning from repository)
   - Download from: https://git-scm.com/downloads

3. **Text Editor or IDE**
   - Recommended: VS Code, PyCharm, or any Python IDE

### Required Accounts
1. **OpenAI API Key**
   - Sign up at: https://platform.openai.com/
   - Create an API key from: https://platform.openai.com/api-keys
   - Keep your API key secure (you'll need it later)

## 🚀 Installation

Follow these steps carefully to set up the project:

### Step 1: Clone or Download the Project

**Option A: If you have Git installed**
```bash
git clone <your-repo-url>
cd agentic-weightloss-motivator
```

**Option B: If you downloaded as ZIP**
1. Extract the ZIP file to a folder (e.g., `F:\Agentic AI\agentic-weightloss-motivator`)
2. Open Command Prompt or PowerShell in that folder

### Step 2: Create a Virtual Environment

A virtual environment isolates your project dependencies. This is a best practice.

**On Windows:**
```bash
python -m venv venv
```

**On macOS/Linux:**
```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment

**On Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your command prompt, indicating the virtual environment is active.

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages:
- `openai-agents` - OpenAI Agents SDK
- `ddgs` - DuckDuckGo search
- `pydantic` - Data validation
- `pytest` - Testing framework
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `youtube-search-python` - YouTube search
- `python-dotenv` - Environment variable management

**Note:** If you encounter errors, try:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 5: Verify Installation

Check if Python can import the packages:
```bash
python -c "import openai; import ddgs; import pydantic; print('All packages installed successfully!')"
```

## ⚙️ Configuration

### Step 1: Create Environment File

Create a file named `.env` in the project root directory (`agentic-weightloss-motivator/`).

**On Windows:**
```bash
type nul > .env
```

**On macOS/Linux:**
```bash
touch .env
```

Or create it manually using a text editor.

### Step 2: Add Your API Key

Open the `.env` file in a text editor and add:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Important Security Notes:**
- Replace `your_openai_api_key_here` with your actual OpenAI API key
- Never commit the `.env` file to version control
- Keep your API key secret and secure

### Step 3: Verify Configuration

The `.env` file should be in the same directory as `requirements.txt`:
```
agentic-weightloss-motivator/
├── .env                    ← Your API key file
├── requirements.txt
├── README.md
└── src/
```

## 💻 Usage

### Option 1: Run Complete System Test (Recommended for First Time)

This runs the complete system with multiple test scenarios:

```bash
python run_system.py
```

**What this does:**
- Tests 5 different health scenarios
- Shows how the system analyzes different user states
- Demonstrates all agents working together
- Displays planning decisions and results

**Expected Output:**
You should see output like:
```
🏃‍♂️ AGENTIC WEIGHTLOSS MOTIVATOR - COMPLETE SYSTEM
======================================================================
🧪 Testing 5 different health scenarios...

🎯 TEST 1: WEIGHT LOSS PROGRESS
📊 Health Data: ...
🎯 Planning Decision:
   Theme: Progress Celebration
   Topic: Health Habits
   Tone: Dana
...
```

### Option 2: Run Individual Tests

Run specific test scenarios:

```bash
python -m pytest tests/test_health_agent.py -v -s
```

This runs all test cases and shows detailed output for each scenario.

### Option 3: Run the Web API Server

Start the FastAPI server:

```bash
python -m uvicorn src.app:app --reload
```

Then open your browser and go to:
- **API Documentation**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/

**Test the API:**
```bash
# Using curl
curl "http://localhost:8000/motivate?user_query=Motivate me to lose weight"

# Or visit in browser
http://localhost:8000/motivate?user_query=Motivate%20me%20to%20lose%20weight
```

### Option 4: Use Python Script Directly

Create a test script `test_my_health.py`:

```python
import asyncio
from src.agents.health_coordinator import HealthCoordinator
from src.tools.apple_health_kit_mock import AppleHealthKitMock

async def main():
    coordinator = HealthCoordinator()
    health_kit_mock = AppleHealthKitMock()
    
    # Generate mock health data
    current_data = health_kit_mock.generate_health_data("user_001", 0, "progress")
    previous_data = health_kit_mock.generate_health_data("user_001", 1, "normal")
    
    # Create health request
    health_data = {
        "user_id": "user_001",
        "current_data": current_data,
        "previous_data": previous_data,
        "goals": ["Lose 10kg in 6 months", "Build healthy habits"],
        "preferences": {"focus": "sustainable habits"},
        "mood": "motivated",
        "energy_level": 7,
        "challenges": ["portion control"],
        "achievements": ["Lost 0.5kg this week"]
    }
    
    # Process request
    result = await coordinator.process_health_request(
        user_id="user_001",
        health_data=health_data,
        custom_instruction="Focus on sustainable weight loss"
    )
    
    # Print results
    print(f"Theme: {result.planning_decision.theme}")
    print(f"Topic: {result.planning_decision.topic}")
    print(f"Tone: {result.planning_decision.tone}")
    print(f"Summary: {result.overall_summary}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python test_my_health.py
```

## 🧪 Running Tests

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test File

```bash
python -m pytest tests/test_health_agent.py -v -s
```

### Run Specific Test Case

```bash
python -m pytest tests/test_health_agent.py::test_weight_loss_results -v -s
```

### Run with Coverage

```bash
pip install pytest-cov
python -m pytest tests/ --cov=src --cov-report=html
```

## 📊 Running Evaluations

The project includes a comprehensive evaluation framework to test system performance.

### Run All Evaluations

```bash
python src/evals/run_evals.py
```

**What this does:**
- Tests 5 different health scenarios
- Evaluates planning decisions, agent success, theme/topic/tone matching
- Generates detailed score reports
- Saves results to `src/eval_results.json`

**Expected Output:**
```
🧪 AGENTIC WEIGHTLOSS MOTIVATOR - EVALUATION SUITE
======================================================================
📈 BATCH EVALUATION SUMMARY
Total Cases: 5
Passed: 5 ✅
Failed: 0 ❌
Pass Rate: 100.00%
Average Score: 91.65%
```

### Run Evaluations with Pytest

```bash
python -m pytest tests/test_evals.py -v -s
```

## 📡 API Documentation

### Start the API Server

```bash
python -m uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

### Available Endpoints

#### 1. Root Endpoint
```
GET http://localhost:8000/
```
Returns basic API information.

#### 2. Motivate Endpoint (GET)
```
GET http://localhost:8000/motivate?user_query=Motivate me to lose weight
```

**Parameters:**
- `user_query` (string): User's motivation request

**Response:**
```json
{
  "response": "Your motivational message here..."
}
```

#### 3. Motivate Endpoint (POST)
```
POST http://localhost:8000/motivate
Content-Type: application/json

{
  "query": "Motivate me to lose weight"
}
```

**Response:**
```json
{
  "response": "Your motivational message here..."
}
```

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Project Structure

```
agentic-weightloss-motivator/
│
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── pytest.ini               # Pytest configuration
├── run_system.py            # Complete system test runner
├── .env                     # Environment variables (create this)
│
├── src/                     # Source code
│   ├── __init__.py
│   ├── app.py              # FastAPI application
│   ├── main.py             # CLI entry point
│   │
│   ├── agents/             # Agent implementations
│   │   ├── health_coordinator.py    # Main coordinator
│   │   ├── planning_agent.py        # Planning agent
│   │   ├── youtube_search_agent.py  # YouTube search
│   │   ├── curated_search_agent.py  # Curated articles
│   │   ├── web_search_agent.py      # Web search
│   │   ├── journaling_agent.py      # Journaling
│   │   └── health_agent.py          # Health motivator
│   │
│   ├── models/             # Data models
│   │   ├── agent_models.py          # Agent request/response models
│   │   ├── health_models.py         # Health data models
│   │   └── health_kit_models.py     # Health Kit data structures
│   │
│   ├── tools/              # Utility tools
│   │   ├── search_web.py           # Web search tool
│   │   ├── search_youtube.py      # YouTube search tool
│   │   ├── planning_tool.py        # Planning logic
│   │   └── apple_health_kit_mock.py # Mock health data
│   │
│   ├── utils/              # Utilities
│   │   └── prompt_builder.py      # Prompt building utilities
│   │
│   ├── config/             # Configuration
│   │   └── settings.py            # Settings and environment
│   │
│   ├── evals/              # Evaluation framework
│   │   ├── eval_datasets.py       # Test case definitions
│   │   ├── eval_scorers.py        # Scoring logic
│   │   ├── eval_runner.py         # Evaluation execution
│   │   └── run_evals.py           # Evaluation script
│   │
│   └── scripts/            # Utility scripts
│       └── run_motivate_agent.py
│
└── tests/                  # Test files
    ├── test_health_agent.py    # Health agent tests
    ├── test_evals.py           # Evaluation tests
    └── conftest.py             # Pytest configuration
```

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution:**
Make sure you're running commands from the project root directory:
```bash
cd agentic-weightloss-motivator
python src/evals/run_evals.py
```

### Issue: "OPENAI_API_KEY is not set"

**Solution:**
1. Create a `.env` file in the project root
2. Add: `OPENAI_API_KEY=your_key_here`
3. Make sure `python-dotenv` is installed: `pip install python-dotenv`

### Issue: "pip install fails"

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Try installing with verbose output
pip install -r requirements.txt -v

# On Windows, you might need Visual C++ Build Tools
```

### Issue: "Virtual environment not activating"

**Windows PowerShell:**
```powershell
# If you get execution policy error
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

### Issue: "YouTube search not working"

**Solution:**
The YouTube search uses `youtube-search-python`. If it fails:
1. Check your internet connection
2. Try updating the package: `pip install --upgrade youtube-search-python`

### Issue: "DuckDuckGo search failing"

**Solution:**
The DuckDuckGo search uses `ddgs`. If it fails:
1. Check your internet connection
2. Try updating: `pip install --upgrade ddgs`

### Issue: "Tests are failing"

**Solution:**
1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Check that your `.env` file has the OpenAI API key
3. Run tests with verbose output: `pytest -v -s`

### Issue: "Port 8000 already in use"

**Solution:**
Use a different port:
```bash
python -m uvicorn src.app:app --reload --port 8001
```

## 🎓 Understanding the System

### Health Score Calculation

The system calculates a health score (0-100) based on:
- **Steps**: 10,000+ steps = +20 points
- **Weight**: Healthy range (60-80kg) = +15 points
- **Sleep**: 7-9 hours = +15 points
- **Calories**: Balanced intake = +10 points

### Theme Selection

Themes are determined by health score:
- **< 30**: Crisis Intervention
- **30-50**: Struggle Support
- **50-70**: Motivation Needed
- **70-85**: Habit Building
- **> 85**: Progress Celebration

### Tone Selection (Indian Historical Context)

- **Sama (सम)**: Gentle, peaceful approach (Buddha's middle path)
  - Used for: Beginners, sensitive situations, crisis
  
- **Dana (दान)**: Generous, supportive approach (wise teacher)
  - Used for: Progress celebration, learning moments
  
- **Dhanda (दंड)**: Firm, disciplinary approach (strict guru)
  - Used for: Lack of progress, need for discipline
  
- **Bedha (भेद)**: Strategic, analytical approach (Chanakya's tactics)
  - Used for: Complex goals, optimization needs

### Topic Selection

Topics are selected based on:
- User goals (keywords: workout, nutrition, habits)
- Health data analysis
- Current health score

## 📝 Example Usage Scenarios

### Scenario 1: Weight Loss Progress

```python
health_data = {
    "user_id": "user_001",
    "current_data": current_data,  # Health Kit data
    "previous_data": previous_data,
    "goals": ["Lose 10kg in 6 months"],
    "mood": "motivated",
    "energy_level": 7,
    "challenges": ["portion control"],
    "achievements": ["Lost 0.5kg this week"]
}

result = await coordinator.process_health_request(
    user_id="user_001",
    health_data=health_data,
    custom_instruction="Focus on sustainable habits"
)
```

**Expected Output:**
- Theme: Progress Celebration
- Topic: Health Habits or Meal Plan
- Tone: Dana (supportive)
- 3-4 agents successful

### Scenario 2: Crisis Intervention

```python
health_data = {
    "user_id": "user_002",
    "current_data": crisis_data,  # Low health score
    "goals": ["Get back on track"],
    "mood": "discouraged",
    "energy_level": 2,
    "challenges": ["motivation", "consistency"]
}
```

**Expected Output:**
- Theme: Crisis Intervention
- Topic: Health Habits
- Tone: Sama (gentle)
- Immediate intervention timing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest tests/`
5. Run evaluations: `python src/evals/run_evals.py`
6. Commit your changes: `git commit -m "Add feature"`
7. Push to branch: `git push origin feature-name`
8. Create a Pull Request

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- OpenAI for the Agents SDK
- DuckDuckGo for search API
- YouTube Search Python library
- All contributors and testers

## 📞 Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the test files for usage examples
3. Check the evaluation results for system performance
4. Open an issue on the repository

---

**Happy Coding! 🚀**

Remember: This is a health motivation tool. Always consult healthcare professionals for medical advice.
