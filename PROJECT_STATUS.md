# CryptoAI Pro

## Project Overview

CryptoAI Pro is an AI-powered cryptocurrency market analysis and paper-trading system.

The project combines live CoinDCX market data, technical indicators, machine learning, hybrid decision logic, risk management, paper trading, SQLite storage, and a Streamlit monitoring dashboard.

> Current mode: Risk-Managed Paper Trading  
> Live-money trading is intentionally disabled.

---

# Development Progress

## Overall Project Progress

**100% Complete**

## Version Progress

| Version | Phase | Progress | Status |
|---|---|---:|---|
| V1 | Core Foundation | 100% | Complete |
| V2 | Paper Trading System | 100% | Complete |
| V3 | AI / ML Intelligence | 100% | Complete |

---

# V1 - Core Foundation

**Status: COMPLETE**

Completed components:

- [x] Project structure
- [x] Git repository
- [x] Environment configuration
- [x] CoinDCX API integration
- [x] Market scanner
- [x] Market ticker retrieval
- [x] Candle data retrieval
- [x] Technical indicator system
- [x] RSI
- [x] EMA20
- [x] EMA50
- [x] MACD
- [x] MACD Signal
- [x] Bollinger Bands
- [x] ATR
- [x] Basic news sentiment analysis
- [x] Fee calculation
- [x] Logging foundation

---

# V2 - Paper Trading System

**Status: COMPLETE**

Completed components:

- [x] Paper trading engine
- [x] BUY simulation
- [x] SELL simulation
- [x] Position tracking
- [x] SQLite database
- [x] Trade history
- [x] Open position storage
- [x] Profit/Loss calculation
- [x] Stop-loss support
- [x] Take-profit support
- [x] Risk management
- [x] Position sizing
- [x] Maximum position protection
- [x] Risk/reward calculation
- [x] Dashboard foundation
- [x] Trading statistics
- [x] Profit/Loss chart

---

# V3 - AI / ML Intelligence

**Status: 100% COMPLETE**

Completed components:

- [x] Historical dataset pipeline
- [x] Multi-market dataset
- [x] Feature engineering
- [x] 19 ML features
- [x] Chronological train/test split
- [x] Logistic Regression baseline
- [x] Random Forest model
- [x] Model evaluation
- [x] Target-return analysis
- [x] Improved ML target
- [x] Live ML inference
- [x] ML-supported market filtering
- [x] AI probability output
- [x] Hybrid decision engine
- [x] Technical confirmation system
- [x] ML confirmation system
- [x] Risk-manager integration
- [x] Safe paper-trading execution gate
- [x] V3 Streamlit dashboard
- [x] Overall/V1/V2/V3 progress display
- [x] Live market analysis dashboard
- [x] AI intelligence dashboard
- [x] Risk-management dashboard

Remaining V3 work:

- [ ] Final documentation cleanup
- [ ] Final GitHub commit and push
- [ ] Final demonstration verification

---

# Machine Learning System

## Model

Random Forest Classifier

## Training Markets

- BTCUSDT
- ETHUSDT
- LSKUSDT

## Features

The model uses **19 engineered features**, including:

- OHLCV market data
- RSI
- Short-term returns
- EMA relationships
- MACD relationships
- Bollinger Band position
- Bollinger Band width
- ATR percentage
- Volume change

## Prediction Target

The current target is:

**Future 5-candle return > +0.20%**

---

# ML Test Results

Unseen chronological test dataset:

- Test Rows: 2,970
- Accuracy: 78.32%
- Precision: 34.78%
- Recall: 76.88%
- F1 Score: 47.100%
- ROC-AUC: 0.8306

Majority-class baseline accuracy:

**87.04%**

The model is experimental. Aggregate ROC-AUC is encouraging, but performance varies significantly between individual markets.

Therefore, ML predictions are used only as one advisory component of the hybrid decision engine.

The model is not considered production-ready.

---

# Hybrid Decision Engine

The trading decision system combines:

1. Market momentum
2. News sentiment
3. EMA trend
4. Price position relative to EMA20
5. RSI
6. MACD
7. Bollinger Bands
8. ATR volatility
9. Random Forest probability

Possible outputs:

- BUY
- WATCH
- AVOID

A BUY signal requires multiple technical confirmations and AI confirmation.

---

# Risk Management

Current default risk rules:

- Account risk limit: 2%
- Maximum position size: 25% of account balance
- Stop Loss: 3%
- Take Profit: 6%
- Minimum Risk/Reward Ratio: 1.5

Default strategy currently produces approximately:

**Risk/Reward = 2:1**

Risk approval does not automatically execute a trade.

A trade is opened only when both:

1. The decision engine generates a valid BUY signal.
2. The risk manager approves the trade parameters.

---

# Paper Trading

Current development balance:

**$200**

The paper trader supports:

- BUY
- SELL
- Position tracking
- Stop Loss
- Take Profit
- Profit/Loss calculation
- SQLite trade storage

No real cryptocurrency is purchased or sold.

---

# V3 Dashboard

The Streamlit dashboard displays:

- Overall project progress
- V1 progress
- V2 progress
- V3 progress
- System status
- Live ML-supported market
- Market price
- 24-hour change
- Volume
- RSI
- EMA20
- EMA50
- MACD
- ATR
- AI probability
- AI signal
- Hybrid trading decision
- Decision score
- Technical confirmations
- Risk-management plan
- Current paper position
- Trading statistics
- Win rate
- Profit/Loss
- Trade history
- ML model information
- System architecture

The dashboard operates in monitoring/analysis mode and does not automatically execute trades.

---

# Current System Pipeline

CoinDCX Market Data

↓

Technical Indicators

↓

Market + News Analysis

↓

Random Forest AI

↓

Hybrid Decision Engine

↓

Risk Manager

↓

Paper Trader

↓

SQLite Database

↓

Streamlit Dashboard

---

# Final System Test

The following modules have been successfully tested:

- [x] Random Forest test evaluation
- [x] ML-supported market scanner
- [x] Risk manager
- [x] Paper trader
- [x] Complete main.py pipeline

Latest end-to-end test successfully produced:

- ML-supported market selection
- Technical indicators
- Market momentum score
- News sentiment score
- Random Forest probability
- Hybrid decision
- Risk calculation
- Safe execution gating

When the decision was AVOID, the system correctly calculated hypothetical risk parameters without opening a paper position.

---

# Safety Status

- [x] Paper trading enabled
- [x] Risk limits enabled
- [x] Stop loss enabled
- [x] Take profit enabled
- [x] ML-supported market filtering enabled
- [x] Decision execution gate enabled
- [x] `.env` excluded from Git
- [x] Dashboard does not automatically execute trades
- [ ] Live-money trading

Live-money trading remains intentionally disabled.

---

# Remaining Work

1. Complete final documentation.
2. Verify Git status.
3. Verify `.env` is ignored.
4. Commit final V3 changes.
5. Push final project to GitHub.
6. Perform final demonstration check.

---

# Current Version

**CryptoAI Pro V3 - AI/ML Risk-Managed Paper Trading**

## Last Updated

19 September 2026