"""
Technical indicators calculation module
Computes RSI, MACD, EMA, Bollinger Bands, and other technical indicators
"""
import pandas as pd
import numpy as np
from typing import Tuple


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI)
    """
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA)
    """
    return data.ewm(span=period, adjust=False).mean()


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA)
    """
    return data.rolling(window=period).mean()


def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    Returns: (macd_line, signal_line, histogram)
    """
    ema_fast = calculate_ema(data, fast)
    ema_slow = calculate_ema(data, slow)

    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands
    Returns: (upper_band, middle_band, lower_band)
    """
    middle_band = calculate_sma(data, period)
    std = data.rolling(window=period).std()

    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)

    return upper_band, middle_band, lower_band


def detect_trend(close_price: float, ema_50: float, rsi: float, macd: float) -> str:
    """
    Detect market trend based on indicators
    Returns: 'Bullish', 'Bearish', or 'Neutral'
    """
    bullish_signals = 0
    bearish_signals = 0

    # Price vs EMA
    if close_price > ema_50:
        bullish_signals += 1
    else:
        bearish_signals += 1

    # RSI analysis
    if rsi < 30:
        bullish_signals += 1  # Oversold, potential reversal
    elif rsi > 70:
        bearish_signals += 1  # Overbought, potential reversal
    elif rsi > 50:
        bullish_signals += 0.5
    else:
        bearish_signals += 0.5

    # MACD analysis
    if macd > 0:
        bullish_signals += 1
    else:
        bearish_signals += 1

    # Determine trend
    if bullish_signals > bearish_signals + 0.5:
        return "Bullish"
    elif bearish_signals > bullish_signals + 0.5:
        return "Bearish"
    else:
        return "Neutral"


def generate_recommendation(rsi: float, macd: float, macd_signal: float,
                           close: float, ema_short: float, ema_long: float,
                           bb_upper: float, bb_lower: float) -> str:
    """
    Generate Buy/Hold/Sell recommendation based on multiple indicators
    """
    buy_signals = 0
    sell_signals = 0

    # RSI signals
    if rsi < 30:
        buy_signals += 2  # Strong buy
    elif rsi < 40:
        buy_signals += 1
    elif rsi > 70:
        sell_signals += 2  # Strong sell
    elif rsi > 60:
        sell_signals += 1

    # MACD signals
    if macd > macd_signal and macd > 0:
        buy_signals += 2
    elif macd > macd_signal:
        buy_signals += 1
    elif macd < macd_signal and macd < 0:
        sell_signals += 2
    elif macd < macd_signal:
        sell_signals += 1

    # EMA crossover
    if ema_short > ema_long:
        buy_signals += 1
    else:
        sell_signals += 1

    # Bollinger Bands
    if close < bb_lower:
        buy_signals += 1
    elif close > bb_upper:
        sell_signals += 1

    # Generate recommendation
    if buy_signals > sell_signals + 1:
        return "Buy"
    elif sell_signals > buy_signals + 1:
        return "Sell"
    else:
        return "Hold"


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators for a dataframe
    Input dataframe should have columns: Open, High, Low, Close, Volume
    """
    if df.empty:
        return df

    # Make a copy to avoid modifying original
    df = df.copy()

    # Calculate indicators
    df['RSI'] = calculate_rsi(df['Close'], 14)
    df['EMA_12'] = calculate_ema(df['Close'], 12)
    df['EMA_50'] = calculate_ema(df['Close'], 50)
    df['SMA_20'] = calculate_sma(df['Close'], 20)
    df['SMA_50'] = calculate_sma(df['Close'], 50)

    # MACD
    macd, signal, hist = calculate_macd(df['Close'])
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Histogram'] = hist

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['Close'])
    df['BB_Upper'] = bb_upper
    df['BB_Middle'] = bb_middle
    df['BB_Lower'] = bb_lower

    # Volume analysis
    df['Volume_SMA'] = calculate_sma(df['Volume'], 20)
    df['Volume_Spike'] = df['Volume'] > (df['Volume_SMA'] * 1.5)

    return df


def get_latest_analysis(df: pd.DataFrame) -> dict:
    """
    Get the latest indicator values and analysis from a dataframe
    """
    if df.empty:
        return {}

    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else latest

    close_price = float(latest['Close'])
    ema_50 = float(latest['EMA_50']) if not pd.isna(latest['EMA_50']) else close_price
    rsi = float(latest['RSI']) if not pd.isna(latest['RSI']) else 50.0
    macd = float(latest['MACD']) if not pd.isna(latest['MACD']) else 0.0
    macd_signal = float(latest['MACD_Signal']) if not pd.isna(latest['MACD_Signal']) else 0.0
    ema_12 = float(latest['EMA_12']) if not pd.isna(latest['EMA_12']) else close_price
    bb_upper = float(latest['BB_Upper']) if not pd.isna(latest['BB_Upper']) else close_price * 1.02
    bb_lower = float(latest['BB_Lower']) if not pd.isna(latest['BB_Lower']) else close_price * 0.98

    trend = detect_trend(close_price, ema_50, rsi, macd)
    recommendation = generate_recommendation(rsi, macd, macd_signal, close_price, ema_12, ema_50, bb_upper, bb_lower)

    return {
        'close': close_price,
        'rsi': rsi,
        'macd': macd,
        'macd_signal': macd_signal,
        'macd_histogram': float(latest['MACD_Histogram']) if not pd.isna(latest['MACD_Histogram']) else 0.0,
        'ema_12': ema_12,
        'ema_50': ema_50,
        'bb_upper': bb_upper,
        'bb_middle': float(latest['BB_Middle']) if not pd.isna(latest['BB_Middle']) else close_price,
        'bb_lower': bb_lower,
        'trend': trend,
        'recommendation': recommendation,
        'price_change': close_price - float(previous['Close']),
        'price_change_percent': ((close_price - float(previous['Close'])) / float(previous['Close'])) * 100
    }
