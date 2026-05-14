"""
QuantPilot 策略框架模块

提供策略基类和5个内置策略:
    1. DualMACrossStrategy - 双均线交叉策略
    2. RSIOversoldOverboughtStrategy - RSI超买超卖策略
    3. MACDGoldenCrossStrategy - MACD金叉死叉策略
    4. BollingerBreakoutStrategy - 布林带突破策略
    5. MultiIndicatorStrategy - 多指标组合策略

用户可通过继承 StrategyBase 创建自定义策略。
"""

from .indicators import ma, ema, rsi, macd, bollinger_bands


class Signal:
    """
    交易信号。

    属性:
        BUY: 买入信号
        SELL: 卖出信号
        HOLD: 持有信号
    """
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class StrategyBase:
    """
    策略基类。

    所有自定义策略必须继承此类并实现 on_bar 方法。
    """

    def __init__(self, name="BaseStrategy", params=None):
        """
        初始化策略。

        Args:
            name: 策略名称
            params: 策略参数字典
        """
        self.name = name
        self.params = params or {}
        self._indicators_cache = {}

    def on_init(self, kline_data):
        """
        策略初始化，在回测开始前调用。

        可在此处进行指标预计算等操作。

        Args:
            kline_data: KLineData 对象
        """
        pass

    def on_bar(self, index, kline_data):
        """
        每根K线调用一次，生成交易信号。

        Args:
            index: 当前K线索引
            kline_data: KLineData 对象

        Returns:
            str: 交易信号 (Signal.BUY / Signal.SELL / Signal.HOLD)
        """
        return Signal.HOLD

    def get_param(self, key, default=None):
        """
        获取策略参数。

        Args:
            key: 参数名
            default: 默认值

        Returns:
            参数值
        """
        return self.params.get(key, default)

    def set_param(self, key, value):
        """
        设置策略参数。

        Args:
            key: 参数名
            value: 参数值
        """
        self.params[key] = value

    def description(self):
        """
        返回策略描述。

        Returns:
            str: 策略描述文本
        """
        return "基础策略基类"

    def __repr__(self):
        return "Strategy(name={}, params={})".format(self.name, self.params)


class DualMACrossStrategy(StrategyBase):
    """
    双均线交叉策略。

    策略逻辑:
        - 计算快线(MA_fast)和慢线(MA_slow)
        - 当快线从下方上穿慢线时，产生买入信号（金叉）
        - 当快线从上方下穿慢线时，产生卖出信号（死叉）

    参数:
        fast_period: 快线周期，默认5
        slow_period: 慢线周期，默认20
    """

    def __init__(self, fast_period=5, slow_period=20):
        params = {"fast_period": fast_period, "slow_period": slow_period}
        super().__init__(name="DualMACross", params=params)
        self._fast_ma = []
        self._slow_ma = []

    def on_init(self, kline_data):
        """预计算均线指标。"""
        closes = kline_data.get_closes()
        self._fast_ma = ma(closes, self.get_param("fast_period"))
        self._slow_ma = ma(closes, self.get_param("slow_period"))

    def on_bar(self, index, kline_data):
        """根据均线交叉生成信号。"""
        if index < 1:
            return Signal.HOLD

        fast_prev = self._fast_ma[index - 1] if index - 1 < len(self._fast_ma) else None
        fast_curr = self._fast_ma[index] if index < len(self._fast_ma) else None
        slow_prev = self._slow_ma[index - 1] if index - 1 < len(self._slow_ma) else None
        slow_curr = self._slow_ma[index] if index < len(self._slow_ma) else None

        if any(v is None for v in [fast_prev, fast_curr, slow_prev, slow_curr]):
            return Signal.HOLD

        # 金叉: 快线从下方上穿慢线
        if fast_prev <= slow_prev and fast_curr > slow_curr:
            return Signal.BUY
        # 死叉: 快线从上方下穿慢线
        if fast_prev >= slow_prev and fast_curr < slow_curr:
            return Signal.SELL

        return Signal.HOLD

    def description(self):
        return (
            "双均线交叉策略: 快线(MA{})上穿慢线(MA{})买入，"
            "下穿卖出".format(
                self.get_param("fast_period"), self.get_param("slow_period")
            )
        )


