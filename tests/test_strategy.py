"""
QuantPilot 策略测试模块

测试策略框架和内置策略。
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quantpilot.data import KLine, KLineData
from quantpilot.strategy import (
    StrategyBase, Signal,
    DualMACrossStrategy, RSIOversoldOverboughtStrategy,
    MACDGoldenCrossStrategy, BollingerBreakoutStrategy,
    MultiIndicatorStrategy,
    create_strategy, list_strategies, STRATEGY_REGISTRY,
)


def create_test_data(n=100):
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


class TestStrategyBase(unittest.TestCase):
    """测试策略基类。"""

    def test_base_strategy(self):
        """测试基类策略默认返回HOLD。"""
        strategy = StrategyBase(name="TestBase")
        kline_data = create_test_data(50)
        strategy.on_init(kline_data)
        signal = strategy.on_bar(10, kline_data)
        self.assertEqual(signal, Signal.HOLD)

    def test_strategy_params(self):
        """测试策略参数。"""
        strategy = StrategyBase(params={"period": 20})
        self.assertEqual(strategy.get_param("period"), 20)
        self.assertIsNone(strategy.get_param("nonexistent"))
        strategy.set_param("period", 30)
        self.assertEqual(strategy.get_param("period"), 30)

    def test_strategy_description(self):
        """测试策略描述。"""
        strategy = StrategyBase()
        desc = strategy.description()
        self.assertIsInstance(desc, str)


class TestDualMACross(unittest.TestCase):
    """测试双均线交叉策略。"""

    def test_strategy_creation(self):
        """测试策略创建。"""
        strategy = DualMACrossStrategy(fast_period=5, slow_period=20)
        self.assertEqual(strategy.name, "DualMACross")
        self.assertEqual(strategy.get_param("fast_period"), 5)

    def test_strategy_init(self):
        """测试策略初始化。"""
        strategy = DualMACrossStrategy(fast_period=5, slow_period=20)
        kline_data = create_test_data(100)
        strategy.on_init(kline_data)
        # 初始化后应该有预计算的均线
        self.assertIsNotNone(strategy._fast_ma)
        self.assertIsNotNone(strategy._slow_ma)

    def test_strategy_signals(self):
        """测试策略信号生成。"""
        strategy = DualMACrossStrategy(fast_period=5, slow_period=20)
        kline_data = create_test_data(100)
        strategy.on_init(kline_data)

        signals = []
        for i in range(len(kline_data)):
            signal = strategy.on_bar(i, kline_data)
            signals.append(signal)

        # 应该有BUY、SELL和HOLD信号
        self.assertIn(Signal.BUY, signals)
        self.assertIn(Signal.SELL, signals)
        self.assertIn(Signal.HOLD, signals)

    def test_strategy_description(self):
        """测试策略描述。"""
        strategy = DualMACrossStrategy(fast_period=5, slow_period=20)
        desc = strategy.description()
        self.assertIn("双均线", desc)
        self.assertIn("5", desc)
        self.assertIn("20", desc)


class TestRSIStrategy(unittest.TestCase):
    """测试RSI超买超卖策略。"""

    def test_strategy_creation(self):
        """测试策略创建。"""
        strategy = RSIOversoldOverboughtStrategy(period=14, oversold=30, overbought=70)
        self.assertEqual(strategy.name, "RSIOversoldOverbought")

    def test_strategy_signals(self):
        """测试策略信号生成。"""
        strategy = RSIOversoldOverboughtStrategy(period=14, oversold=30, overbought=70)
        kline_data = create_test_data(100)
        strategy.on_init(kline_data)

        signals = set()
        for i in range(len(kline_data)):
            signal = strategy.on_bar(i, kline_data)
            signals.add(signal)

        # 应该至少有HOLD信号
        self.assertIn(Signal.HOLD, signals)


class TestMACDStrategy(unittest.TestCase):
    """测试MACD金叉死叉策略。"""

    def test_strategy_creation(self):
        """测试策略创建。"""
        strategy = MACDGoldenCrossStrategy()
        self.assertEqual(strategy.name, "MACDGoldenCross")

    def test_strategy_signals(self):
        """测试策略信号生成。"""
        strategy = MACDGoldenCrossStrategy()
        kline_data = create_test_data(100)
        strategy.on_init(kline_data)

        signals = set()
        for i in range(len(kline_data)):
            signal = strategy.on_bar(i, kline_data)
            signals.add(signal)

        self.assertIn(Signal.HOLD, signals)


class TestBollingerStrategy(unittest.TestCase):
    """测试布林带突破策略。"""

    def test_strategy_creation(self):
        """测试策略创建。"""
        strategy = BollingerBreakoutStrategy(period=20, std_multiplier=2.0)
        self.assertEqual(strategy.name, "BollingerBreakout")

    def test_strategy_signals(self):
        """测试策略信号生成。"""
        strategy = BollingerBreakoutStrategy()
        kline_data = create_test_data(100)
        strategy.on_init(kline_data)

        signals = set()
        for i in range(len(kline_data)):
            signal = strategy.on_bar(i, kline_data)
            signals.add(signal)

        self.assertIn(Signal.HOLD, signals)


class TestMultiIndicatorStrategy(unittest.TestCase):
    """测试多指标组合策略。"""

    def test_strategy_creation(self):
        """测试策略创建。"""
        strategy = MultiIndicatorStrategy()
        self.assertEqual(strategy.name, "MultiIndicator")

    def test_strategy_signals(self):
        """测试策略信号生成。"""
        strategy = MultiIndicatorStrategy()
        kline_data = create_test_data(100)
        strategy.on_init(kline_data)

        signals = set()
        for i in range(len(kline_data)):
            signal = strategy.on_bar(i, kline_data)
            signals.add(signal)

        self.assertIn(Signal.HOLD, signals)


class TestCreateStrategy(unittest.TestCase):
    """测试策略工厂函数。"""

    def test_create_known_strategy(self):
        """测试创建已知策略。"""
        strategy = create_strategy("dual_ma_cross")
        self.assertIsInstance(strategy, DualMACrossStrategy)

    def test_create_with_params(self):
        """测试带参数创建策略。"""
        strategy = create_strategy("dual_ma_cross", fast_period=10, slow_period=30)
        self.assertEqual(strategy.get_param("fast_period"), 10)
        self.assertEqual(strategy.get_param("slow_period"), 30)

    def test_create_unknown_strategy(self):
        """测试创建未知策略。"""
        with self.assertRaises(ValueError):
            create_strategy("nonexistent_strategy")

    def test_list_strategies(self):
        """测试列出策略。"""
        strategies = list_strategies()
        self.assertEqual(len(strategies), 5)
        names = [s["name"] for s in strategies]
        self.assertIn("dual_ma_cross", names)
        self.assertIn("rsi_oversold_overbought", names)
        self.assertIn("macd_golden_cross", names)
        self.assertIn("bollinger_breakout", names)
        self.assertIn("multi_indicator", names)

    def test_registry_completeness(self):
        """测试策略注册表完整性。"""
        self.assertEqual(len(STRATEGY_REGISTRY), 5)
        for name, info in STRATEGY_REGISTRY.items():
            self.assertIn("class", info)
            self.assertIn("desc", info)
            self.assertIn("params", info)


if __name__ == "__main__":
    unittest.main()
