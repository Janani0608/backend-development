"""Remove password_hash from customers

Revision ID: 316de7140d35
Revises: 04862669439a
Create Date: 2025-02-22 11:25:17.895575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '316de7140d35'
down_revision: Union[str, None] = '04862669439a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the password_hash column from the customers table
    op.drop_column('customers', 'password_hash')


def downgrade() -> None:
    # Re-add the password_hash column in case of rollback
    op.add_column('customers', sa.Column('password_hash', sa.String(), nullable=False))
