# PlantSathi AI — Deployment Guide

## 1. Local Development Execution

### Backend:
```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend:
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 2. Docker Compose Deployment

Both services can be run together using Docker Compose:

```powershell
docker-compose up --build
```
* Frontend will be accessible at: `http://localhost:5173`
* Backend will be accessible at: `http://localhost:8000`

---

## 3. Production Hosting

* **Frontend:** Deployable to Vercel, Netlify, or Cloudflare Pages.
  * Build command: `npm run build`
  * Output directory: `dist`
  * Configure environment variable `VITE_API_URL` to point to your live backend domain.
* **Backend:** Deploy to Render, Railway, Fly.io, or AWS EC2 / GCP Cloud Run.
  * Recommended memory: Minimum 2GB RAM to support PyTorch / Transformers model inference.
  * Set `ENVIRONMENT=production` and specify allowed origins in `ALLOWED_ORIGINS`.
