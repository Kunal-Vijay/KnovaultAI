"""Normalize extracted text before Postgres persistence."""


def sanitize_text_for_postgres(text: str) -> str:
    """Remove NUL bytes; PostgreSQL text columns reject \\x00."""
    return text.replace("\x00", "")
