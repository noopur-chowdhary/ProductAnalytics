from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import analytics, decisions, health, overview, propensity, uplift

app = FastAPI(
    title="Product Pulse API",
    version="0.1.0",
    description="Analytics, experimentation, propensity, uplift, and decision endpoints for Product Pulse.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(overview.router, prefix="/api")
app.include_router(analytics.router, prefix="/api/analytics")
app.include_router(propensity.router, prefix="/api/propensity")
app.include_router(uplift.router, prefix="/api/uplift")
app.include_router(decisions.router, prefix="/api")
