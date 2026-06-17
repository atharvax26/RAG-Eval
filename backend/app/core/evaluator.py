from ragas import evaluate
from ragas.metrics import context_precision, context_recall, faithfulness, answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from datasets import Dataset
from typing import List, Optional
from app.config import settings

METRICS = [context_precision, context_recall, faithfulness, answer_relevancy]


def get_ragas_llm():
    return LangchainLLMWrapper(ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0,
    ))


def get_ragas_embeddings():
    return LangchainEmbeddingsWrapper(GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.GEMINI_API_KEY,
    ))


def run_ragas(
    questions: List[str],
    answers: List[str],
    contexts: List[List[str]],
    ground_truths: Optional[List[str]] = None,
) -> dict:
    """
    contexts must be list[list[str]] — one inner list per question.
    Runs RAGAS entirely on Gemini; no OpenAI key required.
    """
    if ground_truths is None:
        ground_truths = [""] * len(questions)

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })

    result = evaluate(
        dataset,
        metrics=METRICS,
        llm=get_ragas_llm(),
        embeddings=get_ragas_embeddings(),
    )
    return {
        "context_precision": float(result["context_precision"]),
        "context_recall": float(result["context_recall"]),
        "faithfulness": float(result["faithfulness"]),
        "answer_relevancy": float(result["answer_relevancy"]),
    }
