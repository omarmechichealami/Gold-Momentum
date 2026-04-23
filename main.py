"""
Gold Trend-Momentum Strategy — Main Entry Point

Usage:
    python main.py

Output:
    - Performance stats printed to console
    - 4 charts saved to ./charts/
"""

from __future__ import annotations
import pandas as pd
from backtest import run_backtest, compute_stats
from visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_trades,
    plot_summary_table,
)
import config as cfg


def _print_stats(stats: dict, label: str) -> None:
    sep = "═" * 48
    print(f"\n{sep}\n  {label}\n{sep}")
    for k, v in stats.items():
        if isinstance(v, float):
            s = f"{v:.2%}" if ("Return" in k or "Drawdown" in k or "Rate" in k) else f"{v:.3f}"
        else:
            s = str(v)
        print(f"  {k:<30}  {s:>10}")
    print(sep)


def main() -> None:
    result = run_backtest()

    if not result.trades:
        print("No trades generated — review parameter thresholds in config.py.")
        return

    df = result.signals_df

    # ── Strategy performance ───────────────────────────────────────────────────
    stats = compute_stats(result.equity_curve, result.trades)
    _print_stats(stats, "Gold Trend-Momentum Strategy  (GC=F, 2015–2024)")

    # ── Benchmark comparison ───────────────────────────────────────────────────
    bh_ret = df["Close"].pct_change().dropna().reindex(result.equity_curve.index).dropna()
    cum_bh = (1 + bh_ret).cumprod()
    n      = len(bh_ret)
    ann_r  = cum_bh.iloc[-1] ** (cfg.ANNUAL_FACTOR / n) - 1
    sh_bh  = (bh_ret.mean() / bh_ret.std(ddof=1)) * cfg.ANNUAL_FACTOR**0.5
    mdd_bh = ((cum_bh / cum_bh.cummax()) - 1).min()
    print(f"\n  Gold Buy & Hold  AnnRet {ann_r:.2%} | Sharpe {sh_bh:.2f} | MaxDD {mdd_bh:.2%}")

    # ── Exit reason breakdown ──────────────────────────────────────────────────
    reasons = pd.Series([t.exit_reason for t in result.trades]).value_counts()
    print("\n── Exit Reasons ──────────────────────────────────────────────────")
    for reason, count in reasons.items():
        print(f"  {reason:<32}  {count:>4} trades")

    # ── Charts ────────────────────────────────────────────────────────────────
    print("\nGenerating charts…")
    plot_equity_curve(result, df["Close"])
    plot_drawdown(result, df["Close"])
    plot_trades(result, df)
    plot_summary_table(stats)
    print("All charts saved to ./charts/\n")


if __name__ == "__main__":
    main()
