# AI Life Admin

React/Vite frontend and FastAPI/MongoDB backend for account-owned tasks, calendar events, finance transactions, documents, and Gemini responses.

## Local Setup

1. Install Docker Desktop, then start MongoDB from `Backened`:

   ```powershell
   cd Backened
   docker compose up -d mongodb
   ```

   Alternatively, set `DATABASE_URL` in `Backened/.env` to a valid MongoDB Atlas URI.

2. Create `Backened/.env` from `Backened/.env.example`. Set a random `JWT_SECRET_KEY` of at least 32 characters. Set `GEMINI_API_KEY` to enable AI responses and PDF/image extraction.

3. Start the backend from `Backened`:

   ```powershell
   .\.venv312\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

4. In another terminal, start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

   Open `http://localhost:5173`, create an account, then use the app. The frontend API URL defaults to `http://127.0.0.1:8000/api/v1`; override it in `frontend/.env` when deploying elsewhere.

## Validation

```powershell
cd Backened
.\.venv312\Scripts\python.exe tests\test_api_contracts.py
cd ..\frontend
npm run lint
npm run build
```

The AI assistant returns advice; it does not silently create or modify tasks, calendar events, or transactions. Those changes are made through their explicit forms.