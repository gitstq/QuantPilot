"""
QuantPilot 数据管理模块

提供K线数据结构、CSV导入/导出、数据验证、日期处理等功能。
"""

import csv
import os
from datetime import datetime

from .utils import parse_date, date_to_str


class KLine:
    """
    K线数据结构（单根K线）。

    属性:
        date: 交易日期 (str, YYYY-MM-DD)
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        amount: 成交额（可选）
    """

    def __init__(self, date, open_price, high, low, close, volume, amount=0.0):
        """
        初始化K线数据。

        Args:
            date: 交易日期
            open_price: 开盘价
            high: 最高价
            low: 最低价
            close: 收盘价
            volume: 成交量
            amount: 成交额，默认0
        """
        self.date = str(date)
        self.open = float(open_price)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.volume = float(volume)
        self.amount = float(amount)

    def to_dict(self):
        """将K线转换为字典。"""
        return {
            "date": self.date,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "amount": self.amount,
        }

    def __repr__(self):
        return (
            "KLine(date={}, O={}, H={}, L={}, C={}, V={})".format(
                self.date, self.open, self.high, self.low, self.close, self.volume
            )
        )

    def __eq__(self, other):
        if not isinstance(other, KLine):
            return False
        return (
            self.date == other.date
            and self.open == other.open
            and self.high == other.high
            and self.low == other.low
            and self.close == other.close
            and self.volume == other.volume
        )


