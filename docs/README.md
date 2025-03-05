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






