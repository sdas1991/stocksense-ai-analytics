-- StockSense AI Database Schema
-- PostgreSQL database schema for stock analysis and recommendations

-- Stock snapshot table storing historical data and computed indicators
CREATE TABLE IF NOT EXISTS stock_snapshot (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date TIMESTAMP NOT NULL,
    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4),
    volume BIGINT,
    rsi NUMERIC(8, 4),
    ema_short NUMERIC(12, 4),
    ema_long NUMERIC(12, 4),
    macd NUMERIC(12, 4),
    macd_signal NUMERIC(12, 4),
    macd_histogram NUMERIC(12, 4),
    bb_upper NUMERIC(12, 4),
    bb_middle NUMERIC(12, 4),
    bb_lower NUMERIC(12, 4),
    recommendation VARCHAR(10),
    trend VARCHAR(20),
    ai_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_stock_symbol_date ON stock_snapshot(symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stock_snapshot(symbol);

-- Stock summary table for latest analysis
CREATE TABLE IF NOT EXISTS stock_summary (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    last_price NUMERIC(12, 4),
    price_change NUMERIC(12, 4),
    price_change_percent NUMERIC(8, 4),
    current_trend VARCHAR(20),
    current_rsi NUMERIC(8, 4),
    current_macd NUMERIC(12, 4),
    recommendation VARCHAR(10),
    ai_summary TEXT,
    confidence_score NUMERIC(5, 2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Watchlist table for user favorites
CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(symbol)
);

-- Stock alerts table
CREATE TABLE IF NOT EXISTS stock_alerts (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    alert_type VARCHAR(20) NOT NULL,
    threshold_value NUMERIC(12, 4),
    triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create seed data for testing
INSERT INTO watchlist (symbol, notes) VALUES
    ('AAPL', 'Apple Inc - Tech leader'),
    ('TSLA', 'Tesla - EV innovation'),
    ('MSFT', 'Microsoft - Cloud computing'),
    ('GOOGL', 'Alphabet - Search and AI'),
    ('AMZN', 'Amazon - E-commerce giant')
ON CONFLICT (symbol) DO NOTHING;
