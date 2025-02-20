from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class Customer(Base):
    #define the tablename in the database
    __tablename__ = "customers" 

    #define the keys based on the given requirements
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, nullable = False)

    #defining a bi-directiontional relationship between the customer and the one or many accounts the customer has
    #use account.owner to retrieve the customer details of the account
    #use customer.accounts to get the one or many accounts of the customer
    accounts = relationship("Account", back_populates = "owner")

class Account(Base):
    #define the tablename in the database
    __tablename__ = "accounts"

    id = Column(Integer, primary_key = True, index = True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable = False)
    balance = Column(Float, default = 0.0)

    #defining the bi-directional relationships
    owner = relationship("Customer", back_populates = "accounts")
    transactions = relationship("Transaction", back_populates = "account")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key = True, index = True)
    from_account = Column(Integer, ForeignKey("accounts.id"), nullable = False)
    to_account = Column(Integer, ForeignKey("accounts.id"), nullable = False)
    amount = Column(Float, nullable = False)
    timestamp = Column(DateTime(timezone =  True), server_default = func.now())

    #defining the bi-direction relationship
    account = relationship("Account", back_populates = "transactions")
