# DesignMentor AI — Production Deployment Guide

## Recommended Platform: Railway.app

Railway is the best fit for this project. It handles PostgreSQL, Redis, FastAPI, and Next.js in one place with:
- Automatic HTTPS on every service
- Built-in PostgreSQL and Redis plugins (one click)
- Deploy from GitHub automatically on every push
- Free tier to start, affordable to scale

---

## Option 1: Railway.app (Recommended)

### Prerequisites
- GitHub account with this repo pushed
- Railway account: https://railway.app (sign up free)
- Groq API key: https://console.groq.com/keys

---

### Step 1: Create a Railway Project

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your `DesignMentor-AI` repository
4. Railway detects the repo — click **"Add service"**

---

### Step 2: Deploy the Backend (FastAPI)

#### 2a. Configure the service

1. In your Railway project, click **"New Service"** → **"GitHub Repo"**
2. Select your repo
3. Railway will auto-detect the `Dockerfile.prod` — if not, set:
   - **Build Command**: (leave blank — Dockerfile handles it)
   - **Dockerfile Path**: `Dockerfile.prod`

#### 2b. Add PostgreSQL

1. Click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway creates the database and **auto-injects** `DATABASE_URL` into your backend service

#### 2c. Add Redis

1. Click **"New"** → **"Database"** → **"Add Redis"**
2. Railway creates Redis and **auto-injects** `REDIS_URL`

#### 2d. Set Backend Environment Variables

In your backend service → **Variables** tab, add:

```
ENVIRONMENT=production
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=groq
LLM_FALLBACK_ENABLED=true
CORS_ORIGINS=["https://your-frontend.up.railway.app"]
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
WEB_CONCURRENCY=2
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
ANALYTICS_ENABLED=true
PDF_EXPORT_ENABLED=true
SESSION_TTL_SECONDS=1800
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> **Note**: `DATABASE_URL` and `REDIS_URL` are injected automatically by Railway plugins. Do NOT set them manually.

#### 2e. Deploy

Click **"Deploy"**. Railway will:
1. Build the Docker image
2. Run database migrations (Alembic auto-runs on startup in production)
3. Start Gunicorn with 2 Uvicorn workers

**Your backend URL will be**: `https://your-service-name.up.railway.app`

---

### Step 3: Deploy the Frontend (Next.js)

#### 3a. Add a second service

1. In the same Railway project, click **"New Service"** → **"GitHub Repo"**
2. Select the same repo
3. Set **Root Directory**: `frontend-next`
4. Set **Dockerfile Path**: `frontend-next/Dockerfile`

#### 3b. Set Frontend Environment Variables

```
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NODE_ENV=production
```

Replace `your-backend.up.railway.app` with your **actual backend URL** from Step 2e.

#### 3c. Deploy

Click **"Deploy"**. Railway builds the Next.js standalone image.

**Your frontend URL will be**: `https://your-frontend-name.up.railway.app`

---

### Step 4: Update CORS

Now that you have the frontend URL, go back to the **backend service** → Variables and update:

```
CORS_ORIGINS=["https://your-frontend-name.up.railway.app"]
```

Click **"Redeploy"** on the backend.

---

### Step 5: Custom Domain (Optional)

#### Backend
1. Backend service → **Settings** → **Domains** → **"Add Custom Domain"**
2. Enter: `api.yourdomain.com`
3. Railway shows a CNAME record — add it to your DNS provider
4. HTTPS is automatic via Let's Encrypt

#### Frontend
1. Frontend service → **Settings** → **Domains** → **"Add Custom Domain"**
2. Enter: `yourdomain.com` or `www.yourdomain.com`
3. Add the CNAME to your DNS provider
4. Update backend `CORS_ORIGINS` to include your custom domain

---

### Step 6: Database Migrations

Migrations run **automatically** on every deploy in production.

The `lifespan` function in `app/main.py` runs:
```bash
alembic upgrade head
```
before accepting traffic.

To run migrations manually via Railway CLI:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run a one-off command
railway run alembic upgrade head
```

---

## Option 2: Render.com

### Backend (Web Service)

1. Go to https://render.com → **"New Web Service"**
2. Connect your GitHub repo
3. Settings:
   - **Environment**: Docker
   - **Dockerfile Path**: `Dockerfile.prod`
   - **Instance Type**: Starter ($7/month) for production
4. Add environment variables (same list as Railway above)
5. Add **PostgreSQL** → Render creates a managed DB, injects `DATABASE_URL`
6. Add **Redis** → Render Redis, injects `REDIS_URL`

### Frontend (Static Site or Web Service)

**Option A — Static (free)**:
1. New **Static Site** → connect repo
2. Root directory: `frontend-next`
3. Build command: `npm run build && npm run export` (requires `output: "export"` in next.config.js — not recommended if using API routes)

**Option B — Web Service (recommended)**:
1. New **Web Service** → Docker → Root: `frontend-next`
2. Dockerfile: `frontend-next/Dockerfile`
3. Set `NEXT_PUBLIC_API_URL`

---

## Option 3: Vercel (Frontend) + Railway (Backend)

Best combination for performance. Vercel's edge network serves Next.js fastest.

### Frontend on Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repo
3. Set **Root Directory**: `frontend-next`
4. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
   ```
