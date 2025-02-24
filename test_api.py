"""
Test Suite for Banking API

This module contains test cases for the Banking API using FastAPI's `TestClient`
and pytest framework. It includes tests for authentication, account management, 
transactions, and edge cases such as concurrency and security.

Dependencies:
    - FastAPI TestClient for API testing
    - Pytest for unit testing and fixture management
    - SQLAlchemy for database interactions
    - JWT for authentication token handling
    - Threading for concurrency testing
"""
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, GERMANY_TZ, TEST_DATABASE_URL
from app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models.models import Base, Account, Customer, Employee, Transaction
from datetime import timedelta, datetime, timezone
from threading import Thread
import threading
import json
import jwt
import pytest
import logging
import time

# -----------------------------------
# Database Setup for Testing
# -----------------------------------
engine = create_engine(TEST_DATABASE_URL, isolation_level="SERIALIZABLE")
TestingSessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

@pytest.fixture(autouse=True)
def override_get_db(db_session: Session):
    """Override the database dependency to use a test session."""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Create test database tables before tests and drop them after tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Provide a database session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI TestClient for API interaction
client = TestClient(app)

def create_test_access_token(employee: Employee):
    """
    Generate an access token for an employee.

    Args:
        employee (Employee): The employee instance.

    Returns:
        str: A JWT access token.
    """
    payload = {
        "sub": employee.username,
        "role": employee.role,
        "exp": int((datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@pytest.fixture(scope="function")
def setup_test_data(db_session: Session):
    """
    Pre-populate test database with sample customers, accounts, and employees.

    Returns:
        dict: A dictionary containing test employees for authentication.
    """

    #clear existing data
    db_session.query(Transaction).delete()
    db_session.query(Account).delete()
    db_session.query(Employee).delete()
    db_session.query(Customer).delete()
    db_session.commit()

    # Add customers
    customer1 = Customer(id=1, name="Arisha Barron")
    customer2 = Customer(id=2, name="Branden Gibson")
    db_session.add_all([customer1, customer2])
    db_session.commit()
    
    # Add accounts (using customer_id to link with Customer)
    account1 = Account(id=101, customer_id=1, balance=1000.00)
    account2 = Account(id=102, customer_id=2, balance=500.00)
    db_session.add_all([account1, account2])
    db_session.commit()
    
    # Add sample employees
    employee_manager = Employee(id=1, username="manager_user", password_hash="password1", role="manager")
    employee_teller = Employee(id=2, username="teller_user", password_hash="password2", role="teller")
    employee_admin = Employee(id=3, username="admin_user", password_hash="password3", role="admin")
    db_session.add_all([employee_manager, employee_teller, employee_admin])
    db_session.commit()
    
    return {
        "manager": employee_manager,
        "teller": employee_teller,
        "admin": employee_admin
    }


###############################################################################
#                        Basic Functional Tests                             #
###############################################################################
def test_view_customers_as_admin(setup_test_data):
    """Test that an admin can retrieve the list of all customers."""
    token = create_test_access_token(setup_test_data["admin"])
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/view-customers", headers=headers)
    assert response.status_code == 200  # Admins should have access
    data = response.json()
    assert isinstance(data, list)  # Response should be a list
    assert len(data) > 0  # Customers exist in DB
    assert data[0]["name"] in ["Arisha Barron", "Branden Gibson"]


def test_view_customers_as_non_admin(setup_test_data):
    """Test that a non-admin user is forbidden from viewing customers."""
    token = create_test_access_token(setup_test_data["teller"])  # Teller is NOT an admin
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/view-customers", headers=headers)
    assert response.status_code == 403  # Expecting "Forbidden"


def test_view_accounts_as_admin(setup_test_data):
    """Test that an admin can view accounts of a specific customer."""
    token = create_test_access_token(setup_test_data["admin"])
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/view-accounts/1", headers=headers)  # Customer ID 1
    assert response.status_code == 200  # Admin should be able to view
    data = response.json()
    assert isinstance(data, list)  # Response should be a list
    assert len(data) > 0  # Accounts exist for this customer
    assert data[0]["customer_id"] == 1  # Validate account belongs to customer


def test_view_accounts_as_non_admin(setup_test_data):
    """Test that a non-admin user cannot view accounts of a specific customer."""
    token = create_test_access_token(setup_test_data["teller"])  # Teller is NOT an admin
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/view-accounts/1", headers=headers)  # Customer ID 1
    assert response.status_code == 403  # Expecting "Forbidden"

def test_create_account(setup_test_data):
    """Test creating a new bank account with manager credentials."""
    token = create_test_access_token(setup_test_data["manager"])
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/accounts/", headers=headers, json={"customer_id": 1, "initial_deposit": 150.00})
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == 1

def test_get_balance(setup_test_data):
    """Test retrieving account balance with teller credentials."""
    token = create_test_access_token(setup_test_data["teller"])
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/accounts/101/balance", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 1000.00

def test_deposit_money(setup_test_data):
    """Test depositing money into an account with teller credentials."""
    token = create_test_access_token(setup_test_data["teller"])
    headers = {"Authorization": f"Bearer {token}"}
    deposit_amount = 200.00
    response = client.post("/deposit/", headers=headers, json={"account_id": 101, "amount": deposit_amount})
    assert response.status_code == 200
    data = response.json()
    assert data["curr_balance"] == 1000.00 + deposit_amount

def test_withdraw_money(setup_test_data):
    """Test withdrawing money from an account with teller credentials."""
    token = create_test_access_token(setup_test_data["teller"])
    headers = {"Authorization": f"Bearer {token}"}
    withdraw_amount = 300.00
    response = client.post("/withdraw/", headers=headers, json={"account_id": 101, "amount": withdraw_amount})
    assert response.status_code == 200
    data = response.json()
    assert data["curr_balance"] == 1000.00 - withdraw_amount

###############################################################################
#                             Edge Case Tests                                 #
###############################################################################
def test_view_accounts_non_existent_customer(setup_test_data):
    """Test that requesting accounts for a non-existent customer returns 404."""
    token = create_test_access_token(setup_test_data["admin"])  # Admin can access
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/view-accounts/999", headers=headers)  # Customer ID 999 doesn't exist
    assert response.status_code == 404  # Expecting "Not Found"

def test_create_account_nonexistent_customer(setup_test_data):
    """Test creating an account for a non-existent customer should return 404."""
    token = create_test_access_token(setup_test_data["manager"])
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/accounts/", headers=headers, json={"customer_id": 999, "initial_deposit": 150.00})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"

def test_withdraw_insufficient_funds(setup_test_data):
    """Test withdrawing more money than available should return error."""
    token = create_test_access_token(setup_test_data["teller"])
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/withdraw/", headers=headers, json={"account_id": 102, "amount": 1000.00})
    assert response.status_code == 400
    data = response.json()
    assert "Insufficient funds" in data["detail"]

def test_transfer_negative_amount(setup_test_data):
    """Test transferring a negative amount should be rejected."""
    token = create_test_access_token(setup_test_data["manager"])
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/transfer/", headers=headers, json={"from_account": 101, "to_account": 102, "amount": -50.00})
    assert response.status_code == 400
    data = response.json()
    assert "Amount must be greater than zero" in data["detail"]

def test_transfer_to_same_account(setup_test_data):
    """Test transferring money to the same account should be invalid."""
    token = create_test_access_token(setup_test_data["manager"])
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/transfer/", headers=headers, json={"from_account": 101, "to_account": 101, "amount": 50.00})
    assert response.status_code == 400
    data = response.json()
    assert "Cannot transfer money to the same account" in data["detail"]

###############################################################################
#                             Security Tests                                  #
###############################################################################

def test_create_account_unauthorized(setup_test_data):
    """Test that a teller is not authorized to create an account."""
    token = create_test_access_token(setup_test_data["teller"])
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/accounts/", headers=headers, json={"customer_id": 1, "initial_deposit": 150.00})
    # Expecting 403 Forbidden since teller role should not allow account creation.
    assert response.status_code == 403

def test_transfer_unauthorized(setup_test_data):
    """Test that a teller is not authorized to transfer funds."""
    token = create_test_access_token(setup_test_data["teller"])
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/transfer/", headers=headers, json={"from_account": 101, "to_account": 102, "amount": 50.00})
    assert response.status_code == 403

def test_access_with_invalid_token(setup_test_data):
    """Test access with an invalid token returns 401 Unauthorized."""
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/accounts/101/balance", headers=headers)
    assert response.status_code == 401

###############################################################################
#                   Concurrency & Performance Tests                           #
###############################################################################

@pytest.mark.parametrize("amount", [10, 50, 100])
def test_concurrent_transfers(setup_test_data, amount):
    """Test concurrent transfers to ensure atomicity and consistency."""
    token = create_test_access_token(setup_test_data["manager"])
    headers = {"Authorization": f"Bearer {token}"}

    success_counter = 0
    counter_lock = threading.Lock()
    
    def make_transfer():
        nonlocal success_counter
        response = client.post("/transfer/", headers=headers, json={
            "from_account": 101,
            "to_account": 102,
            "amount": amount
        })
        if response.status_code == 200:
            with counter_lock:
                success_counter += 1
        else:
            logging.info(f"Transfer failed with status {response.status_code}")
    
    threads = [Thread(target=make_transfer) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Give a short delay to ensure all transactions are fully committed
    time.sleep(1)
    
    balance1 = client.get("/accounts/101/balance", headers=headers).json()["balance"]
    balance2 = client.get("/accounts/102/balance", headers=headers).json()["balance"]
    
    # The inferred number of transfers based on account 101 should be consistent:
    transfers_occurred = int((1000 - balance1) / amount)
    expected_balance2 = 500 + transfers_occurred * amount
    expected_balance1 = 1000 + transfers_occurred * amount

    total_funds = balance1 + balance2

    # Invariant: Total funds should remain constant.
    assert total_funds == 1500, f"Total funds should remain 1500, got {total_funds}"
    assert balance1 == expected_balance1, f"Expected account 101 balance {expected_balance1}, got {balance1}"
    assert balance2 == expected_balance2, f"Expected account 102 balance {expected_balance2}, got {balance2}"
