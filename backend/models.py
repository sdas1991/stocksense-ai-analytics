"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Numeric, BigInteger, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database import Base
from datetime import datetime


class StockSnapshot(Base):
    __tablename__ = "stock_snapshot"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open = Column(Numeric(12, 4))
    high = Column(Numeric(12, 4))
    low = Column(Numeric(12, 4))
    close = Column(Numeric(12, 4))
    volume = Column(BigInteger)
    rsi = Column(Numeric(8, 4))
    ema_short = Column(Numeric(12, 4))
    ema_long = Column(Numeric(12, 4))
    macd = Column(Numeric(12, 4))
    macd_signal = Column(Numeric(12, 4))
    macd_histogram = Column(Numeric(12, 4))
    bb_upper = Column(Numeric(12, 4))
    bb_middle = Column(Numeric(12, 4))
    bb_lower = Column(Numeric(12, 4))
    recommendation = Column(String(10))
    trend = Column(String(20))
    ai_summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class StockSummary(Base):
    __tablename__ = "stock_summary"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    last_price = Column(Numeric(12, 4))
    price_change = Column(Numeric(12, 4))
    price_change_percent = Column(Numeric(8, 4))
    current_trend = Column(String(20))
    current_rsi = Column(Numeric(8, 4))
    current_macd = Column(Numeric(12, 4))
    recommendation = Column(String(10))
    ai_summary = Column(Text)
    confidence_score = Column(Numeric(5, 2))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)
    added_at = Column(DateTime, server_default=func.now())
    notes = Column(Text)


class StockAlert(Base):
    __tablename__ = "stock_alerts"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False)
    alert_type = Column(String(20), nullable=False)
    threshold_value = Column(Numeric(12, 4))
    triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
