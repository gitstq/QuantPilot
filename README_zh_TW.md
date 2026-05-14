<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Indicators-19-orange.svg" alt="19 Indicators">
  <img src="https://img.shields.io/badge/Strategies-5-purple.svg" alt="5 Strategies">
  <img src="https://img.shields.io/badge/Tests-94%20Passed-brightgreen.svg" alt="94 Tests">
</p>

<p align="center">
  <a href="README_zh_CN.md">简体中文</a> | <b>繁體中文</b> | <a href="README.md">English</a>
</p>

---

# 📈 QuantPilot - 輕量級終端AI量化策略回測引擎

> 零依賴 · 純Python標準庫 · 19個技術指標 · 5個內建策略 · TUI儀表板 · 多格式報告

## 🎉 專案介紹

**QuantPilot** 是一款輕量級的終端量化策略回測引擎，專為量化交易愛好者和開發者打造。它完全基於 Python 標準庫建構，**零外部依賴**，開箱即用。

### 💡 靈感來源

受 GitHub Trending 上熱門 AI 交易專案啟發，我們希望打造一個**更輕量、更專注、更易用**的量化回測工具。不同於重量級的交易系統，QuantPilot 專注於**策略回測**這一核心場景，讓使用者能夠快速驗證交易策略的有效性。

### 🌟 自研差異化亮點

- **真正的零依賴**：不依賴 pandas、numpy 等第三方庫，純 Python 標準庫實現
- **完整的指標引擎**：19 個技術指標，每個都有完整的數學公式註釋
- **專業風控分析**：20+ 項風控指標，包括夏普比率、Sortino 比率、Calmar 比率等
- **精美的 HTML 報告**：深色主題、漸層背景、毛玻璃效果的專業分析報告
- **TUI 互動式儀表板**：終端內直接查看淨值曲線、回撤圖、月度收益柱狀圖

---

## ✨ 核心特性

### 📊 技術指標引擎（19個）
| 類別 | 指標 |
|------|------|
| **趨勢類** | SMA（簡單移動平均）、EMA（指數移動平均）、VWAP（成交量加權平均價）、TRIX（三重指數平滑移動平均）、SAR（拋物線止損轉向） |
| **動量類** | RSI（相對強弱指數）、MACD（指數平滑異同移動平均線）、ROC（變動速率）、MFI（資金流量指標）、STOCH（隨機指標）、CCI（商品通道指數）、WR（威廉指標） |
| **波動類** | BOLL（布林帶）、ATR（真實波幅）、KDJ（隨機指標） |
| **量能類** | OBV（能量潮）、WAD（威廉累積/派發）、DMI（趨向指標） |

### 🎯 內建回測策略（5個）
- **雙均線交叉策略**：快線上穿慢線買入，下穿賣出
- **RSI 超買超賣策略**：RSI 低於閾值買入，高於閾值賣出
- **MACD 金叉死叉策略**：DIF 上穿 DEA 買入，下穿賣出
- **布林帶突破策略**：價格突破布林帶上/下軌時交易
- **多指標組合策略**：綜合均線 + RSI + MACD 多維度信號

### 📈 回測引擎
- ✅ 手續費模擬（可配置費率）
- ✅ 滑點模擬
- ✅ 止損止盈
- ✅ 倉位管理
- ✅ 多策略組合支援

### 📋 風控分析（20+項指標）
- 總收益率 / 年化收益率 / 最大回撤 / 回撤持續天數
- 年化波動率 / 夏普比率 / Sortino 比率 / Calmar 比率
- 交易次數 / 勝率 / 盈虧比 / 最大連續盈虧
- 月度收益統計 / 平均持倉天數 / 總手續費

### 📑 多格式報告輸出
- 🖥️ **終端表格報告**：快速預覽核心指標
- 📄 **JSON 報告**：程式化處理和資料交換
- 🌐 **HTML 報告**：專業深色主題，內嵌 CSS 樣式
- 📝 **Markdown 報告**：文件整合和分享

---

## 🚀 快速開始

### 📋 環境要求

- **Python** 3.8 或更高版本
- 無需安裝任何第三方依賴

### 📦 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/QuantPilot.git
cd QuantPilot

# 安裝（可選）
pip install -e .
```

### 🎮 快速運行

```bash
# 查看版本
python -m quantpilot --version

# 查看幫助
python -m quantpilot --help

# 列出所有可用策略
python -m quantpilot list-strategies

# 列出所有可用指標
python -m quantpilot list-indicators

# 使用模擬資料快速回測
python -m quantpilot quick-backtest --strategy dual_ma_cross --days 250

# 使用 CSV 資料回測
python -m quantpilot backtest -f your_data.csv -s dual_ma_cross --capital 100000

# 生成 HTML 報告
python -m quantpilot backtest -f your_data.csv -s macd_golden_cross --format html --output report

# 生成 JSON 報告
python -m quantpilot backtest -f your_data.csv -s rsi_oversold_overbought --format json --output result

