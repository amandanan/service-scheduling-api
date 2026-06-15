"""add appointment price_charged, cancelled_by, period index

Revision ID: 4780b114d008
Revises: c081621e1b62
Create Date: 2026-06-15 12:16:18.170293

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4780b114d008'
down_revision: Union[str, Sequence[str], None] = 'c081621e1b62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price_charged', sa.Float(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('cancelled_by', sa.String(), nullable=True))

    # backfill historical rows with the service's current price (best available
    # approximation — there is no price history to reconstruct the real value)
    op.execute(
        "UPDATE appointments SET price_charged = COALESCE("
        "(SELECT price FROM services WHERE services.id = appointments.service_id), 0)"
    )

    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.alter_column('price_charged', server_default=None)

    # supports the period-scoped metric aggregations
    op.create_index(
        'ix_appointments_owner_scheduled',
        'appointments',
        ['owner_id', 'scheduled_at'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_appointments_owner_scheduled', table_name='appointments')

    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.drop_column('cancelled_by')
        batch_op.drop_column('price_charged')
