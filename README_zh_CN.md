<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Indicators-19-orange.svg" alt="19 Indicators">
  <img src="https://img.shields.io/badge/Strategies-5-purple.svg" alt="5 Strategies">
  <img src="https://img.shields.io/badge/Tests-94%20Passed-brightgreen.svg" alt="94 Tests">
</p>

<p align="center">
  <b>简体中文</b> | <a href="README_zh_TW.md">繁體中文</a> | <a href="README.md">English</a>
</p>

---

# 📈 QuantPilot - 轻量级终端AI量化策略回测引擎

> 零依赖 · 纯Python标准库 · 19个技术指标 · 5个内置策略 · TUI仪表板 · 多格式报告

## 🎉 项目介绍

**QuantPilot** 是一款轻量级的终端量化策略回测引擎，专为量化交易爱好者和开发者打造。它完全基于 Python 标准库构建，**零外部依赖**，开箱即用。

### 💡 灵感来源

受 GitHub Trending 上热门 AI 交易项目启发，我们希望打造一个**更轻量、更专注、更易用**的量化回测工具。不同于重量级的交易系统，QuantPilot 专注于**策略回测**这一核心场景，让用户能够快速验证交易策略的有效性。

### 🌟 自研差异化亮点

- **真正的零依赖**：不依赖 pandas、numpy 等第三方库，纯 Python 标准库实现
- **完整的指标引擎**：19 个技术指标，每个都有完整的数学公式注释
- **专业风控分析**：20+ 项风控指标，包括夏普比率、Sortino 比率、Calmar 比率等
- **精美的 HTML 报告**：深色主题、渐变背景、毛玻璃效果的专业分析报告
- **TUI 交互式仪表板**：终端内直接查看净值曲线、回撤图、月度收益柱状图

---

## ✨ 核心特性

### 📊 技术指标引擎（19个）
| 类别 | 指标 |
|------|------|
| **趋势类** | SMA（简单移动平均）、EMA（指数移动平均）、VWAP（成交量加权平均价）、TRIX（三重指数平滑移动平均）、SAR（抛物线止损转向） |
| **动量类** | RSI（相对强弱指数）、MACD（指数平滑异同移动平均线）、ROC（变动速率）、MFI（资金流量指标）、STOCH（随机指标）、CCI（商品通道指数）、WR（威廉指标） |
| **波动类** | BOLL（布林带）、ATR（真实波幅）、KDJ（随机指标） |
| **量能类** | OBV（能量潮）、WAD（威廉累积/派发）、DMI（趋向指标） |

### 🎯 内置回测策略（5个）
- **双均线交叉策略**：快线上穿慢线买入，下穿卖出
- **RSI 超买超卖策略**：RSI 低于阈值买入，高于阈值卖出
- **MACD 金叉死叉策略**：DIF 上穿 DEA 买入，下穿卖出
- **布林带突破策略**：价格突破布林带上/下轨时交易
- **多指标组合策略**：综合均线 + RSI + MACD 多维度信号

### 📈 回测引擎
- ✅ 手续费模拟（可配置费率）
- ✅ 滑点模拟
- ✅ 止损止盈
- ✅ 仓位管理
- ✅ 多策略组合支持

### 📋 风控分析（20+项指标）
- 总收益率 / 年化收益率 / 最大回撤 / 回撤持续天数
- 年化波动率 / 夏普比率 / Sortino 比率 / Calmar 比率
- 交易次数 / 胜率 / 盈亏比 / 最大连续盈利亏损
- 月度收益统计 / 平均持仓天数 / 总手续费

### 📑 多格式报告输出
- 🖥️ **终端表格报告**：快速预览核心指标
- 📄 **JSON 报告**：程序化处理和数据交换
- 🌐 **HTML 报告**：专业深色主题，内嵌 CSS 样式
- 📝 **Markdown 报告**：文档集成和分享

---

## 🚀 快速开始

### 📋 环境要求

- **Python** 3.8 或更高版本
- 无需安装任何第三方依赖

### 📦 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/QuantPilot.git
cd QuantPilot

# 安装（可选）
pip install -e .
```

### 🎮 快速运行

```bash
# 查看版本
python -m quantpilot --version

# 查看帮助
python -m quantpilot --help

# 列出所有可用策略
python -m quantpilot list-strategies

# 列出所有可用指标
python -m quantpilot list-indicators

# 使用模拟数据快速回测
python -m quantpilot quick-backtest --strategy dual_ma_cross --days 250

# 使用 CSV 数据回测
python -m quantpilot backtest -f your_data.csv -s dual_ma_cross --capital 100000

# 生成 HTML 报告
python -m quantpilot backtest -f your_data.csv -s macd_golden_cross --format html --output report

