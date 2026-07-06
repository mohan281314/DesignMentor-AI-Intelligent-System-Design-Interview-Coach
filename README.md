# DesignMentor AI v2.1 🎓

> **The Most Advanced AI-Powered System Design Interview Coach**
>
> Multi-agent LLaMA 3.3 70B · Next.js 15 · FastAPI · PostgreSQL · Redis · JWT Auth · 7 Unique Features

---

## 🚀 What Makes v2.1 Unique

Most system design tools give you a generic design and a checklist. **DesignMentor AI v2.1 is different** — it feels like a personal FAANG coach who knows your weaknesses, remembers your history, and challenges you in ways that actually prepare you for the real thing.

### 7 Features You Won't Find Anywhere Else

| Feature | What It Does |
|---------|-------------|
| 🎭 **AI Persona Interviewers** | Practice with 7 distinct AI interviewers — each with a unique style, depth, and feedback tone |
| 💥 **Failure Mode Analyzer** | After designing a system, ask "What could go wrong?" — get chaos engineering experiments and a resilience score |
| 📊 **Experience-Aware Design** | Input your years of experience + tech stack → get a design calibrated to your exact seniority level |
| 🧠 **Memory-Powered Coach** | Your AI coach remembers your past mistakes, weak areas, and interview history across sessions |
| ⚔️ **Design Battle Mode** | Compete against the AI on the same topic — an impartial AI judge scores both and declares a winner |
| 🗺️ **Smart 30-Day Roadmap** | Personalised week-by-week learning plan based on your actual performance data and target companies |
| 🔍 **Design Critique Mode** | Submit your design for adversarial review from a Google, Amazon, Netflix, or Startup engineering lens |

---

## ✨ What's New in v2.0

