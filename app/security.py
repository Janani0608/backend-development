from passlib.context import CryptContext
import jwt
import logging
from config import GERMANY_TZ, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta, timezone
from models import models
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from sqlalchemy.orm import Session

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# Password hashing configuration using bcrypt
pwd_hasher = CryptContext(schemes = ["bcrypt"], deprecated = "auto", bcrypt__ident="2b")

def hash_password(password: str) -> str:
    """
    Hashes the given password using bcrypt.

    Args:
        password (str): The plain-text password.

    Returns:
        str: The hashed password.
    """
    return pwd_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the provided plain-text password matches the stored hashed password.

    Args:
        plain_password (str): The password entered by the user.
        hashed_password (str): The stored password hash.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_hasher.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generates a JWT access token with an expiration time.

    Args:
        data (dict): The data to encode in the token (e.g., user details).
        expires_delta (timedelta, optional): Token expiration duration. Defaults to `ACCESS_TOKEN_EXPIRE_MINUTES`.

    Returns:
        str: The encoded JWT access token.
    """
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow().replace(tzinfo=timezone.utc) + expires_delta

    # Convert expire time to Germany timezone for logging
    germany_expire = expire.astimezone(GERMANY_TZ)
    logging.info(f"Token expires at: {germany_expire.strftime('%Y-%m-%d %H:%M:%S %Z')} (Germany Time)")

    to_encode = data.copy()
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

def decode_access_token(access_token: str):
    """
    Decodes and validates a JWT access token.

    Args:
        access_token (str): The JWT token to decode.

    Returns:
        dict | None: The decoded token payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_employee(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Authenticates the current employee based on the provided JWT token.

    Args:
        token (str): The JWT token provided by the user.
        db (Session): The database session.

    Returns:
        models.Employee: The authenticated employee object.

    Raises:
        HTTPException: If the token is invalid, expired, or the employee is not found.
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code = 401, detail = "Session expired, login again")
    
    username = payload.get("sub")
    employee = db.query(models.Employee).filter(models.Employee.username == username).first()
    if not employee:
        raise HTTPException(status_code = 401, detail = "Employee not found")
    
    return employee




