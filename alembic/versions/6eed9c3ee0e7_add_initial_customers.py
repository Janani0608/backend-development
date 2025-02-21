"""Add initial customers

Revision ID: 6eed9c3ee0e7
Revises: 4b5db511abfb
Create Date: 2025-02-21 00:20:30.897285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext


# revision identifiers, used by Alembic.
revision: str = '6eed9c3ee0e7'
down_revision: Union[str, None] = '4b5db511abfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

#Initialize password hasher
pwd_hasher = CryptContext(schemes = ["bcrypt"], deprecated = "auto", bcrypt__ident="2b")

def hash_password(password):
    return pwd_hasher.hash(password)

# Pre-populate the db witht he given customers and additional password column for added security
customers = [
    {"id": 1, "name": "Arisha Barron", "password_hash": hash_password("password1")},
    {"id": 2, "name": "Branden Gibson", "password_hash": hash_password("password2")},
    {"id": 3, "name": "Rhonda Church", "password_hash": hash_password("password3")},
    {"id": 4, "name": "Georgina Hazel", "password_hash": hash_password("password4")}
]

def upgrade() -> None:
    # Add the password_hash column
    op.add_column("customers", sa.Column("password_hash", sa.String(), nullable=False))

    # Insert initial customers into the customers table
    for customer in customers:
        op.execute(
            f"INSERT INTO customers (id, name, password_hash) VALUES ({customer['id']}, '{customer['name']}', '{customer['password_hash']}')"
        )


def downgrade() -> None:
     # Remove the initial customers if the migration is rolled back
    op.execute("DELETE FROM customers WHERE id IN (1,2,3,4);")
