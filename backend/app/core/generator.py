import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
_model = None


def get_model():
    global _model
    if _model is None:
        _model = genai.GenerativeModel(settings.GENERATION_MODEL)
    return _model


def generate_answer(query: str, context: str) -> str:
    prompt = (
        "Answer the question based only on the provided context. "
        "If the answer is not in the context, say 'I don't have enough information to answer this.'\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )
    response = get_model().generate_content(prompt)
    return response.text
