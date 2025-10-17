🧠 Strategy Logic: Gold (PAXGUSDT) Intraday Momentum

📈 Entry Criteria

This strategy enters a long position based on momentum confirmation and volume anomalies, with the following conditions evaluated on 15-minute candles:
	1.	MACD Histogram Momentum (on 15m candles):
	•	The MACD histogram must be above a threshold (> 0.1)
	•	The MACD momentum (change in histogram) must be positive and significant (> 0.01)
	•	This ensures the entry is backed by recent momentum acceleration.
	2.	Volume Spike on Small Candle (5m candles):
	•	A volume spike is detected when the volume is greater than 12× the 24h rolling average.
	•	The candle body must be small (body < 0.1%)
	•	This is a contrarian entry signal indicating potential reversal after aggressive buying or selling on low price movement.
	3.	Cooldown Period:
	•	After each trade, the system waits at least COOLDOWN_BARS = 12 bars (i.e. 1 hour on 5m candles) before taking a new position.

⸻

📉 Exit Criteria

Once in position, exits are monitored on 5-minute candles:
	1.	Take Profit:
	•	Exit if the position reaches a gain of +1%
	2.	Stop Loss:
	•	Exit if the loss reaches -0.5%
	3.	Volume Anomaly Exit (optional but active):
	•	If a volume spike + small candle is detected after entry AND the trade is currently losing, exit early.

⚠️ Note: There is no MACD-based exit in this version. The logic focuses purely on price-based and anomaly-based exits.
	     Transaction Fees: 0% assumed

<img width="1106" height="437" alt="Capture d’écran 2025-10-17 à 18 14 26" src="https://github.com/user-attachments/assets/d172f76f-57d6-41a2-8c68-c5f4aea1ad30" />
<img width="337" height="170" alt="Capture d’écran 2025-10-17 à 18 14 12" src="https://github.com/user-attachments/assets/dc29ecac-7b2c-4263-aa70-d1d1388bdac2" />
<img width="484" height="68" alt="Capture d’écran 2025-10-17 à 18 13 43" src="https://github.com/user-attachments/assets/08158871-ac73-4497-a036-10c84eb0d8a1" />
