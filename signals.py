"""
Signal generation for the Gold Trend-Momentum strategy.
No lookahead: signals computed at bar t are acted on at bar t+1 (shift(1)).
"""

from __future__ import annotations
import pandas as pd

from indicators import ema, rsi, macd, atr, bollinger_bands, bb_bandwidth
import config as cfg


def compute_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich raw OHLCV DataFrame with all indicators and trading signals.

    Parameters
    ----------
    df : DataFrame with columns Open, High, Low, Close, Volume.

    Returns
    -------
    DataFrame enriched with signal columns (lag-1 shifted where required).
    """
    d = df.copy()

    # ── Secular trend filter ──────────────────────────────────────────────────
    d["ema200"]      = ema(d["Close"], cfg.TREND_EMA)
    d["above_trend"] = d["Close"] > d["ema200"]

    # ── EMA crossover ─────────────────────────────────────────────────────────
    d["ema_fast"]    = ema(d["Close"], cfg.FAST_EMA)
    d["ema_slow"]    = ema(d["Close"], cfg.SLOW_EMA)
    d["ema_bullish"] = d["ema_fast"] > d["ema_slow"]
    # Golden cross (fast crosses above slow)
    d["golden_cross"]= (
        (d["ema_fast"] >  d["ema_slow"]) &
        (d["ema_fast"].shift(1) <= d["ema_slow"].shift(1))
    )
    # Death cross (fast crosses below slow)
    d["death_cross"] = (
        (d["ema_fast"] <  d["ema_slow"]) &
        (d["ema_fast"].shift(1) >= d["ema_slow"].shift(1))
    )

    # ── RSI ───────────────────────────────────────────────────────────────────
    d["rsi"] = rsi(d["Close"], cfg.RSI_PERIOD)

    # ── MACD ──────────────────────────────────────────────────────────────────
    d["macd_line"], d["macd_sig"], d["macd_hist"] = macd(
        d["Close"], cfg.MACD_FAST, cfg.MACD_SLOW, cfg.MACD_SIGNAL
    )
    d["macd_bullish"] = d["macd_hist"] > 0

    # ── Bollinger Band Squeeze ─────────────────────────────────────────────────
    d["bb_upper"], d["bb_mid"], d["bb_lower"] = bollinger_bands(
        d["Close"], cfg.BB_PERIOD, cfg.BB_STD
    )
    d["bb_width"]    = bb_bandwidth(d["bb_upper"], d["bb_lower"], d["bb_mid"])
    d["bb_squeeze"]  = d["bb_width"] < cfg.BB_SQUEEZE_THRESHOLD
    # Breakout: squeeze released + price closes above prior upper band
    d["sq_breakout"] = (
        d["bb_squeeze"].shift(1).fillna(False) &
        ~d["bb_squeeze"] &
        (d["Close"] > d["bb_upper"].shift(1))
    )

    # ── ATR ───────────────────────────────────────────────────────────────────
    d["atr_val"] = atr(d["High"], d["Low"], d["Close"], cfg.ATR_PERIOD)

    # ── Composite entry signal ────────────────────────────────────────────────
    # Primary: EMA crossover + all confirmations
    primary = (
        d["above_trend"] &
        d["ema_bullish"] &
        (d["rsi"] > cfg.RSI_ENTRY_MIN) &
        d["macd_bullish"]
    )
    # Secondary: squeeze breakout in uptrend
    secondary = d["above_trend"] & d["sq_breakout"]

    # Shift by 1 to avoid lookahead
    d["entry_signal"] = (primary | secondary).shift(1).fillna(False)

    # ── Exit signals (also lag-1 shifted) ────────────────────────────────────
    d["trend_exit"] = (d["death_cross"] | ~d["ema_bullish"]).shift(1).fillna(False)
    d["rsi_exit"]   = (d["rsi"] < cfg.RSI_EXIT).shift(1).fillna(False)

    return d
