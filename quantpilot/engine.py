"""
QuantPilot 回测引擎核心模块

提供策略回测执行、信号生成、持仓管理、止损止盈、手续费计算等功能。

主要组件:
    - Position: 持仓信息
    - TradeRecord: 交易记录
    - BacktestEngine: 回测引擎
"""

from .strategy import Signal
from .utils import round_to


class Position:
    """
    持仓信息。

    属性:
        symbol: 标的代码
        direction: 持仓方向 ("long" / "short")
        quantity: 持仓数量
        avg_price: 平均持仓价格
        current_price: 当前价格
        stop_loss: 止损价
        take_profit: 止盈价
        open_date: 开仓日期
    """

    def __init__(self, symbol, direction, quantity, price, date):
        self.symbol = symbol
        self.direction = direction  # "long" 或 "short"
        self.quantity = quantity
        self.avg_price = round_to(price)
        self.current_price = round_to(price)
        self.stop_loss = None
        self.take_profit = None
        self.open_date = date

    @property
    def market_value(self):
        """持仓市值。"""
        return round_to(self.quantity * self.current_price)

    @property
    def cost(self):
        """持仓成本。"""
        return round_to(self.quantity * self.avg_price)

    @property
    def pnl(self):
        """浮动盈亏。"""
        if self.direction == "long":
            return round_to((self.current_price - self.avg_price) * self.quantity)
        else:
            return round_to((self.avg_price - self.current_price) * self.quantity)

    @property
    def pnl_percent(self):
        """浮动盈亏百分比。"""
        if self.avg_price == 0:
            return 0.0
        if self.direction == "long":
            return round_to((self.current_price - self.avg_price) / self.avg_price)
        else:
            return round_to((self.avg_price - self.current_price) / self.avg_price)

    def update_price(self, price):
        """更新当前价格。"""
        self.current_price = round_to(price)

    def __repr__(self):
        return (
            "Position(symbol={}, dir={}, qty={}, avg={}, "
            "cur={}, pnl={})".format(
                self.symbol, self.direction, self.quantity,
                self.avg_price, self.current_price, self.pnl
            )
        )


class TradeRecord:
    """
    交易记录。

    属性:
        date: 交易日期
        symbol: 标的代码
        action: 交易动作 ("buy" / "sell")
        price: 成交价格
        quantity: 成交数量
        commission: 手续费
        slippage: 滑点成本
        pnl: 平仓盈亏（开仓时为0）
        signal: 触发信号
        reason: 交易原因
    """

    def __init__(self, date, symbol, action, price, quantity,
                 commission=0.0, slippage=0.0, pnl=0.0,
                 signal="", reason=""):
        self.date = date
        self.symbol = symbol
        self.action = action
        self.price = round_to(price)
        self.quantity = quantity
        self.commission = round_to(commission)
        self.slippage = round_to(slippage)
        self.pnl = round_to(pnl)
        self.signal = signal
        self.reason = reason

    def to_dict(self):
        """转换为字典。"""
        return {
            "date": self.date,
            "symbol": self.symbol,
            "action": self.action,
            "price": self.price,
            "quantity": self.quantity,
            "commission": self.commission,
            "slippage": self.slippage,
            "pnl": self.pnl,
            "signal": self.signal,
            "reason": self.reason,
        }

    def __repr__(self):
        return (
            "TradeRecord(date={}, {} {} {}@{}, "
            "comm={}, pnl={})".format(
                self.date, self.action, self.quantity,
                self.symbol, self.price, self.commission, self.pnl
            )
        )


class BacktestConfig:
    """
    回测配置。

    属性:
        initial_capital: 初始资金
        commission_rate: 手续费率（默认万三）
        slippage: 滑点（固定金额或百分比）
        slippage_type: 滑点类型 ("fixed" / "percent")
        stop_loss: 止损比例（如0.05表示5%）
        take_profit: 止盈比例（如0.10表示10%）
        position_size: 仓位比例（如0.9表示90%资金）
        symbol: 标的代码
    """

    def __init__(self, initial_capital=1000000.0, commission_rate=0.0003,
                 slippage=0.01, slippage_type="fixed",
                 stop_loss=None, take_profit=None,
                 position_size=0.9, symbol="DEFAULT"):
        self.initial_capital = float(initial_capital)
        self.commission_rate = float(commission_rate)
        self.slippage = float(slippage)
        self.slippage_type = slippage_type
        self.stop_loss = float(stop_loss) if stop_loss is not None else None
        self.take_profit = float(take_profit) if take_profit is not None else None
        self.position_size = float(position_size)
        self.symbol = symbol


