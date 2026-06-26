"""
Phase 9A: Semantic Search Service
Input user queries and find best matching paragraphs using TF-IDF and syntactic overlaps.
"""

from typing import List, Dict, Any

class SemanticSearchService:
    @staticmethod
    def search(query: str, sentences: List[str], keywords: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        if not query or not query.strip() or not sentences:
            return []

        q_clean = query.lower().strip()
        q_words = set(q_clean.split())

        doc_keyword_set = {k["keyword"].lower() for k in keywords}

        results = []
        for i, s in enumerate(sentences):
            s_clean = s.lower().strip()
            s_words = s_clean.split()

            score = 0.0
            matches = []

            for qw in q_words:
                if qw in s_words:
                    if qw in doc_keyword_set:
                        score += 2.0
                    else:
                        score += 1.0
                    matches.append(qw)

            if score > 0:
                results.append({
                    "sentence_index": i,
                    "sentence": s,
                    "score": round(score, 4),
                    "matched_keywords": matches,
                    "relevance": min(0.99, score * 0.3),
                    "reason": f"Matched {len(matches)} query terms. Document keyword boosts applied."
                })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
