from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class TestCase(BaseModel):
    question: str
    knowledge_base_id: int
    expected_sources: List[str] # e.g., list of document filenames or IDs
    expected_answer_keywords: List[str] # Keywords expected in the answer

class EvaluationDataset(BaseModel):
    test_cases: List[TestCase]

class EvaluationMetric(BaseModel):
    name: str
    value: Any

class EvaluationResult(BaseModel):
    test_case: TestCase
    answer: str
    citations: List[str] # Simplified citations for evaluation
    metrics: List[EvaluationMetric]
    timestamp: datetime = datetime.utcnow()

class BaselineResult(BaseModel):
    metrics: List[EvaluationMetric] # Aggregate metrics or per-test-case metrics
    timestamp: datetime

class EvaluationReport(BaseModel):
    current_results: List[EvaluationResult]
    baseline: Optional[BaselineResult] = None
    comparison_report: Optional[str] = None # Textual comparison summary
    overall_status: str # e.g., "PASS", "FAIL"