class BacktestEngine:
    """
    回测引擎。

    执行策略回测，管理持仓和资金，记录交易。

    使用方式:
        engine = BacktestEngine(config)
        result = engine.run(strategy, kline_data)
    """

    def __init__(self, config=None):
        """
        初始化回测引擎。

        Args:
            config: BacktestConfig 配置对象，默认使用标准配置
        """
        self.config = config or BacktestConfig()

        # 账户状态
        self._cash = self.config.initial_capital
        self._position = None  # 当前持仓
        self._trades = []  # 交易记录
        self._daily_values = []  # 每日净值

    @property
    def cash(self):
        """当前现金。"""
        return round_to(self._cash)

    @property
    def position(self):
        """当前持仓。"""
        return self._position

    @property
    def trades(self):
        """交易记录列表。"""
        return self._trades

    @property
    def daily_values(self):
        """每日净值序列。"""
        return self._daily_values

    @property
    def total_assets(self):
        """总资产 = 现金 + 持仓市值。"""
        position_value = self._position.market_value if self._position else 0
        return round_to(self._cash + position_value)

    def _calculate_commission(self, price, quantity):
        """
        计算手续费。

        公式: commission = price * quantity * commission_rate

        Args:
            price: 成交价格
            quantity: 成交数量

        Returns:
            float: 手续费
        """
        return round_to(price * quantity * self.config.commission_rate)

    def _calculate_slippage(self, price):
        """
        计算滑点。

        Args:
            price: 原始价格

        Returns:
            float: 滑点后的价格
        """
        if self.config.slippage_type == "percent":
            return round_to(price * (1 + self.config.slippage))
        else:
            return round_to(price + self.config.slippage)

    def _calculate_quantity(self, price):
        """
        计算可买入数量。

        使用全部可用资金的 position_size 比例。

        Args:
            price: 买入价格

        Returns:
            int: 可买入数量（取整）
        """
        available = self._cash * self.config.position_size
        # 预留手续费
        max_cost = available / (1 + self.config.commission_rate)
        quantity = int(max_cost / price)
        return max(quantity, 0)

    def _buy(self, date, price, signal="", reason=""):
        """
        执行买入操作。

        Args:
            date: 交易日期
            price: 买入价格
            signal: 触发信号
            reason: 交易原因
        """
        # 计算滑点
        exec_price = self._calculate_slippage(price)
        quantity = self._calculate_quantity(exec_price)

        if quantity <= 0:
            return

        commission = self._calculate_commission(exec_price, quantity)
        total_cost = exec_price * quantity + commission

        if total_cost > self._cash:
            # 资金不足，减少数量
            quantity = int((self._cash - commission) / exec_price)
            if quantity <= 0:
                return
            commission = self._calculate_commission(exec_price, quantity)
            total_cost = exec_price * quantity + commission

        self._cash -= total_cost

        self._position = Position(
            symbol=self.config.symbol,
            direction="long",
            quantity=quantity,
            price=exec_price,
            date=date,
        )

        # 设置止损止盈
        if self.config.stop_loss is not None:
            self._position.stop_loss = round_to(
                exec_price * (1 - self.config.stop_loss)
            )
        if self.config.take_profit is not None:
            self._position.take_profit = round_to(
                exec_price * (1 + self.config.take_profit)
            )

        trade = TradeRecord(
            date=date,
            symbol=self.config.symbol,
            action="buy",
            price=exec_price,
            quantity=quantity,
            commission=commission,
            slippage=round_to(exec_price - price),
            signal=signal,
            reason=reason,
        )
        self._trades.append(trade)

    def _sell(self, date, price, signal="", reason=""):
        """
        执行卖出操作。

        Args:
            date: 交易日期
            price: 卖出价格
            signal: 触发信号
            reason: 交易原因
        """
        if self._position is None:
            return

        # 计算滑点（卖出时滑点为负）
        if self.config.slippage_type == "percent":
            exec_price = round_to(price * (1 - self.config.slippage))
        else:
            exec_price = round_to(price - self.config.slippage)

        quantity = self._position.quantity
        commission = self._calculate_commission(exec_price, quantity)
        total_revenue = exec_price * quantity - commission

        # 计算盈亏
        cost = self._position.avg_price * quantity
        pnl = total_revenue - cost

        self._cash += total_revenue

        trade = TradeRecord(
            date=date,
            symbol=self.config.symbol,
            action="sell",
            price=exec_price,
            quantity=quantity,
            commission=commission,
            slippage=round_to(price - exec_price),
            pnl=pnl,
            signal=signal,
            reason=reason,
        )
        self._trades.append(trade)
        self._position = None

    def _check_stop_loss_take_profit(self, date, kline):
        """
        检查止损止盈。

        Args:
            date: 当前日期
            kline: 当前K线

        Returns:
            str or None: 触发的操作 ("stop_loss" / "take_profit" / None)
        """
        if self._position is None:
            return None

        high = kline.high
        low = kline.low

        # 检查止损
        if self._position.stop_loss is not None:
            if low <= self._position.stop_loss:
                self._sell(date, self._position.stop_loss, "STOP_LOSS", "止损")
                return "stop_loss"

        # 检查止盈
        if self._position.take_profit is not None:
            if high >= self._position.take_profit:
                self._sell(date, self._position.take_profit, "TAKE_PROFIT", "止盈")
                return "take_profit"

        return None

    def run(self, strategy, kline_data):
        """
        执行回测。

        Args:
            strategy: 策略实例 (StrategyBase)
            kline_data: K线数据 (KLineData)

        Returns:
            dict: 回测结果字典，包含:
                - trades: 交易记录列表
                - daily_values: 每日净值列表
                - daily_returns: 每日收益率列表
                - config: 回测配置
                - strategy_name: 策略名称
                - data_summary: 数据摘要
        """
        # 重置状态
        self._cash = self.config.initial_capital
        self._position = None
        self._trades = []
        self._daily_values = []

        # 初始化策略
        strategy.on_init(kline_data)

        # 逐根K线执行
        for i in range(len(kline_data)):
            kline = kline_data[i]

            # 更新持仓价格
            if self._position is not None:
                self._position.update_price(kline.close)

            # 检查止损止盈
            sl_tp = self._check_stop_loss_take_profit(kline.date, kline)
            if sl_tp is not None:
                # 止损/止盈后记录净值
                self._daily_values.append({
                    "date": kline.date,
                    "total_assets": self.total_assets,
                    "cash": self._cash,
                    "position_value": self._position.market_value if self._position else 0,
                    "close": kline.close,
                })
                continue

            # 获取策略信号
            signal = strategy.on_bar(i, kline_data)

            # 执行交易
            if signal == Signal.BUY and self._position is None:
                self._buy(kline.date, kline.close, signal, "策略信号买入")
            elif signal == Signal.SELL and self._position is not None:
                self._sell(kline.date, kline.close, signal, "策略信号卖出")

            # 记录每日净值
            self._daily_values.append({
                "date": kline.date,
                "total_assets": self.total_assets,
                "cash": self._cash,
                "position_value": self._position.market_value if self._position else 0,
                "close": kline.close,
            })

        # 计算每日收益率
        daily_returns = []
        for i, dv in enumerate(self._daily_values):
            if i == 0:
                daily_returns.append(0.0)
            else:
                prev_assets = self._daily_values[i - 1]["total_assets"]
                if prev_assets != 0:
                    ret = (dv["total_assets"] - prev_assets) / prev_assets
                    daily_returns.append(round_to(ret))
                else:
                    daily_returns.append(0.0)

        return {
            "trades": [t.to_dict() for t in self._trades],
            "daily_values": self._daily_values,
            "daily_returns": daily_returns,
            "config": {
                "initial_capital": self.config.initial_capital,
                "commission_rate": self.config.commission_rate,
                "slippage": self.config.slippage,
                "slippage_type": self.config.slippage_type,
                "stop_loss": self.config.stop_loss,
                "take_profit": self.config.take_profit,
                "position_size": self.config.position_size,
                "symbol": self.config.symbol,
            },
            "strategy_name": strategy.name,
            "strategy_desc": strategy.description(),
            "data_summary": kline_data.summary(),
        }
