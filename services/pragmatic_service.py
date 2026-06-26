"""
Phase 8: Pragmatic & Discourse Intelligence Engine
Analyzes coreference, discourse relations, sentence intent, entity tracking, and timeline.
Implements Explainable AI (XAI) by returning reasons and confidence scores for every inference.
"""

import re
from typing import List, Dict, Any, Tuple


class CoreferenceResolver:
    """
    Heuristic Coreference Resolution without heavy deep learning models.
    Tracks recent proper nouns or noun phrases and maps pronouns back to them.
    """
    PRONOUNS = {
        "he": ["male", "person"], "him": ["male", "person"], "his": ["male", "person"],
        "she": ["female", "person"], "her": ["female", "person"], "hers": ["female", "person"],
        "it": ["object", "thing", "organization", "animal"], "its": ["object", "thing"],
        "they": ["group", "plural"], "them": ["group", "plural"], "their": ["group", "plural"]
    }

    @classmethod
    def resolve(cls, sentences: List[str], pos_tags: List[Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        results = []
        entities_info = [] # tuples of (word, type)
        
        # Flatten pos_tags into a simple list of (word, tag)
        flat_tags = []
        for p in pos_tags:
            if isinstance(p, dict) and "word" in p and "tag" in p:
                flat_tags.append((p["word"], p["tag"]))
            elif isinstance(p, (list, tuple)) and len(p) == 2:
                flat_tags.append((p[0], p[1]))

        # Track entities (Proper nouns or Nouns)
        for i, (word, tag) in enumerate(flat_tags):
            if tag.startswith("NNP") or (tag.startswith("NN") and word[0].isupper()):
                if not any(e[0] == word for e in entities_info):
                    entities_info.append((word, "person"))
            elif tag.startswith("NN") and len(word) > 2:
                if not any(e[0] == word for e in entities_info):
                    entities_info.append((word, "object"))

            wl = word.lower()
            if wl in cls.PRONOUNS and entities_info:
                # Find most recent matching entity type
                expected_types = cls.PRONOUNS[wl]
                target = entities_info[-1][0] # default
                for e_word, e_type in reversed(entities_info):
                    if e_type in expected_types:
                        target = e_word
                        break
                
                # Context sentence finder
                context_sent = ""
                for s in sentences:
                    if word in s.split() or wl in s.lower().split():
                        context_sent = s
                        break
                
                results.append({
                    "pronoun": word,
                    "resolved_to": target,
                    "sentence": context_sent,
                    "reason": f"'{word}' mapped to recent compatible entity '{target}'.",
                    "confidence": 0.75
                })

        return results, [e[0] for e in entities_info]


class DiscourseAnalyzer:
    """Detects discourse markers and their communicative functions."""
    MARKERS = {
        "however": "Contrast", "but": "Contrast", "although": "Contrast", "whereas": "Contrast", "yet": "Contrast",
        "therefore": "Conclusion", "thus": "Conclusion", "hence": "Conclusion", "consequently": "Conclusion",
        "because": "Cause", "since": "Cause", "as": "Cause", "due to": "Cause",
        "furthermore": "Addition", "moreover": "Addition", "additionally": "Addition", "and": "Addition",
        "finally": "Sequence", "then": "Sequence", "next": "Sequence", "firstly": "Sequence", "meanwhile": "Sequence"
    }

    @classmethod
    def analyze(cls, sentences: List[str]) -> List[Dict[str, Any]]:
        results = []
        for s in sentences:
            sl = s.lower()
            for marker, relation in cls.MARKERS.items():
                # Check for word boundary to avoid partial matches
                if re.search(r'\b' + re.escape(marker) + r'\b', sl):
                    results.append({
                        "marker": marker,
                        "relation": relation,
                        "sentence": s,
                        "reason": f"The discourse marker '{marker}' explicitly indicates a '{relation}' relationship.",
                        "confidence": 0.90
                    })
        return results


class IntentClassifier:
    """Classifies sentence communicative intent."""
    @classmethod
    def classify(cls, sentences: List[str]) -> List[Dict[str, Any]]:
        results = []
        for s in sentences:
            s_clean = s.strip()
            if not s_clean: continue
            
            sl = s_clean.lower()
            intent = "Statement"
            reason = "Default declarative structure."
            conf = 0.6
            
            if s_clean.endswith("?"):
                intent = "Question"
                reason = "Sentence ends with a question mark."
                conf = 0.95
            elif sl.startswith(("please", "kindly", "can you", "could you")):
                intent = "Request"
                reason = "Contains polite request markers at the start."
                conf = 0.85
            elif re.match(r'^(do|make|get|take|buy|let|run|stop|go)\b', sl):
                intent = "Instruction"
                reason = "Starts with an imperative verb."
                conf = 0.75
            elif "i think" in sl or "i believe" in sl or "in my opinion" in sl or "wishes" in sl:
                intent = "Opinion"
                reason = "Contains subjective phrasing ('I think', 'wishes', etc.)."
                conf = 0.88
            elif "is defined as" in sl or "refers to" in sl:
                intent = "Definition"
                reason = "Contains definitional phrasing."
                conf = 0.90
            elif sl.startswith(("so", "therefore", "in conclusion")):
                intent = "Conclusion"
                reason = "Starts with a conclusive discourse marker."
                conf = 0.85
            elif "should" in sl or "could" in sl or "maybe" in sl or "suggest" in sl:
                intent = "Suggestion"
                reason = "Contains modal verbs of suggestion or possibility."
                conf = 0.75

            results.append({
                "sentence": s_clean,
                "intent": intent,
                "reason": reason,
                "confidence": conf
            })
        return results


class EntityTimelineBuilder:
    """Builds a chronological timeline of entities and their actions."""
    @classmethod
    def build(cls, sentences: List[str], pos_tags: List[Any], coref: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Simplified subject-verb tracking based on sentences
        timeline = []
        for i, s in enumerate(sentences):
            # Very naive extraction: find a capitalized word followed shortly by a verb-like word
            words = s.split()
            if len(words) >= 2:
                for j, w in enumerate(words):
                    if w[0].isupper() and j < len(words) - 1:
                        entity = w.strip('.,!?;:"\'')
                        action = words[j+1].strip('.,!?;:"\'')
                        if action.islower() and len(action) > 2:  # Naive verb check
                            # Check coref
                            mapped_entity = entity
                            for c in coref:
                                if c["pronoun"].lower() == entity.lower():
                                    mapped_entity = c["resolved_to"]
                                    break
                            
                            timeline.append({
                                "step": i + 1,
                                "entity": mapped_entity,
                                "action": action,
                                "context": s,
                                "reason": f"Extracted '{mapped_entity}' acting as subject for '{action}'.",
                                "confidence": 0.65
                            })
                            break
        return timeline


class ContextTracker:
    """Tracks entity mentions across the document flow."""
    @classmethod
    def track(cls, coref: List[Dict[str, Any]], entities: List[str]) -> List[Dict[str, Any]]:
        # Consolidates references
        chains = {}
        for ent in entities:
            chains[ent] = [ent]
            
        for c in coref:
            target = c["resolved_to"]
            if target in chains:
                if c["pronoun"] not in chains[target]:
                    chains[target].append(c["pronoun"])
            else:
                chains[target] = [target, c["pronoun"]]
                
        # Filter chains that actually have multiple references
        results = []
        for target, chain in chains.items():
            if len(chain) > 1:
                results.append({
                    "entity": target,
                    "chain": chain,
                    "reason": f"Entity '{target}' is referenced {len(chain)} times through the document.",
                    "confidence": 0.80
                })
        return results


class ExplainabilityGenerator:
    """Formats explainability outputs and aggregates confidences."""
    @classmethod
    def explain_ambiguity(cls, semantic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Reuse semantic Phase 7 WSD output
        wsd = semantic_data.get("wsd", [])
        if isinstance(wsd, list):
            return [{
                "word": w.get("word", ""),
                "chosen_meaning": w.get("sense", ""),
                "reason": w.get("reason", "Context overlap matched via Lesk algorithm."),
                "confidence": 0.85
            } for w in wsd if isinstance(w, dict)]
        return []

    @classmethod
    def aggregate_confidence(cls, component_results: List[List[Dict[str, Any]]]) -> Dict[str, float]:
        scores = []
        for comp in component_results:
            for item in comp:
                if "confidence" in item:
                    scores.append(item["confidence"])
        
        avg = sum(scores) / len(scores) if scores else 0.0
        return {
            "average_confidence": round(avg, 2),
            "high_confidence_count": len([s for s in scores if s >= 0.8]),
            "low_confidence_count": len([s for s in scores if s < 0.8]),
            "total_inferences": len(scores)
        }


class PragmaticSummaryGenerator:
    """Generates a high-level pragmatic summary."""
    @classmethod
    def summarize(cls, intents: List[Dict[str, Any]], discourse: List[Dict[str, Any]], entities: List[str]) -> Dict[str, Any]:
        # Determine dominant intent
        intent_counts = {}
        for i in intents:
            intent_counts[i["intent"]] = intent_counts.get(i["intent"], 0) + 1
            
        primary_intent = max(intent_counts, key=intent_counts.get) if intent_counts else "Statement"
        
        # Determine style
        style = "Informative"
        if primary_intent == "Question": style = "Inquisitive"
        elif primary_intent == "Instruction": style = "Direct / Instructional"
        elif primary_intent == "Opinion": style = "Subjective / Opinionated"
        elif primary_intent == "Request": style = "Polite / Requesting"
        
        return {
            "main_entities": entities[:5],
            "primary_intent": primary_intent,
            "overall_communication_style": style,
            "total_discourse_markers": len(discourse),
            "reason": f"Summary based on dominant intent ({primary_intent}) and {len(entities)} tracked entities.",
            "confidence": 0.85
        }


class PragmaticService:
    """
    Main orchestrator for Phase 8 Pragmatic Analysis.
    Combines submodules and outputs the master JSON struct.
    """
    @staticmethod
    def run_analysis(sentences: List[str], tokens: List[str], syntax_data: Dict[str, Any], semantic_data: Dict[str, Any]) -> Dict[str, Any]:
        pos_tags = syntax_data.get("pos_tags", [])
        
        # 1. Intent Classification
        intents = IntentClassifier.classify(sentences)
        
        # 2. Discourse Analysis
        discourse = DiscourseAnalyzer.analyze(sentences)
        
        # 3. Coreference Resolution
        coref, entities = CoreferenceResolver.resolve(sentences, pos_tags)
        
        # 4. Context Tracking
        context_entities = ContextTracker.track(coref, entities)
        
        # 5. Entity Timeline
        timeline = EntityTimelineBuilder.build(sentences, pos_tags, coref)
        
        # 6. Ambiguity Resolution
        ambiguity = ExplainabilityGenerator.explain_ambiguity(semantic_data)
        
        # 7. Pragmatic Summary
        summary = PragmaticSummaryGenerator.summarize(intents, discourse, entities)
        
        # 8. Confidence aggregation
        confidence = ExplainabilityGenerator.aggregate_confidence([intents, discourse, coref, context_entities, timeline, ambiguity])
        
        return {
            "intent_classification": intents,
            "discourse_relations": discourse,
            "coreference": coref,
            "context_entities": context_entities,
            "entity_timeline": timeline,
            "ambiguity_resolution": ambiguity,
            "pragmatic_summary": summary,
            "confidence_scores": confidence,
            "discourse_markers": [d["marker"] for d in discourse]
        }
