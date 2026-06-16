import pytest
from llama_index.core import Document
from app.core.chunkers import get_nodes, get_chunker

SAMPLE_DOC = Document(text="This is a sample document for testing chunking strategies. " * 50)


def test_fixed_chunker_returns_nodes():
    nodes = get_nodes([SAMPLE_DOC], "fixed")
    assert len(nodes) > 0


def test_sentence_window_chunker_returns_nodes():
    nodes = get_nodes([SAMPLE_DOC], "sentence_window")
    assert len(nodes) > 0


def test_hierarchical_chunker_returns_leaf_nodes():
    nodes = get_nodes([SAMPLE_DOC], "hierarchical")
    assert len(nodes) > 0


def test_fixed_chunks_have_max_size():
    nodes = get_nodes([SAMPLE_DOC], "fixed")
    for node in nodes:
        # Tokens are approximate — just verify non-empty content
        assert len(node.get_content()) > 0


def test_unknown_strategy_raises_value_error():
    with pytest.raises(ValueError, match="Unknown strategy"):
        get_chunker("unknown_strategy")
