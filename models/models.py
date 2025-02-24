from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class Employee(Base):
    """
    Represents an employee in the banking system.

    Attributes:
        id (int): Unique identifier for the employee.
        username (str): Unique username for authentication.
        password_hash (str): Hashed password for security.
        role (str): Role of the employee (admin, manager, teller).
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Role-based access control:
    # - "admin": Full access
    # - "manager": Can approve transfers, create accounts
    # - "teller": Can view accounts, deposit/withdraw money
    role = Column(String, default="teller")  # Default role is "teller"

class Customer(Base):
    """
    Represents a customer who holds one or more bank accounts.

    Attributes:
        id (int): Unique identifier for the customer.
        name (str): Full name of the customer.
        accounts (relationship): One-to-many relationship with Account.
    """
    __tablename__ = "customers" 

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, nullable = False)

    # Relationship: A customer can have multiple accounts.
    accounts = relationship("Account", back_populates = "owner")

class Account(Base):
    """
    Represents a bank account associated with a customer.

    Attributes:
        id (int): Unique identifier for the account.
        customer_id (int): Foreign key linking to the customer.
        balance (float): Account balance.
        owner (relationship): Relationship to Customer.
        sent_transactions (relationship): Transactions sent from this account.
        received_transactions (relationship): Transactions received by this account.
    """
    __tablename__ = "accounts"

    id = Column(Integer, primary_key = True, index = True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable = False)
    balance = Column(Float, default = 0.0)

    # Define relationships
    owner = relationship("Customer", back_populates = "accounts")
    sent_transactions = relationship("Transaction", foreign_keys="[Transaction.from_account]", back_populates="sender_account")
    received_transactions = relationship("Transaction", foreign_keys="[Transaction.to_account]", back_populates="receiver_account")

class Transaction(Base):
    """
    Represents a financial transaction between two accounts.

    Attributes:
        id (int): Unique transaction identifier.
        from_account (int): Foreign key linking to the sender's account.
        to_account (int): Foreign key linking to the recipient's account.
        amount (float): The transaction amount.
        timestamp (datetime): Time of transaction creation.
        sender_account (relationship): Relationship to the sender's account.
        receiver_account (relationship): Relationship to the recipient's account.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key = True, index = True)
    from_account = Column(Integer, ForeignKey("accounts.id"), nullable = False)
    to_account = Column(Integer, ForeignKey("accounts.id"), nullable = False)
    amount = Column(Float, nullable = False)
    timestamp = Column(DateTime(timezone =  True), server_default = func.now())

    # Define relationships with explicit foreign_keys to avoid ambiguity
    sender_account = relationship("Account", foreign_keys=[from_account], back_populates="sent_transactions")
    receiver_account = relationship("Account", foreign_keys=[to_account], back_populates="received_transactions")