class RSIOversoldOverboughtStrategy(StrategyBase):
    """
    RSI超买超卖策略。

    策略逻辑:
        - 计算RSI指标
        - RSI低于超卖线时买入
        - RSI高于超买线时卖出

    参数:
        period: RSI周期，默认14
        oversold: 超卖线，默认30
        overbought: 超买线，默认70
    """

    def __init__(self, period=14, oversold=30, overbought=70):
        params = {
            "period": period,
            "oversold": oversold,
            "overbought": overbought,
        }
        super().__init__(name="RSIOversoldOverbought", params=params)
        self._rsi_values = []

    def on_init(self, kline_data):
        """预计算RSI指标。"""
        closes = kline_data.get_closes()
        self._rsi_values = rsi(closes, self.get_param("period"))

    def on_bar(self, index, kline_data):
        """根据RSI超买超卖生成信号。"""
        if index < 1:
            return Signal.HOLD

        rsi_prev = self._rsi_values[index - 1] if index - 1 < len(self._rsi_values) else None
        rsi_curr = self._rsi_values[index] if index < len(self._rsi_values) else None

        if rsi_prev is None or rsi_curr is None:
            return Signal.HOLD

        oversold = self.get_param("oversold")
        overbought = self.get_param("overbought")

        # RSI从超卖区域上穿
        if rsi_prev < oversold and rsi_curr >= oversold:
            return Signal.BUY
        # RSI从超买区域下穿
        if rsi_prev > overbought and rsi_curr <= overbought:
            return Signal.SELL

        return Signal.HOLD

    def description(self):
        return (
            "RSI超买超卖策略: RSI({})低于{}买入，"
            "高于{}卖出".format(
                self.get_param("period"),
                self.get_param("oversold"),
                self.get_param("overbought"),
            )
        )


class MACDGoldenCrossStrategy(StrategyBase):
    """
    MACD金叉死叉策略。

    策略逻辑:
        - 计算MACD指标（DIF, DEA, MACD柱）
        - DIF上穿DEA时买入（金叉）
        - DIF下穿DEA时卖出（死叉）

    参数:
        fast_period: 快线周期，默认12
        slow_period: 慢线周期，默认26
        signal_period: 信号线周期，默认9
    """

    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        params = {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period,
        }
        super().__init__(name="MACDGoldenCross", params=params)
        self._dif = []
        self._dea = []
        self._macd_hist = []

    def on_init(self, kline_data):
        """预计算MACD指标。"""
        closes = kline_data.get_closes()
        self._dif, self._dea, self._macd_hist = macd(
            closes,
            self.get_param("fast_period"),
            self.get_param("slow_period"),
            self.get_param("signal_period"),
        )

    def on_bar(self, index, kline_data):
        """根据MACD金叉死叉生成信号。"""
        if index < 1:
            return Signal.HOLD

        dif_prev = self._dif[index - 1] if index - 1 < len(self._dif) else None
        dif_curr = self._dif[index] if index < len(self._dif) else None
        dea_prev = self._dea[index - 1] if index - 1 < len(self._dea) else None
        dea_curr = self._dea[index] if index < len(self._dea) else None

        if any(v is None for v in [dif_prev, dif_curr, dea_prev, dea_curr]):
            return Signal.HOLD

        # 金叉: DIF从下方上穿DEA
        if dif_prev <= dea_prev and dif_curr > dea_curr:
            return Signal.BUY
        # 死叉: DIF从上方下穿DEA
        if dif_prev >= dea_prev and dif_curr < dea_curr:
            return Signal.SELL

        return Signal.HOLD

    def description(self):
        return (
            "MACD金叉死叉策略: DIF上穿DEA买入，"
            "DIF下穿DEA卖出 (fast={}, slow={}, signal={})".format(
                self.get_param("fast_period"),
                self.get_param("slow_period"),
                self.get_param("signal_period"),
            )
        )


