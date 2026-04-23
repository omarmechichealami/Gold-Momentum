"""
Gold Trend-Momentum Strategy — Configuration
All tunable parameters. Edit only this file to adjust the strategy.
"""

# ── Data ──────────────────────────────────────────────────────────────────────
TICKER:     str = "GC=F"          # COMEX Gold Futures via Yahoo Finance
START_DATE: str = "2015-01-01"
END_DATE:   str = "2024-12-31"

# ── Trend Filter (Secular Regime) ─────────────────────────────────────────────
TREND_EMA: int = 200              # Price must be above EMA-200 to go long

# ── Primary Entry — EMA Crossover System ─────────────────────────────────────
FAST_EMA:      int   = 21         # Short-term EMA
SLOW_EMA:      int   = 55         # Medium-term EMA
RSI_PERIOD:    int   = 14
RSI_ENTRY_MIN: float = 50.0       # RSI must be above 50 on entry

# ── MACD Confirmation ─────────────────────────────────────────────────────────
MACD_FAST:   int = 12
MACD_SLOW:   int = 26
MACD_SIGNAL: int = 9

# ── Secondary Entry — Bollinger Band Squeeze Breakout ────────────────────────
BB_PERIOD:             int   = 20
BB_STD:                float = 2.0
BB_SQUEEZE_THRESHOLD:  float = 0.015   # Normalized band-width < 1.5% → squeeze

# ── ATR-Based Risk Management ─────────────────────────────────────────────────
ATR_PERIOD:      int   = 14
ATR_STOP_MULT:   float = 2.5      # Initial stop-loss = entry − 2.5×ATR
ATR_TRAIL_MULT:  float = 3.0      # Trailing stop     = high-water − 3.0×ATR

# ── Additional Exit ───────────────────────────────────────────────────────────
RSI_EXIT: float = 38.0            # Exit if RSI collapses below 38

# ── Position Sizing ───────────────────────────────────────────────────────────
RISK_PER_TRADE: float = 0.02      # Risk 2% of equity per trade

# ── Drawdown Circuit-Breaker ──────────────────────────────────────────────────
MAX_ROLLING_DD:   float = -0.12   # Pause new entries if 60-day DD < −12%
DD_LOOKBACK_DAYS: int   = 60

# ── Execution Costs ───────────────────────────────────────────────────────────
FEE_RATE: float = 0.0002          # 0.02% per side (futures commission)
SLIPPAGE: float = 0.0003          # 0.03% per side

# ── Misc ──────────────────────────────────────────────────────────────────────
INITIAL_EQUITY: float = 100_000.0
COOLDOWN_BARS:  int   = 5         # Bars to wait after exit before new entry
ANNUAL_FACTOR:  int   = 252       # Trading days for annualisation
