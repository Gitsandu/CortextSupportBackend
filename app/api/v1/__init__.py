from fastapi import APIRouter
from .endpoints import users, auth

# Main API router for v1 endpoints
api_router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        500: {"description": "Internal server error"}
    }
)

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users")
