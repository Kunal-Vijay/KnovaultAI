import asyncio
import os
import sys
import json
from datetime import datetime

# Add the app directory to the path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.evaluation import evaluation_service
from app.schemas.evaluation import EvaluationReport

async def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "run"

    if action == "run":
        print("Running LLM regression evaluations...")
        report: EvaluationReport = evaluation_service.run_evaluations()
        print("\n--- Evaluation Report ---")
        print(f"Overall Status: {report.overall_status}")
        if report.comparison_report:
            print(report.comparison_report)
        else:
            print("No baseline found for comparison.")

        print("\nIndividual Test Results:")
        for result in report.current_results:
            print(f"  Question: {result.test_case.question[:70]}...")
            print(f"    Answer: {result.answer[:100]}...")
            print(f"    Metrics: {json.dumps([m.model_dump() for m in result.metrics], indent=2, default=str)}")
            print(f"    Citations: {result.citations}")
            print("-" * 20)

    elif action == "save_baseline":
        print("Running evaluations to save new baseline...")
        report: EvaluationReport = evaluation_service.run_evaluations()
        evaluation_service.save_baseline(report.current_results)
        print("Baseline saved based on current evaluation results.")

    else:
        print(f"Unknown action: {action}")
        print("Usage: python run_evals.py [run|save_baseline]")

if __name__ == "__main__":
    asyncio.run(main())
