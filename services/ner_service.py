"""
Phase 9A: NER Service
Extracts named entities using spaCy en_core_web_sm.
"""

import spacy
from typing import List, Dict, Any

class NERService:
    # Load spaCy model only when needed to save memory
    _nlp = None

    @classmethod
    def get_nlp(cls):
        if cls._nlp is None:
            try:
                cls._nlp = spacy.load("en_core_web_sm")
            except OSError:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
                cls._nlp = spacy.load("en_core_web_sm")
        return cls._nlp

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"entities": [], "distribution": {}, "top_entities": []}

        nlp = cls.get_nlp()
        doc = nlp(text)

        entities = []
        type_dist = {}
        freq = {}

        # Allowed entity types from requirements
        ALLOWED_TYPES = {"PERSON", "ORG", "GPE", "LOC", "DATE", "TIME", "MONEY", "PRODUCT", "EVENT", "LAW", "LANGUAGE"}

        for ent in doc.ents:
            if ent.label_ not in ALLOWED_TYPES:
                continue

            # Basic entity info
            entity_text = ent.text.strip()
            ent_type = ent.label_
            
            entities.append({
                "entity": entity_text,
                "type": ent_type,
                "sentence": ent.sent.text.strip(),
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                "confidence": 0.85, # spaCy doesn't output confidence directly for NER by default
                "reason": f"spaCy recognized '{entity_text}' as {ent_type}."
            })

            # Stats tracking
            type_dist[ent_type] = type_dist.get(ent_type, 0) + 1
            freq_key = (entity_text.lower(), ent_type)
            freq[freq_key] = freq.get(freq_key, 0) + 1

        # Format Top Entities
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top_entities = [
            {"entity": k[0], "type": k[1], "count": v}
            for k, v in sorted_freq[:20]
        ]

        return {
            "entities": entities,
            "distribution": type_dist,
            "top_entities": top_entities
        }
