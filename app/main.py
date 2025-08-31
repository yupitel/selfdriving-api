import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.cores.db_init import initialize_database, get_db_mode
from app.routers import measurements, datastreams, vehicles, pipelines, drivers, health, pipelinedata, pipelinestate, pipelinedependency, scenes
from app.schemas.base import BaseResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up application...")
    
    # Initialize database based on mode
    db_mode = get_db_mode()
    logger.info(f"Database mode: {db_mode}")
    
    try:
        initialize_database(mode=db_mode)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title="Self-Driving Data Collection API",
    description="API for managing self-driving vehicle measurement data",
    version="1.0.0",
    lifespan=lifespan
)


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(
            success=False,
            error=exc.detail,
            message=f"HTTP {exc.status_code}: {exc.detail}"
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content=BaseResponse(
            success=False,
            error="Validation Error",
            message="Request validation failed",
            data={"errors": errors}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=BaseResponse(
            success=False,
            error="Internal Server Error",
            message="An unexpected error occurred"
        ).model_dump()
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


# Include routers
app.include_router(health.router)
app.include_router(measurements.router)
app.include_router(datastreams.router)
app.include_router(vehicles.router)
app.include_router(pipelines.router)
app.include_router(drivers.router)
app.include_router(pipelinedata.router)
app.include_router(pipelinestate.router)
app.include_router(pipelinedependency.router)
app.include_router(scenes.router)

# Root endpoint
@app.get("/", response_model=BaseResponse)
async def root():
    """Root endpoint"""
    return BaseResponse(
        success=True,
        message="Self-Driving Data Collection API",
        data={
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/v1/health",
                "measurements": "/api/v1/measurements",
            "datastreams": "/api/v1/datastreams",
            "scenes": "/api/v1/scenes",
            "vehicles": "/api/v1/vehicles",
                "pipelines": "/api/v1/pipelines",
                "drivers": "/api/v1/drivers",
                "pipelinedata": "/api/v1/pipelinedata",
                "pipelinestates": "/api/v1/pipelinestates",
                "pipelinedependencies": "/api/v1/pipelinedependencies",
                "pipelinestate (legacy)": "/api/v1/pipelinestate",
                "pipelinedependency (legacy)": "/api/v1/pipelinedependency"
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
