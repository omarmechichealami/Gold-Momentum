# Gold-Momentum
Python-based quantitative trading strategy applied to PAXG/USDT on the 5-minute timeframe, leveraging historical market data.

✅ Entry Conditions (all must be true)

We enter a long position on Gold (PAXG/USDT) only when the following two conditions are met:
	1.	MACD shows strong bullish momentum
➤ MACD histogram has been positive for at least 3 consecutive candles
➤ Suggests sustained upward momentum
	2.	High market volatility
➤ The current ATR (Average True Range) is above its 50-period average
➤ Indicates strong market activity and room for movement

⸻

❌ Exit Conditions (any one is enough)

We exit the Gold position if any of the following conditions occur:
	1.	MACD momentum reverses
➤ MACD histogram turns negative
➤ Suggests a shift in trend
	2.	Take-profit hit
➤ Price rises +2% from the entry
➤ Secure gains in strong up moves
	3.	Stop-loss triggered
➤ Price drops -1% from the entry
➤ Risk management to protect capital
	4.	Maximum holding time reached
➤ Trade exceeds 24 candles (2 hours on a 5-minute chart)
➤ Ensures positions aren’t held in sideways markets

<img width="1082" height="443" alt="Capture d’écran 2025-10-17 à 00 05 17" src="https://github.com/user-attachments/assets/8f8e1aa4-04d9-494b-a9b7-32af66811bd3" />
<img width="497" height="72" alt="Capture d’écran 2025-10-17 à 00 05 07" src="https://github.com/user-attachments/assets/3d1deda5-4dd2-4fca-9881-285c50108f09" />
<img width="312" height="220" alt="Capture d’écran 2025-10-17 à 00 05 21" src="https://github.com/user-attachments/assets/d71d28f9-37e1-4338-b02f-22ad59f3997a" />
