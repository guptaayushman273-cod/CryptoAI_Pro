# CryptoAI Pro

> AI-Powered Cryptocurrency Market Analysis and Risk-Managed Paper Trading System

---

## Project Information

**Project Name:** CryptoAI Pro  
**Current Version:** V3  
**Developer:** Ayushman Gupta  
**Program:** B.Tech Artificial Intelligence & Machine Learning  
**Institution:** NMIMS  

---

## Project Overview

CryptoAI Pro is a Python-based cryptocurrency analysis and paper-trading platform designed as a software engineering and artificial intelligence project.

The system collects live cryptocurrency market data from CoinDCX, calculates technical indicators, performs machine-learning inference, combines multiple signals through a hybrid decision engine, applies risk-management rules, and simulates trades through a paper-trading system.

The project also includes SQLite database storage and a Streamlit dashboard for monitoring the system.

> **Current Mode:** Risk-Managed Paper Trading  
> **Live-Money Trading:** Disabled

---

## Development Progress

**Overall Project Progress: 100%**

| Version | Description | Progress |
|---|---|---:|
| V1 | Core Foundation | 100% |
| V2 | Paper Trading System | 100% |
| V3 | AI / ML Intelligence | 100% |

---

## Current Features

### Market Data

- CoinDCX API integration
- Live market scanner
- ML-supported market filtering
- Live ticker data
- Historical candle retrieval
- 24-hour market change
- Trading volume analysis

### Technical Analysis

The system currently calculates:

- RSI
- EMA20
- EMA50
- MACD
- MACD Signal
- Bollinger Bands
- ATR
- Price returns
- Volume changes

### Artificial Intelligence

- Historical ML dataset pipeline
- Multi-market training dataset
- 19 engineered ML features
- Chronological train/test split
- Logistic Regression baseline
- Random Forest classifier
- Live Random Forest inference
- AI probability calculation
- AI signal generation
- Coin-by-coin model evaluation

### Hybrid Decision Engine

CryptoAI Pro combines:

- Market momentum
- News sentiment
- EMA trend
- RSI
- MACD
- Bollinger Bands
- ATR volatility
- Machine-learning probability

The decision engine can generate:

- BUY
- WATCH
- AVOID

A BUY requires multiple confirmations instead of relying on a single indicator.

### Risk Management

The risk-management system includes:

- Account risk limits
- Position-size calculation
- Maximum position-size protection
- Stop Loss
- Take Profit
- Risk/Reward calculation
- Trade approval/rejection

Current default configuration:

| Parameter | Value |
|---|---:|
| Risk Limit | 2% |
| Maximum Position | 25% |
| Stop Loss | 3% |
| Take Profit | 6% |
| Minimum Risk/Reward | 1.5 |
| Default Risk/Reward | 2:1 |

### Paper Trading

- Simulated BUY orders
- Simulated SELL orders
- Position tracking
- Stop-loss exits
- Take-profit exits
- Profit/Loss calculation
- Trade history
- SQLite persistence

No real cryptocurrency is purchased or sold.

### Dashboard

The Streamlit V3 dashboard displays:

- Overall project progress
- V1/V2/V3 progress
- System status
- Selected ML-supported market
- Current market price
- 24-hour market change
- Volume
- Technical indicators
- AI probability
- AI signal
- Hybrid trading decision
- Decision score
- Technical confirmations
- Risk-management plan
- Current paper position
- Trading statistics
- Win rate
- Cumulative Profit/Loss
- Trade history
- Machine-learning information
- System pipeline

The dashboard is monitoring/analysis only and does not automatically execute trades.

---

## Machine Learning Model

### Algorithm

**Random Forest Classifier**

### Training Markets

- BTCUSDT
- ETHUSDT
- LSKUSDT

### Number of Features

**19**

### Prediction Target

The model predicts whether:

**Future 5-candle return > +0.20%**

---

## ML Evaluation

The Random Forest was evaluated on an unseen chronological test dataset containing **2,970 rows**.

| Metric | Result |
|---|---:|
| Accuracy | 78.32% |
| Precision | 34.78% |
| Recall | 76.88% |
| F1 Score | 47.90% |
| ROC-AUC | 0.8306 |
| Majority Baseline Accuracy | 87.04% |

### Important Model Limitation

Performance differs significantly across BTCUSDT, ETHUSDT, and LSKUSDT.

Because of this, the model is considered **experimental**.

ML output is used as an advisory component of the hybrid decision system rather than as an independent trading signal.

The model is not considered production-ready.

---

## System Architecture

