"""
Banking System API Module

This module provides various banking operations such as creating accounts, 
retrieving balances, handling deposits, withdrawals, and fund transfers. 
It also includes utilities for transaction safety and rollback mechanisms.

Dependencies:
- FastAPI for API routing
- SQLAlchemy for database interactions
- Pydantic for request validation
- Logging for error handling and debugging
- Security utilities for authentication and role-based access control
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.database import get_db
from models import models
from pydantic import BaseModel
from typing import List
from config import GERMANY_TZ, MAX_RETRIES
from app.security import verify_password, decode_access_token, get_current_employee
from app.role_dependency import require_role
import datetime
import logging

router = APIRouter()

# ------------------------------------
# Pydantic Schemas for API Requests
# ------------------------------------
class CreateAccount(BaseModel):
    """Request schema for creating a new bank account."""
    customer_id: int
    initial_deposit: float

class TransferRequest(BaseModel):
    """Request schema for transferring money between accounts."""
    from_account: int
    to_account: int
    amount: float

class DepositWithdrawRequest(BaseModel):
    """Request schema for deposit and withdrawal operations."""
    account_id: int
    amount: float

# ------------------------------------
# Pydantic Schemas for API Responses
# ------------------------------------
class CreateAccountResponse(BaseModel):
    """Response schema for account creation."""
    message: str
    account_id: int
    customer_id: int

class BalanceResponse(BaseModel):
    """Response schema for retrieving account balance."""
    customer_id: int
    account_id: int
    balance: float

class TransactionResponse(BaseModel):
    """Response schema for deposit and withdrawal transactions."""
    message: str
    amount: float
    account_id: int
    curr_balance: float

class TransferResponse(BaseModel):
    """Response schema for money transfers."""
    message: str
    timestamp: str

class TransactionRecord(BaseModel):
    """Schema for a single transaction record."""
    from_account: int
    to_account: int
    amount: float
    transaction_time: str

class TransactionHistoryResponse(BaseModel):
    """Response schema for fetching transaction history."""
    transactions: List[TransactionRecord]

# ------------------------------------
# Utility Functions
# ------------------------------------
def reset_db_session(db: Session) -> Session:
    """Rollback and close the current DB session, and return a fresh session."""
    try:
        db.rollback()
    except Exception as rollback_err:
        logging.error(f"Rollback error: {rollback_err}")
    finally:
        db.close()
    # Return a new session from the dependency override generator:
    return next(get_db())

def safe_rollback(db: Session):
    """Safely rollback the session only if it is active."""
    try:
        if db.in_transaction():  # Ensure rollback only occurs if a transaction is active
            db.rollback()
        else:
            logging.warning("Skipping rollback because session is inactive")
    except Exception as rollback_err:
        logging.error(f"Rollback error: {rollback_err}")

# ---------------------------------------------------------------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------------------------------------------------------------
@router.get("/view-customers")
def view_customers(current_employee: models.Employee = Depends(get_current_employee), db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()

    """Retrieve a list of all customers."""
    return customers

@router.get("/view-accounts/{customer_id}")
def view_accounts(customer_id: int, current_employee: models.Employee = Depends(get_current_employee), db: Session = Depends(get_db)):
    accounts = db.query(models.Account).filter(models.Account.customer_id == customer_id).all()

    """Retrieve all accounts for a given customer."""
    return accounts

@router.post("/accounts/", response_model = CreateAccountResponse, dependencies = [Depends(require_role("manager"))])
def create_account(request: CreateAccount, db: Session = Depends(get_db)):
    """Create a new bank account for a customer."""
    customer = db.query(models.Customer).filter(models.Customer.id == request.customer_id).first()

    if not customer:
        raise HTTPException(status_code = 404, detail = "User not found")
    
    new_account = models.Account(customer_id = request.customer_id, balance = request.initial_deposit)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return {"message": "Account created successfully", "account_id": new_account.id, "customer_id": new_account.customer_id}

@router.get("/accounts/{account_id}/balance", response_model = BalanceResponse, dependencies = [Depends(require_role("teller"))])
def get_balance(account_id: int, db: Session = Depends(get_db)):
    """Retrieve the balance of a specific account."""
    account = db.query(models.Account).filter(models.Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code = 404, detail = "Account not found")
    
    return {"customer_id": account.customer_id, "account_id": account_id, "balance": account.balance}

@router.post("/deposit/", response_model = TransactionResponse, dependencies = [Depends(require_role("teller"))])
def deposit_money(request: DepositWithdrawRequest, db: Session = Depends(get_db)):
    """Deposit money into an account."""
    if request.amount <=0:
        raise HTTPException(status_code = 400, detail = "Amount must be greater than zero")

    account = db.query(models.Account).filter(models.Account.id == request.account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        account.balance += request.amount
        db.commit()
        db.refresh(account)
        return {"message": "Amount credited to the account", "amount": request.amount, "account_id": request.account_id, "curr_balance": account.balance}
    except Exception as e:
        safe_rollback()
        logging.info(f"Unexpected error: {e}")  # Log the error
        raise HTTPException(status_code = 500, detail = "Internal server error")

@router.post("/withdraw/", response_model = TransactionResponse, dependencies = [Depends(require_role("teller"))])
def withdraw_money(request: DepositWithdrawRequest, db: Session = Depends(get_db)):
    """Withdraw money from an account."""
    if request.amount <=0:
        raise HTTPException(status_code = 400, detail = "Amount must be greater than zero")

    account = db.query(models.Account).filter(models.Account.id == request.account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if request.amount > account.balance:
        raise HTTPException(status_code = 400, detail = "Insufficient funds for withdrawal")
    
    try:
        account.balance -= request.amount
        db.commit()
        db.refresh(account)
        return {"message": "Amount debited from the account", "amount": request.amount, "account_id": request.account_id, "curr_balance": account.balance}
    except Exception as e:
        safe_rollback() #To prevent incorrectly updating the record when a transaction fails
        logging.info(f"Unexpected error: {e}")  # Log the error
        raise HTTPException(status_code = 500, detail = "Internal server error")
 
@router.post("/transfer/", response_model = TransferResponse, dependencies = [Depends(require_role("manager"))])
def transfer_money(request: TransferRequest, current_employee: models.Employee = Depends(get_current_employee), db: Session = Depends(get_db)):
    """Transfer money in between accounts"""
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    if request.from_account == request.to_account:
        raise HTTPException(status_code=400, detail="Cannot transfer money to the same account")

    retries = 0

    while retries < MAX_RETRIES:
        try:
            logging.info(f"Attempting transfer: {request.from_account} -> {request.to_account} for amount {request.amount}")
            
            if request.from_account < request.to_account:
                db.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")  # Ensures transactions execute in sequence
                from_account = db.query(models.Account).filter(models.Account.id == request.from_account).with_for_update().first()
                to_account = db.query(models.Account).filter(models.Account.id == request.to_account).with_for_update().first()
            else:
                db.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")  # Ensures transactions execute in sequence
                to_account = db.query(models.Account).filter(models.Account.id == request.to_account).with_for_update().first()
                from_account = db.query(models.Account).filter(models.Account.id == request.from_account).with_for_update().first()

            if not from_account or not to_account:
                raise HTTPException(status_code=404, detail="One or both accounts not found")

            if from_account.balance < request.amount:
                raise HTTPException(status_code=400, detail="Insufficient funds for transfer")

            logging.info(f"Before update: from_account.balance={from_account.balance}, to_account.balance={to_account.balance}")

            from_account.balance -= request.amount
            to_account.balance += request.amount

            logging.info(f"After update (pre-commit): from_account.balance={from_account.balance}, to_account.balance={to_account.balance}")

            transaction = models.Transaction(
                from_account=request.from_account,
                to_account=request.to_account,
                amount=request.amount,
                timestamp=datetime.datetime.now(GERMANY_TZ)
            )
            db.add(transaction)
            db.commit()
            db.refresh(from_account)
            db.refresh(to_account)
            logging.info(f"After commit: from_account.balance={from_account.balance}, to_account.balance={to_account.balance}")
            logging.info("Transaction successful")

            return {"message": "Transaction successful", "timestamp": transaction.timestamp.isoformat()}

        except OperationalError:
            #To prevent the sessions becoming invalid after a rollback in a high concurrency situation
            if db.is_active:
                safe_rollback(db)
            else:
                db = reset_db_session(db)  # Reset session only if it’s invalid
            retries += 1
            if retries >= MAX_RETRIES:
                raise HTTPException(status_code=500, detail="Database transaction error, try again later")
            time.sleep(0.5)  # Small delay before retrying to reduce contention

        except Exception as e:
            #To ensure uniform recovery so that retries or concurrent requests do not use a stale session
            if db.is_active:
                safe_rollback(db)
            else:
                db = reset_db_session(db)  # Reset session only if it’s invalid
            logging.info(f"Unexpected error: {e}")  # Log the error
            raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/accounts/{account_id}/transactions", response_model = TransactionHistoryResponse, dependencies = [Depends(require_role("manager"))])
def get_transactions(account_id: int, current_employee: models.Employee = Depends(get_current_employee), db: Session = Depends(get_db)):
    """Retrieve transaction history for an account."""
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code = 404, detail = "Account not found")
    
    #Transactions are fetched and sorted from most recent to least recent
    transactions = db.query(models.Transaction).filter(
        (models.Transaction.from_account == account_id) |
        (models.Transaction.to_account == account_id)
    ).order_by(models.Transaction.timestamp.desc()).all()
    
    return { "transactions": [
        {
            "from_account": t.from_account, 
            "to_account": t.to_account, 
            "amount": t.amount, 
            "transaction_time": t.timestamp.astimezone(GERMANY_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
        } for t in transactions]
    }



