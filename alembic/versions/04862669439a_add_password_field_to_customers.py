"""Add password field to customers

Revision ID: 04862669439a
Revises: 6eed9c3ee0e7
Create Date: 2025-02-21 13:48:17.680846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext


# revision identifiers, used by Alembic.
revision: str = '04862669439a'
down_revision: Union[str, None] = '4b5db511abfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Initialize password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def upgrade() -> None:
    # Add password_hash column (temporarily allowing NULL values)
    op.add_column('customers', sa.Column('password_hash', sa.String(), nullable=True))

    # Now enforce NOT NULL constraint
    op.alter_column('customers', 'password_hash', nullable=False)

def downgrade() -> None:
    # Drop the password_hash column if rolling back
    op.drop_column('customers', 'password_hash')
