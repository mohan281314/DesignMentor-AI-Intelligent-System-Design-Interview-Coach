"""API v1 — all authenticated endpoints."""

from fastapi import APIRouter

from app.api.v1 import auth, users, designs, interviews, analytics, sharing, exports, unique

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(designs.router)
api_router.include_router(interviews.router)
api_router.include_router(analytics.router)
api_router.include_router(sharing.router)
api_router.include_router(exports.router)
api_router.include_router(unique.router)   # v2.1 unique features