```text
CoinDCX Market Data
        |
        v
Technical Indicators
        |
        v
Market + News Analysis
        |
        v
Random Forest AI
        |
        v
Hybrid Decision Engine
        |
        v
Risk Manager
        |
        v
Paper Trader
        |
        v
SQLite Database
        |
        v
Streamlit Dashboard
```

---

## Project Structure

```text
CryptoAI_Bot/
|
|-- ai/
|   |-- ml_predictor.py
|
|-- api/
|   |-- coindcx_api.py
|
|-- backtesting/
|
|-- dashboard/
|   |-- app.py
|
|-- data/
|   |-- candles/
|   |-- models/
|   |-- dataset_builder.py
|   |-- prepare_ml_data.py
|   |-- train_model.py
|   |-- test_model.py
|   |-- analyze_model.py
|   |-- analyze_random_forest.py
|   |-- analyze_target.py
|
|-- database/
|   |-- database.py
|   |-- trade_history.py
|
|-- indicators/
|   |-- indicators.py
|
|-- market/
|   |-- market_data.py
|
|-- risk/
|   |-- risk_manager.py
|
|-- strategy/
|   |-- decision_engine.py
|   |-- news_ai.py
|
|-- trader/
|   |-- paper_trader.py
|   |-- position_monitor.py
|   |-- fee_manager.py
|
|-- tests/
|
|-- utils/
|
|-- config.py
|-- logging_config.py
|-- main.py
|-- trading_bot.py
|-- README.md
|-- PROJECT_STATUS.md
|-- ROADMAP.md
|-- CHANGELOG.md
|-- SESSION_HANDOVER.md
```

---

## Running CryptoAI Pro

### Main Analysis System

From the project root:

```bat
python main.py
```

The program will:

1. Scan ML-supported CoinDCX markets.
2. Select a market.
3. Download candle data.
4. Calculate technical indicators.
5. Analyze market momentum.
6. Run sentiment analysis.
7. Run the Random Forest model.
8. Generate a hybrid trading decision.
9. Calculate risk parameters.
10. Execute a paper BUY only when all required conditions pass.

---

## Running the Dashboard

Start the Streamlit dashboard with:

```bat
streamlit run dashboard/app.py
```

If the `streamlit` command is unavailable:

```bat
python -m streamlit run dashboard/app.py
```

The dashboard should normally become available through Streamlit's local development server.

---

## Testing

Important system tests include:

```bat
python -m data.test_model
python -m market.market_data
python -m risk.risk_manager
python -m trader.paper_trader
python main.py
```

These tests verify the major AI, market-data, risk-management, paper-trading, and integration components.

---

## Safety Design

CryptoAI Pro currently operates in paper-trading mode.

Important safeguards include:

- Live-money trading disabled
- Maximum position limits
- Stop-loss calculation
- Take-profit calculation
- Risk/reward validation
- Hybrid BUY confirmation
- ML-supported market filtering
- API credentials stored outside source code
- `.env` excluded from Git
- Dashboard cannot automatically execute trades

---

## Technologies

- Python
- pandas
- NumPy
- scikit-learn
- Streamlit
- SQLite
- CoinDCX API
- Machine Learning
- Technical Analysis
- Git
- GitHub

---

## Current Development Status

### V1 - Core Foundation

**100% Complete**

### V2 - Paper Trading

**100% Complete**

### V3 - AI / ML Intelligence

**100% Complete**

Current V3 work includes the complete ML pipeline, Random Forest inference, hybrid decision engine, risk-managed paper trading integration, and V3 dashboard.

Remaining work is primarily final documentation, repository cleanup, and demonstration verification.

---

## Future Development

Possible future versions may include:

- Improved per-market ML models
- Better target engineering
- Walk-forward validation
- Advanced backtesting
- Portfolio-level risk management
- Improved real-time news ingestion
- Model monitoring
- Telegram notifications
- More advanced dashboard analytics
- Deployment to a server/VPS

Live-money trading should only be considered after substantially more testing, validation, security work, and risk controls.

---

## Learning Goals

CryptoAI Pro is also a practical learning project covering:

- Python software development
- API integration
- Git and GitHub
- Database design
- Technical analysis
- Machine learning
- Feature engineering
- Model evaluation
- Risk management
- Software architecture
- Dashboard development
- Testing and debugging

---

## Disclaimer

CryptoAI Pro is an educational and experimental software project.

The current system uses simulated paper trading. Machine-learning predictions and technical indicators are experimental and should not be interpreted as financial advice or guaranteed trading signals.

---

## Developer

**Ayushman Gupta**

B.Tech Artificial Intelligence & Machine Learning

---

## Last Updated

19 September 2026