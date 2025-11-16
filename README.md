# MotivAI

A comprehensive AI-powered health coaching system that provides personalized health advice, motivation, web articles, YouTube videos, and journaling support using OpenAI GPT models and multi-agent architecture.

## Table of Contents

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

## Overview

The Agentic Weightloss Motivator is an intelligent health assistant that uses a multi-agent system to provide personalized health guidance. The system coordinates multiple specialized agents that work together to:

- Analyze health data and determine appropriate intervention strategies
- Search for relevant health content (articles, videos)
- Create personalized journal entries
- Provide motivation based on user's current health state



## Features

### Core Capabilities
- **Health Data Analysis**: Analyzes steps, calories, weight, sleep, and workout data
- **Intelligent Planning**: Determines themes, topics, and timing based on health scores
- **Multi-Agent Coordination**: Orchestrates 4 parallel agents:
  - **Planning Agent**: Analyzes health data and creates strategic plans
  - **YouTube Search Agent**: Finds relevant fitness and health videos
  - **Curated Search Agent**: Searches for high-quality health articles from trusted sources
  - **Web Search Agent**: Finds general health information and community content
  - **Journaling Agent**: Creates personalized reflective journal entries

### Key Features
- OpenAi Web Search tool
- API-free YouTube search
- Mock Apple Health Kit integration for testing

## Architecture

The system uses a coordinator pattern where:

1. **Health Coordinator** receives health requests
2. **Planning Agent** analyzes data and creates a plan (theme, topic, timing)
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
│   Agent     │   Agent      │   Agent     │   Agent     │
└─────────────┴──────────────┴─────────────┴─────────────┘
    ↓
Coordinated Response
```

## Running Tests
## Agent Evals

This project includes simple Agent Evals you can run locally:

Datasets:
- `datasets/planning.jsonl` (planning quality)
- `datasets/resources.jsonl` (resource relevance)
- `datasets/journaling.jsonl` (journaling usefulness)

Run each eval:
```bash
python scripts/evals/run_planning_eval.py
python scripts/evals/run_resources_eval.py
python scripts/evals/run_journaling_eval.py
```

### Details

- What gets evaluated
  - Planning quality: Does the plan choose the correct topic and explicitly address listed challenges? Is timing appropriate?
  - Resource relevance: Do top web and YouTube results align with the user context and come from reputable sources?
  - Journaling usefulness: Is the entry empathetic, actionable, and aligned with the user’s stated goals/mood?

- Datasets (JSONL)
  - Each line is a JSON object. Example (planning):
    ```json
    {"id":"p1","user_goals":["Lose 5kg in 2 months"],"mood":"motivated","energy_level":7,"challenges":["evening snacking"],"expected_topic":"Meal Plan","expected_success_criteria":["mentions sustainable habits","addresses evening snacking"]}
    ```
  - You can add more lines/cases to expand coverage.

- Running in Windows CMD (recommended)
  - From project root:
    ```cmd
    python scripts\evals\run_planning_eval.py > results_planning.json
    type results_planning.json
    ```
  - Similarly for resources/journaling:
    ```cmd
    python scripts\evals\run_resources_eval.py > results_resources.json
    python scripts\evals\run_journaling_eval.py > results_journaling.json
    ```

- Running in PowerShell
  - ```pwsh
    python scripts/evals/run_planning_eval.py | Out-File -Encoding utf8 results_planning.json
    Get-Content results_planning.json
    ```

- Interpreting results
  - Output fields:
    - `average`: overall score (0..1)
    - `results[]`: per-case scores and notes
  - Typical acceptance targets:
    - Planning average ≥ 0.8
    - Resources average ≥ 0.7
    - Journaling average ≥ 0.7

- Observability in OpenAI Dashboard
  - Requests are tagged with metadata to aid filtering:
    - Planning: `agent=planning_agent`, `purpose=health_planning`
    - Web: `agent=web_search`, `purpose=content_discovery`
    - YouTube: `agent=youtube_search`, `purpose=content_discovery`
    - Curated: `agent=curated_search`, `purpose=curation`
    - Journaling: `agent=journaling`
  - In Logs → Requests, set Date=Today, Model=gpt-4o-mini, and add Metadata filter by `agent=...`.

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

## Project Structure

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
│   └── scripts/            # Utility scripts
│       └── run_motivate_agent.py
│
└── tests/                  # Test files
    ├── test_health_agent.py    # Health agent tests
    └── conftest.py             # Pytest configuration
```

Remember: This is a health motivation tool. Always consult healthcare professionals for medical advice.
