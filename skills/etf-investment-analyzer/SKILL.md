---
name: etf-investment-analyzer
description: >
  Comprehensive ETF investment analysis and trading recommendation system.
  Use when: analyzing ETF portfolios, generating daily investment reports,
  backtesting trading strategies, monitoring ETF positions, or providing
  buy/sell/hold recommendations based on technical indicators.

  Features:
  - Multi-timeframe analysis (long-term 1-year + short-term 1-month rolling data)
  - Triple-year data support (2024+2025+2026 historical data)
  - Technical indicator calculations (MA, MACD, RSI, KDJ, Bollinger Bands)
  - Strategy backtesting and optimization (Buy&Hold, MA Cross, RSI, Bollinger)
  - Simulated trading system with trade logging
  - Automated daily report generation
  - Feishu document integration
  - Support for A-share, US, and sector ETFs

  Data sources: QVeris (THS iFinD), AKShare, local historical data (2024+2025)
---

# ETF Investment Analyzer

A comprehensive ETF investment analysis system with multi-timeframe technical analysis, dual-year data support, strategy backtesting, and automated reporting.

## Core Features

1. **Multi-Timeframe Analysis**
   - Long-term: Rolling 1-year data (243 trading days) for trend judgment
   - Short-term: Rolling 1-month data (20 trading days) for signal capture
   - Dual-year support: 2024 + 2025 historical data combined

2. **Technical Indicators**
   - Moving Averages (MA5, MA10, MA20, MA60)
   - MACD (DIF, DEA, Histogram) with golden/death cross detection
   - RSI (6, 14 periods) with overbought/oversold signals
   - KDJ (K, D, J values) with cross signals
   - Bollinger Bands (20, 2) with breakout detection

3. **Strategy Backtesting**
   - Buy & Hold
   - Moving Average Crossover (MA5/MA20, customizable)
   - RSI Overbought/Oversold
   - Bollinger Band Breakout
   - Optimal strategy recommendation per ETF

4. **Simulated Trading System**
   - Initial capital: ¥100,000
   - Trade logging with reasons
   - Portfolio valuation
   - Performance tracking

5. **Automated Reporting**
   - Daily market review (A-share + US markets)
   - Portfolio analysis with P&L
   - Trading recommendations
   - Risk warnings
   - Feishu document sync

## Quick Start

### Daily Analysis Workflow

```bash
# 1. Data collection (8:00 AM)
python3 scripts/daily_data_collection.py

# 2. Generate analysis report (8:30 AM)
python3 scripts/daily_report.py

# 3. Sync to Feishu
python3 scripts/sync_feishu.py
```

### Manual ETF Analysis

```python
from scripts.etf_analyzer import ETFAnalyzer, TradingSimulator

# Initialize analyzer with dual-year data support
analyzer = ETFAnalyzer()

# Analyze single ETF with dual-year data
result = analyzer.analyze_etf('510050', use_dual_year=True)

# Analyze portfolio
portfolio = analyzer.analyze_portfolio()

# Backtest strategy
backtest = analyzer.backtest_strategy(
    etf_code='510050',
    strategy='ma_cross',
    start_date='20240101',
    end_date='20250325'
)

# Get optimal strategy for ETF
optimal = analyzer.get_optimal_strategy('510050')

# Simulated trading
sim = TradingSimulator(initial_capital=100000)
sim.buy('510050', price=3.105, shares=1000, reason='MACD金叉')
sim.sell('510050', price=3.200, shares=500, reason='止盈20%')
```

## Data Sources

### Primary: Local Historical Data (Dual-Year)
- 2024 data: ~3132 records per ETF
- 2025 data: ~2916 records per ETF
- Combined: Full trading history for analysis

### Secondary: QVeris (THS iFinD)
- Professional financial database
- Real-time and historical A-share ETF data
- Requires QVERIS_API_KEY

### Tertiary: AKShare
- Free open-source alternative
- Backup data source

## Configuration

### Environment Variables

```bash
# Required for QVeris (optional if using local data)
export QVERIS_API_KEY="your-api-key"

# Optional: Feishu integration
export FEISHU_APP_ID="your-app-id"
export FEISHU_APP_SECRET="your-app-secret"
```

### Portfolio Configuration

Edit `references/portfolio_config.json`:

```json
{
  "holdings": [
    {"code": "510050.SH", "name": "上证50ETF", "shares": 8100, "cost": 2.382},
    {"code": "510300.SH", "name": "沪深300ETF", "shares": 5600, "cost": 2.728}
  ],
  "analysis_config": {
    "long_term_days": 243,
    "short_term_days": 20,
    "data_sources": {
      "primary": "local_dual_year",
      "secondary": "qveris",
      "backup": "akshare"
    }
  }
}
```

## Analysis Framework

### Long-Term Trend (1-Year Rolling)

Used for:
- Strategy selection
- Position sizing
- Trend confirmation

Indicators:
- MA20 vs MA60
- Annual return rate
- Maximum drawdown

### Short-Term Signals (1-Month Rolling)

Used for:
- Entry/exit timing
- Signal confirmation
- Risk management

Indicators:
- RSI overbought/oversold
- Bollinger band position
- KDJ cross signals

### Decision Matrix

| Long-Term | Short-Term | Action |
|-----------|-----------|--------|
| Upward | Oversold | **Buy** |
| Upward | Overbought | Hold/Partial Sell |
| Downward | Oversold | Wait |
| Downward | Overbought | **Sell** |

## Output Format

### Daily Report Structure

1. **Market Review**
   - A-share indices (Shanghai, Shenzhen, ChiNext)
   - US markets (DJI, S&P500, NASDAQ, VIX)

2. **Strategy Selection**
   - Current market regime
   - Optimal strategy recommendation
   - Strategy backtest comparison

3. **Portfolio Analysis**
   - All holdings with P&L
   - Technical indicators
   - Trading signals
   - Recommendations per ETF

4. **Simulated Trading Status**
   - Current cash position
   - Holdings value
   - Total return
   - Recent trades

5. **Action Items**
   - Immediate execution
   - Watch list
   - Hold positions

6. **Risk Warnings**
   - Market risks
   - Position risks
   - Strategy risks

## Scripts

- `etf_analyzer.py` - Core analysis engine with dual-year support
- `daily_report.py` - Daily report generation
- `daily_data_collection.py` - Automated data collection
- `sync_feishu.py` - Feishu document sync
- `backtest_engine.py` - Strategy backtesting (integrated in etf_analyzer)
- `simulator.py` - Trading simulator (integrated in etf_analyzer)

## References

- [Portfolio Configuration](references/portfolio_config.json)
- [Strategy Guide](references/strategy_guide.md)
- [API Reference](references/api_reference.md)

## Assets

- `report_template.md` - Daily report template
- `chart_styles.css` - Visualization styles

## Updates

**2026-03-25 Update:**
- Added dual-year data support (2024+2025)
- Enhanced signal generation with trend detection
- Added TradingSimulator class for paper trading
- Improved backtesting with multiple strategies
- Added optimal strategy recommendation
- Enhanced portfolio analysis with recommendations
