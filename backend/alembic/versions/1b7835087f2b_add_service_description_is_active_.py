"""add service description, is_active, professional_id

Revision ID: 1b7835087f2b
Revises: 42e72eb1be71
Create Date: 2026-06-13 17:02:58.301948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b7835087f2b'
down_revision: Union[str, Sequence[str], None] = '42e72eb1be71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # existing services default to active; drop the server default afterwards
    # so new rows rely on the application default.
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column('professional_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_services_professional_id', 'professionals', ['professional_id'], ['id']
        )

    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.alter_column('is_active', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.drop_constraint('fk_services_professional_id', type_='foreignkey')
        batch_op.drop_column('professional_id')
        batch_op.drop_column('is_active')
        batch_op.drop_column('description')
