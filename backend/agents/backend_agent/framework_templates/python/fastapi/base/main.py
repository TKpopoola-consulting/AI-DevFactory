from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI(
    title="{{app_name}}",
    description="Auto-generated FastAPI backend",
    version="1.0.0"
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to {{app_name}} API"}

# Import routers
from api.v1.routers import api_router
app.include_router(api_router, prefix="/api/v1")