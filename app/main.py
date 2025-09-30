import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.cores.db_init import initialize_database, get_db_mode
from app.routers import measurements, datastreams, vehicles, pipelines, drivers, health, pipelinedata, pipelinestate, pipelinedependency, scenes, sensors, datasets
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
    description=(
        "API for managing self-driving vehicle measurement data.\n\n"
        "Important: Create endpoints are bulk-at-root. Send array-wrapped payloads to POST /{resource}.\n"
        "Legacy /bulk endpoints have been removed."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration (driven by environment variables)
origins_env = os.getenv("ALLOWED_ORIGINS", "")
methods_env = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS")
headers_env = os.getenv("ALLOWED_HEADERS", "*")
allow_credentials_env = os.getenv("CORS_ALLOW_CREDENTIALS", "false")

allowed_origins = [o.strip() for o in origins_env.split(",") if o.strip()] or [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
allowed_methods = [m.strip() for m in methods_env.split(",") if m.strip()] or ["*"]
if headers_env.strip() == "*":
    allowed_headers = ["*"]
else:
    allowed_headers = [h.strip() for h in headers_env.split(",") if h.strip()] or ["*"]
allow_credentials = allow_credentials_env.lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
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
app.include_router(sensors.router)
app.include_router(datasets.router)

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
                "datasets": "/api/v1/datasets",
                "scenes": "/api/v1/scenes",
                "vehicles": "/api/v1/vehicles",
                "pipelines": "/api/v1/pipelines",
                "drivers": "/api/v1/drivers",
                "sensors": "/api/v1/sensors",
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
