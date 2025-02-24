"""
Database Seeding Script

This script initializes the database with sample data for employees and customers.
It is intended to be used for testing or setting up an initial environment.

Usage:
    Run this script to populate the database with predefined employees and customers.

Dependencies:
    - SQLAlchemy for ORM interactions
    - FastAPI application context for database connection
"""
import sys
import os

# Add project root to sys.path to allow module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from app.database import get_db 
from models import models
from app.security import hash_password
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Establish a database session
db: Session = next(get_db())

def add_if_not_exists(obj):
    """Add an object to the session only if it doesn’t already exist."""
    try:
        db.add(obj)
        db.commit()
    except IntegrityError:
        db.rollback()  # Ignore duplicate entry errors

# Define sample employees
employees = [
    models.Employee(id=4, username="John Doe", password_hash = "password1", role="Manager"),
    models.Employee(id=5, username="Jane Smith", password_hash = "password2", role="Teller")
]

# Define sample employees
customers = [
    models.Customer(id=101, name="Alice"),
    models.Customer(id=102, name="Bob")
]

for emp in employees:
    add_if_not_exists(emp)

for cust in customers:
    add_if_not_exists(cust)

print("Seed data added (existing records unchanged).")
