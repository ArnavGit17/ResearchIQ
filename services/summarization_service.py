"""
Phase 9A: Summarization Service
Extractive text summarization by combining TF-IDF, Keyword Density, and Entity Importance.
"""

from typing import List, Dict, Any

class SummarizationService:
    @staticmethod
    def generate_summary(sentences: List[str], keywords: List[Dict[str, Any]], entities: List[Dict[str, Any]], compression_ratio: float = 0.3) -> Dict[str, Any]:
        if not sentences:
            return {"summary_text": "", "ranked_sentences": [], "statistics": {}}

        # Extract raw target words for quick lookup
        keyword_set = {k["keyword"].lower() for k in keywords}
        entity_set = {e["entity"].lower() for e in entities}

        sentence_scores = []
        for i, s in enumerate(sentences):
            words = [w.strip('.,!?;:"\'').lower() for w in s.split()]
            if not words:
                continue

            # Base score
            score = 0.0

            # 1. Keyword density
            kw_matches = sum(1 for w in words if w in keyword_set)
            score += (kw_matches / len(words)) * 2.0

            # 2. Entity importance
            ent_matches = sum(1 for w in words if w in entity_set)
            score += (ent_matches / len(words)) * 3.0

            # 3. Position weighting (lead sentences often more important)
            if i == 0:
                score += 1.0 # First sentence boost

            sentence_scores.append({
                "index": i,
                "sentence": s,
                "score": round(score, 4),
                "reason": f"Matched {kw_matches} keywords and {ent_matches} entities. Position: {i}",
                "confidence": min(0.95, 0.5 + (score * 0.1))
            })

        # Rank and filter top sentences
        target_count = max(1, int(len(sentences) * compression_ratio))
        
        # Sort by score descending to get top sentences
        ranked = sorted(sentence_scores, key=lambda x: x["score"], reverse=True)
        top_sentences_meta = ranked[:target_count]
        
        # Sort back by original index to maintain document flow
        top_sentences_meta.sort(key=lambda x: x["index"])

        summary_text = " ".join([m["sentence"] for m in top_sentences_meta])

        stats = {
            "original_sentences": len(sentences),
            "summary_sentences": len(top_sentences_meta),
            "compression_ratio": round(len(top_sentences_meta) / len(sentences), 2) if sentences else 0
        }

        return {
            "summary_text": summary_text,
            "ranked_sentences": ranked, # Include all for explainability panel
            "statistics": stats
        }
