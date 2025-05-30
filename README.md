# Banking API (FastAPI)  

This is an internal banking API that allows bank employees to manage customer accounts, perform transactions, and retrieve financial data. The API is built using **FastAPI** and follows role-based access control for security.  

## Features  

- **Customer Management**: View customer details (Admin only).  
- **Account Management**: Create new accounts, retrieve balances, and view transaction history.  
- **Transactions**: Deposit, withdraw, and transfer funds securely between accounts.  
- **Role-Based Access Control**: Employees have different levels of access (Admin, Manager, Teller).  
- **Security**: JWT-based authentication.  
- **Concurrency Handling**: Ensures consistent transfers under high load.  
- **Database Migrations**: Uses Alembic for schema migrations.  
- **Comprehensive Tests**: Includes unit and integration tests with `pytest`.

### Prerequisites
- Python 3.9+
- PostgreSQL
- Virtual Environment (venv or conda)

### Installation & Setup

1. **Create the virtual environment**  
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

2. **Install dependencies** 
    pip install -r requirements.txt

3. **Setup environment variables** 
    DATABASE_URL=postgresql://user:password@localhost/bank_db
    SECRET_KEY=your_secret_key

4. **Run Database migrations** 
    alembic upgrade head

5. **Start the API server** 
    uvicorn main:app --reload

6. **Access API documentation** (Swagger UI)
    http://127.0.0.1:8000/docs

7. **Running the test**
    pytest






### Objective

Your assignment is to build an internal API for a fake financial institution using Python and any framework.

### Brief

While modern banks have evolved to serve a plethora of functions, at their core, banks must provide certain basic features. Today, your task is to build the basic HTTP API for one of those banks! Imagine you are designing a backend API for bank employees. It could ultimately be consumed by multiple frontends (web, iOS, Android etc).

### Tasks

- Implement assignment using:
  - Language: **Python**
  - Framework: **any framework except Django** 
- There should be API routes that allow them to:
  - Create a new bank account for a customer, with an initial deposit amount. A
    single customer may have multiple bank accounts.
  - Transfer amounts between any two accounts, including those owned by
    different customers.
  - Retrieve balances for a given account.
  - Retrieve transfer history for a given account.
- Write tests for your business logic

Feel free to pre-populate your customers with the following:

```json
[
  {
    "id": 1,
    "name": "Arisha Barron"
  },
  {
    "id": 2,
    "name": "Branden Gibson"
  },
  {
    "id": 3,
    "name": "Rhonda Church"
  },
  {
    "id": 4,
    "name": "Georgina Hazel"
  }
]
```
