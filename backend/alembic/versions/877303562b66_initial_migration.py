"""initial_migration

Revision ID: 877303562b66
Revises: 
Create Date: 2026-06-04 11:11:26.372086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '877303562b66'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'customers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('whatsapp', sa.String(length=20), nullable=False),
        sa.Column('cpf', sa.String(length=14), nullable=True),
        sa.Column('cnpj', sa.String(length=18), nullable=True),
        sa.Column('email', sa.String(length=254), nullable=True),
        sa.Column('street', sa.String(length=120), nullable=True),
        sa.Column('neighborhood', sa.String(length=80), nullable=True),
        sa.Column('number', sa.String(length=20), nullable=True),
        sa.Column('complement', sa.String(length=120), nullable=True),
        sa.Column('zip_code', sa.String(length=9), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deactivated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cnpj'),
        sa.UniqueConstraint('cpf'),
        sa.UniqueConstraint('whatsapp')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('customers')
