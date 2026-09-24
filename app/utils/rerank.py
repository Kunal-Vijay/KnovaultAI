from typing import List, Dict, Any

def reciprocal_rank_fusion(ranked_lists: List[List[Dict[str, Any]]], k: int = 60) -> List[Dict[str, Any]]:
    """
    Applies Reciprocal Rank Fusion (RRF) to combine multiple ranked lists.

    Args:
        ranked_lists: A list of ranked lists. Each inner list contains dictionaries
                      representing search results, where each dictionary must have a unique 'id'.
        k: A constant that determines the contribution of lower ranks. Default is 60.

    Returns:
        A single re-ranked list of unique results, sorted by their RRF score.
    """
    fused_scores: Dict[Any, float] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list):
            item_id = item['id'] # Assuming each item has a unique 'id'
            # Check if 'score' exists, otherwise default to a high score for RRF
            # This is primarily for semantic search results where score is distance (lower is better)
            # and keyword search where there might not be a score or it's a count.
            # For RRF, we care about rank, so actual scores are less important here.
            score = item.get('score', 0.0) # Placeholder, not directly used in RRF score calculation

            fused_scores.setdefault(item_id, 0.0)
            fused_scores[item_id] += 1 / (k + rank + 1)

    # Sort items by their fused RRF score in descending order
    reranked_results = sorted(fused_scores.items(), key=lambda item: item[1], reverse=True)

    # Reconstruct the list of result items, maintaining original item data
    # This requires looking up the original item data. For simplicity here,
    # we'll just return the IDs and their fused scores, but in a real system,
    # you'd map back to the full chunk objects.
    # For now, let's create a mapping of item_id to the full item object
    all_items: Dict[Any, Dict[str, Any]] = {}
    for ranked_list in ranked_lists:
        for item in ranked_list:
            all_items[item['id']] = item

    final_ranked_list = []
    for item_id, score in reranked_results:
        original_item = all_items[item_id].copy()
        original_item['fused_score'] = score # Add the fused score for inspection if needed
        final_ranked_list.append(original_item)

    return final_ranked_list

