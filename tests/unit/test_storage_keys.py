from app.core.storage import build_document_object_key, sanitize_filename


def test_sanitize_filename_strips_path_components():
    assert sanitize_filename("../../etc/passwd") == "passwd"


def test_sanitize_filename_replaces_unsafe_chars():
    assert sanitize_filename("my report (1).pdf") == "my_report_1_.pdf"


def test_build_document_object_key_includes_kb_id_and_unique_segment():
    key = build_document_object_key(42, "notes.pdf", "abc123")
    assert key == "42/abc123/notes.pdf"


def test_build_document_object_key_unique_per_call():
    a = build_document_object_key(1, "same.txt", "aaa")
    b = build_document_object_key(1, "same.txt", "bbb")
    assert a != b
