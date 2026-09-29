# LegalEase — AI-Powered Legal Document Generator

LegalEase is a Streamlit + FastAPI application that generates editable legal-document drafts with Gemini and exports them to TXT, DOCX, and PDF.

> **Important:** LegalEase generates draft legal information, not legal advice. Important documents should be reviewed by a qualified lawyer in the relevant jurisdiction before signing or relying on them.

## Architecture
- `frontend/app.py` — Streamlit UI
- `backend/main.py` — FastAPI application
- `backend/routes.py` — API endpoints and validation
- `backend/ai_core/gemini_generator.py` — Gemini integration
- `backend/services/document_formatter.py` — TXT/DOCX/PDF generation
- `tests/` — automated tests
- `assets/logo.png` — default branding logo

The supplied documentation specifies Streamlit + FastAPI + Gemini and TXT/DOCX/PDF export. This implementation keeps that architecture while using Google's current `google-genai` SDK instead of the older `google-generativeai` package.

## Quick start
### 1. Virtual environment
Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Gemini configuration
Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
For UI/API testing without a key, set `MOCK_MODE=true`.

### 4. Run FastAPI
```bash
uvicorn backend.main:app --reload --port 8000
```
Then open `http://127.0.0.1:8000/docs`.

### 5. Run Streamlit
In a second terminal:
```bash
streamlit run frontend/app.py
```
Open the URL shown by Streamlit, normally `http://localhost:8501`.

### 6. Test
```bash
pytest -q
```

## API
POST `/generate` accepts:
```json
{
  "document_type": "Non-Disclosure Agreement",
  "parties": "Jane Doe (Disclosing Party); TechNova Inc. (Receiving Party)",
  "terms": "Confidential information must be protected for 3 years; either party may terminate with 15 days notice",
  "effective_date": "2026-09-22"
}
```

## VS Code
Open the `LegalEase` folder. Select the `.venv` interpreter. Use two integrated terminals: one for Uvicorn and one for Streamlit. Recommended extensions: Python and Pylance.

## Production notes
- Restrict CORS to the real frontend origin.
- Put the Gemini key in the deployment secret manager.
- Add authentication, rate limiting, audit logging, and encrypted persistence before handling sensitive production workloads.
- Do not treat generated documents as legal advice.
