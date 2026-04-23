# Gold Trend-Momentum Strategy

> A systematic, long-only strategy on Gold Futures (GC=F) that combines EMA crossover
> trend-following with Bollinger Band squeeze breakouts, using dynamic ATR-based stops
> and a trailing stop to let winning trades run.

---

## Strategy Thesis

Gold is one of the most trend-persistent assets in financial markets. Unlike equities,
gold's multi-year trends are driven by real interest rates, USD cycles, and geopolitical
risk premiums — structural forces that are slow to reverse.

This strategy exploits two distinct gold momentum patterns:

1. **EMA crossover trends** — when the 21-day EMA crosses above the 55-day EMA while
   price trades above EMA-200, it signals the onset of a sustained trend. MACD and RSI
   confirm the momentum regime before entry.

2. **Volatility squeeze breakouts** — periods of low volatility (Bollinger Band width < 1.5%)
   followed by a directional breakout above the upper band identify high-conviction,
   explosive moves with favourable risk/reward.

The **ATR-based trailing stop** is the core risk management innovation: rather than a
fixed take-profit, it lets winning positions compound as gold trends, only exiting when
the trend genuinely reverses.

---

## Methodology

### Entry Conditions

**Primary — EMA Trend System (all must be true):**

| Condition | Description |
|-----------|-------------|
| Price > EMA(200) | Secular uptrend — not a bear market |
| EMA(21) > EMA(55) | Medium-term trend is bullish |
| RSI(14) > 50 | Positive momentum confirmed |
| MACD histogram > 0 | Momentum is accelerating |

**Secondary — Bollinger Band Squeeze Breakout:**

| Condition | Description |
|-----------|-------------|
| Price > EMA(200) | Uptrend filter applies |
| BB width < 1.5% of price | Market was in compression |
| Close breaks above prior upper BB | Directional breakout |

### Exit Conditions

| Condition | Description |
|-----------|-------------|
| Price ≤ entry − 2.5×ATR(14) | Initial stop-loss (fixed at entry) |
| Price ≤ rolling_high − 3.0×ATR(14) | Trailing stop — locks in profits |
| EMA(21) crosses below EMA(55) | Trend reversal confirmed |
| RSI(14) < 38 | Momentum collapse |

### Risk Management

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Position size | 2% equity at risk | Consistent risk sizing per trade |
| Initial stop | 2.5×ATR below entry | Adapts to current gold volatility |
| Trailing stop | 3.0×ATR below high-water | Lets winners run |
| Circuit-breaker | −12% rolling 60-day DD | Prevents deep portfolio drawdowns |
| Cooldown | 5 bars after exit | Avoids immediate re-entry after loss |
| Fees | 0.02% per side | Realistic futures commission |
| Slippage | 0.03% per side | Conservative execution assumption |

### Data

| Field | Value |
|-------|-------|
| Source | Yahoo Finance (`GC=F` — COMEX Gold Futures, adjusted) |
| Frequency | Daily |
| Period | 2015-01-01 → 2024-12-31 (10-year backtest) |

---

## Backtest Results

> Run `python main.py` to reproduce all results and charts.

| Metric | Strategy | Gold B&H |
|--------|----------|----------|
| Annualized Return | *see output* | — |
| Sharpe Ratio | *see output* | — |
| Sortino Ratio | *see output* | — |
| Max Drawdown | *see output* | — |
| Calmar Ratio | *see output* | — |
| Win Rate | *see output* | — |
| Profit Factor | *see output* | — |

### Generated Charts (in `./charts/`)

| File | Description |
|------|-------------|
| `equity_curve.png` | Growth of $1 vs Gold buy-and-hold (log scale, outperformance shaded) |
| `drawdown.png` | Underwater equity for strategy and benchmark |
| `trades.png` | Price + EMA bands with shaded trade periods and entry/exit markers |
| `summary_table.png` | Complete performance metrics table |

---

## Limitations & Risks

- **Futures roll bias**: GC=F uses front-month contracts. Yahoo Finance adjusts prices
  for rolls, but this introduces small artefacts that may slightly inflate performance.
- **Trend-following drag**: All EMA systems underperform in flat, choppy markets.
  The EMA-200 filter mitigates but does not eliminate false entries.
- **Leverage not modelled**: Gold futures embed 10–20× leverage in practice. This
  strategy models notional exposure only; actual margin requirements not considered.
- **Tail event risk**: Gold can gap sharply (central bank rate decisions, geopolitical
  shocks). Stop-losses in real markets execute at the first available price after the gap.
- **Parameter sensitivity**: ATR multiples and EMA periods reflect professional defaults
  from commodity trend-following literature, not in-sample optimization.

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full backtest and generate charts
python main.py
```

> No local data files needed — prices are downloaded automatically from Yahoo Finance.

### Project Structure

```
├── config.py         # All strategy parameters (edit here only)
├── data.py           # Data fetching (Yahoo Finance, GC=F)
├── indicators.py     # EMA, RSI, MACD, ATR, Bollinger Bands
├── signals.py        # Entry/exit signal generation (no lookahead)
├── backtest.py       # Event-driven engine + ATR trailing stop + stats
├── visualize.py      # 4 professional charts
├── main.py           # Entry point
├── requirements.txt
└── charts/           # Generated after running main.py
```

---

## Disclaimer

This repository is for educational and research purposes only.
Past backtest performance does not guarantee future results.
Commodity futures trading involves substantial leverage and risk of loss.