| Feature | v1 | v2 |
|---|---|---|
| Authentication | ❌ None | ✅ JWT + OAuth (Google/GitHub) |
| Session storage | RAM (lost on restart) | ✅ Redis + PostgreSQL persistent |
| Interview history | ❌ None | ✅ Full history with scores |
| Performance tracking | ❌ None | ✅ Radar charts, trends, recommendations |
| Diagram types | 1 (flowchart) | ✅ 5 (C4, Sequence, ERD, DataFlow, Flowchart) |
| LLM providers | Groq only | ✅ Groq (default) + OpenAI fallback |
| Design quality | Single chain | ✅ Multi-agent (requirements → capacity → design → critic) |
| PDF export | ❌ None | ✅ Designs + interview reports |
| Sharing | ❌ None | ✅ Public links with expiration |
| Frontend | Vanilla HTML/CSS/JS | ✅ Next.js 15 + TypeScript + Tailwind + shadcn/ui |
| Rate limiting | ❌ None | ✅ Per-IP sliding window |
| API versioning | ❌ None | ✅ /api/v1/* with Swagger docs |
| Docker | ❌ None | ✅ Docker Compose (API + Postgres + Redis) |

---

## 🚀 Quick Start

### Option A — Local (no Docker)

```bash
# 1. Backend
pip install -r requirements.txt
# Edit .env (see .env.example)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. Frontend (new tab)
cd frontend-next
npm install --legacy-peer-deps
npm run dev
```

- Backend (+ legacy UI): http://localhost:8000
- New Next.js frontend:   http://localhost:3000

### Option B — Docker Compose (recommended)

```bash
cp .env.example .env    # fill in GROQ_API_KEY and SECRET_KEY
docker compose up -d    # starts API, PostgreSQL, Redis

# First-time DB setup
docker exec -it designmentor_api python scripts/init_db.py
```

Then visit http://localhost:8000

---

## 📁 Project Structure

```
DesignMentor-AI/
├── app/                      # FastAPI backend
│   ├── ai/                   # LLM providers + multi-agent orchestrator
│   │   ├── agents/           # RequirementsAgent, CapacityAgent, DesignAgent, CriticAgent
│   │   └── providers/        # Groq + OpenAI (with automatic fallback)
│   ├── api/v1/               # Versioned REST API
│   │   ├── auth.py           # Register, login, JWT refresh
│   │   ├── users.py          # Profile management
│   │   ├── designs.py        # Design CRUD + generation
│   │   ├── interviews.py     # Persistent interview sessions
│   │   ├── analytics.py      # Performance metrics + recommendations
│   │   ├── sharing.py        # Public share links
│   │   └── exports.py        # PDF export
│   ├── core/                 # Config, security, middleware, logging
│   ├── db/                   # SQLAlchemy base, Redis client, session manager
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic layer
│   ├── utils/                # PDF generator, utilities
│   ├── chains.py             # LangChain chains with retry + rate-limit handling
│   ├── main.py               # App factory with all routes
│   └── session_manager.py    # In-memory fallback for dev
│
├── frontend-next/            # Next.js 15 frontend
│   ├── app/                  # App Router pages
│   │   ├── page.tsx          # Landing page
│   │   ├── login/            # Authentication
│   │   ├── register/         # Registration
│   │   ├── dashboard/        # Analytics + recommendations
│   │   ├── design/           # System design generator
│   │   ├── interview/        # Mock interview
│   │   ├── diagrams/         # Architecture diagrams (5 types)
│   │   ├── evaluate/         # Answer evaluator
│   │   ├── feedback/         # Learning reports
│   │   ├── chat/             # Coaching chat
│   │   └── settings/         # Profile + theme
│   ├── components/           # Reusable UI components (shadcn/ui)
│   └── lib/                  # API client, Zustand auth store, utilities
│
├── frontend/                 # Original vanilla JS frontend (still works at /)
├── prompts/                  # All LLM prompt templates
│   ├── system.txt            # Base system prompt
│   ├── design_generator.txt  # Full system design
│   ├── diagram_*.txt         # 5 diagram type prompts
│   └── ...
├── alembic/                  # Database migrations
├── scripts/                  # DB init, seed data
├── Dockerfile                # Multi-stage backend image
├── docker-compose.yml        # Full stack (API + Postgres + Redis)
└── .env.example              # All environment variables documented
```

---

## 🔌 API Reference

### Base URL
- **Local**: `http://localhost:8000`
- **API Docs (Swagger)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication
```bash
# Register
POST /api/v1/auth/register
{"email": "you@example.com", "password": "password123"}

# Login → returns {access_token, refresh_token}
POST /api/v1/auth/login
{"email": "you@example.com", "password": "password123"}

# Use token
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Legacy endpoints (no auth needed — works with guest UI)
```
POST /design            → Generate system design
POST /interview/start   → Start mock interview
POST /interview/answer  → Submit answer + get evaluation
POST /evaluate          → One-shot answer evaluation
POST /diagram           → Generate Mermaid diagram (5 types)
POST /feedback          → Learning report
POST /chat              → Coaching chat
GET  /health            → Liveness check
```

### Authenticated endpoints (/api/v1/*)
```
GET  /api/v1/analytics/performance     → Radar chart data, scores, trends
GET  /api/v1/analytics/recommendations → Personalised topic suggestions
GET  /api/v1/designs/                  → List saved designs
POST /api/v1/designs/generate          → Generate + save design
GET  /api/v1/interviews/               → Interview history
GET  /api/v1/exports/designs/{id}/pdf  → Download design as PDF
GET  /api/v1/exports/interviews/{id}/pdf → Download interview report
POST /api/v1/share/create              → Create public share link
GET  /api/v1/share/{public_id}         → View shared resource
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required
GROQ_API_KEY=gsk_...
SECRET_KEY=<32+ random chars>   # openssl rand -hex 32

# Optional (with defaults)
DATABASE_URL=postgresql+psycopg2://designmentor:designmentor@localhost:5432/designmentor
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=                 # enables OpenAI fallback
LLM_PROVIDER=groq               # groq | openai
ENVIRONMENT=development         # development | production
```

---

## 🧪 Testing

```bash
# Backend
pytest tests/ -v

# Quick API test
python final_verification.py

# Frontend type-check
cd frontend-next
npx tsc --noEmit
```

---

## 🐳 Docker

```bash
# Start full stack
docker compose up -d

# With optional tools (pgAdmin + Redis Insight)
docker compose --profile tools up -d

# With Next.js frontend
docker compose --profile nextjs up -d

# Logs
docker compose logs -f api

# Stop
docker compose down
```

---

## 🔧 Tech Stack

### Backend
| Package | Version | Purpose |
|---|---|---|
| FastAPI | 0.115+ | Async web framework |
| LangChain | 0.3+ | LLM orchestration |
| LangChain-Groq | 0.2+ | Groq integration |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.13+ | Migrations |
| Redis | 5.0+ | Caching + sessions |
| python-jose | 3.3+ | JWT tokens |
| passlib | 1.7+ | Password hashing |
| ReportLab | 4.0+ | PDF generation |
| Pydantic | 2.x | Validation |

### Frontend (Next.js)
| Package | Purpose |
|---|---|
| Next.js 15 | App Router framework |
| TypeScript 5 | Type safety |
| Tailwind CSS 3 | Styling |
| Radix UI | Accessible components |
| Recharts | Analytics charts |
| TanStack Query | API state management |
| Zustand | Auth store |
| React Markdown | Markdown rendering |
| Mermaid.js | Diagram rendering |
| Sonner | Toast notifications |

---

## 🚢 Production Deployment

### Environment checklist
- [ ] `ENVIRONMENT=production`
- [ ] `SECRET_KEY` is 32+ random characters
- [ ] `DEBUG=false`
- [ ] `DB_ECHO=false`
- [ ] PostgreSQL is externally managed (RDS, Supabase, etc.)
- [ ] Redis is externally managed (ElastiCache, Upstash, etc.)
- [ ] CORS origins set to your domain

### Recommended platforms
- **Backend**: Railway, Render, Fly.io, AWS ECS
- **Frontend**: Vercel, Netlify, Cloudflare Pages
- **Database**: Supabase, Neon, PlanetScale, AWS RDS
- **Redis**: Upstash (free tier), Redis Cloud

### Gunicorn for production
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📊 Architecture Overview

```
Browser (Next.js 15)
    ↓  HTTPS / fetch()
FastAPI (port 8000)
    ├─ /api/v1/*        ← authenticated endpoints
    │       ↓
    │   Services Layer   ← business logic
    │       ↓
    │   SQLAlchemy ORM  ← PostgreSQL
    │       ↓
    │   Redis            ← sessions, cache, rate-limiting
    │
    ├─ /design, /chat, etc.  ← legacy endpoints (no auth)
    │       ↓
    │   LangChain Chains
    │       ↓
    │   Multi-Agent Orchestrator
    │       ↓
    │   Groq API  ←→  OpenAI API (fallback)
    │
    └─ /static          ← original vanilla JS frontend
```

---

## 🔐 Rate Limiting

The API has a built-in sliding-window rate limiter:

- **Default**: 60 requests / minute per IP
- **Burst**: 10 extra requests allowed
- **429 response**:
```json
{
  "detail": "Rate limit exceeded. Please wait before making more requests.",
  "retry_after_seconds": 60
}
```

Groq free tier also applies its own limit (30 req/min). The chains implement automatic retry with exponential back-off so users see a clean error rather than a crash.

---

## 🏆 v2.0 Checklist

- [x] PostgreSQL + SQLAlchemy models + Alembic migrations
- [x] Redis session manager (persistent, TTL-aware)
- [x] JWT authentication (access + refresh tokens)
- [x] User registration + login + OAuth-ready
- [x] User performance profiles (5-dimension scoring)
- [x] API v1 with full CRUD: designs, interviews, diagrams
- [x] Analytics: radar charts, trends, recommendations
- [x] Public share links with optional expiration
- [x] Multi-provider LLM (Groq default, OpenAI fallback)
- [x] Multi-agent design pipeline (4 agents)
- [x] 5 diagram types: Flowchart, C4, Sequence, ERD, Data Flow
- [x] PDF export for designs and interview reports
- [x] Next.js 15 frontend with TypeScript + Tailwind
- [x] Landing page, login, register pages
- [x] Dashboard with Recharts analytics
- [x] All 6 features: Design, Interview, Evaluate, Diagrams, Feedback, Chat
- [x] Settings: profile, theme (dark/light), password change
- [x] Rate limiting middleware
- [x] Security headers middleware
- [x] Request logging middleware
- [x] Docker + Docker Compose
- [x] Groq 429 retry with exponential back-off

---

*Built with ❤️ — FastAPI + LangChain + LLaMA 3.3 70B + Next.js 15*


---

## 🌟 v2.1 — Unique Features Deep Dive

### 🎭 1. AI Persona Interviewers

Practice with 7 distinct AI interviewer characters. Each has a unique background, questioning style, and feedback tone. The same system design question feels completely different depending on who's interviewing you.

| Persona | Background | Style |
|---------|-----------|-------|
| `google_staff` | Ex-Google Staff Engineer, built Search & YouTube infra | Deep technical drilling, scale-first |
| `meta_e5` | Meta E5, News Feed & messaging systems | Pragmatic, product-impact focused |
| `netflix_architect` | Netflix Principal, designed Chaos Engineering | Resilience-obsessed, failure-first |
| `amazon_sde3` | Amazon SDE-3, AWS Platform | Leadership Principles, customer obsession |
| `kind_mentor` | Engineering Coach, 20yr veteran | Supportive, hints not gotchas |
| `brutal_critic` | Ex-CTO of two unicorns | Zero tolerance for hand-waving |
| `startup_cto` | Series B CTO, ex-Stripe | Pragmatism, anti-over-engineering |

```bash
# Start interview with Netflix Architect
POST /api/v1/unique/persona-interview/start
{ "topic": "Netflix", "persona_id": "netflix_architect" }

# Submit answer and get in-character follow-up
POST /api/v1/unique/persona-interview/answer
{ "topic": "Netflix", "persona_id": "netflix_architect", "answer": "...", "turn_number": 1 }
```

---

### 💥 2. Failure Mode Analyzer

Stop designing systems that look good on paper but fail in production. After generating any design, submit it for a production-grade failure analysis. Get:

- **Critical failure modes** with blast radius, MTTR, and fixes
- **Cascading failure** scenarios
- **Chaos engineering experiments** to validate resilience
- **Resilience score** across 4 dimensions
- **Top 3 most dangerous gaps** in your design

```bash
POST /api/v1/unique/failure-analysis
{
  "topic": "Twitter",
  "design_summary": "# My Twitter Design\n## Architecture\n..."
}
```

---

### 📊 3. Experience-Aware Design Generator

Generic designs don't help. A Staff Engineer and a new grad need completely different things. Input your level, years of experience, and tech stack — get a design calibrated to exactly what's expected of you.

| Level | Description | What Changes |
|-------|-------------|-------------|
| `sde1` | 0-2 years | Basic components, monolith-first, simple CRUD |
| `sde2` | 2-4 years | Caching, basic horizontal scaling, queues |
| `sde3` | 5-8 years | Full distributed systems, deep trade-offs, CAP theorem |
| `staff` | 8-12 years | Platform thinking, cost optimization, cross-team |
| `principal` | 12+ years | Org-wide decisions, build vs buy, multi-region |

```bash
POST /api/v1/unique/design/experience-aware
{
  "topic": "Instagram",
  "level": "staff",
  "years_exp": 10,
  "tech_stack": "Python, PostgreSQL, Redis, AWS",
  "target_companies": "google"
}
```

---

### 🧠 4. Memory-Powered Personal Coach

Unlike every other chatbot, this coach **remembers you**. When authenticated, the coach knows:
- Your exact weak and strong areas from past interviews
- Every topic you've practiced and your scores on them
- Your total interview count and experience level
- Your learning goals and preferences

The result: responses like *"Last time you struggled with consistency when designing Twitter, so let's focus on that here"* — not generic advice.

```bash
POST /api/v1/unique/memory-coach
{ "message": "How should I approach database sharding?" }
# When authenticated: coach references your specific history
# When guest: still powerful, just not personalised
```

---

### ⚔️ 5. Design Battle Mode

The most engaging way to practice. You and the AI design the same system. An impartial AI judge then:
- Scores both designs on 5 criteria (1-10 each)
- Gives a head-to-head comparison
- Declares a winner with detailed reasoning
- Tells you exactly what to learn to beat the AI next time

```bash
POST /api/v1/unique/design-battle
{
  "topic": "Uber",
  "user_design": "# My Uber Design\n## Requirements\n..."
}
# Returns: ai_design, judgment with scores, winner, learning points
```

---

### 🗺️ 6. Smart 30-Day Learning Roadmap

Most study plans are generic. This one is built from your actual performance data:

- **Week-by-week breakdown** with daily 30-45 min tasks
- **Calibrated to your specific weak areas** (if you scored low on scalability, Week 1 targets that)
- **Company-specific prep** for your target companies
- **Realistic score targets** for each week
- **Curated resources** (not just "read DDIA" — specific chapters, videos, exercises)
- **Red flags** — the traps that derail candidates at your level

```bash
POST /api/v1/unique/roadmap
{
  "target_companies": "Google, Meta",
  "target_level": "Staff",
  "timeline_weeks": 6
}
```

---

### 🔍 7. Design Critique Mode

Submit any design for expert adversarial review in 5 different lenses:

| Mode | Focus |
|------|-------|
| `adversarial` | Maximum critique — finds every possible flaw |
| `google` | Scalability, engineering elegance, simplicity |
| `amazon` | Operational excellence, cost, customer impact |
| `netflix` | Resilience, chaos engineering, continuous delivery |
| `startup` | Pragmatism, speed, avoiding over-engineering |

Each critique gives: critical issues (must fix), significant issues (fix before scale), minor improvements, genuine praise, the hardest follow-up question, and a final hire signal verdict.

```bash
POST /api/v1/unique/design-critique
{
  "topic": "WhatsApp",
  "design": "# My WhatsApp Design\n...",
  "mode": "netflix"
}
```

---

## 🔌 v2.1 API Reference

All unique endpoints live under `/api/v1/unique/`:

```
GET  /api/v1/unique/personas              — list all AI persona interviewers
GET  /api/v1/unique/levels                — list experience levels
GET  /api/v1/unique/critique-modes        — list critique modes

POST /api/v1/unique/persona-interview/start   — start persona interview
POST /api/v1/unique/persona-interview/answer  — submit answer + get followup

POST /api/v1/unique/failure-analysis          — production failure analysis
POST /api/v1/unique/design/experience-aware   — level-calibrated design
POST /api/v1/unique/memory-coach              — memory-powered coaching chat
POST /api/v1/unique/design-battle             — user vs AI design battle
POST /api/v1/unique/roadmap                   — personalised 30-day plan
POST /api/v1/unique/design-critique           — adversarial design review
```

**All v2.1 endpoints work without authentication** (memory coach and roadmap auto-personalise when authenticated).

Explore interactively: **http://localhost:8000/docs** → tag `v2.1 Unique Features`

---

## 📊 v2.1 Technical Implementation

### New Files Added

```
app/
  chains_v21.py           — All 7 new AI chains
  api/v1/
    unique.py             — 11 new REST endpoints

prompts/
  persona_interviewer.txt      — Character-based interview prompt
  failure_mode_analysis.txt    — Production failure simulation
  experience_aware_design.txt  — Seniority-calibrated design
  memory_coach.txt             — Long-term memory coaching
  design_battle.txt            — Dual design judging
  learning_roadmap.txt         — Personalised study plan
  design_critique.txt          — Adversarial review
```

### Key Technical Choices

**Why prompts-first, not fine-tuning?**
The persona, experience level, and critique mode are all achieved through carefully engineered prompts — not fine-tuned models. This means: zero training cost, instant persona updates, and full control over the output format.

**Memory without a vector database**
The memory coach uses structured profile data from the existing `UserProfile` model (weak_topics, strong_topics, total_interviews, experience_level) — no external vector DB needed. This keeps the stack simple while delivering genuinely personalised responses.

**Design Battle: sequential not parallel**
The AI design is generated first, then judged alongside the user's design. Sequential generation ensures the AI doesn't inadvertently "see" the user's design when creating its own.

---

*v2.1 released: July 2026 | 11 new endpoints | 7 new prompts | 0 new dependencies*
