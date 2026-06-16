import pytest
from unittest.mock import patch, MagicMock


def test_run_ragas_returns_four_metrics():
    mock_result = {
        "context_precision": 0.80,
        "context_recall": 0.75,
        "faithfulness": 0.85,
        "answer_relevancy": 0.80,
    }
    with patch("app.core.evaluator.evaluate", return_value=mock_result):
        from app.core.evaluator import run_ragas
        result = run_ragas(
            questions=["What is RAG?"],
            answers=["RAG is Retrieval-Augmented Generation."],
            contexts=[["RAG stands for Retrieval-Augmented Generation."]],
        )
        assert "context_precision" in result
        assert "context_recall" in result
        assert "faithfulness" in result
        assert "answer_relevancy" in result


def test_run_ragas_fills_empty_ground_truths():
    mock_result = {
        "context_precision": 0.75,
        "context_recall": 0.70,
        "faithfulness": 0.80,
        "answer_relevancy": 0.78,
    }
    with patch("app.core.evaluator.evaluate", return_value=mock_result):
        from app.core.evaluator import run_ragas
        # ground_truths=None should default to empty strings, not raise
        result = run_ragas(
            questions=["Q1", "Q2"],
            answers=["A1", "A2"],
            contexts=[["context1"], ["context2"]],
            ground_truths=None,
        )
        assert isinstance(result["faithfulness"], float)
