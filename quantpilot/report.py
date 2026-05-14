"""
QuantPilot 报告生成器模块

支持多种格式的报告输出:
    - 终端表格报告
    - JSON报告
    - HTML报告（内嵌CSS样式）
    - Markdown报告
"""

import json
import os
from datetime import datetime

from .analyzer import PerformanceAnalyzer
from .utils import format_percent, format_number


class ReportGenerator:
    """
    报告生成器。

    根据回测结果和分析指标生成多种格式的报告。
    """

    def __init__(self, backtest_result):
        """
        初始化报告生成器。

        Args:
            backtest_result: BacktestEngine.run() 返回的结果字典
        """
        self.result = backtest_result
        self.analyzer = PerformanceAnalyzer(backtest_result)
        self._metrics = self.analyzer.analyze()

    def generate_terminal(self):
        """
        生成终端表格报告。

        Returns:
            str: 终端格式报告文本
        """
        return self.analyzer.summary_text()

    def generate_json(self, filepath=None):
        """
        生成JSON报告。

        Args:
            filepath: 输出文件路径，为None时不写入文件

        Returns:
            str: JSON格式报告字符串
        """
        report_data = {
            "report_title": "QuantPilot 回测报告",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "strategy": {
                "name": self.result["strategy_name"],
                "description": self.result["strategy_desc"],
            },
            "data_info": self.result["data_summary"],
            "config": self.result["config"],
            "performance": {
                "total_return": self._metrics["total_return"],
                "annual_return": self._metrics["annual_return"],
                "max_drawdown": self._metrics["max_drawdown"],
                "max_drawdown_duration": self._metrics["max_drawdown_duration"],
                "volatility": self._metrics["volatility"],
                "sharpe_ratio": self._metrics["sharpe_ratio"],
                "sortino_ratio": self._metrics["sortino_ratio"],
                "calmar_ratio": self._metrics["calmar_ratio"],
            },
            "trading_stats": {
                "total_trades": self._metrics["total_trades"],
                "win_rate": self._metrics["win_rate"],
                "profit_loss_ratio": self._metrics["profit_loss_ratio"],
                "max_consecutive_wins": self._metrics["max_consecutive_wins"],
                "max_consecutive_losses": self._metrics["max_consecutive_losses"],
                "avg_profit": self._metrics["avg_profit"],
                "avg_loss": self._metrics["avg_loss"],
                "total_commission": self._metrics["total_commission"],
                "total_pnl": self._metrics["total_pnl"],
                "avg_holding_days": self._metrics["avg_holding_days"],
            },
            "capital": {
                "initial_capital": self.result["config"]["initial_capital"],
                "final_capital": self._metrics["final_capital"],
                "peak_capital": self._metrics["peak_capital"],
                "min_capital": self._metrics["min_capital"],
            },
            "monthly_returns": self._metrics["monthly_returns"],
            "trades": self.result["trades"],
        }

        json_str = json.dumps(report_data, indent=2, ensure_ascii=False, default=str)

        if filepath:
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)

        return json_str

    def generate_html(self, filepath=None):
        """
        生成HTML报告（内嵌CSS样式，美观专业）。

        Args:
            filepath: 输出文件路径，为None时不写入文件

        Returns:
            str: HTML格式报告字符串
        """
        m = self._metrics
        trades = self.result["trades"]

        # 构建交易记录表格行
        trade_rows = ""
        for t in trades:
            pnl_class = "profit" if t.get("pnl", 0) > 0 else ("loss" if t.get("pnl", 0) < 0 else "")
            action_class = "buy" if t["action"] == "buy" else "sell"
            action_text = "买入" if t["action"] == "buy" else "卖出"
            trade_rows += (
                '<tr class="%s">'
                '<td>%s</td>'
                '<td class="%s">%s</td>'
                '<td>%s</td>'
                '<td>%s</td>'
                '<td>%s</td>'
                '<td class="%s">%s</td>'
                '</tr>\n'
            ) % (
                pnl_class,
                t["date"],
                action_class, action_text,
                format_number(t["price"]),
                t["quantity"],
                format_number(t["commission"]),
                pnl_class,
                format_number(t.get("pnl", 0)),
            )

        # 构建月度收益表格行
        monthly_rows = ""
        monthly = m["monthly_returns"]
        for month, ret in sorted(monthly.items()):
            ret_class = "profit" if ret > 0 else ("loss" if ret < 0 else "")
            monthly_rows += (
                '<tr class="%s"><td>%s</td><td class="%s">%s</td></tr>\n'
            ) % (ret_class, month, ret_class, format_percent(ret))

        # 收益率颜色
        total_ret_class = "profit" if m["total_return"] > 0 else ("loss" if m["total_return"] < 0 else "")
        ann_ret_class = "profit" if m["annual_return"] > 0 else ("loss" if m["annual_return"] < 0 else "")
        sharpe_class = "profit" if m["sharpe_ratio"] > 1 else ("loss" if m["sharpe_ratio"] < 0 else "neutral")
        sortino_class = "profit" if m["sortino_ratio"] > 1 else ("loss" if m["sortino_ratio"] < 0 else "neutral")
        calmar_class = "profit" if m["calmar_ratio"] > 1 else ("loss" if m["calmar_ratio"] < 0 else "neutral")
        win_class = "profit" if m["win_rate"] > 0.5 else ("loss" if m["win_rate"] < 0.3 else "neutral")
        pnl_class = "profit" if m["total_pnl"] > 0 else ("loss" if m["total_pnl"] < 0 else "neutral")
        final_class = "profit" if m["final_capital"] >= self.result["config"]["initial_capital"] else "loss"

        stop_loss_str = format_percent(self.result["config"]["stop_loss"]) if self.result["config"]["stop_loss"] else "未设置"
        take_profit_str = format_percent(self.result["config"]["take_profit"]) if self.result["config"]["take_profit"] else "未设置"

        html_parts = []
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="zh-CN">')
        html_parts.append('<head>')
        html_parts.append('    <meta charset="UTF-8">')
        html_parts.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append('    <title>QuantPilot 回测报告</title>')
        html_parts.append('    <style>')
        html_parts.append('        * { margin: 0; padding: 0; box-sizing: border-box; }')
        html_parts.append('        body {')
        html_parts.append('            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;')
        html_parts.append('            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);')
        html_parts.append('            color: #e0e0e0;')
        html_parts.append('            min-height: 100vh;')
        html_parts.append('            padding: 20px;')
        html_parts.append('        }')
        html_parts.append('        .container { max-width: 1200px; margin: 0 auto; }')
        html_parts.append('        .header {')
        html_parts.append('            text-align: center;')
        html_parts.append('            padding: 40px 20px;')
        html_parts.append('            background: rgba(255,255,255,0.05);')
        html_parts.append('            border-radius: 16px;')
        html_parts.append('            margin-bottom: 24px;')
        html_parts.append('            backdrop-filter: blur(10px);')
        html_parts.append('            border: 1px solid rgba(255,255,255,0.1);')
        html_parts.append('        }')
        html_parts.append('        .header h1 {')
        html_parts.append('            font-size: 2.5em;')
        html_parts.append('            background: linear-gradient(90deg, #00d2ff, #3a7bd5);')
        html_parts.append('            -webkit-background-clip: text;')
        html_parts.append('            -webkit-text-fill-color: transparent;')
        html_parts.append('            margin-bottom: 8px;')
        html_parts.append('        }')
        html_parts.append('        .header .subtitle { color: #8899aa; font-size: 1em; }')
        html_parts.append('        .header .meta { color: #667788; font-size: 0.85em; margin-top: 12px; }')
        html_parts.append('        .card {')
        html_parts.append('            background: rgba(255,255,255,0.05);')
        html_parts.append('            border-radius: 12px;')
        html_parts.append('            padding: 24px;')
        html_parts.append('            margin-bottom: 20px;')
        html_parts.append('            backdrop-filter: blur(10px);')
        html_parts.append('            border: 1px solid rgba(255,255,255,0.08);')
        html_parts.append('        }')
        html_parts.append('        .card h2 {')
        html_parts.append('            font-size: 1.3em;')
        html_parts.append('            color: #00d2ff;')
        html_parts.append('            margin-bottom: 16px;')
        html_parts.append('            padding-bottom: 8px;')
        html_parts.append('            border-bottom: 1px solid rgba(0,210,255,0.2);')
        html_parts.append('        }')
        html_parts.append('        .metrics-grid {')
        html_parts.append('            display: grid;')
        html_parts.append('            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));')
        html_parts.append('            gap: 16px;')
        html_parts.append('        }')
        html_parts.append('        .metric-item {')
        html_parts.append('            background: rgba(255,255,255,0.03);')
        html_parts.append('            border-radius: 8px;')
        html_parts.append('            padding: 16px;')
        html_parts.append('            text-align: center;')
        html_parts.append('            border: 1px solid rgba(255,255,255,0.05);')
        html_parts.append('        }')
        html_parts.append('        .metric-item .label { color: #8899aa; font-size: 0.85em; margin-bottom: 6px; }')
        html_parts.append('        .metric-item .value { font-size: 1.5em; font-weight: 600; }')
        html_parts.append('        .metric-item .value.profit { color: #00e676; }')
        html_parts.append('        .metric-item .value.loss { color: #ff5252; }')
        html_parts.append('        .metric-item .value.neutral { color: #ffd740; }')
        html_parts.append('        table { width: 100%; border-collapse: collapse; font-size: 0.9em; }')
        html_parts.append('        th {')
        html_parts.append('            background: rgba(0,210,255,0.1);')
        html_parts.append('            color: #00d2ff;')
        html_parts.append('            padding: 10px 12px;')
        html_parts.append('            text-align: left;')
        html_parts.append('            font-weight: 600;')
        html_parts.append('            border-bottom: 2px solid rgba(0,210,255,0.2);')
        html_parts.append('        }')
        html_parts.append('        td { padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }')
        html_parts.append('        tr:hover { background: rgba(255,255,255,0.03); }')
        html_parts.append('        .profit { color: #00e676; }')
        html_parts.append('        .loss { color: #ff5252; }')
        html_parts.append('        .buy { color: #40c4ff; }')
        html_parts.append('        .sell { color: #ff8a65; }')
        html_parts.append('        .strategy-info { display: flex; gap: 20px; flex-wrap: wrap; }')
        html_parts.append('        .strategy-info .item {')
        html_parts.append('            background: rgba(255,255,255,0.03);')
        html_parts.append('            padding: 12px 20px;')
        html_parts.append('            border-radius: 8px;')
        html_parts.append('            border: 1px solid rgba(255,255,255,0.05);')
        html_parts.append('        }')
        html_parts.append('        .strategy-info .item .label { color: #8899aa; font-size: 0.8em; }')
        html_parts.append('        .strategy-info .item .value { color: #e0e0e0; font-size: 1.1em; margin-top: 4px; }')
        html_parts.append('        .footer { text-align: center; padding: 20px; color: #556677; font-size: 0.8em; }')
        html_parts.append('        @media (max-width: 768px) {')
        html_parts.append('            .metrics-grid { grid-template-columns: repeat(2, 1fr); }')
        html_parts.append('            .header h1 { font-size: 1.8em; }')
        html_parts.append('        }')
        html_parts.append('    </style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        html_parts.append('    <div class="container">')

        # Header
        html_parts.append('        <div class="header">')
        html_parts.append('            <h1>QuantPilot 回测报告</h1>')
        html_parts.append('            <div class="subtitle">%s - %s</div>' % (self.result["strategy_name"], self.result["strategy_desc"]))
        html_parts.append('            <div class="meta">')
        html_parts.append('                报告生成时间: %s | 数据区间: %s ~ %s | 交易天数: %d 天' % (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.result["data_summary"].get("start_date", "N/A"),
            self.result["data_summary"].get("end_date", "N/A"),
            m["trading_days"],
        ))
        html_parts.append('            </div>')
        html_parts.append('        </div>')

        # Strategy Info
        html_parts.append('        <div class="card"><h2>策略信息</h2><div class="strategy-info">')
        html_parts.append('            <div class="item"><div class="label">策略名称</div><div class="value">%s</div></div>' % self.result["strategy_name"])
        html_parts.append('            <div class="item"><div class="label">初始资金</div><div class="value">%s</div></div>' % ("{:,.2f}".format(self.result["config"]["initial_capital"])))
        html_parts.append('            <div class="item"><div class="label">手续费率</div><div class="value">%s</div></div>' % format_percent(self.result["config"]["commission_rate"]))
        html_parts.append('            <div class="item"><div class="label">滑点</div><div class="value">%s</div></div>' % self.result["config"]["slippage"])
        html_parts.append('            <div class="item"><div class="label">止损</div><div class="value">%s</div></div>' % stop_loss_str)
        html_parts.append('            <div class="item"><div class="label">止盈</div><div class="value">%s</div></div>' % take_profit_str)
        html_parts.append('        </div></div>')

        # Performance Metrics
        html_parts.append('        <div class="card"><h2>收益指标</h2><div class="metrics-grid">')
        html_parts.append('            <div class="metric-item"><div class="label">总收益率</div><div class="value %s">%s</div></div>' % (total_ret_class, format_percent(m["total_return"])))
        html_parts.append('            <div class="metric-item"><div class="label">年化收益率</div><div class="value %s">%s</div></div>' % (ann_ret_class, format_percent(m["annual_return"])))
        html_parts.append('            <div class="metric-item"><div class="label">最大回撤</div><div class="value loss">%s</div></div>' % format_percent(m["max_drawdown"]))
        html_parts.append('            <div class="metric-item"><div class="label">回撤持续天数</div><div class="value neutral">%d 天</div></div>' % m["max_drawdown_duration"])
        html_parts.append('            <div class="metric-item"><div class="label">年化波动率</div><div class="value neutral">%s</div></div>' % format_percent(m["volatility"]))
        html_parts.append('            <div class="metric-item"><div class="label">夏普比率</div><div class="value %s">%s</div></div>' % (sharpe_class, format_number(m["sharpe_ratio"])))
        html_parts.append('            <div class="metric-item"><div class="label">Sortino比率</div><div class="value %s">%s</div></div>' % (sortino_class, format_number(m["sortino_ratio"])))
        html_parts.append('            <div class="metric-item"><div class="label">Calmar比率</div><div class="value %s">%s</div></div>' % (calmar_class, format_number(m["calmar_ratio"])))
        html_parts.append('        </div></div>')

        # Trading Stats
        html_parts.append('        <div class="card"><h2>交易统计</h2><div class="metrics-grid">')
        html_parts.append('            <div class="metric-item"><div class="label">交易次数</div><div class="value neutral">%d</div></div>' % m["total_trades"])
        html_parts.append('            <div class="metric-item"><div class="label">胜率</div><div class="value %s">%s</div></div>' % (win_class, format_percent(m["win_rate"])))
        html_parts.append('            <div class="metric-item"><div class="label">盈亏比</div><div class="value neutral">%s</div></div>' % format_number(m["profit_loss_ratio"]))
        html_parts.append('            <div class="metric-item"><div class="label">最大连续盈利</div><div class="value profit">%d 次</div></div>' % m["max_consecutive_wins"])
        html_parts.append('            <div class="metric-item"><div class="label">最大连续亏损</div><div class="value loss">%d 次</div></div>' % m["max_consecutive_losses"])
        html_parts.append('            <div class="metric-item"><div class="label">总盈亏</div><div class="value %s">%s</div></div>' % (pnl_class, format_number(m["total_pnl"])))
        html_parts.append('            <div class="metric-item"><div class="label">总手续费</div><div class="value loss">%s</div></div>' % format_number(m["total_commission"]))
        html_parts.append('            <div class="metric-item"><div class="label">平均持仓天数</div><div class="value neutral">%.1f 天</div></div>' % m["avg_holding_days"])
        html_parts.append('        </div></div>')

        # Capital Stats
        html_parts.append('        <div class="card"><h2>资金曲线</h2><div class="metrics-grid">')
        html_parts.append('            <div class="metric-item"><div class="label">初始资金</div><div class="value neutral">%s</div></div>' % ("{:,.2f}".format(self.result["config"]["initial_capital"])))
        html_parts.append('            <div class="metric-item"><div class="label">最终资金</div><div class="value %s">%s</div></div>' % (final_class, "{:,.2f}".format(m["final_capital"])))
        html_parts.append('            <div class="metric-item"><div class="label">峰值资金</div><div class="value profit">%s</div></div>' % "{:,.2f}".format(m["peak_capital"]))
        html_parts.append('            <div class="metric-item"><div class="label">最低资金</div><div class="value loss">%s</div></div>' % "{:,.2f}".format(m["min_capital"]))
        html_parts.append('        </div></div>')

        # Monthly Returns
        html_parts.append('        <div class="card"><h2>月度收益</h2>')
        html_parts.append('            <table><thead><tr><th>月份</th><th>收益率</th></tr></thead>')
        html_parts.append('            <tbody>%s</tbody></table>' % monthly_rows)
        html_parts.append('        </div>')

        # Trade Records
        html_parts.append('        <div class="card"><h2>交易记录</h2>')
        html_parts.append('            <table><thead><tr>')
        html_parts.append('                <th>日期</th><th>方向</th><th>价格</th><th>数量</th><th>手续费</th><th>盈亏</th>')
        html_parts.append('            </tr></thead>')
        html_parts.append('            <tbody>%s</tbody></table>' % trade_rows)
        html_parts.append('        </div>')

        # Footer
        html_parts.append('        <div class="footer">')
        html_parts.append('            <p>QuantPilot v1.0.0 | 本报告由 QuantPilot 回测引擎自动生成</p>')
        html_parts.append('        </div>')
        html_parts.append('    </div>')
        html_parts.append('</body>')
        html_parts.append('</html>')

        html = "\n".join(html_parts)

        if filepath:
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

        return html

    def generate_markdown(self, filepath=None):
        """
        生成Markdown报告。

        Args:
            filepath: 输出文件路径，为None时不写入文件

        Returns:
            str: Markdown格式报告字符串
        """
        m = self._metrics
        trades = self.result["trades"]

        lines = [
            "# QuantPilot 回测报告",
            "",
            "> 生成时间: %s  |  策略: %s" % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.result["strategy_name"],
            ),
            "",
            "## 策略信息",
            "",
            "| 项目 | 值 |",
            "|------|-----|",
            "| 策略名称 | %s |" % self.result["strategy_name"],
            "| 策略描述 | %s |" % self.result["strategy_desc"],
            "| 初始资金 | %s |" % "{:,.2f}".format(self.result["config"]["initial_capital"]),
            "| 手续费率 | %s |" % format_percent(self.result["config"]["commission_rate"]),
            "| 滑点 | %s |" % self.result["config"]["slippage"],
            "| 止损 | %s |" % (
                format_percent(self.result["config"]["stop_loss"])
                if self.result["config"]["stop_loss"] else "未设置"
            ),
            "| 止盈 | %s |" % (
                format_percent(self.result["config"]["take_profit"])
                if self.result["config"]["take_profit"] else "未设置"
            ),
            "",
            "## 收益指标",
            "",
            "| 指标 | 值 |",
            "|------|-----|",
            "| 总收益率 | %s |" % format_percent(m["total_return"]),
            "| 年化收益率 | %s |" % format_percent(m["annual_return"]),
            "| 最大回撤 | %s |" % format_percent(m["max_drawdown"]),
            "| 回撤持续天数 | %d 天 |" % m["max_drawdown_duration"],
            "| 年化波动率 | %s |" % format_percent(m["volatility"]),
            "| 夏普比率 | %s |" % format_number(m["sharpe_ratio"]),
            "| Sortino比率 | %s |" % format_number(m["sortino_ratio"]),
            "| Calmar比率 | %s |" % format_number(m["calmar_ratio"]),
            "",
            "## 交易统计",
            "",
            "| 指标 | 值 |",
            "|------|-----|",
            "| 交易次数 | %d |" % m["total_trades"],
            "| 胜率 | %s |" % format_percent(m["win_rate"]),
            "| 盈亏比 | %s |" % format_number(m["profit_loss_ratio"]),
            "| 最大连续盈利 | %d 次 |" % m["max_consecutive_wins"],
            "| 最大连续亏损 | %d 次 |" % m["max_consecutive_losses"],
            "| 平均盈利 | %s |" % format_number(m["avg_profit"]),
            "| 平均亏损 | %s |" % format_number(m["avg_loss"]),
            "| 总手续费 | %s |" % format_number(m["total_commission"]),
            "| 总盈亏 | %s |" % format_number(m["total_pnl"]),
            "",
            "## 资金统计",
            "",
            "| 指标 | 值 |",
            "|------|-----|",
            "| 初始资金 | %s |" % "{:,.2f}".format(self.result["config"]["initial_capital"]),
            "| 最终资金 | %s |" % "{:,.2f}".format(m["final_capital"]),
            "| 峰值资金 | %s |" % "{:,.2f}".format(m["peak_capital"]),
            "| 最低资金 | %s |" % "{:,.2f}".format(m["min_capital"]),
            "",
            "## 月度收益",
            "",
            "| 月份 | 收益率 |",
            "|------|--------|",
        ]

        for month, ret in sorted(m["monthly_returns"].items()):
            lines.append("| %s | %s |" % (month, format_percent(ret)))

        lines.extend([
            "",
            "## 交易记录",
            "",
            "| 日期 | 方向 | 价格 | 数量 | 手续费 | 盈亏 | 原因 |",
            "|------|------|------|------|--------|------|------|",
        ])

        for t in trades:
            action = "买入" if t["action"] == "buy" else "卖出"
            lines.append(
                "| %s | %s | %s | %s | %s | %s | %s |" % (
                    t["date"], action, format_number(t["price"]),
                    t["quantity"], format_number(t["commission"]),
                    format_number(t.get("pnl", 0)), t.get("reason", ""),
                )
            )

        lines.extend([
            "",
            "---",
            "*QuantPilot v1.0.0 | 本报告由 QuantPilot 回测引擎自动生成*",
        ])

        md_str = "\n".join(lines)

        if filepath:
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_str)

        return md_str
