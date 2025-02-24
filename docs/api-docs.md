POST /login Login
Authenticates an employee and returns an access token.

Parameters No parameters

Request body
application/json
Example Value | Schema
{
  "username": "string",
  "password": "string"
}
Responses
Code	Description	

200	    Successful Response
Media type  application/json
Controls Accept header.
Example Value |Schema
"string"

---------------------------------------------------------------------------------------------------------------------------------------

GET /view-customers Retrieve all customers

Returns a list of all customers. Only accessible to users with the 'admin' role.

Parameters No parameters

Responses
Code	Description	

200	    Successful response
Media type application/json
Controls Accept header.
Example Value | Schema
[
  {
    "id": 0,
    "name": "string"
  }
]

403	    Forbidden - Requires Admin role

---------------------------------------------------------------------------------------------------------------------------------------

GET  /view-accounts/{customer_id}  Retrieve all accounts


Fetches all accounts associated with a given customer. This endpoint requires admin privileges.

- **Admin Role Required**: Only users with the 'admin' role can access this.
- **Returns**: A list of accounts linked to the specified customer.
- **Error Handling**: 
    - Returns `404 Not Found` if the customer does not exist.
    - Returns `403 Forbidden` if the user is not an admin.

Parameters
Name	      Description
customer_id * integer

Responses
Code	Description	Links

200	    Successful response with a list of accounts.
Media type  application/json
Controls Accept header.
Example Value | Schema
[
  {
    "id": 1,
    "customer_id": 123,
    "account_type": "savings",
    "balance": 5000
  },
  {
    "id": 2,
    "customer_id": 123,
    "account_type": "checking",
    "balance": 2500.5
  }
]

403	    Forbidden - Requires Admin role

404	    Customer not found

---------------------------------------------------------------------------------------------------------------------------------------

POST  /accounts/  Create a new bank account

Creates a new bank account for a customer.
This endpoint requires Manager privileges.

- **Manager Role Required**: Only managers can create accounts.
- **Validations**:
    - The customer must exist in the system.
    - The initial deposit amount must be valid.
- **Returns**:
    - A confirmation message along with the new account details.
- **Error Handling**:
    - `404 Not Found` if the customer does not exist.
    - `403 Forbidden` if the user is not a manager.

Parameters  No parameters

Request body  application/json
Example Value | Schema
{
  "customer_id": 0,
  "initial_deposit": 0
}

Responses
Code	Description	Links

200	    Successful Response
Media type  application/json
Controls Accept header.
Example Value | Schema
{
  "message": "string",
  "account_id": 0,
  "customer_id": 0
}

201	    Account successfully created.
Media type  application/json
Example Value
{
  "message": "Account created successfully",
  "account_id": 101,
  "customer_id": 1
}

403	   Forbidden - Requires Manager role

404	   User not found

---------------------------------------------------------------------------------------------------------------------------------------

GET  /accounts/{account_id}/balance  Retrieve account balance

Fetches the current balance of a specific bank account.
This endpoint requires Teller privileges.

- **Teller Role Required**: Only tellers can access account balances.
- **Validations**:
    - The account must exist in the system.
- **Returns**:
    - The balance of the requested account.
- **Error Handling**:
    - `404 Not Found` if the account does not exist.
    - `403 Forbidden` if the user is not a teller.

Parameters

Name          Description
account_id *  integer

Responses
Code	Description	Links

200	    Account balance retrieved successfully.
Media type  application/json
Controls Accept header.
Example Value | Schema
{
  "customer_id": 1,
  "account_id": 101,
  "balance": 1500.75
}

403	    Forbidden - Requires Teller role

404	    Account not found

---------------------------------------------------------------------------------------------------------------------------------------

POST  /deposit/  Deposit money into an account

Adds funds to a customer's bank account.
This endpoint requires Teller privileges.

- **Teller Role Required**: Only tellers can perform deposits.
- **Validations**:
    - The deposit amount must be greater than zero.
    - The account must exist in the system.
- **Returns**:
    - A success message with updated account balance.
- **Error Handling**:
    - `400 Bad Request` if the deposit amount is invalid.
    - `404 Not Found` if the account does not exist.
    - `500 Internal Server Error` for unexpected issues.

