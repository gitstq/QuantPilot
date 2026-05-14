"""
QuantPilot 工具函数模块

提供通用的数学计算、格式化、数据转换等工具函数。
"""

import math
from datetime import datetime


def round_to(value, decimals=4):
    """
    四舍五入到指定小数位。

    Args:
        value: 数值
        decimals: 小数位数，默认4位

    Returns:
        float: 四舍五入后的数值
    """
    if value is None:
        return 0.0
    return round(float(value), decimals)


def format_percent(value, decimals=2):
    """
    将小数格式化为百分比字符串。

    Args:
        value: 小数值，如 0.15 表示 15%
        decimals: 小数位数

    Returns:
        str: 百分比字符串，如 "15.00%"
    """
    return "{:.{}f}%".format(value * 100, decimals)


def format_number(value, decimals=4):
    """
    格式化数值为字符串。

    Args:
        value: 数值
        decimals: 小数位数

    Returns:
        str: 格式化后的字符串
    """
    if value is None:
        return "N/A"
    return "{:.{}f}".format(float(value), decimals)


def mean(values):
    """
    计算算术平均值。

    数学公式: mean = (1/n) * sum(x_i)

    Args:
        values: 数值列表

    Returns:
        float: 平均值
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def std_dev(values):
    """
    计算总体标准差。

    数学公式: sigma = sqrt((1/n) * sum((x_i - mean)^2))

    Args:
        values: 数值列表

    Returns:
        float: 标准差
    """
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


def sample_std_dev(values):
    """
    计算样本标准差（无偏估计）。

    数学公式: s = sqrt((1/(n-1)) * sum((x_i - mean)^2))

    Args:
        values: 数值列表

    Returns:
        float: 样本标准差
    """
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def median(values):
    """
    计算中位数。

    Args:
        values: 数值列表

    Returns:
        float: 中位数
    """
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 1:
        return sorted_vals[n // 2]
    return (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0


def max_drawdown(values):
    """
    计算最大回撤。

    数学公式:
        MDD = max(1 - trough_i / peak_i)
        其中 peak_i 为到第i天为止的最大值，trough_i 为峰值后的最小值

    Args:
        values: 净值序列

    Returns:
        tuple: (最大回撤值, 回撤开始索引, 回撤结束索引)
    """
    if not values:
        return 0.0, 0, 0
    peak = values[0]
    max_dd = 0.0
    peak_idx = 0
    dd_start = 0
    dd_end = 0
    for i, v in enumerate(values):
        if v > peak:
            peak = v
            peak_idx = i
        dd = (peak - v) / peak if peak != 0 else 0
        if dd > max_dd:
            max_dd = dd
            dd_start = peak_idx
            dd_end = i
    return max_dd, dd_start, dd_end


def safe_divide(numerator, denominator, default=0.0):
    """
    安全除法，避免除零错误。

    Args:
        numerator: 分子
        denominator: 分母
        default: 除零时的默认返回值

    Returns:
        float: 除法结果或默认值
    """
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value, min_val, max_val):
    """
    将数值限制在指定范围内。

    Args:
        value: 输入值
        min_val: 最小值
        max_val: 最大值

    Returns:
        float: 限制后的值
    """
    return max(min_val, min(value, max_val))


def parse_date(date_str):
    """
    解析日期字符串。

    支持格式: YYYY-MM-DD, YYYY/MM/DD, YYYYMMDD

    Args:
        date_str: 日期字符串

    Returns:
        datetime: 日期对象

    Raises:
        ValueError: 日期格式不支持时
    """
    date_str = str(date_str).strip()
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(
        "不支持的日期格式: '{}'，请使用 YYYY-MM-DD 格式".format(date_str)
    )


def date_to_str(dt, fmt="%Y-%m-%d"):
    """
    将日期对象格式化为字符串。

    Args:
        dt: datetime 对象
        fmt: 格式字符串

    Returns:
        str: 格式化后的日期字符串
    """
    if isinstance(dt, str):
        return dt
    return dt.strftime(fmt)


def trading_days_per_year():
    """
    获取每年交易日数量（A股标准）。

    Returns:
        int: 每年交易日数量，默认242
    """
    return 242


def annualize_return(total_return, n_days):
    """
    将总收益率年化。

    数学公式:
        年化收益率 = (1 + total_return) ^ (252 / n_days) - 1

    Args:
        total_return: 总收益率（小数形式）
        n_days: 交易天数

    Returns:
        float: 年化收益率
    """
    if n_days <= 0:
        return 0.0
    try:
        return (1 + total_return) ** (trading_days_per_year() / n_days) - 1
    except (ValueError, OverflowError):
        return 0.0
