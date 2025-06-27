from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
import logging
from typing import Any, Optional
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from pymongo.errors import PyMongoError

from .core.config import settings
from .api.v1 import api_router
from .db.session import connect_to_mongo, close_mongo_connection
from .schemas.common import ErrorResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await connect_to_mongo()
    logger.info("Connected to MongoDB")
    
    yield
    
    # Shutdown: Close MongoDB connection
    await close_mongo_connection()
    logger.info("Closed MongoDB connection")

app = FastAPI(
    title="CortexSupport API Backend",
    version="1.0.0",
    contact={
        "name": "CortexSupport Team",
        "email": "support@cortexsupport.com"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://cortexsupport.com/terms"
    },
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication related endpoints"
        },
        {
            "name": "users",
            "description": "User management endpoints"
        }
    ],
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.BACKEND_CORS_ORIGINS == "*" else [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with a standardized response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            ErrorResponse(
                detail=exc.detail,
                code=getattr(exc, "code", None) or f"http_{exc.status_code}",
            ).model_dump(exclude_none=True)
        ),
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors with a standardized response format."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            ErrorResponse(
                detail="Validation Error",
                code="validation_error",
                errors={
                    "_schema": ["Invalid request format"],
                    "details": exc.errors(),
                },
            ).model_dump(exclude_none=True)
        ),
    )

@app.exception_handler(PyMongoError)
async def mongo_exception_handler(request: Request, exc: PyMongoError) -> JSONResponse:
    """Handle MongoDB related errors."""
    logger.error(f"MongoDB error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            ErrorResponse(
                detail="Database operation failed",
                code="database_error",
            ).model_dump(exclude_none=True)
        ),
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for any unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            ErrorResponse(
                detail="Internal server error",
                code="internal_server_error",
            ).model_dump(exclude_none=True)
        ),
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get(
    "/", 
    tags=["Root"],
    summary="Root endpoint",
    description="""
    Welcome endpoint that provides basic information about the API.
    """,
    response_description="Welcome message"
)
async def root():
    """
    Root endpoint that returns a welcome message.
    
    Returns:
        dict: A welcome message with the project name
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
