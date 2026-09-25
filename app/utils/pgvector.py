def format_pgvector(values: list[float]) -> str:
    """Format embedding for PostgreSQL ::vector cast."""
    return "[" + ",".join(f"{v:.8f}" for v in values) + "]"
