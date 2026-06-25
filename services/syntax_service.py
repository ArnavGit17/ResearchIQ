"""
Syntax Analysis Service
Implements Phase 6 – POS Tagging, Parsing, and HMM/Viterbi Demonstrations.
"""

import nltk
import spacy
from typing import List, Dict, Any
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# Ensure NLTK resources are available
try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger", quiet=True)

try:
    nltk.data.find("taggers/averaged_perceptron_tagger_eng")
except LookupError:
    nltk.download("averaged_perceptron_tagger_eng", quiet=True)

# ── PENN TREEBANK TAG REFERENCE ───────────────────────────────────────────────
PENN_TREEBANK_TAGS = {
    "CC":   "Coordinating conjunction",
    "CD":   "Cardinal number",
    "DT":   "Determiner",
    "EX":   "Existential there",
    "FW":   "Foreign word",
    "IN":   "Preposition or subordinating conjunction",
    "JJ":   "Adjective",
    "JJR":  "Adjective, comparative",
    "JJS":  "Adjective, superlative",
    "LS":   "List item marker",
    "MD":   "Modal",
    "NN":   "Noun, singular or mass",
    "NNS":  "Noun, plural",
    "NNP":  "Proper noun, singular",
    "NNPS": "Proper noun, plural",
    "PDT":  "Predeterminer",
    "POS":  "Possessive ending",
    "PRP":  "Personal pronoun",
    "PRP$": "Possessive pronoun",
    "RB":   "Adverb",
    "RBR":  "Adverb, comparative",
    "RBS":  "Adverb, superlative",
    "RP":   "Particle",
    "SYM":  "Symbol",
    "TO":   "to",
    "UH":   "Interjection",
    "VB":   "Verb, base form",
    "VBD":  "Verb, past tense",
    "VBG":  "Verb, gerund or present participle",
    "VBN":  "Verb, past participle",
    "VBP":  "Verb, non-3rd person singular present",
    "VBZ":  "Verb, 3rd person singular present",
    "WDT":  "Wh-determiner",
    "WP":   "Wh-pronoun",
    "WP$":  "Possessive wh-pronoun",
    "WRB":  "Wh-adverb"
}

def get_tag_description(tag: str) -> str:
    return PENN_TREEBANK_TAGS.get(tag, "Unknown Tag")

def get_tag_category(tag: str) -> str:
    if tag.startswith("NN"): return "Noun"
    if tag.startswith("VB"): return "Verb"
    if tag.startswith("JJ"): return "Adjective"
    if tag.startswith("RB"): return "Adverb"
    if tag == "IN": return "Preposition"
    if tag in ("DT", "WDT", "PDT"): return "Determiner"
    if tag.startswith("PRP") or tag == "WP": return "Pronoun"
    if tag == "CC": return "Conjunction"
    return "Other"