5. Deploy — Vercel auto-detects Next.js, builds and deploys

### Backend on Railway

Follow Option 1 Steps 2-4. Update CORS in backend:
```
CORS_ORIGINS=["https://your-project.vercel.app","https://yourdomain.com"]
```

---

## Production Environment Variables Reference

### Backend (Required)

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Must be `production` | `production` |
| `SECRET_KEY` | JWT signing key (32+ chars) | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | PostgreSQL connection string | Auto-injected by Railway/Render |
| `REDIS_URL` | Redis connection string | Auto-injected by Railway/Render |
| `GROQ_API_KEY` | Groq API key | `gsk_...` |
| `CORS_ORIGINS` | JSON array of allowed origins | `["https://yourfrontend.com"]` |

### Backend (Optional but Recommended)

| Variable | Default | Description |
|----------|---------|-------------|
| `WEB_CONCURRENCY` | `2` | Gunicorn workers |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `json` | Use `json` for log aggregation |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `60` | Per-IP rate limit |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM model |

### Frontend (Required)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend URL (e.g. `https://api.up.railway.app`) |

---

## Build & Start Commands (Without Docker)

If you deploy without Docker (Railway can auto-detect Python/Node):

### Backend
```bash
# Build (install deps)
pip install -r requirements.txt

# Start
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 2 \
  --bind 0.0.0.0:$PORT \
  --timeout 120
```

### Frontend
```bash
# Build
npm ci --legacy-peer-deps && npm run build

# Start
npm start
```

---

## Production Best Practices Applied

### Security
- ✅ `DEBUG=false` in production
- ✅ `/docs` and `/redoc` hidden in production
- ✅ JWT tokens with configurable expiry
- ✅ Passwords hashed with sha256_crypt (200k rounds)
- ✅ Security headers middleware (X-Content-Type, X-Frame-Options, etc.)
- ✅ CORS locked to specific origins
- ✅ Non-root Docker user

### Performance
- ✅ Gunicorn with 2 Uvicorn workers (scale to 4-8 on larger instances)
- ✅ Next.js standalone output mode (smaller image)
- ✅ Redis caching layer
- ✅ Database connection pooling via SQLAlchemy

### Reliability
- ✅ Alembic migrations run automatically on startup
- ✅ Health check endpoints (`/health`, `/api/v1/health/detailed`)
- ✅ Exponential backoff on Groq rate limits
- ✅ OpenAI fallback when Groq is unavailable
- ✅ Graceful Redis fallback (in-memory sessions if Redis is down)

### Monitoring
- ✅ Structured JSON logging in production
- ✅ Request logging middleware (method, path, status, duration)
- ✅ `/api/v1/health/detailed` endpoint shows all service states

---

## Quick Deploy Checklist

```
[ ] Push latest code to GitHub
[ ] Create Railway project
[ ] Add PostgreSQL plugin
[ ] Add Redis plugin
[ ] Deploy backend service (Dockerfile.prod)
[ ] Set backend environment variables (see table above)
[ ] Deploy frontend service (frontend-next/Dockerfile)
[ ] Set NEXT_PUBLIC_API_URL in frontend
[ ] Update CORS_ORIGINS in backend with frontend URL
[ ] Redeploy backend
[ ] Test: open https://your-frontend.up.railway.app
[ ] Test: register an account, generate a design
[ ] (Optional) Add custom domain
```

---

## Troubleshooting

### "Migrations failed"
- Check `DATABASE_URL` is set and the PostgreSQL service is healthy
- Run manually: `railway run alembic upgrade head`

### "CORS error in browser"
- Verify `CORS_ORIGINS` in backend includes your exact frontend URL (with https://)
- No trailing slash

### "Groq rate limit in production"
- The retry logic handles this automatically (waits and retries)
- For high traffic: upgrade to Groq Dev tier or add OpenAI fallback

### "Frontend shows blank page"
- Check `NEXT_PUBLIC_API_URL` points to the correct backend URL
- Must be set **at build time** (baked into the Next.js bundle)
- Redeploy frontend after changing this variable

### "502 Bad Gateway"
- Backend is starting up (migrations running) — wait 30-60 seconds
- Check Railway logs for the backend service

---

## Estimated Railway Costs

| Service | Plan | Monthly Cost |
|---------|------|-------------|
| Backend | Starter | $5-10 |
| Frontend | Starter | $5 |
| PostgreSQL | Starter (1GB) | $5 |
| Redis | Starter (256MB) | $3 |
| **Total** | | **~$18-23/month** |

Railway also has a **Hobby Plan ($5/month credit)** that covers small projects entirely.

---

*Last updated: July 2026 | DesignMentor AI v2.1*
