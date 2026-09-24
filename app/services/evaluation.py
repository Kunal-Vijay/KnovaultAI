import json
import os
import random
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.schemas.evaluation import TestCase, EvaluationDataset, EvaluationResult, EvaluationMetric, BaselineResult, EvaluationReport
from app.schemas.rag import RAGRequest, Citation
from app.services.rag import rag_service
from app.db.session import get_db

logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(self, dataset_path: str, baseline_path: str):
        self.dataset_path = dataset_path
        self.baseline_path = baseline_path

    def load_dataset(self) -> EvaluationDataset:
        with open(self.dataset_path, 'r') as f:
            data = json.load(f)
        return EvaluationDataset(**data)

    def load_baseline(self) -> Optional[BaselineResult]:
        if not os.path.exists(self.baseline_path):
            return None
        with open(self.baseline_path, 'r') as f:
            data = json.load(f)
        return BaselineResult(**data)

    def save_baseline(self, results: List[EvaluationResult]):
        # For simplicity, calculate average metrics across all test cases for baseline
        total_latency = 0
        total_token_usage = 0 # Mocked for now
        total_answer_relevance_score = 0 # Mocked for now
        
        for res in results:
            for metric in res.metrics:
                if metric.name == "latency":
                    total_latency += metric.value
                elif metric.name == "token_usage":
                    total_token_usage += metric.value
                elif metric.name == "answer_relevance_score":
                    total_answer_relevance_score += metric.value

        num_test_cases = len(results)
        baseline_metrics = [
            EvaluationMetric(name="avg_latency_ms", value=(total_latency / num_test_cases) * 1000),
            EvaluationMetric(name="avg_token_usage", value=total_token_usage / num_test_cases),
            EvaluationMetric(name="avg_answer_relevance_score", value=total_answer_relevance_score / num_test_cases)
        ]

        baseline = BaselineResult(metrics=baseline_metrics, timestamp=datetime.utcnow())
        with open(self.baseline_path, 'w') as f:
            json.dump(baseline.model_dump(), f, indent=2, default=str)
        logger.info("Baseline saved successfully.")

    def evaluate_test_case(self, test_case: TestCase) -> EvaluationResult:
        db = next(get_db()) # Get a fresh DB session
        try:
            start_time = time.time()
            rag_request = RAGRequest(
                knowledge_base_id=test_case.knowledge_base_id,
                question=test_case.question
            )
            rag_response = rag_service.get_answer(db, rag_request)
            end_time = time.time()
            latency = end_time - start_time

            # Mock Token Usage and Answer Relevance Score
            token_usage = len(test_case.question.split()) * 2 + len(rag_response.answer.split()) # Simple estimate
            answer_relevance_score = 0.8 + (0.2 * (random.random() - 0.5)) # Mock score around 0.8

            metrics = [
                EvaluationMetric(name="latency", value=latency),
                EvaluationMetric(name="token_usage", value=token_usage),
                EvaluationMetric(name="answer_relevance_score", value=answer_relevance_score)
            ]
            
            citations_simple = [f"{c.source or 'Unknown'} (ID: {c.document_id})" for c in rag_response.citations]

            return EvaluationResult(
                test_case=test_case,
                answer=rag_response.answer,
                citations=citations_simple,
                metrics=metrics
            )
        finally:
            db.close()

    def run_evaluations(self) -> EvaluationReport:
        dataset = self.load_dataset()
        baseline = self.load_baseline()
        current_results: List[EvaluationResult] = []

        logger.info(f"Running evaluations on {len(dataset.test_cases)} test cases.")
        for test_case in dataset.test_cases:
            current_results.append(self.evaluate_test_case(test_case))
            logger.info(f"Completed evaluation for question: {test_case.question[:50]}...")

        report = EvaluationReport(
            current_results=current_results,
            overall_status="PASS"
        )

        if baseline:
            # Simple comparison logic (can be expanded)
            comparison_summary = "Comparison against baseline:\n"
            metric_names = [m.name for m in current_results[0].metrics]
            current_avg_metrics = {}
            for metric_name in metric_names:
                values = [
                    next(m_res for m_res in r.metrics if m_res.name == metric_name).value
                    for r in current_results
                ]
                current_avg_metrics[metric_name] = sum(values) / len(values)
            baseline_avg_metrics = {m.name: m.value for m in baseline.metrics}

            for metric_name, current_avg_value in current_avg_metrics.items():
                if metric_name in baseline_avg_metrics:
                    baseline_value = baseline_avg_metrics[metric_name]
                    diff = (current_avg_value - baseline_value) / baseline_value * 100 if baseline_value else 0
                    comparison_summary += f"- {metric_name}: Current={current_avg_value:.2f}, Baseline={baseline_value:.2f}, Diff={diff:.2f}%\n"
                    # Example threshold: if latency increases by more than 10%, fail
                    if metric_name == "avg_latency_ms" and diff > 10:
                        report.overall_status = "FAIL"
                        comparison_summary += "  FAIL: Average latency increased by more than 10%\n"
                else:
                    comparison_summary += f"- {metric_name}: Current={current_avg_value:.2f} (No baseline for this metric)\n"
            report.comparison_report = comparison_summary
            if report.overall_status == "FAIL":
                logger.error("Evaluation FAILED against baseline thresholds.")
            else:
                logger.info("Evaluation PASSED against baseline.")
        else:
            logger.warning("No baseline found. Skipping comparison.")

        return report

from app.core.config import settings

evaluation_service = EvaluationService(
    dataset_path=os.path.join(os.path.dirname(__file__), settings.EVALUATION_DATASET_PATH),
    baseline_path=os.path.join(os.path.dirname(__file__), settings.EVALUATION_BASELINE_PATH)
)