class BollingerBreakoutStrategy(StrategyBase):
    """
    布林带突破策略。

    策略逻辑:
        - 计算布林带（上轨、中轨、下轨）
        - 价格跌破下轨时买入（超卖反弹）
        - 价格突破上轨时卖出（超买回落）

    参数:
        period: 布林带周期，默认20
        std_multiplier: 标准差倍数，默认2.0
    """

    def __init__(self, period=20, std_multiplier=2.0):
        params = {
            "period": period,
            "std_multiplier": std_multiplier,
        }
        super().__init__(name="BollingerBreakout", params=params)
        self._upper = []
        self._middle = []
        self._lower = []

    def on_init(self, kline_data):
        """预计算布林带指标。"""
        closes = kline_data.get_closes()
        self._upper, self._middle, self._lower = bollinger_bands(
            closes,
            self.get_param("period"),
            self.get_param("std_multiplier"),
        )

    def on_bar(self, index, kline_data):
        """根据布林带突破生成信号。"""
        if index < 1:
            return Signal.HOLD

        close_prev = kline_data[index - 1].close if index - 1 < len(kline_data) else None
        close_curr = kline_data[index].close if index < len(kline_data) else None
        lower_prev = self._lower[index - 1] if index - 1 < len(self._lower) else None
        lower_curr = self._lower[index] if index < len(self._lower) else None
        upper_prev = self._upper[index - 1] if index - 1 < len(self._upper) else None
        upper_curr = self._upper[index] if index < len(self._upper) else None

        if any(v is None for v in [close_prev, close_curr, lower_prev, lower_curr, upper_prev, upper_curr]):
            return Signal.HOLD

        # 价格从下轨下方回到上方 -> 买入
        if close_prev <= lower_prev and close_curr > lower_curr:
            return Signal.BUY
        # 价格从上轨上方回到下方 -> 卖出
        if close_prev >= upper_prev and close_curr < upper_curr:
            return Signal.SELL

        return Signal.HOLD

    def description(self):
        return (
            "布林带突破策略: 价格从下轨下方回到上方买入，"
            "从上轨上方回到下方卖出 (period={}, std={})".format(
                self.get_param("period"),
                self.get_param("std_multiplier"),
            )
        )