# 生成 JSON 报告
python -m quantpilot backtest -f your_data.csv -s rsi_oversold_overbought --format json --output result

# 启动 TUI 仪表板
python -m quantpilot backtest -f your_data.csv -s bollinger_breakout --tui
```

---

## 📖 详细使用指南

### 📁 CSV 数据格式

QuantPilot 支持标准 OHLCV 格式的 CSV 文件：

```csv
date,open,high,low,close,volume
2024-01-02,100.0,102.5,99.8,101.3,1000000
2024-01-03,101.3,103.2,100.5,102.8,1200000
2024-01-04,102.8,104.1,101.9,103.5,1100000
```

也支持自动生成模拟数据进行快速测试：

```bash
python -m quantpilot quick-backtest --strategy dual_ma_cross --days 500
```

### ⚙️ 回测参数详解

```bash
python -m quantpilot backtest -f data.csv \
  -s dual_ma_cross \              # 策略名称
  --capital 100000 \               # 初始资金（默认100000）
  --commission 0.001 \             # 手续费率（默认0.001，即万分之一）
  --slippage 0.001 \               # 滑点（默认0.001）
  --stop-loss 0.05 \               # 止损比例（默认None）
  --take-profit 0.15 \             # 止盈比例（默认None）
  --position-size 0.95 \           # 仓位比例（默认1.0，即全仓）
  --format html \                  # 报告格式：terminal/json/html/markdown
  --output my_report \             # 输出文件名（不含扩展名）
  --tui                            # 启用TUI仪表板
```

### 🎯 自定义策略

继承 `StrategyBase` 基类即可创建自定义策略：

```python
from quantpilot.strategy import StrategyBase, register_strategy
from quantpilot.indicators import TechnicalIndicators

class MyCustomStrategy(StrategyBase):
    """我的自定义策略"""
    
    @property
    def name(self):
        return "my_custom"
    
    @property
    def description(self):
        return "我的自定义交易策略"
    
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

# 注册策略
register_strategy(MyCustomStrategy)
```

### 📊 技术指标使用

```python
from quantpilot.indicators import TechnicalIndicators

closes = [100.0, 101.5, 102.3, 101.8, 103.2, ...]

# 计算各类指标
ma = TechnicalIndicators.sma(closes, period=20)
ema = TechnicalIndicators.ema(closes, period=12)
macd, signal, hist = TechnicalIndicators.macd(closes)
rsi = TechnicalIndicators.rsi(closes, period=14)
boll_upper, boll_middle, boll_lower = TechnicalIndicators.boll(closes, period=20)
```

---

## 💡 设计思路与迭代规划

### 🏗️ 设计理念

1. **零依赖哲学**：不引入任何第三方库，确保在任何 Python 环境中都能直接运行
2. **纯标准库实现**：所有数学计算使用 `math` 模块，数据处理使用内置数据结构
3. **模块化架构**：指标引擎、回测引擎、策略框架、分析器、报告生成器完全解耦
4. **可扩展性**：策略基类 + 注册机制，用户可以轻松添加自定义策略

### 🛠️ 技术选型原因

| 选择 | 原因 |
|------|------|
| 纯 Python 标准库 | 零安装成本，最大兼容性 |
| argparse | 标准库 CLI 解析，无额外依赖 |
| csv/json | 标准库数据格式，通用性强 |
| unittest | 标准库测试框架，开箱即用 |

### 🗺️ 后续迭代计划

- [ ] **v1.1**：增加更多技术指标（Ichimoku、Fibonacci 等）
- [ ] **v1.2**：支持实时行情数据接入（Yahoo Finance、东方财富等）
- [ ] **v1.3**：策略优化器（参数网格搜索、遗传算法优化）
- [ ] **v1.4**：多标的组合回测与资金分配
- [ ] **v2.0**：Web 可视化面板（内置 HTTP 服务器）

---

## 📦 打包与部署指南

### 🔧 从源码安装

```bash
git clone https://github.com/gitstq/QuantPilot.git
cd QuantPilot
pip install -e .
```

安装后可直接使用 `quantpilot` 命令：

```bash
quantpilot --version
quantpilot list-strategies
quantpilot backtest -f data.csv -s dual_ma_cross
```

### 🐍 兼容环境

| 环境 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Python | 3.8+ | 3.10+ |
| 操作系统 | Windows/macOS/Linux | 任意 |
| 终端 | 支持 ANSI 颜色 | iTerm2/Windows Terminal |

### 🧪 运行测试

```bash
cd QuantPilot
python -m unittest discover tests/ -v
```

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 快速贡献流程

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 编写代码和测试
4. 确保测试通过：`python -m unittest discover tests/ -v`
5. 提交代码：`git commit -m "feat: 你的功能描述"`
6. 创建 Pull Request

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
