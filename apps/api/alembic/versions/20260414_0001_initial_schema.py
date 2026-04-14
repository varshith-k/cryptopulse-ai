"""initial schema

Revision ID: 20260414_0001
Revises:
Create Date: 2026-04-14 01:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260414_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "watched_assets",
        sa.Column("symbol", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("market", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("symbol"),
    )
    op.create_table(
        "ai_insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=16), nullable=True),
        sa.Column("insight_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "market_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=16), nullable=False),
        sa.Column("price_usd", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("percent_change_24h", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("volume_24h", sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column("market_cap", sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["symbol"], ["watched_assets.symbol"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "technical_indicators",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=16), nullable=False),
        sa.Column("timeframe", sa.String(length=16), nullable=False),
        sa.Column("sma_20", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("ema_20", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("rsi_14", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column("macd", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("signal", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("rolling_volatility", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column("trend_summary", sa.Text(), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["symbol"], ["watched_assets.symbol"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_alerts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("symbol", sa.String(length=16), nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("threshold", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["symbol"], ["watched_assets.symbol"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_alerts")
    op.drop_table("technical_indicators")
    op.drop_table("market_snapshots")
    op.drop_table("ai_insights")
    op.drop_table("watched_assets")
    op.drop_table("users")
