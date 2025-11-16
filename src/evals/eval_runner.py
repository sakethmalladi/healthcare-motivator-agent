# src/evals/eval_runner.py

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.agents.health_coordinator import HealthCoordinator
from src.evals.eval_datasets import HealthEvalDataset, EvalCase
from src.evals.eval_scorers import HealthEvalScorer, EvalScore
from src.models.agent_models import CoordinatedResponse

class EvalRunner:
    """Runner for evaluating health coordinator and agents"""
    
    def __init__(self):
        self.coordinator = HealthCoordinator()
        self.dataset = HealthEvalDataset()
        self.scorer = HealthEvalScorer()
    
    async def run_single_eval(self, case: EvalCase, verbose: bool = True) -> EvalScore:
        """Run evaluation for a single test case"""
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"🧪 EVALUATING: {case.name}")
            print(f"{'='*70}")
            print(f"Case ID: {case.case_id}")
            print(f"Description: {case.description}")
            print(f"Expected Theme: {case.expected_themes}")
            print(f"Expected Topic: {case.expected_topics}")
            print(f"Expected Tone: {case.expected_tones}")
            print(f"Min Agents Successful: {case.expected_min_agents_successful}")
        
        try:
            # Run the coordinator
            response = await self.coordinator.process_health_request(
                user_id=case.user_id,
                health_data=case.health_data,
                custom_instruction=case.custom_instruction
            )
            
            # Score the response
            score = self.scorer.score_response(case, response)
            
            if verbose:
                self._print_score_results(score, response)
            
            return score
            
        except Exception as e:
            if verbose:
                print(f"❌ ERROR: {str(e)}")
            
            # Return failure score
            return EvalScore(
                case_id=case.case_id,
                case_name=case.name,
                passed=False,
                overall_score=0.0,
                planning_score=0.0,
                agents_success_score=0.0,
                tone_match_score=0.0,
                topic_match_score=0.0,
                theme_match_score=0.0,
                details={"error": str(e)},
                errors=[f"Exception: {str(e)}"]
            )
    
    async def run_batch_eval(self, case_ids: Optional[List[str]] = None, 
                            verbose: bool = True) -> List[EvalScore]:
        """Run evaluation for multiple test cases"""
        
        if case_ids:
            cases = [self.dataset.get_case_by_id(cid) for cid in case_ids]
        else:
            cases = self.dataset.get_all_cases()
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"🚀 RUNNING BATCH EVALUATION")
            print(f"{'='*70}")
            print(f"Total Cases: {len(cases)}")
            print(f"{'='*70}\n")
        
        scores = []
        
        for i, case in enumerate(cases, 1):
            if verbose:
                print(f"\n[{i}/{len(cases)}] Processing case: {case.case_id}")
            
            score = await self.run_single_eval(case, verbose=verbose)
            scores.append(score)
            
            # Small delay between cases to avoid rate limiting
            if i < len(cases):
                await asyncio.sleep(0.5)
        
        return scores
    
    async def run_all_evals(self, verbose: bool = True) -> Dict[str, Any]:
        """Run all evaluations and return summary"""
        
        scores = await self.run_batch_eval(verbose=verbose)
        stats = self.scorer.calculate_batch_stats(scores)
        
        if verbose:
            self._print_batch_summary(stats, scores)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "scores": [self._score_to_dict(s) for s in scores]
        }
    
    def _print_score_results(self, score: EvalScore, response: CoordinatedResponse):
        """Print detailed score results"""
        print(f"\n📊 EVALUATION RESULTS:")
        print(f"   Status: {'✅ PASSED' if score.passed else '❌ FAILED'}")
        print(f"   Overall Score: {score.overall_score:.2%}")
        print(f"\n   Component Scores:")
        print(f"   - Planning: {score.planning_score:.2%}")
        print(f"   - Agents Success: {score.agents_success_score:.2%}")
        print(f"   - Theme Match: {score.theme_match_score:.2%}")
        print(f"   - Topic Match: {score.topic_match_score:.2%}")
        print(f"   - Tone Match: {score.tone_match_score:.2%}")
        
        print(f"\n   Actual Decision:")
        print(f"   - Theme: {response.planning_decision.theme}")
        print(f"   - Topic: {response.planning_decision.topic}")
        print(f"   - Tone: {response.planning_decision.tone}")
        print(f"   - Confidence: {response.planning_decision.confidence_score:.2%}")
        print(f"   - Agents Successful: {response.metadata.get('agents_successful', 0)}/4")
        
        if score.errors:
            print(f"\n   ⚠️  Issues Found:")
            for error in score.errors:
                print(f"   - {error}")
    
    def _print_batch_summary(self, stats: Dict[str, Any], scores: List[EvalScore]):
        """Print batch evaluation summary"""
        print(f"\n{'='*70}")
        print(f"📈 BATCH EVALUATION SUMMARY")
        print(f"{'='*70}")
        print(f"Total Cases: {stats['total_cases']}")
        print(f"Passed: {stats['passed']} ✅")
        print(f"Failed: {stats['failed']} ❌")
        print(f"Pass Rate: {stats['pass_rate']:.2%}")
        print(f"Average Score: {stats['average_score']:.2%}")
        
        print(f"\n📊 Score Breakdown:")
        breakdown = stats['score_breakdown']
        print(f"   Planning: {breakdown['planning']:.2%}")
        print(f"   Agents Success: {breakdown['agents_success']:.2%}")
        print(f"   Theme Match: {breakdown['theme_match']:.2%}")
        print(f"   Topic Match: {breakdown['topic_match']:.2%}")
        print(f"   Tone Match: {breakdown['tone_match']:.2%}")
        
        print(f"\n📋 Individual Results:")
        for score in scores:
            status = "✅" if score.passed else "❌"
            print(f"   {status} {score.case_name}: {score.overall_score:.2%}")
            if not score.passed and score.errors:
                for error in score.errors[:2]:  # Show first 2 errors
                    print(f"      - {error}")
        
        print(f"\n{'='*70}\n")
    
    def _score_to_dict(self, score: EvalScore) -> Dict[str, Any]:
        """Convert EvalScore to dictionary"""
        return {
            "case_id": score.case_id,
            "case_name": score.case_name,
            "passed": score.passed,
            "overall_score": score.overall_score,
            "planning_score": score.planning_score,
            "agents_success_score": score.agents_success_score,
            "tone_match_score": score.tone_match_score,
            "topic_match_score": score.topic_match_score,
            "theme_match_score": score.theme_match_score,
            "details": score.details,
            "errors": score.errors
        }

