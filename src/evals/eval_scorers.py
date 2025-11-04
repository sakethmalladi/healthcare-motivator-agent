# src/evals/eval_scorers.py

from typing import Dict, Any, List
from dataclasses import dataclass
from src.models.agent_models import CoordinatedResponse, PlanningDecision
from src.evals.eval_datasets import EvalCase

@dataclass
class EvalScore:
    """Evaluation score for a single test case"""
    case_id: str
    case_name: str
    passed: bool
    overall_score: float  # 0-1
    planning_score: float
    agents_success_score: float
    tone_match_score: float
    topic_match_score: float
    theme_match_score: float
    details: Dict[str, Any]
    errors: List[str]

class HealthEvalScorer:
    """Scorer for evaluating health coordinator responses"""
    
    def score_response(self, eval_case: EvalCase, response: CoordinatedResponse) -> EvalScore:
        """Score a coordinated response against expected values"""
        
        errors = []
        scores = {}
        
        # 1. Planning Decision Scoring
        planning_score = self._score_planning_decision(
            eval_case, 
            response.planning_decision,
            errors
        )
        scores['planning'] = planning_score
        
        # 2. Agents Success Scoring
        agents_success_score = self._score_agents_success(
            eval_case,
            response,
            errors
        )
        scores['agents_success'] = agents_success_score
        
        # 3. Theme Match Scoring
        theme_score = self._score_theme_match(
            eval_case.expected_themes,
            response.planning_decision.theme,
            errors
        )
        scores['theme'] = theme_score
        
        # 4. Topic Match Scoring
        topic_score = self._score_topic_match(
            eval_case.expected_topics,
            response.planning_decision.topic,
            errors
        )
        scores['topic'] = topic_score
        
        # 5. Tone Match Scoring
        tone_score = self._score_tone_match(
            eval_case.expected_tones,
            response.planning_decision.tone,
            errors
        )
        scores['tone'] = tone_score
        
        # Calculate overall score (weighted average)
        overall_score = (
            planning_score * 0.3 +
            agents_success_score * 0.3 +
            theme_score * 0.15 +
            topic_score * 0.15 +
            tone_score * 0.1
        )
        
        # Determine if passed (threshold: 0.7)
        passed = overall_score >= 0.7
        
        return EvalScore(
            case_id=eval_case.case_id,
            case_name=eval_case.name,
            passed=passed,
            overall_score=overall_score,
            planning_score=planning_score,
            agents_success_score=agents_success_score,
            tone_match_score=tone_score,
            topic_match_score=topic_score,
            theme_match_score=theme_score,
            details={
                "planning_decision": {
                    "theme": response.planning_decision.theme,
                    "topic": response.planning_decision.topic,
                    "tone": response.planning_decision.tone,
                    "confidence": response.planning_decision.confidence_score
                },
                "agents_successful": response.metadata.get('agents_successful', 0),
                "total_agents": response.metadata.get('total_agents', 4),
                "scores": scores
            },
            errors=errors
        )
    
    def _score_planning_decision(self, eval_case: EvalCase, 
                                 decision: PlanningDecision, 
                                 errors: List[str]) -> float:
        """Score the planning decision quality"""
        score = 1.0
        
        # Check if decision exists
        if not decision:
            errors.append("No planning decision returned")
            return 0.0
        
        # Check confidence score
        if decision.confidence_score < 0.5:
            score -= 0.2
            errors.append(f"Low confidence score: {decision.confidence_score}")
        
        # Check reasoning quality
        if not decision.reasoning or len(decision.reasoning) < 20:
            score -= 0.2
            errors.append("Planning reasoning is too short or missing")
        
        # Check timing
        if not decision.timing:
            score -= 0.1
            errors.append("Timing information missing")
        
        return max(0.0, score)
    
    def _score_agents_success(self, eval_case: EvalCase, 
                             response: CoordinatedResponse,
                             errors: List[str]) -> float:
        """Score how many agents succeeded"""
        agents_successful = response.metadata.get('agents_successful', 0)
        total_agents = response.metadata.get('total_agents', 4)
        
        expected_min = eval_case.expected_min_agents_successful
        
        if agents_successful < expected_min:
            errors.append(
                f"Only {agents_successful}/{total_agents} agents succeeded, "
                f"expected at least {expected_min}"
            )
        
        # Score based on ratio (normalized to 0-1)
        if total_agents == 0:
            return 0.0
        
        ratio = agents_successful / total_agents
        
        # Bonus if exceeds minimum
        if agents_successful >= expected_min:
            return min(1.0, ratio * 1.1)  # Slight bonus
        else:
            return ratio
    
    def _score_theme_match(self, expected_themes: List[str], 
                          actual_theme: str, 
                          errors: List[str]) -> float:
        """Score if theme matches expected themes"""
        if actual_theme in expected_themes:
            return 1.0
        
        # Partial match scoring
        actual_lower = actual_theme.lower()
        for expected in expected_themes:
            if expected.lower() in actual_lower or actual_lower in expected.lower():
                return 0.7
        
        errors.append(
            f"Theme '{actual_theme}' not in expected themes: {expected_themes}"
        )
        return 0.3  # Partial credit for having a theme
    
    def _score_topic_match(self, expected_topics: List[str], 
                          actual_topic: str,
                          errors: List[str]) -> float:
        """Score if topic matches expected topics"""
        if actual_topic in expected_topics:
            return 1.0
        
        # Partial match scoring
        actual_lower = actual_topic.lower()
        for expected in expected_topics:
            if expected.lower() in actual_lower or actual_lower in expected.lower():
                return 0.7
        
        errors.append(
            f"Topic '{actual_topic}' not in expected topics: {expected_topics}"
        )
        return 0.3  # Partial credit
    
    def _score_tone_match(self, expected_tones: List[str], 
                         actual_tone: str,
                         errors: List[str]) -> float:
        """Score if tone matches expected tones"""
        if actual_tone in expected_tones:
            return 1.0
        
        errors.append(
            f"Tone '{actual_tone}' not in expected tones: {expected_tones}"
        )
        return 0.5  # Partial credit for having a tone
    
    def calculate_batch_stats(self, scores: List[EvalScore]) -> Dict[str, Any]:
        """Calculate statistics for a batch of evaluations"""
        if not scores:
            return {
                "total_cases": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "average_score": 0.0,
                "score_breakdown": {}
            }
        
        passed = sum(1 for s in scores if s.passed)
        failed = len(scores) - passed
        average_score = sum(s.overall_score for s in scores) / len(scores)
        
        # Calculate average scores by component
        avg_planning = sum(s.planning_score for s in scores) / len(scores)
        avg_agents = sum(s.agents_success_score for s in scores) / len(scores)
        avg_theme = sum(s.theme_match_score for s in scores) / len(scores)
        avg_topic = sum(s.topic_match_score for s in scores) / len(scores)
        avg_tone = sum(s.tone_match_score for s in scores) / len(scores)
        
        return {
            "total_cases": len(scores),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(scores),
            "average_score": average_score,
            "score_breakdown": {
                "planning": avg_planning,
                "agents_success": avg_agents,
                "theme_match": avg_theme,
                "topic_match": avg_topic,
                "tone_match": avg_tone
            }
        }