# 啟動 TUI 儀表板
python -m quantpilot backtest -f your_data.csv -s bollinger_breakout --tui
```

---

## 📖 詳細使用指南

### 📁 CSV 資料格式

QuantPilot 支援標準 OHLCV 格式的 CSV 檔案：

```csv
date,open,high,low,close,volume
2024-01-02,100.0,102.5,99.8,101.3,1000000
2024-01-03,101.3,103.2,100.5,102.8,1200000
2024-01-04,102.8,104.1,101.9,103.5,1100000
```

也支援自動生成模擬資料進行快速測試：

```bash
python -m quantpilot quick-backtest --strategy dual_ma_cross --days 500
```

### ⚙️ 回測參數詳解

```bash
python -m quantpilot backtest -f data.csv \
  -s dual_ma_cross \              # 策略名稱
  --capital 100000 \               # 初始資金（預設100000）
  --commission 0.001 \             # 手續費率（預設0.001，即萬分之一）
  --slippage 0.001 \               # 滑點（預設0.001）
  --stop-loss 0.05 \               # 止損比例（預設None）
  --take-profit 0.15 \             # 止盈比例（預設None）
  --position-size 0.95 \           # 倉位比例（預設1.0，即全倉）
  --format html \                  # 報告格式：terminal/json/html/markdown
  --output my_report \             # 輸出檔案名（不含副檔名）
  --tui                            # 啟用TUI儀表板
```

### 🎯 自訂策略

繼承 `StrategyBase` 基類即可建立自訂策略：

```python
from quantpilot.strategy import StrategyBase, register_strategy
from quantpilot.indicators import TechnicalIndicators

class MyCustomStrategy(StrategyBase):
    """我的自訂策略"""
    
    @property
    def name(self):
        return "my_custom"
    
    @property
    def description(self):
        return "我的自訂交易策略"
    
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

# 註冊策略
register_strategy(MyCustomStrategy)
```

### 📊 技術指標使用

```python
from quantpilot.indicators import TechnicalIndicators

closes = [100.0, 101.5, 102.3, 101.8, 103.2, ...]

# 計算各類指標
ma = TechnicalIndicators.sma(closes, period=20)
ema = TechnicalIndicators.ema(closes, period=12)
macd, signal, hist = TechnicalIndicators.macd(closes)
rsi = TechnicalIndicators.rsi(closes, period=14)
boll_upper, boll_middle, boll_lower = TechnicalIndicators.boll(closes, period=20)
```

---

## 💡 設計思路與迭代規劃

### 🏗️ 設計理念

1. **零依賴哲學**：不引入任何第三方庫，確保在任何 Python 環境中都能直接運行
2. **純標準庫實現**：所有數學計算使用 `math` 模組，資料處理使用內建資料結構
3. **模組化架構**：指標引擎、回測引擎、策略框架、分析器、報告生成器完全解耦
4. **可擴展性**：策略基類 + 註冊機制，使用者可以輕鬆新增自訂策略

### 🛠️ 技術選型原因

| 選擇 | 原因 |
|------|------|
| 純 Python 標準庫 | 零安裝成本，最大相容性 |
| argparse | 標準庫 CLI 解析，無額外依賴 |
| csv/json | 標準庫資料格式，通用性強 |
| unittest | 標準庫測試框架，開箱即用 |

### 🗺️ 後續迭代計畫

- [ ] **v1.1**：增加更多技術指標（Ichimoku、Fibonacci 等）
- [ ] **v1.2**：支援即時行情資料接入（Yahoo Finance、東方財富等）
- [ ] **v1.3**：策略優化器（參數網格搜尋、遺傳演算法優化）
- [ ] **v1.4**：多標的組合回測與資金分配
- [ ] **v2.0**：Web 視覺化面板（內建 HTTP 伺服器）

---

## 📦 打包與部署指南

### 🔧 從原始碼安裝

```bash
git clone https://github.com/gitstq/QuantPilot.git
cd QuantPilot
pip install -e .
```

安裝後可直接使用 `quantpilot` 命令：

```bash
quantpilot --version
quantpilot list-strategies
quantpilot backtest -f data.csv -s dual_ma_cross
```

### 🐍 相容環境

| 環境 | 最低版本 | 推薦版本 |
|------|---------|---------|
| Python | 3.8+ | 3.10+ |
| 作業系統 | Windows/macOS/Linux | 任意 |
| 終端 | 支援 ANSI 顏色 | iTerm2/Windows Terminal |

### 🧪 執行測試

```bash
cd QuantPilot
python -m unittest discover tests/ -v
```

---

## 🤝 貢獻指南

我們歡迎任何形式的貢獻！請閱讀 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳情。

### 快速貢獻流程

1. Fork 本倉庫
2. 建立功能分支：`git checkout -b feature/your-feature`
3. 編寫程式碼和測試
4. 確保測試通過：`python -m unittest discover tests/ -v`
5. 提交程式碼：`git commit -m "feat: 你的功能描述"`
6. 建立 Pull Request

---

## 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
