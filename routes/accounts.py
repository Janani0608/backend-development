from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from models import models
from pydantic import BaseModel
from typing import List
from config import GERMANY_TZ
import datetime

router = APIRouter()

#Pydantic schemas for data validation
class CreateAccount(BaseModel):
    customer_id: int
    initial_deposit: float

class TransferRequest(BaseModel):
    from_account: int
    to_account: int
    amount: float

#API endpoint to create a new account
@router.post("/accounts/", response_model = dict)
def create_account(account: CreateAccount, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == account.customer_id).first()
    if not customer:
        raise HTTPException(status_code = 404, detail = "Customer not found")
    
    new_account = models.Account(customer_id = account.customer_id, balance = account.initial_deposit)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return {"message": "Account created successfully", "account_id": account.customer_id}

#API endpoint to transfer money between accounts
@router.post("/transfer/")
def transfer_money(request: TransferRequest, db: Session = Depends(get_db)):
    from_account = db.query(models.Account).filter(models.Account.id == request.from_account).first()
    to_account = db.query(models.Account).filter(models.Account.id == request.to_account).first()

    if not from_account or not to_account:
        raise HTTPException(status_code = 404, detail = "One or both the accounts not found")
    
    if from_account.balance < request.amount:
        raise HTTPException(status_code = 404, detail = "Requested transfer not possible due to insufficient funds")

    from_account.balance -= request.amount
    to_account.balance += request.amount

    transaction = models.Transaction(
        from_account = request.from_account, 
        to_account = request.to_account, 
        amount = request.amount,
        timestamp = datetime.datetime.now(GERMANY_TZ)
    )
    db.add(transaction)
    db.commit()
    return {"message": "Transaction successful", "timestamp": transaction.timestamp.isoformat()}

#API endpoint to get account balance
@router.get("/accounts/{account_id}/balance")
def get_balance(account_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code = 404, detail = "Account not found")
    
    return {"customer_id": account.customer_id, "account_id": account_id, "balance": account.balance}

#API endpoint to get transaction history
@router.get("/accounts/{account_id}/transactions")
def get_transactions(account_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        (models.Transaction.from_account == account_id) |
        (models.Transactions.to_account == account_id)
    ).all()

    return [
        {
            "from": t.from_account, 
            "to": t.to_account, 
            "amount": t.amount, 
            "transaction_time": t.timestamp.astimezone(GERMANY_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
        } for t in transactions
    ]



