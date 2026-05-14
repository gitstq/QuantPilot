"""
QuantPilot 收益分析器测试模块

测试收益分析器的各项指标计算。
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quantpilot.data import KLine, KLineData
from quantpilot.engine import BacktestEngine, BacktestConfig
from quantpilot.strategy import DualMACrossStrategy
from quantpilot.analyzer import PerformanceAnalyzer
from quantpilot.utils import round_to


def create_test_kline_data(n=100):
    """创建测试用K线数据。"""
    kline_data = KLineData()
    import random
    random.seed(42)
    price = 100.0
    for i in range(n):
        change = random.gauss(0.01, 0.03)
        price *= (1 + change)
        open_p = price * (1 + random.gauss(0, 0.005))
        high = max(open_p, price) * (1 + abs(random.gauss(0, 0.01)))
        low = min(open_p, price) * (1 - abs(random.gauss(0, 0.01)))
        volume = random.randint(100000, 1000000)
        kline = KLine(
            date="2024-{:02d}-{:02d}".format((i // 30) + 1, (i % 30) + 1),
            open_price=round(open_p, 2),
            high=round(high, 2),
            low=round(low, 2),
            close=round(price, 2),
            volume=volume,
        )
        kline_data.append(kline)
    return kline_data


def run_test_backtest(n=200):
    """运行测试回测。"""
    kline_data = create_test_kline_data(n)
    strategy = DualMACrossStrategy(fast_period=5, slow_period=20)
    config = BacktestConfig(initial_capital=1000000)
    engine = BacktestEngine(config)
    return engine.run(strategy, kline_data)


class TestPerformanceAnalyzer(unittest.TestCase):
    """测试收益分析器。"""

    def setUp(self):
        """测试前准备。"""
        self.result = run_test_backtest(200)
        self.analyzer = PerformanceAnalyzer(self.result)

    def test_total_return(self):
        """测试总收益率。"""
        ret = self.analyzer.total_return()
        self.assertIsInstance(ret, float)

    def test_annual_return(self):
        """测试年化收益率。"""
        ret = self.analyzer.annual_return()
        self.assertIsInstance(ret, float)

    def test_max_drawdown(self):
        """测试最大回撤。"""
        mdd = self.analyzer.max_drawdown()
        self.assertGreaterEqual(mdd, 0)
        self.assertLessEqual(mdd, 1)

    def test_max_drawdown_duration(self):
        """测试最大回撤持续天数。"""
        duration = self.analyzer.max_drawdown_duration()
        self.assertGreaterEqual(duration, 0)
        self.assertIsInstance(duration, int)

    def test_volatility(self):
        """测试年化波动率。"""
        vol = self.analyzer.volatility()
        self.assertGreaterEqual(vol, 0)
        self.assertIsInstance(vol, float)

    def test_sharpe_ratio(self):
        """测试夏普比率。"""
        sharpe = self.analyzer.sharpe_ratio()
        self.assertIsInstance(sharpe, float)

    def test_sortino_ratio(self):
        """测试Sortino比率。"""
        sortino = self.analyzer.sortino_ratio()
        self.assertIsInstance(sortino, float)

    def test_calmar_ratio(self):
        """测试Calmar比率。"""
        calmar = self.analyzer.calmar_ratio()
        self.assertIsInstance(calmar, float)

    def test_total_trades(self):
        """测试交易次数。"""
        trades = self.analyzer.total_trades()
        self.assertGreaterEqual(trades, 0)
        self.assertIsInstance(trades, int)

    def test_win_rate(self):
        """测试胜率。"""
        wr = self.analyzer.win_rate()
        self.assertGreaterEqual(wr, 0)
        self.assertLessEqual(wr, 1)

    def test_profit_loss_ratio(self):
        """测试盈亏比。"""
        plr = self.analyzer.profit_loss_ratio()
        self.assertIsInstance(plr, float)

    def test_max_consecutive_wins(self):
        """测试最大连续盈利。"""
        mcw = self.analyzer.max_consecutive_wins()
        self.assertGreaterEqual(mcw, 0)
        self.assertIsInstance(mcw, int)

    def test_max_consecutive_losses(self):
        """测试最大连续亏损。"""
        mcl = self.analyzer.max_consecutive_losses()
        self.assertGreaterEqual(mcl, 0)
        self.assertIsInstance(mcl, int)

    def test_avg_profit(self):
        """测试平均盈利。"""
        ap = self.analyzer.avg_profit()
        self.assertGreaterEqual(ap, 0)

    def test_avg_loss(self):
        """测试平均亏损。"""
        al = self.analyzer.avg_loss()
        self.assertGreaterEqual(al, 0)

    def test_total_commission(self):
        """测试总手续费。"""
        tc = self.analyzer.total_commission()
        self.assertGreaterEqual(tc, 0)

    def test_total_pnl(self):
        """测试总盈亏。"""
        pnl = self.analyzer.total_pnl()
        self.assertIsInstance(pnl, float)

    def test_final_capital(self):
        """测试最终资金。"""
        fc = self.analyzer.final_capital()
        self.assertGreater(fc, 0)

    def test_peak_capital(self):
        """测试峰值资金。"""
        pc = self.analyzer.peak_capital()
        self.assertGreater(pc, 0)

    def test_min_capital(self):
        """测试最低资金。"""
        mc = self.analyzer.min_capital()
        self.assertGreater(mc, 0)

    def test_trading_days(self):
        """测试交易天数。"""
        td = self.analyzer.trading_days()
        self.assertEqual(td, 200)

    def test_monthly_returns(self):
        """测试月度收益。"""
        mr = self.analyzer.monthly_returns()
        self.assertIsInstance(mr, dict)
        for month, ret in mr.items():
            self.assertIsInstance(ret, float)

    def test_monthly_win_rate(self):
        """测试月度胜率。"""
        mwr = self.analyzer.monthly_win_rate()
        self.assertGreaterEqual(mwr, 0)
        self.assertLessEqual(mwr, 1)

    def test_avg_holding_days(self):
        """测试平均持仓天数。"""
        ahd = self.analyzer.avg_holding_days()
        self.assertGreaterEqual(ahd, 0)

    def test_analyze_returns_dict(self):
        """测试analyze()返回字典。"""
        metrics = self.analyzer.analyze()
        self.assertIsInstance(metrics, dict)
        expected_keys = [
            "total_return", "annual_return", "max_drawdown",
            "sharpe_ratio", "sortino_ratio", "calmar_ratio",
            "volatility", "total_trades", "win_rate",
            "profit_loss_ratio", "final_capital",
        ]
        for key in expected_keys:
            self.assertIn(key, metrics)

    def test_summary_text(self):
        """测试摘要文本生成。"""
        text = self.analyzer.summary_text()
        self.assertIsInstance(text, str)
        self.assertIn("QuantPilot", text)
        self.assertIn("总收益率", text)


class TestAnalyzerEdgeCases(unittest.TestCase):
    """测试分析器边界情况。"""

    def test_empty_data(self):
        """测试空数据分析。"""
        # 创建一个没有交易的回测结果
        result = {
            "daily_values": [],
            "daily_returns": [],
            "trades": [],
            "config": {"initial_capital": 1000000},
        }
        analyzer = PerformanceAnalyzer(result)
        self.assertEqual(analyzer.total_return(), 0.0)
        self.assertEqual(analyzer.max_drawdown(), 0.0)
        self.assertEqual(analyzer.total_trades(), 0)
        self.assertEqual(analyzer.win_rate(), 0.0)

    def test_no_loss_trades(self):
        """测试全部盈利交易。"""
        result = {
            "daily_values": [
                {"date": "2024-01-01", "total_assets": 1000000, "cash": 1000000, "position_value": 0, "close": 100},
                {"date": "2024-01-02", "total_assets": 1010000, "cash": 1010000, "position_value": 0, "close": 101},
            ],
            "daily_returns": [0.0, 0.01],
            "trades": [
                {"action": "buy", "pnl": 0, "commission": 3},
                {"action": "sell", "pnl": 10000, "commission": 3},
            ],
            "config": {"initial_capital": 1000000},
        }
        analyzer = PerformanceAnalyzer(result)
        self.assertEqual(analyzer.win_rate(), 1.0)
        self.assertEqual(analyzer.total_trades(), 1)


if __name__ == "__main__":
    unittest.main()
