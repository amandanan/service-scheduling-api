"""add_appointment_id_to_notification_logs

Revision ID: 2b5a53a4106d
Revises: 4780b114d008
Create Date: 2026-06-15 20:50:27.608090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b5a53a4106d'
down_revision: Union[str, Sequence[str], None] = '4780b114d008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "notification_logs",
        sa.Column("appointment_id", sa.Integer(), sa.ForeignKey("appointments.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("notification_logs", "appointment_id")