class KLineData:
    """
    K线数据序列，支持导入、导出、验证和基本操作。
    """

    def __init__(self):
        """初始化空的K线数据序列。"""
        self._data = []

    @property
    def data(self):
        """获取K线数据列表。"""
        return self._data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]

    def __iter__(self):
        return iter(self._data)

    def append(self, kline):
        """
        追加一根K线数据。

        Args:
            kline: KLine 对象

        Raises:
            TypeError: 如果不是 KLine 对象
        """
        if not isinstance(kline, KLine):
            raise TypeError("只能追加 KLine 对象")
        self._data.append(kline)

    def extend(self, klines):
        """
        批量追加K线数据。

        Args:
            klines: KLine 对象列表
        """
        for kline in klines:
            self.append(kline)

    def get_dates(self):
        """获取所有日期列表。"""
        return [k.date for k in self._data]

    def get_closes(self):
        """获取所有收盘价列表。"""
        return [k.close for k in self._data]

    def get_opens(self):
        """获取所有开盘价列表。"""
        return [k.open for k in self._data]

    def get_highs(self):
        """获取所有最高价列表。"""
        return [k.high for k in self._data]

    def get_lows(self):
        """获取所有最低价列表。"""
        return [k.low for k in self._data]

    def get_volumes(self):
        """获取所有成交量列表。"""
        return [k.volume for k in self._data]

    def get_amounts(self):
        """获取所有成交额列表。"""
        return [k.amount for k in self._data]

    def slice_by_range(self, start_date, end_date):
        """
        按日期范围截取数据。

        Args:
            start_date: 起始日期 (str)
            end_date: 结束日期 (str)

        Returns:
            KLineData: 截取后的数据
        """
        result = KLineData()
        for kline in self._data:
            if start_date <= kline.date <= end_date:
                result.append(kline)
        return result

    def sort_by_date(self):
        """按日期升序排列。"""
        self._data.sort(key=lambda k: k.date)

    def validate(self):
        """
        验证K线数据的完整性和合理性。

        Returns:
            list: 错误信息列表，空列表表示无错误
        """
        errors = []
        if not self._data:
            errors.append("数据为空")
            return errors

        for i, kline in enumerate(self._data):
            # 验证价格合理性
            if kline.high < kline.low:
                errors.append(
                    "第{}条: 最高价({})低于最低价({})".format(
                        i + 1, kline.high, kline.low
                    )
                )
            if kline.open < 0 or kline.close < 0:
                errors.append("第{}条: 价格不能为负数".format(i + 1))
            if kline.volume < 0:
                errors.append("第{}条: 成交量不能为负数".format(i + 1))
            # 验证日期格式
            try:
                parse_date(kline.date)
            except ValueError:
                errors.append("第{}条: 日期格式错误 '{}'".format(i + 1, kline.date))

        # 验证日期连续性（仅警告）
        if len(self._data) > 1:
            dates = self.get_dates()
            for i in range(1, len(dates)):
                if dates[i] <= dates[i - 1]:
                    errors.append(
                        "日期非递增: 第{}条({}) <= 第{}条({})".format(
                            i, dates[i], i + 1, dates[i - 1]
                        )
                    )

        return errors

    @classmethod
    def from_csv(cls, filepath, delimiter=",", has_header=True):
        """
        从CSV文件导入K线数据。

        支持的列名（不区分大小写）:
        date, open, high, low, close, volume, amount
        也支持中文列名: 日期, 开盘, 最高, 最低, 收盘, 成交量, 成交额

        Args:
            filepath: CSV文件路径
            delimiter: 分隔符，默认逗号
            has_header: 是否有表头，默认True

        Returns:
            KLineData: K线数据对象

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 数据格式错误
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError("文件不存在: {}".format(filepath))

        kline_data = cls()

        # 列名映射
        col_map = {
            "date": "date",
            "日期": "date",
            "open": "open",
            "开盘": "open",
            "开盘价": "open",
            "high": "high",
            "最高": "high",
            "最高价": "high",
            "low": "low",
            "最低": "low",
            "最低价": "low",
            "close": "close",
            "收盘": "close",
            "收盘价": "close",
            "volume": "volume",
            "成交量": "volume",
            "vol": "volume",
            "amount": "amount",
            "成交额": "amount",
            "turnover": "amount",
        }

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)

        if not rows:
            raise ValueError("CSV文件为空")

        start_row = 0
        col_indices = {}

        if has_header:
            header = [h.strip().lower() for h in rows[0]]
            for i, h in enumerate(header):
                if h in col_map:
                    col_indices[col_map[h]] = i
            start_row = 1

        # 如果没有找到列名，尝试按位置映射
        if not col_indices and not has_header:
            col_indices = {"date": 0, "open": 1, "high": 2, "low": 3, "close": 4, "volume": 5}

        required = ["date", "open", "high", "low", "close"]
        for req in required:
            if req not in col_indices:
                raise ValueError(
                    "CSV文件缺少必要列: '{}'。请确保包含 date, open, high, low, close 列".format(
                        req
                    )
                )

        for row_idx, row in enumerate(rows[start_row:], start=start_row + 1):
            if not row or all(cell.strip() == "" for cell in row):
                continue
            try:
                date_val = row[col_indices["date"]].strip()
                open_val = float(row[col_indices["open"]])
                high_val = float(row[col_indices["high"]])
                low_val = float(row[col_indices["low"]])
                close_val = float(row[col_indices["close"]])
                volume_val = float(row[col_indices.get("volume", 5)]) if "volume" in col_indices else 0.0
                amount_val = (
                    float(row[col_indices["amount"]]) if "amount" in col_indices else 0.0
                )

                kline = KLine(
                    date=date_val,
                    open_price=open_val,
                    high=high_val,
                    low=low_val,
                    close=close_val,
                    volume=volume_val,
                    amount=amount_val,
                )
                kline_data.append(kline)
            except (IndexError, ValueError) as e:
                raise ValueError("第{}行数据格式错误: {}".format(row_idx, e))

        kline_data.sort_by_date()
        return kline_data

    def to_csv(self, filepath, delimiter=","):
        """
        将K线数据导出为CSV文件。

        Args:
            filepath: 输出文件路径
            delimiter: 分隔符，默认逗号
        """
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(["date", "open", "high", "low", "close", "volume", "amount"])
            for kline in self._data:
                writer.writerow([
                    kline.date,
                    kline.open,
                    kline.high,
                    kline.low,
                    kline.close,
                    kline.volume,
                    kline.amount,
                ])

    @classmethod
    def from_list(cls, data_list):
        """
        从字典列表创建KLineData。

        Args:
            data_list: 字典列表，每个字典包含 date, open, high, low, close, volume 等键

        Returns:
            KLineData: K线数据对象
        """
        kline_data = cls()
        for item in data_list:
            kline = KLine(
                date=item["date"],
                open_price=item.get("open", item.get("open_price", 0)),
                high=item.get("high", 0),
                low=item.get("low", 0),
                close=item.get("close", 0),
                volume=item.get("volume", 0),
                amount=item.get("amount", 0),
            )
            kline_data.append(kline)
        kline_data.sort_by_date()
        return kline_data

    def summary(self):
        """
        获取数据摘要信息。

        Returns:
            dict: 包含数据统计信息的字典
        """
        if not self._data:
            return {"count": 0}

        closes = self.get_closes()
        volumes = self.get_volumes()
        dates = self.get_dates()

        return {
            "count": len(self._data),
            "start_date": dates[0],
            "end_date": dates[-1],
            "first_close": closes[0],
            "last_close": closes[-1],
            "max_close": max(closes),
            "min_close": min(closes),
            "avg_volume": sum(volumes) / len(volumes),
            "total_volume": sum(volumes),
        }

    def generate_sample_data(self, n_days=250, start_price=100.0, volatility=0.02):
        """
        生成模拟K线数据用于测试。

        使用几何布朗运动模型生成随机价格序列。

        Args:
            n_days: 生成天数，默认250
            start_price: 起始价格，默认100
            volatility: 日波动率，默认0.02

        Returns:
            KLineData: 模拟K线数据
        """
        import random

        random.seed(42)
        self._data = []
        price = start_price
        base_date = datetime(2024, 1, 2)

        for i in range(n_days):
            # 跳过周末
            current_date = base_date
            days_added = 0
            while days_added <= i:
                current_date += __import__("datetime").timedelta(days=1)
                if current_date.weekday() < 5:
                    days_added += 1

            # 几何布朗运动
            drift = 0.0002  # 微弱上涨趋势
            shock = random.gauss(0, volatility)
            price = price * math.exp(drift + shock)

            # 生成OHLC
            day_volatility = volatility * price
            open_price = price * (1 + random.gauss(0, volatility * 0.3))
            high = max(open_price, price) + abs(random.gauss(0, day_volatility * 0.5))
            low = min(open_price, price) - abs(random.gauss(0, day_volatility * 0.5))
            high = max(high, open_price, price)
            low = min(low, open_price, price)
            volume = random.randint(100000, 5000000)

            kline = KLine(
                date=current_date.strftime("%Y-%m-%d"),
                open_price=round(open_price, 2),
                high=round(high, 2),
                low=round(low, 2),
                close=round(price, 2),
                volume=volume,
            )
            self._data.append(kline)

        return self


# 需要在 generate_sample_data 中使用
import math
