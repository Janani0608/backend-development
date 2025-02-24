"""
This module provides an authentication endpoint for employees in a banking system.

It allows employees to log in using their username and password, verifying credentials
and generating a JWT access token for authentication in subsequent requests.

Dependencies:
- FastAPI for API routing
- SQLAlchemy for database interactions
- Pydantic for request validation
- Security utilities for password verification and token creation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import verify_password, create_access_token
from datetime import timedelta
from pydantic import BaseModel
from models import models
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

class EmployeeLogin(BaseModel):
    username: str
    password: str
    

@router.post("/login")
def login(request: EmployeeLogin, db: Session = Depends(get_db)):
    """
    Authenticates an employee and returns an access token.

    Parameters:
    - request: EmployeeLogin (Pydantic model with username and password)
    - db: Database session (provided by FastAPI dependency injection)

    Returns:
    - A JSON object with an access token and token type if authentication is successful.
    - Raises HTTP 404 if the employee does not exist.
    - Raises HTTP 401 if the password is incorrect.
    """

    # Retrieve the employee from the database using the provided username
    employee = db.query(models.Employee).filter(models.Employee.username == request.username).first()
    if not employee:
        raise HTTPException(status_code = 404, detail = "Employee not found")
    if not verify_password(request.password, employee.password_hash):
        raise HTTPException(status_code = 401, detail = "Invalid username or password")

    access_token = create_access_token(data = {"sub": employee.username}, expires_delta = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}
