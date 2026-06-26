"""
Phase 9A: Keyword Service
Extracts and ranks keywords using TF-IDF and POS tagging.
"""

from typing import List, Dict, Any

class KeywordService:
    @staticmethod
    def extract_keywords(tf_idf_data: Dict[str, float], pos_tags: List[Any], top_n: int = 20) -> List[Dict[str, Any]]:
        """
        Combines TF-IDF scores with POS tagging to extract top domain keywords.
        Prioritises Nouns and Adjectives.
        """
        if not tf_idf_data:
            return []

        # Build a mapping of lowercased word to POS tags
        word_pos_map = {}
        # pos_tags format: List of dicts or List of tuples
        for p in pos_tags:
            word = ""
            tag = ""
            if isinstance(p, dict) and "word" in p and "tag" in p:
                word = p["word"]
                tag = p["tag"]
            elif isinstance(p, (list, tuple)) and len(p) == 2:
                word = p[0]
                tag = p[1]
            
            if word and tag:
                wl = word.lower()
                if wl not in word_pos_map:
                    word_pos_map[wl] = []
                word_pos_map[wl].append(tag)

        # Rank keywords
        keywords = []
        for word, score in tf_idf_data.items():
            wl = word.lower()
            tags = word_pos_map.get(wl, [])
            
            # Get the most common tag for this word
            primary_tag = "UNKNOWN"
            if tags:
                primary_tag = max(set(tags), key=tags.count)

            # Heuristic: Boost score slightly if it's a Noun (NN) or Adjective (JJ)
            final_score = score
            if primary_tag.startswith("NN"):
                final_score *= 1.2
            elif primary_tag.startswith("JJ"):
                final_score *= 1.1

            keywords.append({
                "keyword": word,
                "score": round(final_score, 4),
                "part_of_speech": primary_tag,
                "reason": f"Selected via TF-IDF ({score:.4f}) and POS syntactic weight ({primary_tag}).",
                "confidence": min(0.95, 0.5 + (final_score * 0.1)) # Naive confidence metric
            })

        # Sort and return top_n
        keywords.sort(key=lambda x: x["score"], reverse=True)
        return keywords[:top_n]
