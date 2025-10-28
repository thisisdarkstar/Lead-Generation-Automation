# Lead Generation Automation

Minimal development README — how to run backend and frontend

1) Backend (create venv, install requirements, start uvicorn)

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# start the API (uvicorn with 4 workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

macOS / Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# start the API (uvicorn with 4 workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

2) Frontend (in a second terminal)

```bash
cd frontend
npm install
npm run dev
```

3) Open the GUI

- Visit http://localhost:3000 in your browser (frontend dev server).
- Backend API listens on http://localhost:8000 by default.

That's it — minimal steps to get both backend and frontend running for development.
