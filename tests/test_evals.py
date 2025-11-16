# tests/test_evals.py

import pytest
import asyncio
from src.evals.eval_runner import EvalRunner
from src.evals.eval_datasets import HealthEvalDataset
from src.evals.eval_scorers import HealthEvalScorer

@pytest.fixture
def eval_runner():
    """Evaluation runner fixture"""
    return EvalRunner()

@pytest.fixture
def eval_dataset():
    """Evaluation dataset fixture"""
    return HealthEvalDataset()

@pytest.fixture
def eval_scorer():
    """Evaluation scorer fixture"""
    return HealthEvalScorer()

@pytest.mark.asyncio
async def test_eval_dataset_creation(eval_dataset):
    """Test that evaluation dataset is created correctly"""
    cases = eval_dataset.get_all_cases()
    assert len(cases) > 0, "Dataset should have at least one test case"
    
    # Check that all cases have required fields
    for case in cases:
        assert case.case_id, "Case should have an ID"
        assert case.name, "Case should have a name"
        assert case.health_data, "Case should have health data"
        assert case.expected_themes, "Case should have expected themes"
        assert case.expected_topics, "Case should have expected topics"
        assert case.expected_tones, "Case should have expected tones"

@pytest.mark.asyncio
async def test_single_eval_case(eval_runner):
    """Test evaluating a single case"""
    dataset = eval_runner.dataset
    cases = dataset.get_all_cases()
    
    if cases:
        # Run first case
        score = await eval_runner.run_single_eval(cases[0], verbose=False)
        
        assert score is not None, "Score should be returned"
        assert score.case_id == cases[0].case_id, "Score should match case ID"
        assert 0 <= score.overall_score <= 1, "Overall score should be between 0 and 1"
        assert isinstance(score.passed, bool), "Passed should be boolean"

@pytest.mark.asyncio
async def test_batch_eval(eval_runner):
    """Test batch evaluation"""
    scores = await eval_runner.run_batch_eval(verbose=False)
    
    assert len(scores) > 0, "Should return scores for all cases"
    
    # Check score structure
    for score in scores:
        assert hasattr(score, 'case_id'), "Score should have case_id"
        assert hasattr(score, 'overall_score'), "Score should have overall_score"
        assert hasattr(score, 'passed'), "Score should have passed"
        assert 0 <= score.overall_score <= 1, "Score should be between 0 and 1"

@pytest.mark.asyncio
async def test_eval_scorer(eval_scorer, eval_dataset):
    """Test evaluation scorer"""
    from src.agents.health_coordinator import HealthCoordinator
    
    coordinator = HealthCoordinator()
    case = eval_dataset.get_all_cases()[0]
    
    # Run coordinator
    response = await coordinator.process_health_request(
        user_id=case.user_id,
        health_data=case.health_data,
        custom_instruction=case.custom_instruction
    )
    
    # Score the response
    score = eval_scorer.score_response(case, response)
    
    assert score is not None, "Score should be returned"
    assert 0 <= score.overall_score <= 1, "Overall score should be between 0 and 1"
    assert isinstance(score.passed, bool), "Passed should be boolean"
    assert isinstance(score.errors, list), "Errors should be a list"

@pytest.mark.asyncio
async def test_all_evals_complete(eval_runner):
    """Test that all evaluations complete without errors"""
    results = await eval_runner.run_all_evals(verbose=False)
    
    assert 'stats' in results, "Results should have stats"
    assert 'scores' in results, "Results should have scores"
    assert results['stats']['total_cases'] > 0, "Should have evaluated cases"
    
    # Check stats structure
    stats = results['stats']
    assert 'pass_rate' in stats, "Stats should have pass_rate"
    assert 'average_score' in stats, "Stats should have average_score"
    assert 0 <= stats['pass_rate'] <= 1, "Pass rate should be between 0 and 1"
    assert 0 <= stats['average_score'] <= 1, "Average score should be between 0 and 1"

@pytest.mark.asyncio
async def test_eval_case_by_id(eval_dataset):
    """Test getting evaluation case by ID"""
    cases = eval_dataset.get_all_cases()
    
    if cases:
        case_id = cases[0].case_id
        case = eval_dataset.get_case_by_id(case_id)
        
        assert case is not None, "Should return a case"
        assert case.case_id == case_id, "Should return the correct case"
        
        # Test invalid ID
        with pytest.raises(ValueError):
            eval_dataset.get_case_by_id("invalid_case_id")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

