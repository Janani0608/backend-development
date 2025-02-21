from fastapi import FastAPI
from app.database import engine
from models import models
from routes import accounts

#Initialize FastAPI
app = FastAPI()

app.include_router(accounts.router)

#Endpoint
@app.get("/")
def home():
    return{"message": "Welcome to the Bank"}