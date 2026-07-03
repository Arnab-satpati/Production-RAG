from rag.utils.text import generate_id, stable_hash, truncate_text


def test_truncate_text_short():
    assert truncate_text("hello", max_length=10) == "hello"


def test_truncate_text_long():
    result = truncate_text("A" * 100, max_length=20)
    assert len(result) == 20
    assert result.endswith("...")


def test_generate_id():
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2
    assert len(id1) == 12


def test_generate_id_with_prefix():
    result = generate_id("doc")
    assert result.startswith("doc:")


def test_stable_hash():
    h1 = stable_hash("hello")
    h2 = stable_hash("hello")
    h3 = stable_hash("world")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 16
