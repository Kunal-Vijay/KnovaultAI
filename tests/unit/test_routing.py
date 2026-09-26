from app.core.llm.routing import RoutingContext, RoutingPolicy


def test_routing_quality_when_no_chunks():
    policy = RoutingPolicy(default_plug="gemma-26b", quality_plug="gemma-31b", fast_plug="gemma-26b")
    sel = policy.select(RoutingContext(question="hello", chunks_retrieved=0, top_retrieval_score=None))
    assert sel.policy == "quality"
    assert sel.plug_name == "gemma-31b"


def test_routing_fast_for_short_question_with_strong_retrieval():
    policy = RoutingPolicy(default_plug="gemma-26b", quality_plug="gemma-31b", fast_plug="gemma-26b")
    sel = policy.select(
        RoutingContext(question="What is RAG?", chunks_retrieved=3, top_retrieval_score=0.9)
    )
    assert sel.policy == "fast"
    assert sel.plug_name == "gemma-26b"
    assert "similarity=0.900" in sel.reason


def test_routing_quality_for_low_semantic_similarity():
    policy = RoutingPolicy(default_plug="gemma-26b", quality_plug="gemma-31b", fast_plug="gemma-26b")
    sel = policy.select(
        RoutingContext(question="What is tokenization?", chunks_retrieved=5, top_retrieval_score=0.033)
    )
    assert sel.policy == "quality"
    assert "semantic similarity" in sel.reason
    assert "0.033" in sel.reason


def test_routing_quality_when_no_semantic_signal():
    policy = RoutingPolicy(default_plug="gemma-26b", quality_plug="gemma-31b", fast_plug="gemma-26b")
    sel = policy.select(
        RoutingContext(question="query", chunks_retrieved=2, top_retrieval_score=None)
    )
    assert sel.policy == "quality"
    assert "keyword-only" in sel.reason.lower() or "No semantic" in sel.reason


def test_routing_default_for_strong_long_question():
    policy = RoutingPolicy(default_plug="gemma-26b", quality_plug="gemma-31b", fast_plug="gemma-26b")
    long_q = (
        "Explain in detail how tokenization affects cost, latency, throughput, and context-window "
        "usage in production LLM systems, including model-specific special tokens and tradeoffs."
    )
    assert len(long_q.strip()) > 120
    sel = policy.select(
        RoutingContext(question=long_q, chunks_retrieved=5, top_retrieval_score=0.55)
    )
    assert sel.policy == "default"
    assert "similarity=0.550" in sel.reason
