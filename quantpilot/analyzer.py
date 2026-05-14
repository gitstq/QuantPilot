"""
QuantPilot 收益分析器模块

计算回测结果的核心风控指标:
    - 总收益率
    - 年化收益率
    - 最大回撤
    - 夏普比率 (Sharpe Ratio)
    - Sortino比率 (Sortino Ratio)
    - Calmar比率 (Calmar Ratio)
    - 胜率
    - 盈亏比
    - 最大连续盈利/亏损次数
    - 月度收益统计
    - 交易统计
"""

import math
from collections import defaultdict

from .utils import (
    round_to, format_percent, format_number,
    mean, sample_std_dev, max_drawdown, safe_divide,
    annualize_return, trading_days_per_year,
)


class PerformanceAnalyzer:
    """
    收益分析器。

    对回测结果进行全面的风险收益分析。
    """

    def __init__(self, backtest_result):
        """
        初始化分析器。

        Args:
            backtest_result: BacktestEngine.run() 返回的结果字典
        """
        self.result = backtest_result
        self._daily_values = backtest_result["daily_values"]
        self._daily_returns = backtest_result["daily_returns"]
        self._trades = backtest_result["trades"]
        self._initial_capital = backtest_result["config"]["initial_capital"]
        self._metrics = None

    def analyze(self):
        """
        执行全部分析。

        Returns:
            dict: 包含所有分析指标的字典
        """
        if self._metrics is not None:
            return self._metrics

        self._metrics = {
            # 基本收益指标
            "total_return": self.total_return(),
            "annual_return": self.annual_return(),
            "max_drawdown": self.max_drawdown(),
            "max_drawdown_duration": self.max_drawdown_duration(),
            # 风险调整指标
            "sharpe_ratio": self.sharpe_ratio(),
            "sortino_ratio": self.sortino_ratio(),
            "calmar_ratio": self.calmar_ratio(),
            # 波动率
            "volatility": self.volatility(),
            "downside_volatility": self.downside_volatility(),
            # 交易统计
            "total_trades": self.total_trades(),
            "win_rate": self.win_rate(),
            "profit_loss_ratio": self.profit_loss_ratio(),
            "max_consecutive_wins": self.max_consecutive_wins(),
            "max_consecutive_losses": self.max_consecutive_losses(),
            "avg_profit": self.avg_profit(),
            "avg_loss": self.avg_loss(),
            "total_commission": self.total_commission(),
            "total_pnl": self.total_pnl(),
            # 资金统计
            "final_capital": self.final_capital(),
            "peak_capital": self.peak_capital(),
            "min_capital": self.min_capital(),
            # 月度统计
            "monthly_returns": self.monthly_returns(),
            "monthly_win_rate": self.monthly_win_rate(),
            # 附加信息
            "avg_holding_days": self.avg_holding_days(),
            "trading_days": self.trading_days(),
        }

        return self._metrics

    def total_return(self):
        """
        计算总收益率。

        公式: total_return = (final_capital - initial_capital) / initial_capital

        Returns:
            float: 总收益率（小数形式）
        """
        if not self._daily_values:
            return 0.0
        final = self._daily_values[-1]["total_assets"]
        return round_to((final - self._initial_capital) / self._initial_capital)

    def annual_return(self):
        """
        计算年化收益率。

        公式: annual_return = (1 + total_return) ^ (252 / n_days) - 1

        Returns:
            float: 年化收益率（小数形式）
        """
        n_days = len(self._daily_values)
        return round_to(annualize_return(self.total_return(), n_days))

    def max_drawdown(self):
        """
        计算最大回撤。

        公式: MDD = max(1 - trough / peak)

        Returns:
            float: 最大回撤（正数，小数形式）
        """
        if not self._daily_values:
            return 0.0
        asset_values = [dv["total_assets"] for dv in self._daily_values]
        mdd, _, _ = max_drawdown(asset_values)
        return round_to(mdd)

    def max_drawdown_duration(self):
        """
        计算最大回撤持续天数。

        Returns:
            int: 最大回撤持续天数
        """
        if not self._daily_values:
            return 0
        asset_values = [dv["total_assets"] for dv in self._daily_values]
        _, start, end = max_drawdown(asset_values)
        return end - start

    def volatility(self):
        """
        计算年化波动率。

        公式: volatility = std(daily_returns) * sqrt(252)

        Returns:
            float: 年化波动率
        """
        if len(self._daily_returns) < 2:
            return 0.0
        daily_std = sample_std_dev(self._daily_returns)
        return round_to(daily_std * math.sqrt(trading_days_per_year()))

    def downside_volatility(self):
        """
        计算下行波动率（仅计算负收益的标准差）。

        公式: downside_vol = std(min(r_i, 0)) * sqrt(252)

        Returns:
            float: 年化下行波动率
        """
        negative_returns = [min(r, 0) for r in self._daily_returns]
        if len(negative_returns) < 2:
            return 0.0
        daily_down_std = sample_std_dev(negative_returns)
        return round_to(daily_down_std * math.sqrt(trading_days_per_year()))

    def sharpe_ratio(self, risk_free_rate=0.03):
        """
        计算夏普比率。

        公式: Sharpe = (annual_return - risk_free_rate) / volatility

        Args:
            risk_free_rate: 无风险利率（年化），默认3%

        Returns:
            float: 夏普比率
        """
        vol = self.volatility()
        if vol == 0:
            return 0.0
        ann_ret = self.annual_return()
        return round_to((ann_ret - risk_free_rate) / vol)

    def sortino_ratio(self, risk_free_rate=0.03):
        """
        计算Sortino比率。

        公式: Sortino = (annual_return - risk_free_rate) / downside_volatility

        Args:
            risk_free_rate: 无风险利率（年化），默认3%

        Returns:
            float: Sortino比率
        """
        down_vol = self.downside_volatility()
        if down_vol == 0:
            return 0.0
        ann_ret = self.annual_return()
        return round_to((ann_ret - risk_free_rate) / down_vol)

    def calmar_ratio(self):
        """
        计算Calmar比率。

        公式: Calmar = annual_return / max_drawdown

        Returns:
            float: Calmar比率
        """
        mdd = self.max_drawdown()
        if mdd == 0:
            return 0.0
        return round_to(self.annual_return() / mdd)

    def total_trades(self):
        """
        计算总交易次数（仅计算卖出/平仓次数）。

        Returns:
            int: 交易次数
        """
        sell_trades = [t for t in self._trades if t["action"] == "sell"]
        return len(sell_trades)

    def win_rate(self):
        """
        计算胜率。

        公式: win_rate = winning_trades / total_trades

        Returns:
            float: 胜率（小数形式）
        """
        sell_trades = [t for t in self._trades if t["action"] == "sell"]
        if not sell_trades:
            return 0.0
        wins = [t for t in sell_trades if t["pnl"] > 0]
        return round_to(len(wins) / len(sell_trades))

    def profit_loss_ratio(self):
        """
        计算盈亏比。

        公式: P/L Ratio = avg_profit / |avg_loss|

        Returns:
            float: 盈亏比
        """
        sell_trades = [t for t in self._trades if t["action"] == "sell"]
        profits = [t["pnl"] for t in sell_trades if t["pnl"] > 0]
        losses = [t["pnl"] for t in sell_trades if t["pnl"] < 0]

        if not losses:
            return float("inf") if profits else 0.0
        if not profits:
            return 0.0

        avg_profit = sum(profits) / len(profits)
        avg_loss = abs(sum(losses) / len(losses))

        if avg_loss == 0:
            return float("inf")
        return round_to(avg_profit / avg_loss)

    def max_consecutive_wins(self):
        """
        计算最大连续盈利次数。

        Returns:
            int: 最大连续盈利次数
        """
        sell_trades = [t for t in self._trades if t["action"] == "sell"]
        if not sell_trades:
            return 0

        max_wins = 0
        current_wins = 0
        for trade in sell_trades:
            if trade["pnl"] > 0:
                current_wins += 1
                max_wins = max(max_wins, current_wins)
            else:
                current_wins = 0

        return max_wins

    def max_consecutive_losses(self):
        """
        计算最大连续亏损次数。

        Returns:
            int: 最大连续亏损次数
        """
        sell_trades = [t for t in self._trades if t["action"] == "sell"]
        if not sell_trades:
            return 0

        max_losses = 0
        current_losses = 0
        for trade in sell_trades:
            if trade["pnl"] < 0:
                current_losses += 1
                max_losses = max(max_losses, current_losses)
            else:
                current_losses = 0

        return max_losses

    def avg_profit(self):
        """
        计算平均盈利。

        Returns:
            float: 平均盈利金额
        """
        sell_trades = [t for t in self._trades if t["action"] == "sell"]
        profits = [t["pnl"] for t in sell_trades if t["pnl"] > 0]
        if not profits:
            return 0.0
        return round_to(sum(profits) / len(profits))

    def avg_loss(self):
        """
        计算平均亏损。

        Returns:
            float: 平均亏损金额（正数）
        """
        sell_trades = [t for t in self._trades if t["action"] == "sell"]
        losses = [t["pnl"] for t in sell_trades if t["pnl"] < 0]
        if not losses:
            return 0.0
        return round_to(abs(sum(losses) / len(losses)))

    def total_commission(self):
        """
        计算总手续费。

        Returns:
            float: 总手续费
        """
        return round_to(sum(t["commission"] for t in self._trades))

    def total_pnl(self):
        """
        计算总盈亏。

        Returns:
            float: 总盈亏
        """
        sell_trades = [t for t in self._trades if t["action"] == "sell"]
        return round_to(sum(t["pnl"] for t in sell_trades))

    def final_capital(self):
        """
        获取最终资金。

        Returns:
            float: 最终资金
        """
        if not self._daily_values:
            return self._initial_capital
        return round_to(self._daily_values[-1]["total_assets"])

    def peak_capital(self):
        """
        获取峰值资金。

        Returns:
            float: 峰值资金
        """
        if not self._daily_values:
            return self._initial_capital
        return round_to(max(dv["total_assets"] for dv in self._daily_values))

    def min_capital(self):
        """
        获取最低资金。

        Returns:
            float: 最低资金
        """
        if not self._daily_values:
            return self._initial_capital
        return round_to(min(dv["total_assets"] for dv in self._daily_values))

    def trading_days(self):
        """
        获取交易天数。

        Returns:
            int: 交易天数
        """
        return len(self._daily_values)

    def monthly_returns(self):
        """
        计算月度收益率。

        Returns:
            dict: {月份字符串: 收益率} 如 {"2024-01": 0.05}
        """
        if not self._daily_values:
            return {}

        monthly = defaultdict(list)
        for dv in self._daily_values:
            month_key = dv["date"][:7]  # "YYYY-MM"
            monthly[month_key].append(dv["total_assets"])

        result = {}
        months_sorted = sorted(monthly.keys())
        prev_last = None

        for month in months_sorted:
            values = monthly[month]
            if prev_last is not None:
                month_return = (values[-1] - prev_last) / prev_last if prev_last != 0 else 0
                result[month] = round_to(month_return)
            prev_last = values[-1]

        return result

    def monthly_win_rate(self):
        """
        计算月度胜率。

        Returns:
            float: 月度胜率（小数形式）
        """
        monthly = self.monthly_returns()
        if not monthly:
            return 0.0
        wins = sum(1 for r in monthly.values() if r > 0)
        return round_to(wins / len(monthly))

    def avg_holding_days(self):
        """
        计算平均持仓天数。

        Returns:
            float: 平均持仓天数
        """
        buy_trades = [t for t in self._trades if t["action"] == "buy"]
        sell_trades = [t for t in self._trades if t["action"] == "sell"]

        if not buy_trades or not sell_trades:
            return 0.0

        n_pairs = min(len(buy_trades), len(sell_trades))
        total_days = 0

        for i in range(n_pairs):
            buy_date = buy_trades[i]["date"]
            sell_date = sell_trades[i]["date"]
            try:
                from .utils import parse_date
                d1 = parse_date(buy_date)
                d2 = parse_date(sell_date)
                total_days += (d2 - d1).days
            except (ValueError, IndexError):
                continue

        if n_pairs == 0:
            return 0.0
        return round_to(total_days / n_pairs)

    def summary_text(self):
        """
        生成分析摘要文本。

        Returns:
            str: 格式化的分析摘要
        """
        metrics = self.analyze()
        lines = [
            "=" * 60,
            "  QuantPilot 回测分析报告",
            "=" * 60,
            "",
            "-- 基本收益 --",
            "  总收益率:       {}".format(format_percent(metrics["total_return"])),
            "  年化收益率:     {}".format(format_percent(metrics["annual_return"])),
            "  最大回撤:       {}".format(format_percent(metrics["max_drawdown"])),
            "  回撤持续天数:   {} 天".format(metrics["max_drawdown_duration"]),
            "",
            "-- 风险指标 --",
            "  年化波动率:     {}".format(format_percent(metrics["volatility"])),
            "  夏普比率:       {}".format(format_number(metrics["sharpe_ratio"])),
            "  Sortino比率:    {}".format(format_number(metrics["sortino_ratio"])),
            "  Calmar比率:     {}".format(format_number(metrics["calmar_ratio"])),
            "",
            "-- 交易统计 --",
            "  交易次数:       {}".format(metrics["total_trades"]),
            "  胜率:           {}".format(format_percent(metrics["win_rate"])),
            "  盈亏比:         {}".format(format_number(metrics["profit_loss_ratio"])),
            "  最大连续盈利:   {} 次".format(metrics["max_consecutive_wins"]),
            "  最大连续亏损:   {} 次".format(metrics["max_consecutive_losses"]),
            "  平均盈利:       {}".format(format_number(metrics["avg_profit"])),
            "  平均亏损:       {}".format(format_number(metrics["avg_loss"])),
            "  总手续费:       {}".format(format_number(metrics["total_commission"])),
            "",
            "-- 资金统计 --",
            "  初始资金:       {}".format(format_number(self._initial_capital)),
            "  最终资金:       {}".format(format_number(metrics["final_capital"])),
            "  峰值资金:       {}".format(format_number(metrics["peak_capital"])),
            "  最低资金:       {}".format(format_number(metrics["min_capital"])),
            "  总盈亏:         {}".format(format_number(metrics["total_pnl"])),
            "",
            "-- 其他 --",
            "  交易天数:       {} 天".format(metrics["trading_days"]),
            "  平均持仓天数:   {:.1f} 天".format(metrics["avg_holding_days"]),
            "  月度胜率:       {}".format(format_percent(metrics["monthly_win_rate"])),
            "",
            "=" * 60,
        ]
        return "\n".join(lines)
