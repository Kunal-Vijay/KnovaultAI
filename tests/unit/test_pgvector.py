from app.utils.pgvector import format_pgvector


def test_format_pgvector():
    vec = format_pgvector([0.1, 0.2, 0.3])
    assert vec.startswith("[")
    assert vec.endswith("]")
    assert "0.10000000" in vec
