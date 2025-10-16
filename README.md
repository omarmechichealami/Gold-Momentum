# Gold-Momentum
Python-based quantitative trading strategy applied to PAXG/USDT on the 5-minute timeframe, leveraging historical market data.

🟡 PAXG/USDT 5m Trading Strategy – MACD + Volatility Filter

A high-frequency backtesting engine using Python to trade tokenized gold (PAXG) on Binance, based on MACD momentum and volatility filters.

⸻

📌 Overview

This project implements a rule-based quantitative trading strategy on the PAXG/USDT pair using 5-minute candlesticks from Binance. It uses technical indicators like MACD, ATR, and time-based exits to generate entries and exits, simulates equity over time, and compares the strategy against Buy & Hold performance.

⸻

⚙️ Strategy Logic
	•	Entry Signal:
	•	At least 3 consecutive bars with positive MACD histogram (macd_positive_streak)
	•	Volatility above average (measured via ATR)
	•	Exit Conditions (any of the following):
	•	MACD histogram turns negative (momentum reversal)
	•	+2% take profit hit
	•	-1% stop loss hit
	•	Trade open for more than 2 hours (24 bars on 5m)
	•	Fees:
	•	0.005% per trade (realistic Binance taker fee)

<img width="1082" height="443" alt="Capture d’écran 2025-10-17 à 00 05 17" src="https://github.com/user-attachments/assets/8f8e1aa4-04d9-494b-a9b7-32af66811bd3" />
<img width="497" height="72" alt="Capture d’écran 2025-10-17 à 00 05 07" src="https://github.com/user-attachments/assets/3d1deda5-4dd2-4fca-9881-285c50108f09" />
<img width="312" height="220" alt="Capture d’écran 2025-10-17 à 00 05 21" src="https://github.com/user-attachments/assets/d71d28f9-37e1-4338-b02f-22ad59f3997a" />
