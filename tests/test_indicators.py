"""
QuantPilot 技术指标计算测试模块

测试所有技术指标计算函数的正确性。
"""

import unittest
import math
import random
import os
import sys

# 确保可以导入项目模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quantpilot.indicators import (
    ma, ema, sma, macd, rsi, bollinger_bands, atr, kdj,
    obv, wr, cci, dmi, roc, mfi, stoch, vwap, trix, sar,
    williams_ad, compute_indicator, list_indicators,
    INDICATOR_REGISTRY,
)


class TestMA(unittest.TestCase):
    """测试简单移动平均线。"""

    def test_basic_ma(self):
        """测试基本MA计算。"""
        data = [1, 2, 3, 4, 5]
        result = ma(data, 3)
        # 前2个为None
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        # MA(3) = (1+2+3)/3 = 2.0
        self.assertAlmostEqual(result[2], 2.0, places=4)
        # MA(3) = (2+3+4)/3 = 3.0
        self.assertAlmostEqual(result[3], 3.0, places=4)
        # MA(3) = (3+4+5)/3 = 4.0
        self.assertAlmostEqual(result[4], 4.0, places=4)

    def test_ma_length(self):
        """测试MA输出长度与输入一致。"""
        data = list(range(100))
        result = ma(data, 20)
        self.assertEqual(len(result), 100)

    def test_ma_constant(self):
        """测试常数序列的MA。"""
        data = [10] * 30
        result = ma(data, 10)
        for i in range(9, 30):
            self.assertAlmostEqual(result[i], 10.0, places=4)

    def test_ma_empty(self):
        """测试空数据。"""
        with self.assertRaises(ValueError):
            ma([], 5)


