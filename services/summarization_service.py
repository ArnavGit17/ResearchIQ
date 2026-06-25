"""
services/summarization_service.py
PLACEHOLDER – Summarization Service

Future implementation will include:
- Extractive summarisation (TextRank, LSA)
- Abstractive summarisation (T5, BART, Pegasus)
- Multi-document summarisation
- Structured abstract generation for research papers
"""


class SummarizationService:
    """Generates concise summaries from research documents."""

    @staticmethod
    def summarise(text: str, max_length: int = 200) -> dict:
        return {
            "status": "not_implemented",
            "message": "Summarization service is under development.",
            "summary": "",
            "word_count": 0,
            "compression_ratio": 0.0,
        }
