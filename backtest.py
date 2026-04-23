"""
Event-driven backtest engine for the Gold Trend-Momentum strategy.

Key design choices:
  - ATR-based initial stop set at entry, held fixed
  - ATR-based trailing stop that ratchets up with price
  - RSI and EMA cross exits complement the trailing stop
  - Circuit-breaker: no new entries when 60-day portfolio DD < −12%
  - All costs (fee + slippage) applied on both entry and exit
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import pandas as pd

import config as cfg
from data import load_gold
from signals import compute_signals


@dataclass
class Trade:
    entry_date:  pd.Timestamp
    exit_date:   pd.Timestamp
    entry_price: float
    exit_price:  float
    stop_loss:   float
    units:       float
    gross_pnl:   float
    net_pnl:     float
    exit_reason: str


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades:       List[Trade] = field(default_factory=list)
    signals_df:   Optional[pd.DataFrame] = None


def run_backtest() -> BacktestResult:
    """Execute the full Gold backtest and return results."""
    print("  Fetching Gold Futures data from Yahoo Finance…")
    df_raw = load_gold()
    print("  Computing indicators and signals…")
    df     = compute_signals(df_raw)

    equity       = cfg.INITIAL_EQUITY
    equity_curve : list[tuple[pd.Timestamp, float]] = []
    trades       : list[Trade] = []

    in_position  = False
    entry_price  = 0.0
    stop_loss    = 0.0
    high_water   = 0.0    # tracks highest price since entry for trailing stop
    units        = 0.0
    entry_date   = None
    last_exit_i  = -cfg.COOLDOWN_BARS - 1

    dates = df.index

    for i in range(1, len(dates)):
        t     = dates[i]
        row   = df.iloc[i]
        price = float(row["Close"])

        equity_curve.append((t, equity))

        # ── Circuit-breaker ────────────────────────────────────────────────────
        recent = pd.Series([v for _, v in equity_curve[-cfg.DD_LOOKBACK_DAYS:]])
        if len(recent) >= 10:
            peak = recent.max()
            if (recent.iloc[-1] / peak - 1.0) < cfg.MAX_ROLLING_DD and not in_position:
                continue

        if in_position:
            # Update trailing stop high-water mark
            if price > high_water:
                high_water = price
            atr_val       = float(row["atr_val"])
            trailing_stop = high_water - cfg.ATR_TRAIL_MULT * atr_val

            if price <= stop_loss:
                reason = "Stop Loss"
            elif price <= trailing_stop:
                reason = "Trailing Stop"
            elif bool(row["trend_exit"]):
                reason = "Trend Exit (EMA cross)"
            elif bool(row["rsi_exit"]):
                reason = "RSI Exit"
            else:
                reason = None

            if reason:
                cost       = price * units * (cfg.FEE_RATE + cfg.SLIPPAGE)
                entry_cost = entry_price * units * (cfg.FEE_RATE + cfg.SLIPPAGE)
                gross_pnl  = (price - entry_price) * units
                net_pnl    = gross_pnl - cost - entry_cost
                equity    += net_pnl

                trades.append(Trade(
                    entry_date=entry_date,
                    exit_date=t,
                    entry_price=entry_price,
                    exit_price=price,
                    stop_loss=stop_loss,
                    units=units,
                    gross_pnl=gross_pnl,
                    net_pnl=net_pnl,
                    exit_reason=reason,
                ))
                in_position = False
                last_exit_i = i

        else:
            cooldown_ok = (i - last_exit_i) >= cfg.COOLDOWN_BARS
            if bool(row["entry_signal"]) and cooldown_ok:
                atr_val    = float(row["atr_val"])
                stop_loss  = price - cfg.ATR_STOP_MULT * atr_val
                risk_per_u = price - stop_loss
                if risk_per_u <= 0:
                    continue
                units       = (equity * cfg.RISK_PER_TRADE) / risk_per_u
                in_position = True
                entry_price = price
                high_water  = price
                entry_date  = t

    # Close open position at end of period
    if in_position:
        last_price = float(df["Close"].iloc[-1])
        cost       = last_price * units * (cfg.FEE_RATE + cfg.SLIPPAGE)
        entry_cost = entry_price * units * (cfg.FEE_RATE + cfg.SLIPPAGE)
        gross_pnl  = (last_price - entry_price) * units
        net_pnl    = gross_pnl - cost - entry_cost
        equity    += net_pnl
        trades.append(Trade(
            entry_date=entry_date,
            exit_date=dates[-1],
            entry_price=entry_price,
            exit_price=last_price,
            stop_loss=stop_loss,
            units=units,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            exit_reason="End of Period",
        ))

    eq_series = pd.Series(
        [v for _, v in equity_curve],
        index=[d  for d, _ in equity_curve],
        name="Equity",
    )
    return BacktestResult(equity_curve=eq_series, trades=trades, signals_df=df)


def compute_stats(
    equity: pd.Series,
    trades: list[Trade],
    ann:    int = cfg.ANNUAL_FACTOR,
) -> dict:
    """Compute standard quantitative performance metrics."""
    returns  = equity.pct_change().dropna()
    cum      = equity / equity.iloc[0]
    n        = len(returns)
    ann_ret  = cum.iloc[-1] ** (ann / n) - 1.0 if n > 0 else float("nan")
    sharpe   = (returns.mean() / returns.std(ddof=1)) * ann**0.5 if returns.std() > 0 else float("nan")
    down_std = returns[returns < 0].std(ddof=1)
    sortino  = (returns.mean() / down_std) * ann**0.5 if down_std > 0 else float("nan")
    drawdown = (cum / cum.cummax()) - 1.0
    max_dd   = drawdown.min()
    calmar   = ann_ret / abs(max_dd) if max_dd != 0 else float("nan")

    wins     = [t for t in trades if t.net_pnl > 0]
    losses   = [t for t in trades if t.net_pnl <= 0]
    win_rate = len(wins) / len(trades) if trades else float("nan")
    pf_den   = abs(sum(t.net_pnl for t in losses))
    pf_num   = sum(t.net_pnl for t in wins)
    pf       = pf_num / pf_den if pf_den > 0 else float("inf")

    return {
        "Total Return":      cum.iloc[-1] - 1.0,
        "Annualized Return": ann_ret,
        "Sharpe Ratio":      sharpe,
        "Sortino Ratio":     sortino,
        "Calmar Ratio":      calmar,
        "Max Drawdown":      max_dd,
        "Win Rate":          win_rate,
        "Profit Factor":     pf,
        "Avg Win  ($)":      np.mean([t.net_pnl for t in wins])   if wins   else 0.0,
        "Avg Loss ($)":      np.mean([t.net_pnl for t in losses]) if losses else 0.0,
        "Total Trades":      len(trades),
    }
