# Syllabus Mapping

This document tracks the mapping between the ResearchIQ platform modules and the core syllabus concepts for NLP.

## Completed Modules

### Phase 1 & 2: Foundation & Document Intelligence
- [x] Basic Application Architecture
- [x] Authentication & Access Control
- [x] File Parsing (TXT, DOCX, PDF)
- [x] Simple Text Statistics

### Phase 3: NLP Preprocessing Engine
- [x] Generic NLP Pipeline Architecture
- [x] Text Preprocessing
- [x] Normalization (Lowercasing, whitespace, punctuation spacing)
- [x] Sentence Segmentation
- [x] Tokenization

## Planned Modules

### Phase 4: Morphology
- [x] Part-of-Speech (POS) Tagging
- [x] Stemming
- [x] Lemmatization
- [x] Stopword Removal (Configurable)

### Phase 5: Statistical NLP
- [x] Unigram Models
- [x] Bigram Models
- [x] Trigram Models
- [x] Language Modeling (Unigram / Bigram / Trigram with Laplace smoothing)
- [x] Term Frequency (TF)
- [x] TF-IDF Analysis
- [x] Perplexity Demonstration

### Phase 6: Syntax Analysis
- [x] POS Tagging
- [x] Penn Treebank Tags
- [x] Constituency Parsing
- [x] Dependency Parsing
- [x] HMM Demonstration
- [x] Viterbi Algorithm
- [x] Syntax Analysis Dashboard

### Phase 7: Semantic Analysis
- [x] WordNet Integration
- [x] Synonyms
- [x] Antonyms
- [x] Hypernyms
- [x] Hyponyms
- [x] Semantic Similarity
- [x] Word Sense Disambiguation
- [x] Semantic Analysis

### Phase 8: Pragmatics & Discourse Intelligence Engine
  - **Topic:** Coreference resolution, intent classification, and entity timeline.
  - **Code:** `services/pragmatic_service.py` -> `run_analysis()`
  - **Tasks:**
    - [x] Context Tracking and Discourse Analysis
    - [x] Coreference Resolution
    - [x] Intent Detection
    - [x] Ambiguity Resolution integration
  - **Status:** **IMPLEMENTATION** (Pragmatic Dashboard integrated)

### Phase 9: NLP Applications
- [ ] Document Summarization (Extractive & Abstractive)
- [ ] Semantic Search (Dense Vector Retrieval)
- [ ] Question Answering Engine
