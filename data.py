"""
Data loading — Gold Futures (GC=F) daily OHLCV from Yahoo Finance.
Handles futures roll gaps via forward-fill on adjusted prices.
"""

from __future__ import annotations
import pandas as pd
import yfinance as yf
from config import TICKER, START_DATE, END_DATE


def load_gold(
    ticker: str = TICKER,
    start:  str = START_DATE,
    end:    str = END_DATE,
) -> pd.DataFrame:
    """
    Download and clean daily OHLCV for Gold Futures (GC=F).

    Returns
    -------
    DataFrame with columns: Open, High, Low, Close, Volume
    Index: DatetimeIndex (trading days only)
    """
    raw = yf.download(ticker, start=start, end=end,
                      auto_adjust=True, progress=False)
    raw.columns = [c[0] if isinstance(c, tuple) else c for c in raw.columns]
    raw.index   = pd.to_datetime(raw.index)
    df = raw[["Open", "High", "Low", "Close", "Volume"]].dropna()
    # Forward-fill any isolated NaN rows (contract roll artefacts)
    df = df.ffill()
    return df
