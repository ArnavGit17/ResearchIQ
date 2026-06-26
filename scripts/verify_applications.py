"""
Phase 9A Verification Script
Tests NER, Keyword Extraction, Summarization, QA, and Semantic Search heuristic algorithms.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.ner_service import NERService
from services.keyword_service import KeywordService
from services.summarization_service import SummarizationService
from services.question_answering_service import QAService
from services.search_service import SemanticSearchService

def test_applications():
    print("============================================================")
    print("APPLICATION LAYER - ADVANCED VERIFICATION (Phase 9A)")
    print("============================================================\n")

    test_doc = (
        "Apple Inc. is an American multinational technology company headquartered in Cupertino, California. "
        "It was founded by Steve Jobs on April 1, 1976. "
        "The iPhone is one of its most popular products, generating billions of dollars in revenue. "
        "However, the company faces strict regulations from the European Union regarding antitrust laws. "
        "Tim Cook is the current CEO of the organization."
    )

    sentences = [
        "Apple Inc. is an American multinational technology company headquartered in Cupertino, California.",
        "It was founded by Steve Jobs on April 1, 1976.",
        "The iPhone is one of its most popular products, generating billions of dollars in revenue.",
        "However, the company faces strict regulations from the European Union regarding antitrust laws.",
        "Tim Cook is the current CEO of the organization."
    ]

    # Mock POS and TF-IDF data from previous phases
    mock_pos = [
        ("Apple", "NNP"), ("Inc.", "NNP"), ("Steve", "NNP"), ("Jobs", "NNP"),
        ("iPhone", "NNP"), ("revenue", "NN"), ("regulations", "NN"),
        ("technology", "NN"), ("company", "NN"), ("European", "NNP"), ("Union", "NNP")
    ]
    
    mock_tfidf = {
        "apple": 0.8, "steve": 0.6, "jobs": 0.6, "iphone": 0.9,
        "revenue": 0.4, "regulations": 0.5, "european": 0.7, "union": 0.7,
        "company": 0.3
    }

    all_passed = True

    # 1. Test NER
    print("------------------------------------------------------------")
    print("TEST 1: Named Entity Recognition (spaCy)")
    print("------------------------------------------------------------")
    try:
        ner_res = NERService.extract_entities(test_doc)
        entities = [e["entity"] for e in ner_res["entities"]]
        
        if "Apple Inc." in entities and "Steve Jobs" in entities and "Cupertino" in entities:
            print("  [PASS] Found key entities (Apple Inc., Steve Jobs, Cupertino).")
            print(f"    Entities found: {len(entities)}")
            print(f"    Distribution: {ner_res['distribution']}")
        else:
            print(f"  [FAIL] Missing key entities. Found: {entities}")
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] NER Error: {e}")
        all_passed = False

    # 2. Test Keywords
    print("\n------------------------------------------------------------")
    print("TEST 2: Keyword Extraction")
    print("------------------------------------------------------------")
    try:
        kw_res = KeywordService.extract_keywords(mock_tfidf, mock_pos)
        keywords = [k["keyword"].lower() for k in kw_res]
        
        if "iphone" in keywords and "apple" in keywords:
            print("  [PASS] Extracted and ranked keywords correctly based on POS/TF-IDF.")
            print(f"    Top Keyword: {kw_res[0]['keyword']} (Score: {kw_res[0]['score']})")
        else:
            print(f"  [FAIL] Missing key keywords. Found: {keywords}")
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] Keyword Error: {e}")
        all_passed = False

    # 3. Test Summarization
    print("\n------------------------------------------------------------")
    print("TEST 3: Extractive Summarization")
    print("------------------------------------------------------------")
    try:
        sum_res = SummarizationService.generate_summary(sentences, kw_res, ner_res["entities"], compression_ratio=0.4)
        
        stats = sum_res["statistics"]
        if stats["summary_sentences"] == 2 and stats["compression_ratio"] == 0.4:
            print("  [PASS] Summarization compressed document successfully.")
            print(f"    Compression Ratio: {stats['compression_ratio']}")
            print(f"    Summary: {sum_res['summary_text']}")
        else:
            print(f"  [FAIL] Summarization stats incorrect. Got: {stats}")
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] Summarization Error: {e}")
        all_passed = False

    # 4. Test Question Answering
    print("\n------------------------------------------------------------")
    print("TEST 4: Document Question Answering")
    print("------------------------------------------------------------")
    try:
        q = "What is the iPhone?"
        qa_res = QAService.answer_question(q, sentences, kw_res)
        
        if "revenue" in qa_res["answer"]:
            print(f"  [PASS] QA Answered successfully. Q: '{q}'")
            print(f"    A: {qa_res['answer']} (Confidence: {qa_res['confidence']})")
        else:
            print(f"  [FAIL] QA returned incorrect answer: {qa_res['answer']}")
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] QA Error: {e}")
        all_passed = False

    # 5. Test Semantic Search
    print("\n------------------------------------------------------------")
    print("TEST 5: Semantic Search")
    print("------------------------------------------------------------")
    try:
        q_search = "antitrust regulations"
        search_res = SemanticSearchService.search(q_search, sentences, kw_res)
        
        if search_res and "regulations from the European Union" in search_res[0]["sentence"]:
            print(f"  [PASS] Semantic search found highly relevant result for: '{q_search}'")
            print(f"    Result: {search_res[0]['sentence']} (Relevance: {search_res[0]['relevance']})")
        else:
            print(f"  [FAIL] Semantic search failed to find correct sentence.")
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] Search Error: {e}")
        all_passed = False

    print("\n============================================================")
    if all_passed:
        print("VERIFICATION RESULT: PASS  [OK]  All Phase 9A Application checks succeeded.")
        sys.exit(0)
    else:
        print("VERIFICATION RESULT: FAIL  [X]  One or more checks failed. See output above.")
        sys.exit(1)

if __name__ == "__main__":
    test_applications()