class MultiIndicatorStrategy(StrategyBase):
    """
    多指标组合策略。

    策略逻辑:
        - 结合均线趋势、RSI超买超卖、MACD方向三个维度
        - 买入条件: 快线在慢线上方(趋势向上) + RSI未超买 + MACD金叉
        - 卖出条件: 快线在慢线下方(趋势向下) + RSI未超卖 + MACD死叉

    参数:
        fast_period: 快线周期，默认5
        slow_period: 慢线周期，默认20
        rsi_period: RSI周期，默认14
        macd_fast: MACD快线周期，默认12
        macd_slow: MACD慢线周期，默认26
        macd_signal: MACD信号线周期，默认9
    """

    def __init__(self, fast_period=5, slow_period=20, rsi_period=14,
                 macd_fast=12, macd_slow=26, macd_signal=9):
        params = {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "rsi_period": rsi_period,
            "macd_fast": macd_fast,
            "macd_slow": macd_slow,
            "macd_signal": macd_signal,
        }
        super().__init__(name="MultiIndicator", params=params)
        self._fast_ma = []
        self._slow_ma = []
        self._rsi_values = []
        self._dif = []
        self._dea = []

    def on_init(self, kline_data):
        """预计算所有指标。"""
        closes = kline_data.get_closes()
        self._fast_ma = ma(closes, self.get_param("fast_period"))
        self._slow_ma = ma(closes, self.get_param("slow_period"))
        self._rsi_values = rsi(closes, self.get_param("rsi_period"))
        self._dif, self._dea, _ = macd(
            closes,
            self.get_param("macd_fast"),
            self.get_param("macd_slow"),
            self.get_param("macd_signal"),
        )

    def on_bar(self, index, kline_data):
        """根据多指标组合生成信号。"""
        if index < 1:
            return Signal.HOLD

        fast_ma = self._fast_ma[index] if index < len(self._fast_ma) else None
        slow_ma = self._slow_ma[index] if index < len(self._slow_ma) else None
        rsi_val = self._rsi_values[index] if index < len(self._rsi_values) else None
        dif_prev = self._dif[index - 1] if index - 1 < len(self._dif) else None
        dif_curr = self._dif[index] if index < len(self._dif) else None
        dea_prev = self._dea[index - 1] if index - 1 < len(self._dea) else None
        dea_curr = self._dea[index] if index < len(self._dea) else None

        if any(v is None for v in [fast_ma, slow_ma, rsi_val, dif_prev, dif_curr, dea_prev, dea_curr]):
            return Signal.HOLD

        # 买入条件: 趋势向上 + RSI未超买(<=70) + MACD金叉
        trend_up = fast_ma > slow_ma
        rsi_not_overbought = rsi_val <= 70
        macd_golden = dif_prev <= dea_prev and dif_curr > dea_curr

        if trend_up and rsi_not_overbought and macd_golden:
            return Signal.BUY

        # 卖出条件: 趋势向下 + RSI未超卖(>=30) + MACD死叉
        trend_down = fast_ma < slow_ma
        rsi_not_oversold = rsi_val >= 30
        macd_dead = dif_prev >= dea_prev and dif_curr < dea_curr

        if trend_down and rsi_not_oversold and macd_dead:
            return Signal.SELL

        return Signal.HOLD

    def description(self):
        return (
            "多指标组合策略: 结合均线趋势+RSI+MACD三维度，"
            "多条件共振时产生买卖信号"
        )


# 策略注册表
STRATEGY_REGISTRY = {
    "dual_ma_cross": {
        "class": DualMACrossStrategy,
        "desc": "双均线交叉策略",
        "params": {"fast_period": 5, "slow_period": 20},
    },
    "rsi_oversold_overbought": {
        "class": RSIOversoldOverboughtStrategy,
        "desc": "RSI超买超卖策略",
        "params": {"period": 14, "oversold": 30, "overbought": 70},
    },
    "macd_golden_cross": {
        "class": MACDGoldenCrossStrategy,
        "desc": "MACD金叉死叉策略",
        "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    },
    "bollinger_breakout": {
        "class": BollingerBreakoutStrategy,
        "desc": "布林带突破策略",
        "params": {"period": 20, "std_multiplier": 2.0},
    },
    "multi_indicator": {
        "class": MultiIndicatorStrategy,
        "desc": "多指标组合策略",
        "params": {
            "fast_period": 5, "slow_period": 20, "rsi_period": 14,
            "macd_fast": 12, "macd_slow": 26, "macd_signal": 9,
        },
    },
}


def list_strategies():
    """
    列出所有可用的策略。

    Returns:
        list: 策略信息列表
    """
    return [
        {
            "name": name,
            "desc": info["desc"],
            "params": info["params"],
        }
        for name, info in STRATEGY_REGISTRY.items()
    ]


def create_strategy(name, **params):
    """
    通过名称创建策略实例。

    Args:
        name: 策略名称
        **params: 策略参数（覆盖默认值）

    Returns:
        StrategyBase: 策略实例

    Raises:
        ValueError: 策略名称不存在
    """
    if name not in STRATEGY_REGISTRY:
        available = ", ".join(STRATEGY_REGISTRY.keys())
        raise ValueError("未知策略: '{}'，可用策略: {}".format(name, available))

    default_params = STRATEGY_REGISTRY[name]["params"].copy()
    default_params.update(params)
    return STRATEGY_REGISTRY[name]["class"](**default_params)
