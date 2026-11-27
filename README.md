# Credit Card Recommender

A full-stack demo that helps users discover the best Indian credit cards for their needs using a conversational agent (Gemini LLM) and vector-search (Pinecone). This repository contains a Next.js frontend and a FastAPI backend which together implement a session-based Q&A flow, structured preference extraction, reward simulation fallbacks, and explainable card recommendations.

---

**Contents**
- **Frontend**: Next.js app (App Router) with chat UI and recommendations flow — `frontend/`
- **Backend**: FastAPI service implementing chat, preference extraction, and recommendation logic — `backend/`
- **Card data**: curated card metadata used for embeddings — `backend/data/cards.json`

---

**Live demo**
- If deployed, frontend is typically hosted on Vercel and backend on Render/other cloud. See `frontend/README.md` for an example deployment link used by the original project.

---

**Highlights**
- Conversational Q&A to collect user profile and spending habits
- Gemini (Google Generative AI) for chat, embeddings, and explanation generation
- Pinecone for vector similarity search over card embeddings
- Reward-simulation logic with LLM fallback to regex-based heuristics
- Session-based persistence (in-memory + `sessions.json` file)

---

**Quick Start (development)**

Prerequisites:
- Python 3.11+ (or compatible)
- Node.js 18+ and npm/yarn
- Pinecone account + API key
- Google Generative AI (Gemini) API key

1) Clone repository

```bash
git clone <repo-url>
cd creditCardRecommender
```

2) Backend setup

```bash
cd backend
python -m venv .venv            # optional but recommended
.venv\\Scripts\\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/` containing:

```
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
CORS_ORIGINS=http://localhost:3000
```

Run the backend (development):

```bash
# from backend/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Key backend files:
- `backend/app/main.py` — FastAPI app entrypoint
- `backend/app/routes.py` — `/chat` and `/recommend` endpoints
- `backend/app/gemini_api.py` — Gemini client interactions and session persistence
- `backend/app/embedding_utils.py` — embedding creation helpers
- `backend/app/utils.py` — preference extraction, reward simulation, recommendation logic
- `backend/app/seed_cards.py` — helper to generate embeddings and prepare Pinecone vectors

3) Frontend setup

```bash
cd ../frontend
npm install
npm run dev
```

By default the frontend expects a backend at `http://localhost:8000`. For production, set `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local`.

Key frontend files:
- `frontend/src/components/ChatBox.tsx` — chat UI and session management
- `frontend/src/app/recommendations/page.tsx` — recommendation results UI
- `frontend/src/lib/api.ts` — client calls to backend (`/chat`, `/recommend`)

---

API (backend)
- POST `/chat` — body: `{ "session_id": "<id>", "user_input": "<text>" }` → returns `{ reply, history }`
- POST `/recommend` — query params: `session_id` and `top_k` → returns `{ recommendations: [...] }`

Notes:
- Sessions are stored in memory and written to a local `sessions.json` file. This is a single-process development mechanism, not durable multi-user storage. Session files may contain personal financial preferences; keep them private and never commit them. The root `.gitignore` excludes the file.
- The `recommend` flow extracts structured preferences from session history, embeds those preferences, queries Pinecone for nearest card metadata, and adds an LLM-generated explanation.
- The backend CORS allow-list is configured through `CORS_ORIGINS`; use the exact deployed frontend origin(s), comma-separated. Avoid wildcard origins when credentials are enabled.
- The Pinecone seed script prepares vector records, but its `index.upsert` call remains commented out. Provision and seed the index deliberately before expecting recommendations to work.

---

Seeding Pinecone
- The repository contains `backend/data/cards.json` (curated cards). Use `backend/app/seed_cards.py` to build embeddings and upsert to your Pinecone index. The seed script is a helper and may require small changes depending on your Gemini embedding API response shape.

High-level seed steps:

```bash
# from backend/
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
# make sure .env has keys
python app/seed_cards.py
```

Note: `seed_cards.py` currently prepares the vector objects and shows how to call `index.upsert(vectors=...)` — the upsert call is commented out so review and enable it after verifying API responses.

---

Environment variables summary
- `GEMINI_API_KEY` — Google Generative AI API key (Gemini)
- `PINECONE_API_KEY` — Pinecone API key
- `NEXT_PUBLIC_API_BASE_URL` (frontend) — backend base URL used by the Next app when deployed

---

Deployment
- Frontend: Vercel (push the `frontend/` folder or the whole repo), set `NEXT_PUBLIC_API_BASE_URL` in Vercel settings.
- Backend: Render / Railway / Fly / any container host. Ensure CORS allows the frontend origin (`backend/app/main.py` currently allows `*` origins).

Production considerations
- Replace file-based `sessions.json` with a persistent store (Redis/Postgres) and add session expiry and deletion controls.
- Secure secrets via host-provided environment variables (do not commit `.env`).
- Restrict CORS to trusted frontend origins.
- Add authentication, request-rate limits, input-size limits and structured audit logging.
- Monitor LLM and Pinecone costs.

---


## Offline backend tests

From the repository root:

```bash
cd backend
python -m pip install -r requirements.txt
GEMINI_API_KEY=test-placeholder python -m pytest tests/ -q
```

The utility tests mock the Gemini generation boundary and verify preference summarization plus the deterministic reward-estimation fallback. They do not require live Gemini or Pinecone API calls. GitHub Actions runs these tests on pushes and pull requests.

Contributing
- Feel free to open issues or PRs. For changes to prompts or model usage, include rationale and tests/examples for regressions.

---

License
- MIT

---
