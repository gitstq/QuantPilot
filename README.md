<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Indicators-19-orange.svg" alt="19 Indicators">
  <img src="https://img.shields.io/badge/Strategies-5-purple.svg" alt="5 Strategies">
  <img src="https://img.shields.io/badge/Tests-94%20Passed-brightgreen.svg" alt="94 Tests">
</p>

<p align="center">
  <a href="README_zh_CN.md">简体中文</a> | <a href="README_zh_TW.md">繁體中文</a> | <b>English</b>
</p>

---

# 📈 QuantPilot - Lightweight Terminal AI Quantitative Strategy Backtesting Engine

> Zero Dependencies · Pure Python Standard Library · 19 Technical Indicators · 5 Built-in Strategies · TUI Dashboard · Multi-format Reports

## 🎉 Introduction

**QuantPilot** is a lightweight terminal-based quantitative strategy backtesting engine, designed for quant trading enthusiasts and developers. Built entirely with Python's standard library, it has **zero external dependencies** and works out of the box.

### 💡 Inspiration

Inspired by trending AI trading projects on GitHub, we set out to build a **lighter, more focused, and more user-friendly** quantitative backtesting tool. Unlike heavyweight trading systems, QuantPilot focuses on the core scenario of **strategy backtesting**, enabling users to quickly validate the effectiveness of their trading strategies.

### 🌟 Differentiation Highlights

- **True Zero Dependencies**: No pandas, numpy, or any third-party libraries — pure Python standard library
- **Comprehensive Indicator Engine**: 19 technical indicators, each with complete mathematical formula documentation
- **Professional Risk Analysis**: 20+ risk metrics including Sharpe Ratio, Sortino Ratio, Calmar Ratio, and more
- **Beautiful HTML Reports**: Professional analysis reports with dark theme, gradient backgrounds, and glassmorphism effects
- **Interactive TUI Dashboard**: View equity curves, drawdown charts, and monthly return bar charts directly in the terminal

---

## ✨ Core Features

### 📊 Technical Indicator Engine (19 Indicators)
| Category | Indicators |
|----------|-----------|
| **Trend** | SMA (Simple Moving Average), EMA (Exponential Moving Average), VWAP (Volume Weighted Average Price), TRIX (Triple Exponential Smoothed Moving Average), SAR (Parabolic SAR) |
| **Momentum** | RSI (Relative Strength Index), MACD (Moving Average Convergence Divergence), ROC (Rate of Change), MFI (Money Flow Index), STOCH (Stochastic Oscillator), CCI (Commodity Channel Index), WR (Williams %R) |
| **Volatility** | BOLL (Bollinger Bands), ATR (Average True Range), KDJ (Stochastic Oscillator) |
| **Volume** | OBV (On-Balance Volume), WAD (Williams Accumulation/Distribution), DMI (Directional Movement Index) |

### 🎯 Built-in Backtesting Strategies (5)
- **Dual Moving Average Crossover**: Buy when fast MA crosses above slow MA, sell on cross below
- **RSI Overbought/Oversold**: Buy when RSI drops below threshold, sell above threshold
- **MACD Golden Cross / Death Cross**: Buy on DIF crossing above DEA, sell on cross below
- **Bollinger Bands Breakout**: Trade when price breaks above/below Bollinger Bands
- **Multi-Indicator Combo**: Combined signals from MA + RSI + MACD

### 📈 Backtesting Engine
- ✅ Commission simulation (configurable rate)
- ✅ Slippage simulation
- ✅ Stop-loss & take-profit
- ✅ Position sizing
- ✅ Multi-strategy combination support

### 📋 Risk Analysis (20+ Metrics)
- Total Return / Annualized Return / Maximum Drawdown / Drawdown Duration
- Annualized Volatility / Sharpe Ratio / Sortino Ratio / Calmar Ratio
- Trade Count / Win Rate / Profit/Loss Ratio / Max Consecutive Wins/Losses
- Monthly Return Statistics / Average Holding Period / Total Commission

### 📑 Multi-format Report Output
- 🖥️ **Terminal Table Report**: Quick preview of core metrics
- 📄 **JSON Report**: Programmatic processing and data exchange
- 🌐 **HTML Report**: Professional dark theme with embedded CSS styles
- 📝 **Markdown Report**: Documentation integration and sharing

---

## 🚀 Quick Start

### 📋 Requirements

- **Python** 3.8 or higher
- No third-party dependencies required

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/QuantPilot.git
cd QuantPilot

# Install (optional)
pip install -e .
```

### 🎮 Quick Run

```bash
# Check version
python -m quantpilot --version

# View help
python -m quantpilot --help

# List all available strategies
python -m quantpilot list-strategies

# List all available indicators
python -m quantpilot list-indicators

# Quick backtest with simulated data
python -m quantpilot quick-backtest --strategy dual_ma_cross --days 250

# Backtest with CSV data
python -m quantpilot backtest -f your_data.csv -s dual_ma_cross --capital 100000

# Generate HTML report
python -m quantpilot backtest -f your_data.csv -s macd_golden_cross --format html --output report

# Generate JSON report
python -m quantpilot backtest -f your_data.csv -s rsi_oversold_overbought --format json --output result