class TestEMA(unittest.TestCase):
    """测试指数移动平均线。"""

    def test_basic_ema(self):
        """测试基本EMA计算。"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = ema(data, 3)
        self.assertEqual(len(result), 10)
        # 前2个为None
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        # 第一个EMA = SMA(3) = (1+2+3)/3 = 2.0
        self.assertAlmostEqual(result[2], 2.0, places=4)
        # 后续EMA应该递增
        self.assertIsNotNone(result[3])
        self.assertGreater(result[3], result[2])

    def test_ema_constant(self):
        """测试常数序列的EMA。"""
        data = [5.0] * 20
        result = ema(data, 5)
        for i in range(4, 20):
            self.assertAlmostEqual(result[i], 5.0, places=4)


class TestSMA(unittest.TestCase):
    """测试平滑移动平均线。"""

    def test_basic_sma(self):
        """测试基本SMMA计算。"""
        data = [1, 2, 3, 4, 5]
        result = sma(data, 3)
        self.assertEqual(len(result), 5)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        self.assertAlmostEqual(result[2], 2.0, places=4)


class TestMACD(unittest.TestCase):
    """测试MACD指标。"""

    def test_macd_structure(self):
        """测试MACD返回结构。"""
        data = list(range(50, 150))
        dif, dea, hist = macd(data)
        self.assertEqual(len(dif), 100)
        self.assertEqual(len(dea), 100)
        self.assertEqual(len(hist), 100)

    def test_macd_hist_relation(self):
        """测试MACD柱 = 2 * (DIF - DEA)。"""
        data = [100 + i * 0.5 + random.gauss(0, 1) for i in range(100)]
        random.seed(42)
        dif, dea, hist = macd(data)
        for i in range(len(hist)):
            if dif[i] is not None and dea[i] is not None and hist[i] is not None:
                self.assertAlmostEqual(hist[i], 2 * (dif[i] - dea[i]), places=3)


class TestRSI(unittest.TestCase):
    """测试RSI指标。"""

    def test_rsi_range(self):
        """测试RSI值在0-100之间。"""
        random.seed(42)
        data = [100 + random.gauss(0, 2) for _ in range(100)]
        result = rsi(data, 14)
        for val in result:
            if val is not None:
                self.assertGreaterEqual(val, 0)
                self.assertLessEqual(val, 100)

    def test_rsi_uptrend(self):
        """测试持续上涨时RSI应较高。"""
        data = [10 + i for i in range(50)]
        result = rsi(data, 14)
        # 最后一个RSI应该接近100
        last_valid = [v for v in result if v is not None]
        self.assertGreater(last_valid[-1], 70)

    def test_rsi_downtrend(self):
        """测试持续下跌时RSI应较低。"""
        data = [100 - i for i in range(50)]
        result = rsi(data, 14)
        last_valid = [v for v in result if v is not None]
        self.assertLess(last_valid[-1], 30)


class TestBollingerBands(unittest.TestCase):
    """测试布林带。"""

    def test_bollinger_structure(self):
        """测试布林带返回结构。"""
        data = [100 + random.gauss(0, 2) for _ in range(50)]
        random.seed(42)
        upper, middle, lower = bollinger_bands(data, 20)
        self.assertEqual(len(upper), 50)
        self.assertEqual(len(middle), 50)
        self.assertEqual(len(lower), 50)

    def test_bollinger_order(self):
        """测试上轨 > 中轨 > 下轨。"""
        data = [100 + random.gauss(0, 5) for _ in range(100)]
        random.seed(42)
        upper, middle, lower = bollinger_bands(data, 20)
        for i in range(len(data)):
            if upper[i] is not None:
                self.assertGreater(upper[i], middle[i])
                self.assertGreater(middle[i], lower[i])


class TestATR(unittest.TestCase):
    """测试ATR指标。"""

    def test_atr_positive(self):
        """测试ATR值为正。"""
        random.seed(42)
        n = 50
        highs = [100 + random.random() * 5 for _ in range(n)]
        lows = [95 + random.random() * 5 for _ in range(n)]
        closes = [97 + random.random() * 3 for _ in range(n)]
        result = atr(highs, lows, closes, 14)
        for val in result:
            if val is not None:
                self.assertGreater(val, 0)


class TestKDJ(unittest.TestCase):
    """测试KDJ指标。"""

    def test_kdj_structure(self):
        """测试KDJ返回结构。"""
        random.seed(42)
        n = 50
        highs = [100 + random.random() * 10 for _ in range(n)]
        lows = [90 + random.random() * 10 for _ in range(n)]
        closes = [95 + random.random() * 5 for _ in range(n)]
        k, d, j = kdj(highs, lows, closes)
        self.assertEqual(len(k), n)
        self.assertEqual(len(d), n)
        self.assertEqual(len(j), n)


class TestOBV(unittest.TestCase):
    """测试OBV指标。"""

    def test_obv_basic(self):
        """测试基本OBV计算。"""
        closes = [10, 11, 10, 12, 11]
        volumes = [100, 200, 150, 300, 250]
        result = obv(closes, volumes)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], 0)
        # 10->11 上涨, OBV += 200
        self.assertEqual(result[1], 200)
        # 11->10 下跌, OBV -= 150
        self.assertEqual(result[2], 50)
        # 10->12 上涨, OBV += 300
        self.assertEqual(result[3], 350)
        # 12->11 下跌, OBV -= 250
        self.assertEqual(result[4], 100)


class TestWR(unittest.TestCase):
    """测试威廉指标。"""

    def test_wr_range(self):
        """测试WR值在[-100, 0]之间。"""
        random.seed(42)
        n = 50
        highs = [100 + random.random() * 10 for _ in range(n)]
        lows = [90 + random.random() * 10 for _ in range(n)]
        closes = [95 + random.random() * 5 for _ in range(n)]
        result = wr(highs, lows, closes, 14)
        for val in result:
            if val is not None:
                self.assertGreaterEqual(val, -100)
                self.assertLessEqual(val, 0)


class TestCCI(unittest.TestCase):
    """测试CCI指标。"""

    def test_cci_structure(self):
        """测试CCI返回结构。"""
        random.seed(42)
        n = 50
        highs = [100 + random.random() * 10 for _ in range(n)]
        lows = [90 + random.random() * 10 for _ in range(n)]
        closes = [95 + random.random() * 5 for _ in range(n)]
        result = cci(highs, lows, closes, 20)
        self.assertEqual(len(result), n)


class TestDMI(unittest.TestCase):
    """测试DMI指标。"""

    def test_dmi_structure(self):
        """测试DMI返回结构。"""
        random.seed(42)
        n = 50
        highs = [100 + random.random() * 10 for _ in range(n)]
        lows = [90 + random.random() * 10 for _ in range(n)]
        closes = [95 + random.random() * 5 for _ in range(n)]
        pdi, ndi, adx = dmi(highs, lows, closes)
        self.assertEqual(len(pdi), n)
        self.assertEqual(len(ndi), n)
        self.assertEqual(len(adx), n)


class TestROC(unittest.TestCase):
    """测试ROC指标。"""

    def test_roc_calculation(self):
        """测试ROC计算。"""
        data = [100, 102, 104, 106, 108]
        result = roc(data, 2)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        # ROC = (104 - 100) / 100 * 100 = 4.0
        self.assertAlmostEqual(result[2], 4.0, places=4)
        # ROC = (106 - 102) / 102 * 100
        expected = (106 - 102) / 102 * 100
        self.assertAlmostEqual(result[3], expected, places=4)


class TestMFI(unittest.TestCase):
    """测试MFI指标。"""

    def test_mfi_range(self):
        """测试MFI值在[0, 100]之间。"""
        random.seed(42)
        n = 50
        highs = [100 + random.random() * 10 for _ in range(n)]
        lows = [90 + random.random() * 10 for _ in range(n)]
        closes = [95 + random.random() * 5 for _ in range(n)]
        volumes = [random.randint(1000, 5000) for _ in range(n)]
        result = mfi(highs, lows, closes, volumes, 14)
        for val in result:
            if val is not None:
                self.assertGreaterEqual(val, 0)
                self.assertLessEqual(val, 100)


class TestSTOCH(unittest.TestCase):
    """测试随机振荡指标。"""

    def test_stoch_range(self):
        """测试%K值在[0, 100]之间。"""
        random.seed(42)
        n = 50
        highs = [100 + random.random() * 10 for _ in range(n)]
        lows = [90 + random.random() * 10 for _ in range(n)]
        closes = [95 + random.random() * 5 for _ in range(n)]
        k, d = stoch(highs, lows, closes)
        for val in k:
            if val is not None:
                self.assertGreaterEqual(val, 0)
                self.assertLessEqual(val, 100)


class TestVWAP(unittest.TestCase):
    """测试VWAP指标。"""

    def test_vwap_basic(self):
        """测试基本VWAP计算。"""
        highs = [110, 112]
        lows = [100, 102]
        closes = [105, 107]
        volumes = [1000, 2000]
        result = vwap(highs, lows, closes, volumes)
        # VWAP_0 = (110+100+105)/3 * 1000 / 1000 = 105.0
        self.assertAlmostEqual(result[0], 105.0, places=4)
        # VWAP_1 = (TP0*V0 + TP1*V1) / (V0+V1)
        tp0 = (110 + 100 + 105) / 3
        tp1 = (112 + 102 + 107) / 3
        expected = (tp0 * 1000 + tp1 * 2000) / 3000
        self.assertAlmostEqual(result[1], expected, places=4)


class TestTRIX(unittest.TestCase):
    """测试TRIX指标。"""

    def test_trix_structure(self):
        """测试TRIX返回结构。"""
        data = [100 + random.gauss(0, 2) for _ in range(100)]
        random.seed(42)
        result = trix(data, 12)
        self.assertEqual(len(result), 100)


class TestSAR(unittest.TestCase):
    """测试SAR指标。"""

    def test_sar_structure(self):
        """测试SAR返回结构。"""
        random.seed(42)
        n = 50
        highs = [100 + random.random() * 10 for _ in range(n)]
        lows = [90 + random.random() * 10 for _ in range(n)]
        result = sar(highs, lows)
        self.assertEqual(len(result), n)


class TestWilliamsAD(unittest.TestCase):
    """测试威廉累积/派发线。"""

    def test_wad_basic(self):
        """测试基本WAD计算。"""
        highs = [110, 112]
        lows = [100, 102]
        closes = [105, 107]
        result = williams_ad(highs, lows, closes)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 0)
        # 上涨: AD += (107 - 102) = 5
        self.assertAlmostEqual(result[1], 5.0, places=4)


class TestComputeIndicator(unittest.TestCase):
    """测试通过名称计算指标。"""

    def test_compute_by_name(self):
        """测试通过名称计算MA指标。"""
        data = [1, 2, 3, 4, 5]
        result = compute_indicator("MA", data, 3)
        self.assertEqual(len(result), 5)

    def test_compute_unknown(self):
        """测试未知指标名称。"""
        with self.assertRaises(ValueError):
            compute_indicator("UNKNOWN", [1, 2, 3])

    def test_list_indicators(self):
        """测试列出所有指标。"""
        indicators = list_indicators()
        self.assertGreater(len(indicators), 15)
        names = [ind["name"] for ind in indicators]
        self.assertIn("MA", names)
        self.assertIn("RSI", names)
        self.assertIn("MACD", names)


class TestIndicatorRegistry(unittest.TestCase):
    """测试指标注册表完整性。"""

    def test_registry_has_19_indicators(self):
        """测试注册表包含19个指标。"""
        self.assertGreaterEqual(len(INDICATOR_REGISTRY), 19)

    def test_all_indicators_callable(self):
        """测试所有注册指标可调用。"""
        random.seed(42)
        n = 50
        closes = [100 + random.gauss(0, 2) for _ in range(n)]
        highs = [h + 2 for h in closes]
        lows = [l - 2 for l in closes]
        volumes = [random.randint(1000, 5000) for _ in range(n)]

        # 测试单参数指标
        for name in ["MA", "EMA", "SMA", "RSI", "ROC", "TRIX"]:
            result = INDICATOR_REGISTRY[name]["func"](closes, 10)
            self.assertEqual(len(result), n)

        # 测试OHLC指标
        for name in ["ATR", "WR", "CCI"]:
            result = INDICATOR_REGISTRY[name]["func"](highs, lows, closes, 10)
            self.assertEqual(len(result), n)


if __name__ == "__main__":
    unittest.main()
