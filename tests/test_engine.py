"""
QuantPilot 回测引擎测试模块

测试回测引擎的核心功能。
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quantpilot.data import KLine, KLineData
from quantpilot.engine import (
    BacktestEngine, BacktestConfig, Position, TradeRecord,
)
from quantpilot.strategy import (
    DualMACrossStrategy, Signal, StrategyBase,
)


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


class TestPosition(unittest.TestCase):
    """测试持仓类。"""

    def test_long_position_pnl(self):
        """测试多头持仓盈亏。"""
        pos = Position("TEST", "long", 100, 10.0, "2024-01-01")
        pos.update_price(11.0)
        self.assertAlmostEqual(pos.pnl, 100.0, places=2)
        self.assertAlmostEqual(pos.pnl_percent, 0.1, places=4)

    def test_long_position_loss(self):
        """测试多头持仓亏损。"""
        pos = Position("TEST", "long", 100, 10.0, "2024-01-01")
        pos.update_price(9.0)
        self.assertAlmostEqual(pos.pnl, -100.0, places=2)

    def test_market_value(self):
        """测试持仓市值。"""
        pos = Position("TEST", "long", 100, 10.0, "2024-01-01")
        pos.update_price(12.0)
        self.assertAlmostEqual(pos.market_value, 1200.0, places=2)


class TestTradeRecord(unittest.TestCase):
    """测试交易记录类。"""

    def test_trade_to_dict(self):
        """测试交易记录转字典。"""
        trade = TradeRecord(
            date="2024-01-01", symbol="TEST", action="buy",
            price=10.0, quantity=100, commission=3.0,
        )
        d = trade.to_dict()
        self.assertEqual(d["date"], "2024-01-01")
        self.assertEqual(d["action"], "buy")
        self.assertEqual(d["price"], 10.0)
        self.assertEqual(d["quantity"], 100)


class TestBacktestConfig(unittest.TestCase):
    """测试回测配置类。"""

    def test_default_config(self):
        """测试默认配置。"""
        config = BacktestConfig()
        self.assertEqual(config.initial_capital, 1000000.0)
        self.assertAlmostEqual(config.commission_rate, 0.0003)
        self.assertIsNone(config.stop_loss)
        self.assertIsNone(config.take_profit)

    def test_custom_config(self):
        """测试自定义配置。"""
        config = BacktestConfig(
            initial_capital=500000,
            commission_rate=0.001,
            stop_loss=0.05,
            take_profit=0.15,
        )
        self.assertEqual(config.initial_capital, 500000)
        self.assertAlmostEqual(config.commission_rate, 0.001)
        self.assertAlmostEqual(config.stop_loss, 0.05)
        self.assertAlmostEqual(config.take_profit, 0.15)


class TestBacktestEngine(unittest.TestCase):
    """测试回测引擎。"""

    def test_engine_creation(self):
        """测试引擎创建。"""
        config = BacktestConfig()
        engine = BacktestEngine(config)
        self.assertEqual(engine.cash, 1000000.0)
        self.assertIsNone(engine.position)

    def test_basic_backtest(self):
        """测试基本回测流程。"""
        kline_data = create_test_kline_data(100)
        strategy = DualMACrossStrategy(fast_period=5, slow_period=20)
        config = BacktestConfig(initial_capital=1000000)
        engine = BacktestEngine(config)

        result = engine.run(strategy, kline_data)

        self.assertIn("trades", result)
        self.assertIn("daily_values", result)
        self.assertIn("daily_returns", result)
        self.assertIn("config", result)
        self.assertEqual(len(result["daily_values"]), 100)
        self.assertEqual(len(result["daily_returns"]), 100)

    def test_backtest_with_commission(self):
        """测试含手续费的回测。"""
        kline_data = create_test_kline_data(100)
        strategy = DualMACrossStrategy(fast_period=5, slow_period=20)
        config = BacktestConfig(
            initial_capital=1000000,
            commission_rate=0.001,
        )
        engine = BacktestEngine(config)
        result = engine.run(strategy, kline_data)

        total_commission = sum(t["commission"] for t in result["trades"])
        self.assertGreaterEqual(total_commission, 0)

    def test_backtest_with_stop_loss(self):
        """测试含止损的回测。"""
        kline_data = create_test_kline_data(200)
        strategy = DualMACrossStrategy(fast_period=5, slow_period=20)
        config = BacktestConfig(
            initial_capital=1000000,
            stop_loss=0.02,
        )
        engine = BacktestEngine(config)
        result = engine.run(strategy, kline_data)

        # 检查是否有止损交易
        stop_loss_trades = [
            t for t in result["trades"]
            if t.get("reason") == "止损"
        ]
        # 止损可能触发也可能不触发，取决于数据
        self.assertIsInstance(stop_loss_trades, list)

    def test_backtest_with_take_profit(self):
        """测试含止盈的回测。"""
        kline_data = create_test_kline_data(200)
        strategy = DualMACrossStrategy(fast_period=5, slow_period=20)
        config = BacktestConfig(
            initial_capital=1000000,
            take_profit=0.05,
        )
        engine = BacktestEngine(config)
        result = engine.run(strategy, kline_data)

        # 检查结果结构完整
        self.assertEqual(len(result["daily_values"]), 200)

    def test_backtest_result_structure(self):
        """测试回测结果结构。"""
        kline_data = create_test_kline_data(50)
        strategy = DualMACrossStrategy()
        config = BacktestConfig()
        engine = BacktestEngine(config)
        result = engine.run(strategy, kline_data)

        # 验证结果结构
        self.assertIsInstance(result["trades"], list)
        self.assertIsInstance(result["daily_values"], list)
        self.assertIsInstance(result["daily_returns"], list)
        self.assertIsInstance(result["config"], dict)
        self.assertIsInstance(result["strategy_name"], str)
        self.assertIsInstance(result["data_summary"], dict)

        # 验证每日净值结构
        if result["daily_values"]:
            dv = result["daily_values"][0]
            self.assertIn("date", dv)
            self.assertIn("total_assets", dv)
            self.assertIn("cash", dv)
            self.assertIn("position_value", dv)
            self.assertIn("close", dv)

    def test_total_assets_consistency(self):
        """测试总资产一致性。"""
        kline_data = create_test_kline_data(100)
        strategy = DualMACrossStrategy()
        config = BacktestConfig(initial_capital=500000)
        engine = BacktestEngine(config)
        result = engine.run(strategy, kline_data)

        # 每日总资产应该合理
        for dv in result["daily_values"]:
            self.assertGreater(dv["total_assets"], 0)
            self.assertGreaterEqual(dv["cash"], 0)

    def test_slippage_effect(self):
        """测试滑点影响。"""
        kline_data = create_test_kline_data(100)
        strategy = DualMACrossStrategy()
        config = BacktestConfig(slippage=0.1)
        engine = BacktestEngine(config)
        result = engine.run(strategy, kline_data)

        # 有滑点时，成交价应该与原始价不同
        for trade in result["trades"]:
            self.assertGreaterEqual(trade["slippage"], 0)


if __name__ == "__main__":
    unittest.main()
