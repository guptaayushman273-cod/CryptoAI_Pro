# CryptoAI Pro - Session Handover

## Current Project State

CryptoAI Pro has reached the finalization stage of V3.

### Overall Progress

100%

### Version Progress

- V1 Core Foundation: 100%
- V2 Paper Trading: 100%
- V3 AI / ML Intelligence: 100%

---

# Current System Mode

AI/ML Risk-Managed Paper Trading

Live-money trading is disabled.

---

# Completed V1

- Project structure
- Git
- CoinDCX API
- Market scanner
- Candle retrieval
- Technical indicators
- Logging
- News sentiment
- Fee calculation
- Main application foundation

---

# Completed V2

- Paper trading
- BUY/SELL simulation
- SQLite database
- Trade history
- Position tracking
- Profit/Loss calculation
- Risk control
- Dashboard foundation
- Trading statistics

---

# Completed V3

## Machine Learning

- Historical dataset pipeline
- BTCUSDT dataset
- ETHUSDT dataset
- LSKUSDT dataset
- 19 engineered features
- Chronological train/test split
- Logistic Regression baseline
- Random Forest model
- Target-return analysis
- Improved target:
  Future 5-candle return > +0.20%
- Model evaluation
- Live ML inference
- AI probability generation

## Model Test Results

Unseen chronological test set:

- Rows: 2,970
- Accuracy: 78.32%
- Precision: 34.78%
- Recall: 76.88%
- F1: 47.100%
- ROC-AUC: 0.8306
- Majority baseline accuracy: 87.04%

Important:

The model has inconsistent coin-by-coin performance.

It must be treated as experimental and advisory only.

---

# Market Integration

ML-supported markets:

- BTCUSDT
- ETHUSDT
- LSKUSDT

The live market scanner can restrict selection to markets represented in the ML training data.

---

# Hybrid Decision Engine

The decision engine combines:

- Market momentum
- News sentiment
- EMA20/EMA50
- Price vs EMA20
- RSI
- MACD
- Bollinger Bands
- ATR
- Random Forest probability

Outputs:

- BUY
- WATCH
- AVOID

BUY requires multiple technical confirmations and AI confirmation.

---

# Risk Manager

Current defaults:

- Risk limit: 2%
- Maximum position: 25%
- Stop Loss: 3%
- Take Profit: 6%
- Minimum Risk/Reward: 1.5
- Normal Risk/Reward: 2:1

Risk approval does NOT automatically mean a trade should execute.

The decision engine must also generate BUY.

---

# Paper Trader

PaperTrader supports:

- BUY
- SELL
- Position tracking
- Stop Loss
- Take Profit
- Profit/Loss
- SQLite trade storage

Current development starting balance:

$200

---

# Dashboard

The V3 Streamlit dashboard includes:

- Overall progress
- V1 progress
- V2 progress
- V3 progress
- System status
- Live market data
- Technical indicators
- AI probability
- AI signal
- Hybrid decision
- Decision reasons
- Risk management
- Current paper position
- Trading performance
- P/L chart
- Trade history
- ML information
- System architecture

The dashboard is monitoring/analysis only.

It must NOT automatically execute trades during Streamlit reruns.

---

# Latest Successful System Test

Commands:

```bat
python -m data.test_model
python -m market.market_data
python -m risk.risk_manager
python -m trader.paper_trader
python main.py