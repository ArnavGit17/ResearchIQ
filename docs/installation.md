# ResearchIQ – Installation Guide

## System Requirements

| Requirement | Version |
|---|---|
| Python | 3.11 or higher |
| pip | 23.0 or higher |
| OS | Windows 10/11, macOS 12+, Ubuntu 20.04+ |
| RAM | Minimum 512 MB |
| Disk | Minimum 200 MB |

---

## Step-by-Step Installation

### Step 1 – Verify Python version

```bash
python --version
# Expected: Python 3.11.x or higher
```

### Step 2 – Navigate to project folder

```bash
cd "C:\Users\YourName\Desktop\ResearchIQ"
```

### Step 3 – Create virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

### Step 4 – Install Python dependencies

```bash
pip install -r requirements.txt
```

Installed packages:
- `Flask` – web framework
- `Flask-SQLAlchemy` – ORM integration
- `Flask-Login` – session management
- `Flask-WTF` – CSRF protection
- `Werkzeug` – security utilities
- `python-dotenv` – environment variable loading
- `PyPDF2` – PDF reading (future use)
- `python-docx` – DOCX reading (future use)

### Step 5 – Configure environment (optional)

Copy `.env.example` to `.env` and edit:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env`:
```env
FLASK_ENV=development
SECRET_KEY=your-long-random-secret-here
PORT=5000
```

### Step 6 – Run the application

```bash
python app.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 7 – Open in browser

Visit: **http://127.0.0.1:5000**

You will be redirected to the login page.
Click **"Create one"** to register your first account.

---

## First-Time Setup

1. Navigate to `http://127.0.0.1:5000/auth/register`
2. Fill in username, email, and password (min. 8 characters)
3. Click **"Create Account"**
4. Log in with your credentials
5. You are now on the Dashboard!

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'flask'`
Make sure your virtual environment is activated:
```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### `Address already in use` (port 5000)
Change the port in `.env`:
```env
PORT=5001
```

### Database not created
The database is created automatically. If not:
```bash
python -c "from app import create_app; from app_extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('OK')"
```

### Upload fails with `413 Request Entity Too Large`
The default limit is 16 MB. To increase it, edit `config.py`:
```python
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB
```

---

## Stopping the Server

Press `Ctrl + C` in the terminal.

To deactivate the virtual environment:
```bash
deactivate
```
