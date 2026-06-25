# ResearchIQ

**Explainable Multi-Level NLP Research Intelligence Platform**

A production-ready Flask web application for uploading, managing, and performing multi-level NLP analysis on research documents (PDF, DOCX, TXT).

---

## Features

| Feature | Status |
|---|---|
| User Registration / Login / Logout | ✅ Implemented |
| Session management & password hashing | ✅ Implemented |
| Document Upload (PDF, DOCX, TXT) | ✅ Implemented |
| Dashboard with statistics | ✅ Implemented |
| Dark / Light mode toggle | ✅ Implemented |
| Responsive sidebar layout | ✅ Implemented |
| Analytics with Chart.js | ✅ Implemented |
| NLP Laboratory overview | ✅ Implemented |
| Preprocessing service | 🔜 Phase 2 |
| Morphology analysis | 🔜 Phase 2 |
| Syntax analysis | 🔜 Phase 2 |
| Semantic analysis | 🔜 Phase 2 |
| Pragmatics analysis | 🔜 Phase 3 |
| Question Answering | 🔜 Phase 3 |
| Summarization | 🔜 Phase 3 |
| Semantic Search | 🔜 Phase 3 |

---

## Technology Stack

**Backend**
- Python 3.11+
- Flask 3.0 (Application Factory pattern)
- SQLAlchemy 3.1 (ORM)
- Flask-Login (session management)
- Werkzeug (password hashing, file utilities)
- SQLite (development database)

**Frontend**
- HTML5 + Jinja2 templates
- CSS3 (custom design system — no Tailwind)
- Bootstrap 5.3
- Bootstrap Icons 1.11
- Chart.js 4.4
- Vanilla JavaScript

---

## Project Structure

```
researchiq/
├── app.py                    # Application factory (entry point)
├── app_extensions.py         # Shared Flask extensions (db, login_manager)
├── config.py                 # Environment configurations
├── requirements.txt
│
├── models/
│   ├── user.py               # User ORM model
│   ├── document.py           # Document ORM model
│   ├── analysis.py           # Analysis ORM model
│   ├── question.py           # Question ORM model
│   └── summary.py            # Summary ORM model
│
├── routes/
│   ├── auth_routes.py        # /auth/register, /auth/login, /auth/logout
│   ├── dashboard_routes.py   # /dashboard/
│   ├── upload_routes.py      # /upload/
│   ├── nlp_routes.py         # /nlp/laboratory, /nlp/syntax, etc.
│   ├── analytics_routes.py   # /analytics/
│   └── settings_routes.py    # /settings/
│
├── services/
│   ├── auth_service.py       # Registration & authentication logic
│   ├── upload_service.py     # File save, validate, DB record creation
│   ├── preprocessing_service.py  # PLACEHOLDER
│   ├── morphology_service.py     # PLACEHOLDER
│   ├── syntax_service.py         # PLACEHOLDER
│   ├── semantic_service.py       # PLACEHOLDER
│   ├── pragmatics_service.py     # PLACEHOLDER
│   ├── qa_service.py             # PLACEHOLDER
│   └── summarization_service.py  # PLACEHOLDER
│
├── templates/
│   ├── base.html             # Master layout (sidebar, navbar, flash)
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   └── index.html
│   ├── upload/
│   │   └── index.html
│   ├── nlp/
│   │   ├── laboratory.html
│   │   └── placeholder.html
│   ├── analytics/
│   │   └── index.html
│   ├── settings/
│   │   └── index.html
│   └── errors/
│       ├── 403.html
│       ├── 404.html
│       └── 500.html
│
├── static/
│   ├── css/main.css          # Custom design system
│   └── js/main.js            # Global JS (theme, sidebar, counters)
│
├── uploads/                  # Uploaded files (git-ignored)
├── database/                 # SQLite database file (git-ignored)
└── utils/
    ├── file_utils.py         # File validation & naming helpers
    └── decorators.py         # Custom route decorators
```

---

## Installation Guide

### 1. Prerequisites

- Python 3.11 or higher
- pip

### 2. Clone / navigate to the project

```bash
cd path/to/ResearchIQ
```

### 3. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables (optional)

Create a `.env` file in the project root:

```env
FLASK_ENV=development
SECRET_KEY=your-very-secret-key-here
PORT=5000
```

### 6. Run the application

```bash
python app.py
```

The application will be available at: **http://127.0.0.1:5000**

The SQLite database (`database/researchiq.db`) and `uploads/` directory are created automatically on first run.

---

## Default Routes

| URL | Description |
|---|---|
| `/` | Redirects to dashboard |
| `/auth/register` | Create a new account |
| `/auth/login` | Sign in |
| `/auth/logout` | Sign out |
| `/dashboard/` | Main dashboard |
| `/upload/` | Upload & manage documents |
| `/nlp/laboratory` | NLP pipeline overview |
| `/analytics/` | Usage statistics |
| `/settings/` | Account settings |

---

## Architecture

ResearchIQ uses the **Application Factory** pattern with Flask Blueprints and a Service Layer.

```
Request → Blueprint Route → Service Layer → SQLAlchemy ORM → SQLite
                                ↓
                         Jinja2 Template → HTML Response
```

- **Blueprints** keep routes modular and independently testable.
- **Service Layer** (`services/`) isolates business logic from HTTP handling.
- **ORM Models** (`models/`) represent database tables as Python classes.
- **Utils** (`utils/`) provide pure functions with no Flask context.

---

## Security

- Passwords hashed with Werkzeug's PBKDF2-SHA256
- Flask-Login session management
- File extension whitelist (PDF, DOCX, TXT only)
- UUID-prefixed stored filenames prevent path traversal
- 16 MB upload size limit enforced by Flask
- CSRF protection via Flask-WTF (enabled in production config)

---

## License

MIT — for academic and educational use.
