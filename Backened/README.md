# AI Life Admin API

FastAPI backend for tasks, documents, calendar actions, and AI assistance.

## Run on Windows

1. Create a local `.env` from `.env.example` and set `DATABASE_URL` to the URI copied from MongoDB Atlas → Connect → Drivers. Use an Atlas database user, not your Atlas website login. URL encode special characters in the username or password.
2. In Atlas Network Access, allow the public IP address of the computer running this API. Keep the cluster active and allow outbound TCP to ports `27015`–`27017`.
3. Install dependencies and start the API from this folder:

   ```powershell
   .\venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

Open `http://127.0.0.1:8000/docs` for Swagger UI. `GET /health` pings MongoDB; it returns HTTP 503 with a diagnostic if the database cannot be reached. The API logs the underlying MongoDB error in the terminal.

### Local MongoDB with Docker

For local development, install Docker Desktop and run `docker compose up -d mongodb` from this folder. Set `DATABASE_URL="mongodb://127.0.0.1:27017"` in `.env`. The development database port is bound to loopback only; use an authenticated Atlas URI for deployment.

If the database contains records created before account ownership was enabled, create the intended account and preview the assignment with `python scripts/assign_legacy_records.py --email you@example.com`. Review the counts, then add `--apply` to assign those unowned records to that account. Do not run the apply command unless that account should own all legacy records.

## Gemini setup

Create or select a valid key in [Google AI Studio](https://aistudio.google.com/app/apikey), set `GEMINI_API_KEY` in `.env`, and restart the API. A rejected key returns HTTP 503 instead of a false HTTP 200 response. The model defaults to `gemini-3.8-flash` and can be changed with `GEMINI_MODEL`.

For account endpoints, set `JWT_SECRET_KEY` in `.env` to a private random value of at least 32 characters before registering or logging in. Do not use the example placeholder or commit the secret.

## Master Agent runs

`POST /api/v1/agent/query` creates an AI run and stores its prompt and response in MongoDB. Read runs with `GET /api/v1/agent/runs` or `GET /api/v1/agent/runs/{run_id}`. `PATCH /api/v1/agent/runs/{run_id}` re-runs the agent with the replacement prompt; `DELETE` removes the saved run.

`GET /health` is a live readiness check, not stored data. It intentionally stays read-only and returns HTTP 503 when MongoDB is unavailable.

## MongoDB connection troubleshooting

- **TLS handshake failed:** verify that `DATABASE_URL` uses the current Atlas cluster hostname. Check that VPN, proxy, firewall, or antivirus software is not intercepting TLS, and allow outbound TCP ports `27015`–`27017`.
- **`Test-NetConnection cluster0...` says name resolution failed:** for an Atlas `mongodb+srv://` URI, check the SRV record rather than looking up the seed hostname as an IP. Run `Resolve-DnsName -Name _mongodb._tcp.<cluster-host> -Type SRV`, then test each returned `NameTarget` on its returned port (usually `27017`).
- **Server selection timeout:** verify the cluster is active, the current public IP is in Atlas Network Access, and DNS can resolve the Atlas SRV record.
- **Authentication failed:** verify the Atlas database username/password and URL encode any special characters in them.

Keep real credentials in `.env` only. Do not commit `.env` or put secrets in `.env.example`.
