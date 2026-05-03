"""add triggered alerts

Revision ID: 20260503_0002
Revises: 20260414_0001
Create Date: 2026-05-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260503_0002"
down_revision = "20260414_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "triggered_alerts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("alert_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("symbol", sa.String(length=16), nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("threshold", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("observed_value", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["alert_id"], ["user_alerts.id"]),
        sa.ForeignKeyConstraint(["symbol"], ["watched_assets.symbol"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("triggered_alerts")
