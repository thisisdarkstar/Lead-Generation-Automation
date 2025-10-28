# Lead Generation Automation

A compact, clear guide to run the project locally (backend API + Next.js frontend) and view example screenshots.

## Quick start (development)

Prerequisites
- Node.js + npm
- Python 3.8+
- (Optional) `pyenv` if you use it to manage Python versions

1) Backend — create a venv, install requirements, start the API

Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# start the API (uvicorn with 4 workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

macOS / Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# start the API (uvicorn with 4 workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

2) Frontend — in a second terminal

```bash
cd frontend
npm install
npm run dev
```

3) Open the GUI

- Frontend: http://localhost:3000
- Backend API (default): http://localhost:8000

## What this repo contains

- `backend/` — FastAPI-compatible Python API and scripts
- `frontend/` — Next.js app (development server via `npm run dev`)

## Screenshots

Example UI screenshots are saved in `./screenshots/` (filenames contain spaces). Links below URL-encode those spaces for compatibility.

1) CSV -> Domains (upload CSV, extract domains, optionally send to lead generation)
![CSV extractor page](./screenshots/csv_extractor%20page.png)

2) JSON leads extractor (extract domains from leads JSON)
![JSON leads extractor](./screenshots/leads_extracto%20page.png)

3) HTML table extractor (extract domains shown in an HTML table)
![HTML table extractor](./screenshots/extract_html%20page.png)

4) Lead generation / send UI
![Lead generation page](./screenshots/lead_generation%20page.png)

## Troubleshooting

- If the frontend can't reach the backend, verify the backend is running on port 8000 and there are no CORS or proxy rules blocking requests.
- On Windows PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` if activation scripts are blocked.

If you'd like, I can also:
- Add small launch scripts (PowerShell / shell) to start backend and frontend in separate terminals.
- Rename screenshot files to remove spaces and update the README links.

That's it — minimal, clear instructions to run the app locally and view the UI.