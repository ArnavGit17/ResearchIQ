"""
services/qa_service.py
PLACEHOLDER – Question Answering Service

Future implementation will include:
- Extractive QA (e.g. via HuggingFace Transformers)
- Generative QA (e.g. via LLM API)
- Context chunking and retrieval
- Confidence scoring
"""


class QAService:
    """Answers natural-language questions over document content."""

    @staticmethod
    def answer(question: str, context: str) -> dict:
        return {
            "status": "not_implemented",
            "message": "QA service is under development.",
            "answer": "",
            "confidence": 0.0,
            "evidence": [],
        }
