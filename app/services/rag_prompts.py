from typing import List

from app.schemas.search import SearchResultItem


def format_retrieved_context(search_results: List[SearchResultItem]) -> str:
    if not search_results:
        return ""

    blocks: list[str] = []
    for index, item in enumerate(search_results, start=1):
        source = item.chunk.source or f"document-{item.chunk.document_id}"
        blocks.append(
            f"[Chunk {index} | source={source} | score={item.score:.3f}]\n"
            f"{item.chunk.content}"
        )
    return "\n\n".join(blocks)


def build_rag_prompt(question: str, search_results: List[SearchResultItem]) -> str:
    context = format_retrieved_context(search_results)
    if not context:
        return (
            "Answer the question using general knowledge. "
            "No retrieved document context was available.\n\n"
            f"Question: {question}"
        )

    return (
        "Use the retrieved context to answer the question. "
        "If the context is insufficient, say what is missing. "
        "Do not invent facts that are not supported by the context. "
        "Reference sources by the chunk labels when helpful.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )
