# Evaluations (Evals)

This directory contains the evaluation framework for the Agentic Weightloss Motivator system.

## Overview

The evals framework provides:
- **Test datasets** - Predefined health scenarios for testing
- **Scoring system** - Automated evaluation of agent responses
- **Batch evaluation** - Run multiple test cases and generate reports
- **Integration** - Easy integration with pytest

## Structure

```
src/evals/
├── __init__.py          # Exports
├── eval_datasets.py     # Test case definitions
├── eval_scorers.py      # Scoring logic
├── eval_runner.py       # Evaluation execution
└── run_evals.py         # Standalone evaluation script
```

## Usage

### Run All Evaluations

```bash
# Using the standalone script
python src/evals/run_evals.py

# Using pytest
pytest tests/test_evals.py -v
```

### Run Single Evaluation Case

```python
from src.evals.eval_runner import EvalRunner

runner = EvalRunner()
case = runner.dataset.get_case_by_id("weight_loss_progress")
score = await runner.run_single_eval(case)
```

### Run Custom Batch

```python
from src.evals.eval_runner import EvalRunner

runner = EvalRunner()
scores = await runner.run_batch_eval(
    case_ids=["weight_loss_progress", "crisis_intervention"]
)
```

## Evaluation Metrics

Each evaluation scores:
1. **Planning Score** (30%) - Quality of planning decision
2. **Agents Success Score** (30%) - How many agents succeeded
3. **Theme Match** (15%) - Matches expected theme
4. **Topic Match** (15%) - Matches expected topic
5. **Tone Match** (10%) - Matches expected tone

**Pass Threshold**: 70% overall score

## Test Cases

The default dataset includes:
1. **Weight Loss Progress** - User making progress
2. **Crisis Intervention** - User in crisis needing support
3. **Fitness Enthusiast** - High-performing user
4. **Struggling Beginner** - Beginner needing help
5. **Muscle Building** - Strength-focused user

## Adding Custom Test Cases

```python
from src.evals.eval_datasets import EvalCase

custom_case = EvalCase(
    case_id="my_custom_case",
    name="My Custom Scenario",
    user_id="user_custom",
    health_data={...},
    custom_instruction="...",
    expected_themes=["Progress Celebration"],
    expected_topics=["Workout Plan"],
    expected_tones=["Dana"],
    expected_min_agents_successful=2,
    description="My custom test case"
)

runner.dataset.add_case(custom_case)
```

## Output

Evaluation results are saved to `eval_results.json` with:
- Overall statistics
- Individual case scores
- Detailed breakdowns
- Error messages

## Integration with OpenAI Agent Kit

This evals framework follows OpenAI's evaluation best practices:
- Structured test cases
- Automated scoring
- Batch evaluation
- Statistical analysis
- Error tracking

The framework is designed to be compatible with OpenAI's Agent Kit evaluation patterns.

