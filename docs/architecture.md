# ResearchIQ – Project Architecture

## Overview

ResearchIQ is built with a **modular, layered architecture** designed for maintainability and extensibility.

```
┌─────────────────────────────────────────────────────────┐
│                      Client Browser                      │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────┐
│                Flask Application (app.py)                │
│             Application Factory Pattern                  │
│  ┌──────────┬──────────┬──────────┬──────────────────┐  │
│  │  auth_bp │ dash_bp  │upload_bp │nlp_bp analytics… │  │
│  │ Blueprint│Blueprint │Blueprint │Blueprints        │  │
│  └────┬─────┴────┬─────┴────┬─────┴──────┬───────────┘  │
│       │          │          │             │               │
│  ┌────▼──────────▼──────────▼─────────────▼──────────┐   │
│  │                  Service Layer                     │   │
│  │  AuthService │ UploadService │ NLP Services…      │   │
│  └────────────────────────┬───────────────────────────┘  │
│                           │                              │
│  ┌────────────────────────▼───────────────────────────┐  │
│  │           SQLAlchemy ORM Models                    │  │
│  │  User │ Document │ Analysis │ Question │ Summary   │  │
│  └────────────────────────┬───────────────────────────┘  │
│                           │                              │
│  ┌────────────────────────▼───────────────────────────┐  │
│  │              SQLite Database                       │  │
│  │          database/researchiq.db                    │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Routes (Blueprints)
Handle HTTP request/response cycle only.
- Parse form data and URL parameters
- Call service methods
- Flash messages and redirect or render templates

### 2. Service Layer
Contains all business logic — independent of Flask's request context (except `current_app`).
- `AuthService` – registration and login validation
- `UploadService` – file I/O, validation, and DB record creation
- NLP services (future) – text analysis pipelines

### 3. ORM Models
Define the database schema and provide model-level helpers.
- Properties like `file_size_display` and `icon` keep views clean
- Relationships defined with `db.relationship` for easy traversal

### 4. Utils
Pure, stateless helper functions.
- `file_utils.py` – extension checking, UUID naming, size formatting
- `decorators.py` – route protection decorators

### 5. Templates
Jinja2 templates with a single `base.html` that all pages extend.
- Sidebar and navbar rendered only for authenticated users
- Error pages (403, 404, 500) extend the same base

## Database Schema

```
users              documents           analyses
──────             ─────────           ────────
id (PK)            id (PK)             id (PK)
username           user_id (FK→users)  document_id (FK)
email              filename            analysis_type
password_hash      original_filename   result_json
created_at         file_type           status
                   file_size           created_at
                   upload_date
                   status

questions          summaries
─────────          ─────────
id (PK)            id (PK)
document_id (FK)   document_id (FK)
question           summary
answer             summary_type
confidence         word_count
created_at         created_at
```

## NLP Pipeline (Planned)

```
Raw Document
     │
     ▼
[Preprocessing]  ← Tokenisation, segmentation, stop-word removal
     │
     ▼
[Morphology]     ← POS tagging, lemmatisation, morpheme analysis
     │
     ▼
[Syntax]         ← Dependency parsing, constituency trees
     │
     ▼
[Semantic]       ← NER, word sense disambiguation, coreference
     │
     ▼
[Pragmatics]     ← Sentiment, discourse, speech acts
     │
     ├──► Question Answering
     ├──► Summarization
     └──► Semantic Search
```

## Configuration Strategy

Three environments share a base `Config` class:

| Environment | Database | Debug | CSRF |
|---|---|---|---|
| development | SQLite file | True | False |
| testing | In-memory SQLite | True | False |
| production | SQLite / PostgreSQL | False | True |

Switch environments via the `FLASK_ENV` environment variable.
