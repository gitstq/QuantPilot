"""
QuantPilot TUI仪表板模块

提供终端交互式界面，使用ASCII字符绘制:
    - K线图
    - 净值曲线
    - 指标图表（柱状图、折线图）
    - 回测结果仪表板
"""

from .utils import format_percent, format_number


class ASCIIGraph:
    """
    ASCII图表绘制器。

    使用ASCII字符在终端中绘制各种图表。
    """

    # 图表字符
    BLOCK_FULL = "\u2588"       # 全块
    BLOCK_3_4 = "\u2593"        # 3/4块
    BLOCK_1_2 = "\u2592"        # 1/2块
    BLOCK_1_4 = "\u2591"        # 1/4块
    BAR_UP = "\u2580"           # 上半块
    BAR_DOWN = "\u2584"         # 下半块
    LINE_H = "\u2500"           # 水平线
    LINE_V = "\u2502"           # 垂直线
    LINE_CROSS = "\u253C"       # 十字
    DOT = "\u00B7"              # 点

    @staticmethod
    def draw_line_chart(values, width=80, height=20, title="", labels=None):
        """
        绘制ASCII折线图。

        Args:
            values: 数值列表
            width: 图表宽度，默认80
            height: 图表高度，默认20
            title: 图表标题
            labels: 底部标签列表

        Returns:
            str: ASCII折线图字符串
        """
        if not values:
            return "(无数据)"

        # 过滤None值
        valid_pairs = [(i, v) for i, v in enumerate(values) if v is not None]
        if not valid_pairs:
            return "(无有效数据)"

        valid_indices = [p[0] for p in valid_pairs]
        valid_values = [p[1] for p in valid_pairs]

        min_val = min(valid_values)
        max_val = max(valid_values)

        if max_val == min_val:
            max_val = min_val + 1

        val_range = max_val - min_val

        # 创建画布
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        # 绘制边框
        for x in range(width):
            canvas[height - 1][x] = ASCIIGraph.LINE_H
        for y in range(height):
            canvas[y][0] = ASCIIGraph.LINE_V

        # 绘制Y轴刻度
        for i in range(5):
            y = int((height - 2) * i / 4)
            val = max_val - (val_range * i / 4)
            label = "{:.2f}".format(val)
            for j, ch in enumerate(label[:8]):
                if j < width:
                    canvas[y][j + 1] = ch

        # 绘制数据点
        n = len(valid_values)
        for i, val in enumerate(valid_values):
            x = int((width - 1) * i / max(n - 1, 1))
            x = min(x, width - 1)
            y_ratio = (val - min_val) / val_range
            y = int((height - 2) * (1 - y_ratio))
            y = max(0, min(y, height - 2))

            if 0 <= x < width and 0 <= y < height:
                canvas[y][x] = ASCIIGraph.BLOCK_FULL

        # 构建输出
        lines = []
        if title:
            lines.append("  " + title)
            lines.append("")

        for row in canvas:
            lines.append("  " + "".join(row))

        # 底部标签
        if labels and len(labels) > 0:
            label_line = "  "
            step = max(1, len(labels) // 5)
            for i in range(0, len(labels), step):
                label_line += "{:<16}".format(str(labels[i])[:16])
            lines.append(label_line)

        return "\n".join(lines)

    @staticmethod
    def draw_bar_chart(values, width=80, height=15, title="", labels=None):
        """
        绘制ASCII柱状图。

        Args:
            values: 数值列表
            width: 图表宽度，默认80
            height: 图表高度，默认15
            title: 图表标题
            labels: 底部标签列表

        Returns:
            str: ASCII柱状图字符串
        """
        if not values:
            return "(无数据)"

        max_val = max(abs(v) for v in values) if values else 1
        if max_val == 0:
            max_val = 1

        # 计算每根柱子的宽度
        bar_width = max(1, (width - 10) // max(len(values), 1))
        bar_width = min(bar_width, 8)

        lines = []
        if title:
            lines.append("  " + title)
            lines.append("")

        # 绘制柱子（从上到下）
        for row in range(height, 0, -1):
            threshold = max_val * row / height
            line = "  {:>10.2f} |".format(threshold)
            for val in values:
                if val >= 0:
                    if val >= threshold:
                        line += ASCIIGraph.BLOCK_FULL * bar_width
                    else:
                        line += " " * bar_width
                else:
                    if abs(val) >= threshold:
                        line += ASCIIGraph.BLOCK_FULL * bar_width
                    else:
                        line += " " * bar_width
                line += " "
            lines.append(line)

        # 零轴
        lines.append("  {:>10} |{}|".format("0", ASCIIGraph.LINE_H * (bar_width + 1) * len(values)))

        # 底部标签
        if labels:
            label_line = "  " + " " * 12 + "|"
            for i, label in enumerate(labels):
                lbl = str(label)[:bar_width]
                label_line += lbl.center(bar_width) + " "
            lines.append(label_line)

        return "\n".join(lines)

    @staticmethod
    def draw_kline(opens, highs, lows, closes, width=80, height=20, title=""):
        """
        绘制ASCII K线图。

        使用Unicode字符绘制简化版K线图:
        - 阳线（收涨）: 使用上半块字符
        - 阴线（收跌）: 使用下半块字符

        Args:
            opens: 开盘价列表
            highs: 最高价列表
            lows: 最低价列表
            closes: 收盘价列表
            width: 图表宽度，默认80
            height: 图表高度，默认20
            title: 图表标题

        Returns:
            str: ASCII K线图字符串
        """
        n = len(closes)
        if n == 0:
            return "(无数据)"

        all_prices = highs + lows
        min_price = min(all_prices)
        max_price = max(all_prices)

        if max_price == min_price:
            max_price = min_price + 1

        price_range = max_price - min_price

        # 创建画布
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        # 计算每根K线的列宽
        col_width = max(1, width // n)
        col_width = min(col_width, 4)

        for i in range(n):
            col = min(i * col_width, width - 1)

            # 将价格映射到行
            def price_to_row(price):
                ratio = (price - min_price) / price_range
                return int((height - 1) * (1 - ratio))

            high_row = price_to_row(highs[i])
            low_row = price_to_row(lows[i])
            open_row = price_to_row(opens[i])
            close_row = price_to_row(closes[i])

            high_row = max(0, min(high_row, height - 1))
            low_row = max(0, min(low_row, height - 1))
            open_row = max(0, min(open_row, height - 1))
            close_row = max(0, min(close_row, height - 1))

            is_up = closes[i] >= opens[i]

            # 绘制影线
            for row in range(min(high_row, low_row), max(high_row, low_row) + 1):
                if 0 <= row < height and 0 <= col < width:
                    canvas[row][col] = "|" if is_up else "!"

            # 绘制实体
            body_top = min(open_row, close_row)
            body_bottom = max(open_row, close_row)

            for row in range(body_top, body_bottom + 1):
                if 0 <= row < height:
                    for c in range(col, min(col + col_width, width)):
                        if is_up:
                            canvas[row][c] = ASCIIGraph.BLOCK_FULL
                        else:
                            canvas[row][c] = ASCIIGraph.LINE_H

        # 构建输出
        lines = []
        if title:
            lines.append("  " + title)
            lines.append("")

        for row_idx, row in enumerate(canvas):
            # Y轴标签
            price = max_price - price_range * row_idx / (height - 1)
            label = "{:>10.2f}".format(price)
            lines.append(label + "|" + "".join(row))

        return "\n".join(lines)


class TUIDashboard:
    """
    TUI仪表板。

    整合回测结果，以终端交互式界面展示。
    """

    def __init__(self, backtest_result):
        """
        初始化TUI仪表板。

        Args:
            backtest_result: BacktestEngine.run() 返回的结果字典
        """
        self.result = backtest_result
        self._daily_values = backtest_result["daily_values"]
        self._trades = backtest_result["trades"]

    def show_dashboard(self):
        """
        显示完整的TUI仪表板。

        Returns:
            str: 仪表板文本
        """
        sections = [
            self._header(),
            self._metrics_panel(),
            self._equity_curve(),
            self._drawdown_chart(),
            self._monthly_returns_chart(),
            self._recent_trades(),
        ]
        return "\n\n".join(s for s in sections if s)

    def _header(self):
        """生成仪表板头部。"""
        lines = [
            "=" * 80,
            "  QuantPilot TUI Dashboard",
            "  Strategy: {} | Period: {} ~ {}".format(
                self.result["strategy_name"],
                self.result["data_summary"].get("start_date", "N/A"),
                self.result["data_summary"].get("end_date", "N/A"),
            ),
            "=" * 80,
        ]
        return "\n".join(lines)

    def _metrics_panel(self):
        """生成指标面板。"""
        from .analyzer import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer(self.result)
        m = analyzer.analyze()

        lines = [
            "+------------------+------------------+------------------+------------------+",
            "| 总收益率         | 年化收益率       | 最大回撤         | 夏普比率         |",
            "| {:>14} | {:>14} | {:>14} | {:>14} |".format(
                format_percent(m["total_return"]),
                format_percent(m["annual_return"]),
                format_percent(m["max_drawdown"]),
                format_number(m["sharpe_ratio"]),
            ),
            "+------------------+------------------+------------------+------------------+",
            "| 交易次数         | 胜率             | 盈亏比           | 总盈亏           |",
            "| {:>14} | {:>14} | {:>14} | {:>14} |".format(
                m["total_trades"],
                format_percent(m["win_rate"]),
                format_number(m["profit_loss_ratio"]),
                format_number(m["total_pnl"]),
            ),
            "+------------------+------------------+------------------+------------------+",
        ]
        return "\n".join(lines)

    def _equity_curve(self):
        """生成净值曲线图。"""
        if not self._daily_values:
            return ""

        values = [dv["total_assets"] for dv in self._daily_values]
        dates = [dv["date"] for dv in self._daily_values]

        # 采样以适应宽度
        max_points = 80
        if len(values) > max_points:
            step = len(values) // max_points
            sampled_values = values[::step]
            sampled_dates = dates[::step]
        else:
            sampled_values = values
            sampled_dates = dates

        chart = ASCIIGraph.draw_line_chart(
            sampled_values,
            width=76,
            height=16,
            title="[ Net Asset Value Curve ]",
            labels=sampled_dates,
        )
        return chart

    def _drawdown_chart(self):
        """生成回撤图。"""
        if not self._daily_values:
            return ""

        values = [dv["total_assets"] for dv in self._daily_values]
        peak = values[0]
        drawdowns = []
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak if peak != 0 else 0
            drawdowns.append(-dd)  # 负数表示回撤

        # 采样
        max_points = 80
        if len(drawdowns) > max_points:
            step = len(drawdowns) // max_points
            sampled_dd = drawdowns[::step]
        else:
            sampled_dd = drawdowns

        chart = ASCIIGraph.draw_bar_chart(
            sampled_dd,
            width=76,
            height=10,
            title="[ Drawdown ]",
        )
        return chart

    def _monthly_returns_chart(self):
        """生成月度收益柱状图。"""
        from .analyzer import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer(self.result)
        m = analyzer.analyze()
        monthly = m["monthly_returns"]

        if not monthly:
            return ""

        months = sorted(monthly.keys())
        returns = [monthly[month] for month in months]

        chart = ASCIIGraph.draw_bar_chart(
            returns,
            width=76,
            height=12,
            title="[ Monthly Returns ]",
            labels=months,
        )
        return chart

    def _recent_trades(self):
        """显示最近交易记录。"""
        if not self._trades:
            return "  (无交易记录)"

        recent = self._trades[-10:]  # 最近10笔

        lines = [
            "  [ Recent Trades ]",
            "  {:<12} {:<6} {:>10} {:>8} {:>10} {:>12} {:<10}".format(
                "Date", "Action", "Price", "Qty", "Commission", "PnL", "Reason"
            ),
            "  " + "-" * 74,
        ]

        for t in recent:
            action = "BUY" if t["action"] == "buy" else "SELL"
            pnl = t.get("pnl", 0)
            pnl_str = format_number(pnl) if pnl != 0 else "-"
            lines.append(
                "  {:<12} {:<6} {:>10} {:>8} {:>10} {:>12} {:<10}".format(
                    t["date"],
                    action,
                    format_number(t["price"]),
                    t["quantity"],
                    format_number(t["commission"]),
                    pnl_str,
                    t.get("reason", "")[:10],
                )
            )

        return "\n".join(lines)

    def show_kline_chart(self, kline_data, start=0, count=60):
        """
        显示K线图。

        Args:
            kline_data: KLineData 对象
            start: 起始索引
            count: 显示数量

        Returns:
            str: K线图文本
        """
        end = min(start + count, len(kline_data))
        if start >= len(kline_data):
            return "(无数据)"

        opens = [kline_data[i].open for i in range(start, end)]
        highs = [kline_data[i].high for i in range(start, end)]
        lows = [kline_data[i].low for i in range(start, end)]
        closes = [kline_data[i].close for i in range(start, end)]
        dates = [kline_data[i].date for i in range(start, end)]

        chart = ASCIIGraph.draw_kline(
            opens, highs, lows, closes,
            width=76, height=20,
            title="[ K-Line Chart: {} ~ {} ]".format(dates[0], dates[-1]),
        )

        return chart

    def show_indicator_chart(self, values, title="", indicator_name=""):
        """
        显示指标图表。

        Args:
            values: 指标值列表
            title: 图表标题
            indicator_name: 指标名称

        Returns:
            str: 指标图表文本
        """
        valid_values = [v if v is not None else 0 for v in values]

        chart = ASCIIGraph.draw_line_chart(
            valid_values,
            width=76,
            height=12,
            title=title or "[ {} ]".format(indicator_name),
        )
        return chart
