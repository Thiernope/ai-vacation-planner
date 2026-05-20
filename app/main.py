from fastapi import FastAPI

from app.api.routes.auth import auth_router
from app.api.routes.users import users_router

app = FastAPI(
    title="AI Vacation Planner API",
    description="Backend service for creating trips and storing itineraries.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def read_health_status() -> dict[str, str]:
    """Return a simple status payload so deployments can probe the service."""
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(users_router)
