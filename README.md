## AI Emergency Surgery Assistant

Monorepo: Next.js frontend + Gradio (Python) backend.

- Frontend: Next.js app in `src/` with `next.config.ts`
- Backend: Gradio app in `AI-Emergency-Surgery-Assistant/` (`app.py`)

Reference: Hugging Face Space `aimedica/AI-Emergency-Surgery-Assistant` [`https://huggingface.co/spaces/aimedica/AI-Emergency-Surgery-Assistant?logs=container`]

### 1) Local setup

Node.js 18+ and Python 3.10+ recommended.

```bash
# Frontend
npm i
npm run dev
# http://localhost:3000

# Backend (in another terminal)
cd AI-Emergency-Surgery-Assistant
python -m venv .venv
.venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt
copy env.example .env   # Fill ANTHROPIC_API_KEY
python app.py           # Gradio at http://127.0.0.1:7860
```

Environment variables (`AI-Emergency-Surgery-Assistant/.env`):

```
ANTHROPIC_API_KEY=your_key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
MODAL_CLINIC_ENDPOINT=https://aayushraj0324--healthmate-clinic-lookup-search-clinics.modal.run
GRADIO_SHARE=false
```

### 2) Push to GitHub

Create an empty repo on GitHub, then run:

```bash
git init
git add .
git commit -m "Initial commit: AI Emergency Surgery Assistant"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<REPO>.git
git push -u origin main
```

### 3) Deploy options

- Vercel (frontend): Connect repo, set build to Next.js.
- Hugging Face / Modal (backend): This repo mirrors the Space at [`https://huggingface.co/spaces/aimedica/AI-Emergency-Surgery-Assistant?logs=container`].

### Notes

- Gradio works without `ANTHROPIC_API_KEY`, but AI analysis will be disabled as designed in `app.py`.
- `lookup_clinics` uses a remote endpoint with a DuckDuckGo fallback if the remote is unavailable.
