from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from db.database import Base, engine
import models  # noqa: F401
from routers import auth, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up TaskFlow API...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified OK")
    except Exception as e:
        logger.error(f"Database init failed: {e}")
        raise
    yield
    # Shutdown
    logger.info("Shutting down TaskFlow API...")


app = FastAPI(
    title="TaskFlow – Task Manager API",
    description=(
        "A simple task manager REST API with JWT authentication.\n\n"
        "## Authentication\n"
        "1. **POST /register** – create an account\n"
        "2. **POST /login** – get a JWT token\n"
        "3. Add `Authorization: Bearer <token>` to all task requests\n\n"
        "## Tasks\n"
        "Full CRUD with pagination and completion filtering."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)

# Serve frontend static files
_frontend = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
logger.info(f"Frontend path: {_frontend} | exists: {os.path.isdir(_frontend)}")

if os.path.isdir(_frontend):
    @app.get("/", include_in_schema=False)
    def root():
        return FileResponse(os.path.join(_frontend, "index.html"))

    app.mount("/app", StaticFiles(directory=_frontend, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    def root():
        return {"message": "TaskFlow API is running. Visit /docs for API documentation."}


@app.get("/health", tags=["Health"], summary="Health check")
def health():
    """Returns OK if the service is running."""
    return {"status": "ok"}
