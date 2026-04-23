"""
Professional visualizations for the Gold Trend-Momentum strategy.
Generates 4 charts saved to ./charts/.
"""

from __future__ import annotations
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from backtest import BacktestResult, Trade

OUTPUT_DIR = Path("charts")
OUTPUT_DIR.mkdir(exist_ok=True)

C = {
    "strategy":  "#B8860B",   # Dark gold
    "benchmark": "#888888",
    "positive":  "#2ecc71",
    "negative":  "#e74c3c",
    "ema_fast":  "#3498db",
    "ema_slow":  "#e67e22",
    "bg":        "#fafafa",
}


def _save(fig: plt.Figure, name: str) -> None:
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.close(fig)


def _fmt_pct(ax: plt.Axes) -> None:
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))


# ── Chart 1: Equity Curve ────────────────────────────────────────────────────

def plot_equity_curve(result: BacktestResult, gold_close: pd.Series) -> None:
    """Strategy equity curve vs Gold buy-and-hold."""
    eq   = result.equity_curve
    bh   = gold_close.reindex(eq.index).ffill()
    strat_norm = eq  / eq.iloc[0]
    bh_norm    = bh  / bh.iloc[0]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_facecolor(C["bg"])
    ax.plot(strat_norm.index, strat_norm.values,
            color=C["strategy"],  lw=2.4, label="Gold Trend-Momentum Strategy")
    ax.plot(bh_norm.index, bh_norm.values,
            color=C["benchmark"], lw=1.5, ls="--", alpha=0.8, label="Gold Buy & Hold (GC=F)")
    ax.fill_between(strat_norm.index,
                    strat_norm.values, bh_norm.values,
                    where=(strat_norm.values >= bh_norm.values),
                    alpha=0.12, color=C["positive"])
    ax.fill_between(strat_norm.index,
                    strat_norm.values, bh_norm.values,
                    where=(strat_norm.values < bh_norm.values),
                    alpha=0.10, color=C["negative"])

    ax.set_title("Gold Trend-Momentum — Equity Curve vs Benchmark",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Growth of $1 (log scale)")
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "equity_curve.png")


# ── Chart 2: Drawdown ────────────────────────────────────────────────────────

def plot_drawdown(result: BacktestResult, gold_close: pd.Series) -> None:
    """Underwater equity for strategy and buy-and-hold."""
    eq   = result.equity_curve
    bh   = gold_close.reindex(eq.index).ffill()

    def _dd(s: pd.Series) -> pd.Series:
        cum = s / s.iloc[0]
        return (cum / cum.cummax()) - 1.0

    strat_dd = _dd(eq)
    bh_dd    = _dd(bh)

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.set_facecolor(C["bg"])
    ax.fill_between(strat_dd.index, strat_dd.values, 0,
                    color=C["strategy"],  alpha=0.50, label="Strategy DD")
    ax.fill_between(bh_dd.index, bh_dd.values, 0,
                    color=C["benchmark"], alpha=0.25, label="Gold B&H DD")
    ax.plot(strat_dd.index, strat_dd.values, color=C["strategy"], lw=0.9)
    ax.axhline(-0.12, color="black", lw=1.1, ls="--", label="−12% circuit-breaker")

    ax.set_title("Drawdown Chart — Gold Trend-Momentum Strategy vs Benchmark",
                 fontsize=13, fontweight="bold", pad=12)
    _fmt_pct(ax)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "drawdown.png")


# ── Chart 3: Trade Entry/Exit on Price Chart ─────────────────────────────────

def plot_trades(result: BacktestResult, df: pd.DataFrame) -> None:
    """Price + EMA chart with shaded trade periods and entry/exit markers."""
    eq    = result.equity_curve
    idx   = eq.index
    close = df["Close"].reindex(idx).ffill()
    fast  = df["ema_fast"].reindex(idx).ffill()
    slow  = df["ema_slow"].reindex(idx).ffill()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_facecolor(C["bg"])
    ax.plot(close.index, close.values, color="#555", lw=1.1, alpha=0.9,
            label="Gold (GC=F)", zorder=1)
    ax.plot(fast.index, fast.values, color=C["ema_fast"], lw=1.4,
            alpha=0.8, label="EMA-21", zorder=2)
    ax.plot(slow.index, slow.values, color=C["ema_slow"], lw=1.4, ls="--",
            alpha=0.8, label="EMA-55", zorder=2)

    for t in result.trades:
        if t.entry_date in close.index and t.exit_date in close.index:
            shade = C["positive"] if t.net_pnl > 0 else C["negative"]
            ax.axvspan(t.entry_date, t.exit_date, alpha=0.07, color=shade)
        if t.entry_date in close.index:
            ax.scatter(t.entry_date, t.entry_price,
                       marker="^", s=65, color=C["positive"], zorder=5)
        if t.exit_date in close.index:
            col = C["positive"] if t.net_pnl > 0 else C["negative"]
            ax.scatter(t.exit_date, t.exit_price,
                       marker="v", s=65, color=col, zorder=5)

    ax.set_title("Gold (GC=F) — EMA Crossover with Trade Entry/Exit",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Price (USD/oz)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "trades.png")


# ── Chart 4: Performance Summary Table ───────────────────────────────────────

def plot_summary_table(stats: dict) -> None:
    """Performance metrics as a formatted table."""
    rows = [
        ["Metric", "Value"],
        ["─" * 28, "─" * 14],
        ["Annualized Return",  f"{stats['Annualized Return']:.2%}"],
        ["Total Return",       f"{stats['Total Return']:.2%}"],
        ["Sharpe Ratio",       f"{stats['Sharpe Ratio']:.3f}"],
        ["Sortino Ratio",      f"{stats['Sortino Ratio']:.3f}"],
        ["Calmar Ratio",       f"{stats['Calmar Ratio']:.3f}"],
        ["Max Drawdown",       f"{stats['Max Drawdown']:.2%}"],
        ["Win Rate",           f"{stats['Win Rate']:.2%}"],
        ["Profit Factor",      f"{stats['Profit Factor']:.2f}"],
        ["Total Trades",       str(stats["Total Trades"])],
        ["Avg Win  ($)",       f"${stats['Avg Win  ($)']:,.0f}"],
        ["Avg Loss ($)",       f"${stats['Avg Loss ($)']:,.0f}"],
    ]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axis("off")
    tbl = ax.table(cellText=rows, cellLoc="left", loc="center", bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    for j in range(2):
        tbl[0, j].set_facecolor("#B8860B")
        tbl[0, j].set_text_props(color="white", fontweight="bold")
    for j in range(2):
        tbl[1, j].set_facecolor("#dddddd")
    ax.set_title("Gold Trend-Momentum — Performance Summary",
                 fontsize=13, fontweight="bold", pad=10)
    fig.tight_layout()
    _save(fig, "summary_table.png")
