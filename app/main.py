"""
DesignMentor AI v2.0 — FastAPI application entry point.

Legacy endpoints (preserved for backward compatibility):
  GET  /health
  POST /design
  POST /interview/start
  POST /interview/answer
  POST /evaluate
  POST /diagram
  POST /feedback
  POST /chat
  DELETE /session/{session_id}

New v1 API (authenticated, persistent):
  /api/v1/auth/*     — registration, login, OAuth
  /api/v1/users/*    — profile management
  /api/v1/designs/*  — saved designs
  /api/v1/interviews/* — persistent interviews
  /api/v1/analytics/* — performance tracking
"""

from __future__ import annotations

import logging
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import session_manager as sm
from app.chains import (
    run_chat_chain,
    run_design_chain,
    run_diagram_chain,
    run_evaluation_chain,
    run_feedback_chain,
    run_interview_start_chain,
    run_next_question_chain,
)
from app.schemas_legacy import (
    ChatRequest,
    ChatResponse,
    DesignRequest,
    DesignResponse,
    DiagramRequest,
    DiagramResponse,
    EvaluateRequest,
    EvaluateResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    InterviewAnswerRequest,
    InterviewAnswerResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

MAX_INTERVIEW_TURNS = 5
_META_TOPIC  = "interview_topic"
_META_TURNS  = "interview_turns"
_META_LAST_Q = "interview_last_question"


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from app.core.config import get_settings as _gs
    _s = _gs()
    logger.info("DesignMentor AI v2.0 starting up… [env=%s]", _s.environment)

    # Run Alembic migrations in production; create tables directly in dev/test
    try:
        if _s.is_production:
            import subprocess, sys
            logger.info("Running Alembic migrations…")
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode != 0:
                logger.error("Alembic migration failed:\n%s", result.stderr)
            else:
                logger.info("Migrations applied successfully.")
        else:
            from app.db.base import create_tables
            create_tables()
            logger.info("Database tables ready.")
    except Exception as exc:
        logger.warning("DB setup error (auth endpoints may be unavailable): %s", exc)

    await sm.start_cleanup_task()

    # Connect Redis (non-fatal if unavailable in dev)
    try:
        from app.db.redis import redis_client
        await redis_client.connect()
        logger.info("Redis connected.")
    except Exception as exc:
        logger.warning("Redis unavailable (in-memory sessions will be used): %s", exc)

    yield

    logger.info("DesignMentor AI shutting down.")
    try:
        from app.db.redis import redis_client
        await redis_client.close()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    from app.core.config import get_settings as _get_settings
    _settings = _get_settings()

    # In production hide docs behind a flag
    docs_url   = "/docs"   if not _settings.is_production else None
    redoc_url  = "/redoc"  if not _settings.is_production else None

    app = FastAPI(
        title="DesignMentor AI",
        description=(
            "AI-powered System Design Interview Coach v2.0 — "
            "Generate designs, run mock interviews, evaluate answers, "
            "produce architecture diagrams, and get personalised feedback."
        ),
        version="2.0.0",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
    )

    # ---- CORS --------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # Allow all in dev; tighten via CORS_ORIGINS in production
        allow_credentials=False,  # Must be False when allow_origins=["*"]
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Security + rate limiting + request logging -----------------
    from app.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware, SecurityHeadersMiddleware

    if _settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=_settings.rate_limit_requests_per_minute,
            burst=_settings.rate_limit_burst,
        )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    # ---- Rate-limit + generic exception handlers ---------------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Already-formatted HTTPExceptions bubble through normally
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        logger.error("Unhandled exception: %s\n%s", exc, traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected server error occurred."},
        )

    # ---- Static files & legacy frontend --------------------------------
    frontend_path = Path(__file__).parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_root():
        index_file = frontend_path / "index.html"
        if not index_file.exists():
            return JSONResponse(content={"message": "DesignMentor AI v2.0 — API running"})
        return FileResponse(str(index_file))

    # ---- New v1 API router -------------------------------------------
    try:
        from app.api.v1 import api_router
        app.include_router(api_router, prefix="/api/v1")
        logger.info("Loaded API v1 router.")
    except ImportError as exc:
        logger.warning("Could not load v1 API router (some deps missing): %s", exc)

    # ==================================================================
    # LEGACY ENDPOINTS  (kept for backward compatibility)
    # ==================================================================

    @app.get("/health", response_model=HealthResponse, tags=["Meta"])
    async def health() -> HealthResponse:
        return HealthResponse()

    @app.get("/api/v1/health/detailed", tags=["Meta"], summary="Detailed system health")
    async def health_detailed():
        """Extended health check with Redis and config details."""
        import sys
        from datetime import datetime

        redis_ok = False
        try:
            from app.db.redis import redis_client
            await redis_client.set("_health_check", "1", ex=5)
            redis_ok = True
        except Exception:
            pass

        return {
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "python_version": sys.version.split()[0],
            "services": {
                "api": "healthy",
                "redis": "healthy" if redis_ok else "unavailable",
                "llm_provider": _settings.llm_provider,
            },
            "features": {
                "rate_limiting": _settings.rate_limit_enabled,
                "analytics":     _settings.analytics_enabled,
                "pdf_export":    _settings.pdf_export_enabled,
            },
        }

    # ---- Design Generator --------------------------------------------
    @app.post("/design", response_model=DesignResponse, tags=["Design"])
    async def generate_design(req: DesignRequest) -> DesignResponse:
        session_id, _ = sm.get_or_create_session(req.session_id, req.topic)
        design = await run_design_chain(req.topic)
        sm.add_message(session_id, "user", f"Design {req.topic}")
        sm.add_message(session_id, "assistant", design)
        return DesignResponse(session_id=session_id, topic=req.topic, design=design)

    # ---- Interview ---------------------------------------------------
    @app.post("/interview/start", response_model=InterviewStartResponse, tags=["Interview"])
    async def start_interview(req: InterviewStartRequest) -> InterviewStartResponse:
        session_id, _ = sm.get_or_create_session(req.session_id, req.topic)
        sm.set_metadata(session_id, _META_TOPIC, req.topic)
        sm.set_metadata(session_id, _META_TURNS, 0)
        first_question = await run_interview_start_chain(req.topic)
        sm.set_metadata(session_id, _META_LAST_Q, first_question)
        sm.add_message(session_id, "assistant", first_question)
        return InterviewStartResponse(session_id=session_id, topic=req.topic, first_question=first_question)

    @app.post("/interview/answer", response_model=InterviewAnswerResponse, tags=["Interview"])
    async def submit_answer(req: InterviewAnswerRequest) -> InterviewAnswerResponse:
        session = sm.get_session(req.session_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired. Start a new interview via /interview/start.",
            )
        topic         = sm.get_metadata(req.session_id, _META_TOPIC, "the system")
        last_question = sm.get_metadata(req.session_id, _META_LAST_Q, "")
        turns         = sm.get_metadata(req.session_id, _META_TURNS, 0)

        sm.add_message(req.session_id, "user", req.answer)
        evaluation = await run_evaluation_chain(question=last_question, user_answer=req.answer)
        sm.add_message(req.session_id, "assistant", evaluation)

        turns += 1
        sm.set_metadata(req.session_id, _META_TURNS, turns)

        is_complete   = turns >= MAX_INTERVIEW_TURNS
        next_question = None

        if not is_complete:
            history_text  = sm.get_history_as_text(req.session_id)
            next_question = await run_next_question_chain(topic, history_text)
            sm.set_metadata(req.session_id, _META_LAST_Q, next_question)
            sm.add_message(req.session_id, "assistant", next_question)

        return InterviewAnswerResponse(
            session_id=req.session_id,
            evaluation=evaluation,
            next_question=next_question,
            is_complete=is_complete,
        )

    # ---- Evaluate ----------------------------------------------------
    @app.post("/evaluate", response_model=EvaluateResponse, tags=["Evaluation"])
    async def evaluate_answer(req: EvaluateRequest) -> EvaluateResponse:
        evaluation = await run_evaluation_chain(
            question=req.question,
            user_answer=req.user_answer,
            reference=req.reference,
        )
        return EvaluateResponse(evaluation=evaluation)

    # ---- Diagram -----------------------------------------------------
    @app.post("/diagram", response_model=DiagramResponse, tags=["Design"])
    async def generate_diagram(req: DiagramRequest) -> DiagramResponse:
        result = await run_diagram_chain(req.topic, req.design_summary, req.diagram_type)
        return DiagramResponse(
            topic=req.topic,
            diagram_type=result.get("diagram_type", "flowchart"),
            mermaid_code=result["mermaid_code"],
            explanation=result["explanation"],
            suggestions=result["suggestions"],
        )

    # ---- Feedback ----------------------------------------------------
    @app.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
    async def get_feedback(req: FeedbackRequest) -> FeedbackResponse:
        history_text = sm.get_history_as_text(req.session_id) if req.session_id else ""
        report = await run_feedback_chain(req.topic, history_text)
        return FeedbackResponse(topic=req.topic, report=report)

    # ---- Chat --------------------------------------------------------
    @app.post("/chat", response_model=ChatResponse, tags=["Chat"])
    async def chat(req: ChatRequest) -> ChatResponse:
        session_id, _ = sm.get_or_create_session(req.session_id)
        history = sm.get_history(session_id)
        reply   = await run_chat_chain(req.message, history)
        sm.add_message(session_id, "user", req.message)
        sm.add_message(session_id, "assistant", reply)
        return ChatResponse(session_id=session_id, reply=reply)

    # ---- Session management ------------------------------------------
    @app.delete("/session/{session_id}", tags=["Meta"], status_code=status.HTTP_204_NO_CONTENT)
    async def delete_session(session_id: str) -> None:
        existed = sm.delete_session(session_id)
        if not existed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    return app


# ---------------------------------------------------------------------------
# App instance (used by uvicorn / Gunicorn)
# ---------------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    import uvicorn
    from app.config import get_settings
    s = get_settings()
    uvicorn.run("app.main:app", host=s.host, port=s.port, reload=True)
