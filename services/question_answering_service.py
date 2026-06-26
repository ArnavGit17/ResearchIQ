"""
Phase 9A: Question Answering Service
Implements heuristic document QA without opaque LLMs.
Uses Keyword matching and Semantic Similarity (TF-IDF/WordNet context) to find the best matching sentence.
"""

from typing import List, Dict, Any
import re

class QAService:
    @staticmethod
    def answer_question(question: str, sentences: List[str], keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not question or not question.strip():
            return {"answer": "Please ask a valid question.", "confidence": 0.0}
        
        if not sentences:
            return {"answer": "Document is empty.", "confidence": 0.0}

        # 1. Clean question
        q_clean = question.lower().strip('?.,!')
        q_words = set(q_clean.split())
        
        # Remove stop words heuristically for QA matching
        stop_words = {"who", "what", "where", "when", "why", "how", "is", "are", "do", "does", "did", "the", "a", "an", "in", "on", "at", "to", "for", "of"}
        q_keywords = {w for w in q_words if w not in stop_words}
        
        # If question is too simple, use the whole question words
        if not q_keywords:
            q_keywords = q_words

        # Boost words that are document keywords
        doc_keyword_set = {k["keyword"].lower() for k in keywords}

        best_score = -1.0
        best_sentence = ""
        best_reason = ""

        # 2. Score sentences
        for i, s in enumerate(sentences):
            s_clean = s.lower().strip('?.,!')
            s_words = s_clean.split()
            
            score = 0.0
            matches = []

            for qw in q_keywords:
                if qw in s_words:
                    if qw in doc_keyword_set:
                        score += 2.0 # High value for matching a document keyword
                    else:
                        score += 1.0 # Standard match
                    matches.append(qw)

            # Normalise score slightly by sentence length (penalize overly long sentences)
            # but don't penalize too much.
            if len(s_words) > 0:
                normalized_score = score / (len(s_words) ** 0.3)
            else:
                normalized_score = 0

            if normalized_score > best_score:
                best_score = normalized_score
                best_sentence = s
                best_reason = f"Matched question keywords: {', '.join(matches)}. Raw Score: {score}. (Position: {i})"

        # 3. Format Answer
        confidence = min(0.99, best_score * 0.25) # Scale heuristic
        
        if confidence < 0.2:
            return {
                "question": question,
                "answer": "I could not find a highly confident answer in the document.",
                "matched_sentence": "",
                "confidence": round(confidence, 2),
                "reason": "Keyword matching scores were too low across all sentences.",
                "evidence": []
            }

        return {
            "question": question,
            "answer": best_sentence, # For extractive QA, the sentence is the answer
            "matched_sentence": best_sentence,
            "confidence": round(confidence, 2),
            "reason": best_reason,
            "evidence": [best_sentence] # In a more complex system, this could include surrounding context
        }
