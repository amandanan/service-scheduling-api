"""add user account_owner_id and role

Revision ID: 62d954c83a05
Revises: 0b94e5468aeb
Create Date: 2026-06-13 09:38:51.169667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62d954c83a05'
down_revision: Union[str, Sequence[str], None] = '0b94e5468aeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # existing users are account owners; default role accordingly then drop
    # the server default so new rows rely on the application default.
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_owner_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('role', sa.String(), nullable=False, server_default='owner'))
        batch_op.alter_column('booking_slug',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.create_foreign_key(
            'fk_users_account_owner_id', 'users', ['account_owner_id'], ['id']
        )

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('role', server_default=None)

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_account_owner_id', type_='foreignkey')
        batch_op.alter_column('booking_slug',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.drop_column('role')
        batch_op.drop_column('account_owner_id')
