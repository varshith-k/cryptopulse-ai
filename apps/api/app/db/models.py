import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    alerts: Mapped[list["UserAlert"]] = relationship(back_populates="user")


class WatchedAsset(Base):
    __tablename__ = "watched_assets"

    symbol: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    market: Mapped[str] = mapped_column(String(32), nullable=False, default="crypto")

    snapshots: Mapped[list["MarketSnapshot"]] = relationship(back_populates="asset")
    indicators: Mapped[list["TechnicalIndicator"]] = relationship(back_populates="asset")


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(
        String(16), ForeignKey("watched_assets.symbol"), nullable=False
    )
    price_usd: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    percent_change_24h: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    volume_24h: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    asset: Mapped[WatchedAsset] = relationship(back_populates="snapshots")


class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(
        String(16), ForeignKey("watched_assets.symbol"), nullable=False
    )
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    sma_20: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    ema_20: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    rsi_14: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    macd: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    signal: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    rolling_volatility: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4), nullable=True
    )
    trend_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    asset: Mapped[WatchedAsset] = relationship(back_populates="indicators")


class UserAlert(Base):
    __tablename__ = "user_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(
        String(16), ForeignKey("watched_assets.symbol"), nullable=False
    )
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    threshold: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="alerts")


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str | None] = mapped_column(String(16), nullable=True)
    insight_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
