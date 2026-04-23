"""
Technical indicators for the Gold Trend-Momentum strategy.
All functions operate on pd.Series and return pd.Series.
"""

from __future__ import annotations
import numpy as np
import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential moving average."""
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Wilder RSI (0–100 scale)."""
    delta    = series.diff()
    gain     = delta.clip(lower=0)
    loss     = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs       = avg_gain / avg_loss.replace(0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


def macd(
    series:     pd.Series,
    fast:       int = 12,
    slow:       int = 26,
    signal_per: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    MACD indicator.

    Returns
    -------
    (macd_line, signal_line, histogram)
    """
    macd_line   = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal_per)
    histogram   = macd_line - signal_line
    return macd_line, signal_line, histogram


def atr(
    high:   pd.Series,
    low:    pd.Series,
    close:  pd.Series,
    period: int = 14,
) -> pd.Series:
    """Average True Range using Wilder exponential smoothing."""
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low,
         (high - prev_close).abs(),
         (low  - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(com=period - 1, adjust=False).mean()


def bollinger_bands(
    series: pd.Series,
    period: int   = 20,
    n_std:  float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Bollinger Bands.

    Returns
    -------
    (upper_band, middle_band, lower_band)
    """
    middle = series.rolling(period).mean()
    std    = series.rolling(period).std(ddof=1)
    return middle + n_std * std, middle, middle - n_std * std


def bb_bandwidth(
    upper:  pd.Series,
    lower:  pd.Series,
    middle: pd.Series,
) -> pd.Series:
    """Normalised Bollinger Band width: (upper − lower) / middle."""
    return (upper - lower) / middle.replace(0, np.nan)