Parameters  No parameters

Request body  application/json
Example Value | Schema
{
  "account_id": 0,
  "amount": 0
}

Responses
Code	Description	Links

200	    Amount successfully credited to the account.
Media type  application/json
Controls Accept header.
Example Value | Schema
{
  "message": "Amount credited to the account",
  "amount": 500,
  "account_id": 101,
  "curr_balance": 2000.75
}

400	    Invalid deposit amount

404	    Account not found

422	    Validation Error
Media type  application/json
Example Value | Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

500	    Internal server error

---------------------------------------------------------------------------------------------------------------------------------------

POST  /withdraw/  Withdraw money from an account

Withdraw funds from a customer's bank account.
This endpoint requires Teller privileges.

- **Teller Role Required**: Only tellers can perform deposits.
- **Validations**:
    - The withdraw amount must be greater than zero.
    - The account must exist in the system.
- **Returns**:
    - A success message with updated account balance.
- **Error Handling**:
    - `400 Bad Request` if the withdraw amount is invalid.
    - `404 Not Found` if the account does not exist.
    - `500 Internal Server Error` for unexpected issues.

Parameters  No parameters

Request body  application/json
Example Value | Schema
{
  "account_id": 0,
  "amount": 0
}

Responses
Code	Description	Links

200	    Amount successfully withdrawn from the account.
Media type  application/json
Controls Accept header.
Example Value | Schema
{
  "message": "Amount debited from the account",
  "amount": 500,
  "account_id": 101,
  "curr_balance": 2000.75
}

400	    Invalid withdraw amount

404	    Account not found

422	    Validation Error
Media type  application/json
Example Value | Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

500	    Internal server error

---------------------------------------------------------------------------------------------------------------------------------------

POST  /transfer/  Transfer money between accounts

Transfers a specified amount from one account to another.
This operation requires Manager privileges.

- **Manager Role Required**: Only managers can authorize transfers.
- **Validations**:
    - The transfer amount must be greater than zero.
    - The source and destination accounts must be different.
    - The source account must have sufficient balance.
- **Concurrency Handling**:
    - Uses **serializable transaction isolation** to ensure safe, sequential execution.
    - Implements **retry logic** in case of database contention.
- **Returns**:
    - A success message with the timestamp of the transaction.
- **Error Handling**:
    - `400 Bad Request` for invalid transfer amounts or insufficient funds.
    - `404 Not Found` if one or both accounts do not exist.
    - `500 Internal Server Error` if a database error occurs after retries.

Parameters  No parameters

Request body  application/json
Example Value | Schema
{
  "from_account": 0,
  "to_account": 0,
  "amount": 0
}

Responses
Code	Description	Links

200	    Transaction successful
Media type  application/json
Controls Accept header.
Example Value | Schema
{
  "message": "Transaction successful",
  "timestamp": "2024-02-19T14:25:36.123456"
}

400	    Invalid transfer request (e.g., insufficient funds, same account transfer)

404	    One or both accounts not found

422	    Validation Error
Media type  application/json
Example Value | Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

500	    Database transaction error, try again later

---------------------------------------------------------------------------------------------------------------------------------------

GET  /accounts/{account_id}/transactions  Retrieve transaction history for an account

Retrieves the transaction history for a specified account.
Transactions are sorted from most recent to least recent.

- **Manager Role Required**: Only managers can access this information.
- **Returns**:
    - A list of all transactions associated with the account.
    - Includes both **incoming** (credits) and **outgoing** (debits) transactions.
- **Error Handling**:
    - `404 Not Found` if the account does not exist.

Parameters
Name	     Description
account_id * integer

Responses
Code	Description	Links

200	    Transaction history retrieved successfully
Media type  application/json
Controls Accept header.
Example Value | Schema
{
  "transactions": [
    {
      "from_account": 123,
      "to_account": 456,
      "amount": 250,
      "transaction_time": "2024-02-19 14:30:00 CET"
    },
    {
      "from_account": 789,
      "to_account": 123,
      "amount": 100,
      "transaction_time": "2024-02-18 09:15:00 CET"
    }
  ]
}

404	    Account not found

422	    Validation Error

Media type  application/json
Example Value | Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}