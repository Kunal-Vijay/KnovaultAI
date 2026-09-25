from app.utils.rerank import reciprocal_rank_fusion


def test_rrf_promotes_items_in_both_lists():
    semantic = [{"id": 1, "content": "a", "score": 0.9}, {"id": 2, "content": "b", "score": 0.5}]
    keyword = [{"id": 2, "content": "b", "score": 0.8}, {"id": 3, "content": "c", "score": 0.4}]
    fused = reciprocal_rank_fusion([semantic, keyword], k=60)
    assert [item["id"] for item in fused][0] == 2
