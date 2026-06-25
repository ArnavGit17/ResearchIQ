import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app_extensions import db
from services.morphology_service import MorphologyService

def run_verification():
    """Advanced verification dataset for Phase 4 Morphology."""
    print("=" * 50)
    print("MORPHOLOGY ENGINE - ADVANCED VERIFICATION")
    print("=" * 50)
    
    tokens = ["running", "studies", "playing", "better", "wolves", "children"]
    expected_stems = ["run", "studi", "play", "better", "wolv", "children"]
    expected_lemmas = ["run", "study", "play", "good", "wolf", "child"]
    
    app = create_app('testing')
    with app.app_context():
        print("1. Running Morphology Service...")
        results = MorphologyService.run_morphology(tokens)
        
        print("\n2. Verifying Stems (PorterStemmer):")
        stems = results["stemmed_tokens"]
        stems_passed = True
        for i, (expected, actual) in enumerate(zip(expected_stems, stems)):
            status = "PASS" if expected == actual else f"FAIL (Expected: {expected}, Got: {actual})"
            if expected != actual:
                stems_passed = False
            print(f"   [{tokens[i]}] -> {status}")
            
        print("\n3. Verifying Lemmas (POS-Aware WordNet):")
        lemmas = results["lemmatized_tokens"]
        lemmas_passed = True
        for i, (expected, actual) in enumerate(zip(expected_lemmas, lemmas)):
            status = "PASS" if expected == actual else f"FAIL (Expected: {expected}, Got: {actual})"
            if expected != actual:
                lemmas_passed = False
            print(f"   [{tokens[i]}] -> {status}")
            
        print("\n4. Verifying Explainability Mapping:")
        pairs = results["morphology_pairs"]
        pairs_passed = len(pairs) == len(tokens)
        print(f"   Pairs generated: {len(pairs)} / {len(tokens)}")
        if pairs_passed:
            print(f"   Sample explanation [{pairs[1]['token']} -> stem]: {pairs[1]['stem_explanation']}")
            print(f"   Sample explanation [{pairs[1]['token']} -> lemma]: {pairs[1]['lemma_explanation']}")
            
        print("\n5. Verifying Vocabulary Statistics:")
        print(f"   Original Vocab Size: {results['original_vocabulary_size']}")
        print(f"   Stemmed Vocab Size: {results['stemmed_vocabulary_size']}")
        print(f"   Lemmatized Vocab Size: {results['lemmatized_vocabulary_size']}")
        print(f"   Reduction Percentage: {results['vocabulary_reduction_percentage']}%")
        
        print("\n" + "=" * 50)
        if stems_passed and lemmas_passed and pairs_passed:
            print("VERIFICATION: PASS")
            print("=" * 50)
            sys.exit(0)
        else:
            print("VERIFICATION: FAIL")
            print("=" * 50)
            sys.exit(1)

if __name__ == "__main__":
    run_verification()