# Launch TUI dashboard
python -m quantpilot backtest -f your_data.csv -s bollinger_breakout --tui
```

---

## 📖 Detailed Usage Guide

### 📁 CSV Data Format

QuantPilot supports standard OHLCV format CSV files:

```csv
date,open,high,low,close,volume
2024-01-02,100.0,102.5,99.8,101.3,1000000
2024-01-03,101.3,103.2,100.5,102.8,1200000
2024-01-04,102.8,104.1,101.9,103.5,1100000
```

You can also auto-generate simulated data for quick testing:

```bash
python -m quantpilot quick-backtest --strategy dual_ma_cross --days 500
```

### ⚙️ Backtest Parameters

```bash
python -m quantpilot backtest -f data.csv \
  -s dual_ma_cross \              # Strategy name
  --capital 100000 \               # Initial capital (default: 100000)
  --commission 0.001 \             # Commission rate (default: 0.001)
  --slippage 0.001 \               # Slippage (default: 0.001)
  --stop-loss 0.05 \               # Stop-loss ratio (default: None)
  --take-profit 0.15 \             # Take-profit ratio (default: None)
  --position-size 0.95 \           # Position size (default: 1.0)
  --format html \                  # Report format: terminal/json/html/markdown
  --output my_report \             # Output filename (without extension)
  --tui                            # Enable TUI dashboard
```

### 🎯 Custom Strategy

Extend the `StrategyBase` class to create custom strategies:

```python
from quantpilot.strategy import StrategyBase, register_strategy
from quantpilot.indicators import TechnicalIndicators

class MyCustomStrategy(StrategyBase):
    """My custom trading strategy"""
    
    @property
    def name(self):
        return "my_custom"
    
    @property
    def description(self):
        return "My custom trading strategy"
    
    @property
    def default_params(self):
        return {"period": 14}
    
    def generate_signals(self, klines, params=None):
        p = params or self.default_params
        closes = [k.close for k in klines]
        rsi = TechnicalIndicators.rsi(closes, p["period"])
        
        signals = []
        for i in range(len(klines)):
            if i < p["period"]:
                signals.append("HOLD")
            elif rsi[i] < 30:
                signals.append("BUY")
            elif rsi[i] > 70:
                signals.append("SELL")
            else:
                signals.append("HOLD")
        return signals

# Register the strategy
register_strategy(MyCustomStrategy)
```

### 📊 Using Technical Indicators

```python
from quantpilot.indicators import TechnicalIndicators

closes = [100.0, 101.5, 102.3, 101.8, 103.2, ...]

# Calculate various indicators
ma = TechnicalIndicators.sma(closes, period=20)
ema = TechnicalIndicators.ema(closes, period=12)
macd, signal, hist = TechnicalIndicators.macd(closes)
rsi = TechnicalIndicators.rsi(closes, period=14)
boll_upper, boll_middle, boll_lower = TechnicalIndicators.boll(closes, period=20)
```

---

## 💡 Design Philosophy & Roadmap

### 🏗️ Design Principles

1. **Zero Dependency Philosophy**: No third-party libraries, ensuring it runs in any Python environment
2. **Pure Standard Library**: All math via `math` module, data processing via built-in data structures
3. **Modular Architecture**: Indicator engine, backtesting engine, strategy framework, analyzer, and report generator are fully decoupled
4. **Extensibility**: Strategy base class + registration mechanism for easy custom strategy creation

### 🛠️ Technology Choices

| Choice | Reason |
|--------|--------|
| Pure Python Standard Library | Zero installation cost, maximum compatibility |
| argparse | Standard library CLI parsing, no extra dependencies |
| csv/json | Standard library data formats, universal support |
| unittest | Standard library testing framework, ready to use |

### 🗺️ Roadmap

- [ ] **v1.1**: More technical indicators (Ichimoku, Fibonacci, etc.)
- [ ] **v1.2**: Real-time market data integration (Yahoo Finance, etc.)
- [ ] **v1.3**: Strategy optimizer (grid search, genetic algorithm optimization)
- [ ] **v1.4**: Multi-asset portfolio backtesting & capital allocation
- [ ] **v2.0**: Web visualization dashboard (built-in HTTP server)

---

## 📦 Packaging & Deployment

### 🔧 Install from Source

```bash
git clone https://github.com/gitstq/QuantPilot.git
cd QuantPilot
pip install -e .
```

After installation, use the `quantpilot` command directly:

```bash
quantpilot --version
quantpilot list-strategies
quantpilot backtest -f data.csv -s dual_ma_cross
```

### 🐍 Compatible Environments

| Environment | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10+ |
| OS | Windows/macOS/Linux | Any |
| Terminal | ANSI color support | iTerm2/Windows Terminal |

### 🧪 Running Tests

```bash
cd QuantPilot
python -m unittest discover tests/ -v
```

---

## 🤝 Contributing

We welcome contributions of all forms! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Contribution Workflow

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write code and tests
4. Ensure tests pass: `python -m unittest discover tests/ -v`
5. Commit your code: `git commit -m "feat: your feature description"`
6. Create a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
