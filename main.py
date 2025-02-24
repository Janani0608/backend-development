"""
Main Application Entry Point

This module initializes the FastAPI application, sets up API routes, and 
ensures database models are properly linked.

Dependencies:
    - FastAPI for building the API
    - SQLAlchemy for database interactions
    - Application-specific modules (auth, accounts)
"""
from fastapi import FastAPI
from app.database import engine
from models import models
from routes import auth, accounts

# -----------------------------------
# FastAPI Application Initialization
# -----------------------------------
app = FastAPI(
    title="Banking API",
    description="A simple banking API for managing customers, accounts, and transactions.",
    version="1.0.0"
)


# -----------------------------------
# Register API Routes
# -----------------------------------
app.include_router(auth.router)# Authentication-related routes
app.include_router(accounts.router) # Account management routes

# -----------------------------------
# Root Endpoint
# -----------------------------------
@app.get("/", tags=["General"])
def home():
    """Root endpoint that returns a welcome message."""
    return{"message": "Welcome to the Bank"}