class SyntaxService:
    @staticmethod
    def run_analysis(sentences: List[str], tokens: List[str]) -> Dict[str, Any]:
        """
        Runs the full Phase 6 Syntax Analysis pipeline.
        """
        pos_tags_detailed = []
        syntax_pairs = []
        tag_counts = Counter()
        
        cat_counts = {
            "Noun": 0, "Verb": 0, "Adjective": 0, "Adverb": 0, "Other": 0
        }
        
        for sent in sentences:
            sent_tokens = nltk.word_tokenize(sent)
            tagged = nltk.pos_tag(sent_tokens)
            
            for token, tag in tagged:
                desc = get_tag_description(tag)
                cat = get_tag_category(tag)
                
                if cat in cat_counts:
                    cat_counts[cat] += 1
                else:
                    cat_counts["Other"] += 1
                
                tag_counts[tag] += 1
                
                pos_tags_detailed.append({
                    "token": token,
                    "tag": tag,
                    "description": desc,
                    "category": cat
                })
                
                syntax_pairs.append({
                    "token": token,
                    "tag": tag,
                    "description": desc
                })

        total = sum(cat_counts.values())
        if total == 0: total = 1
        
        n_v_ratio = cat_counts["Noun"] / max(1, cat_counts["Verb"])
        avg_pos_per_sent = len(syntax_pairs) / max(1, len(sentences))
        
        complex_tags = sum(tag_counts[t] for t in tag_counts if t in ("IN", "CC", "WDT", "WP", "WRB"))
        complexity_score = (complex_tags / total) * 10.0
        
        tag_freq_ordered = dict(tag_counts.most_common())

        dependency_results = []
        engine = "none"
        
        try:
            nlp = spacy.load("en_core_web_sm")
            engine = "spacy"
            
            for sent in sentences[:5]:
                doc = nlp(sent)
                sent_deps = []
                for token in doc:
                    if not token.is_punct and not token.is_space:
                        sent_deps.append({
                            "token": token.text,
                            "dependency": token.dep_,
                            "head": token.head.text,
                            "head_pos": token.head.pos_
                        })
                dependency_results.append(sent_deps)
        except Exception as e:
            logger.warning(f"spaCy not available or failed for dependency parsing: {e}")
            engine = "fallback"

        grammar = r"""
          NP: {<DT|PP\$>?<JJ>*<NN.*>+}
          VP: {<MD>?<VB.*><NP|PP>*}
          PP: {<IN><NP>}
        """
        cp = nltk.RegexpParser(grammar)
        
        parse_trees = []
        parse_trees_text = []
        
        for sent in sentences[:5]:
            sent_tokens = nltk.word_tokenize(sent)
            tagged = nltk.pos_tag(sent_tokens)
            tree = cp.parse(tagged)
            
            def tree_to_dict(t):
                if isinstance(t, nltk.Tree):
                    return {
                        "label": t.label(),
                        "children": [tree_to_dict(child) for child in t]
                    }
                else:
                    return {"token": t[0], "tag": t[1]}
            
            parse_trees.append(tree_to_dict(tree))
            parse_trees_text.append(tree.pformat(margin=120))

        return {
            "pos_tags": pos_tags_detailed,
            "syntax_pairs": syntax_pairs,
            "tag_frequency": tag_freq_ordered,
            "noun_count": cat_counts["Noun"],
            "verb_count": cat_counts["Verb"],
            "adjective_count": cat_counts["Adjective"],
            "adverb_count": cat_counts["Adverb"],
            "other_count": cat_counts["Other"],
            "total_tokens": total,
            "noun_verb_ratio": n_v_ratio,
            "avg_pos_per_sentence": avg_pos_per_sent,
            "sentence_complexity_score": complexity_score,
            "dependency": dependency_results,
            "dependency_engine": engine,
            "parse_tree": parse_trees,
            "parse_tree_text": parse_trees_text
        }

class HMMViterbiDemoService:
    @staticmethod
    def get_hmm_demo() -> Dict[str, Any]:
        return {
            "sentence": "The cat sat",
            "observed_words": ["The", "cat", "sat"],
            "hidden_states": ["DT", "NN", "VBD"],
            "explanation": "A Hidden Markov Model (HMM) models a sequence of observations (words) generated by a sequence of hidden states (POS tags).",
            "components": {
                "transition_probabilities": [
                    {"from": "START", "to": "DT", "prob": 0.8},
                    {"from": "DT", "to": "NN", "prob": 0.9},
                    {"from": "NN", "to": "VBD", "prob": 0.6},
                    {"from": "VBD", "to": "END", "prob": 0.7}
                ],
                "emission_probabilities": [
                    {"state": "DT", "word": "The", "prob": 0.85},
                    {"state": "NN", "word": "cat", "prob": 0.05},
                    {"state": "VBD", "word": "sat", "prob": 0.02}
                ]
            }
        }
        
    @staticmethod
    def get_viterbi_demo() -> Dict[str, Any]:
        return {
            "sentence": "The cat sat",
            "explanation": "The Viterbi algorithm uses dynamic programming to find the most likely sequence of hidden states (tags) for the given words, avoiding exponential time complexity.",
            "steps": [
                {
                    "step": 1,
                    "word": "The",
                    "candidates": [
                        {"tag": "DT", "score": 0.68, "selected": True},
                        {"tag": "NN", "score": 0.01, "selected": False}
                    ]
                },
                {
                    "step": 2,
                    "word": "cat",
                    "candidates": [
                        {"tag": "NN", "score": 0.0306, "selected": True},
                        {"tag": "VB", "score": 0.001, "selected": False}
                    ]
                },
                {
                    "step": 3,
                    "word": "sat",
                    "candidates": [
                        {"tag": "VBD", "score": 0.00036, "selected": True},
                        {"tag": "NN", "score": 0.00001, "selected": False}
                    ]
                }
            ],
            "best_path": ["DT", "NN", "VBD"]
        }
