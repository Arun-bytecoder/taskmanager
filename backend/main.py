from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from db.database import Base, engine
import models  # noqa: F401 – registers all models before create_all
from routers import auth, tasks

# Create all tables on startup
Base.metadata.create_all(bind=engine)

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
    contact={"name": "TaskFlow"},
)

# Allow all origins – frontend may be served from a different port (Live Server etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)

# Serve the frontend from FastAPI so http://localhost:8000 shows the UI
_frontend = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.isdir(_frontend):
    @app.get("/", include_in_schema=False)
    def root():
        return FileResponse(os.path.join(_frontend, "index.html"))

    app.mount("/app", StaticFiles(directory=_frontend, html=True), name="frontend")


@app.get("/health", tags=["Health"], summary="Health check")
def health():
    """Returns OK if the service is running."""
    return {"status": "ok"}
