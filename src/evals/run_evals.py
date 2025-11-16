#!/usr/bin/env python3
"""
Run evaluations for the Agentic Weightloss Motivator system
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.evals.eval_runner import EvalRunner

async def main():
    """Main function to run evaluations"""
    
    print("=" * 70)
    print("🧪 AGENTIC WEIGHTLOSS MOTIVATOR - EVALUATION SUITE")
    print("=" * 70)
    print("Testing Health Coordinator and all agents")
    print("=" * 70)
    
    runner = EvalRunner()
    
    # Run all evaluations
    results = await runner.run_all_evals(verbose=True)
    
    # Save results to file
    output_file = Path(__file__).parent.parent / "eval_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Exit with appropriate code
    if results['stats']['pass_rate'] >= 0.7:
        print("\n✅ Evaluation suite passed!")
        sys.exit(0)
    else:
        print("\n❌ Evaluation suite failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

