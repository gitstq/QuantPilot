"""
QuantPilot CLI入口模块

支持通过 python -m quantpilot 运行。
"""

import sys

from . import __version__
from .cli import parse_args
from .data import KLineData
from .engine import BacktestEngine, BacktestConfig
from .strategy import create_strategy, list_strategies
from .indicators import list_indicators, compute_indicator
from .report import ReportGenerator
from .tui import TUIDashboard
from .analyzer import PerformanceAnalyzer


def cmd_backtest(args):
    """执行回测子命令。"""
    # 加载数据
    try:
        kline_data = KLineData.from_csv(args.file)
    except FileNotFoundError as e:
        print("错误: {}".format(e))
        return 1
    except ValueError as e:
        print("数据格式错误: {}".format(e))
        return 1

    # 验证数据
    errors = kline_data.validate()
    if errors:
        print("数据验证警告:")
        for err in errors:
            print("  - {}".format(err))

    print("数据加载完成: {} 条K线, {} ~ {}".format(
        len(kline_data),
        kline_data.summary().get("start_date", "N/A"),
        kline_data.summary().get("end_date", "N/A"),
    ))

    # 创建策略
    try:
        strategy = create_strategy(args.strategy)
    except ValueError as e:
        print("错误: {}".format(e))
        return 1

    print("使用策略: {} - {}".format(strategy.name, strategy.description()))

    # 创建回测配置
    config = BacktestConfig(
        initial_capital=args.capital,
        commission_rate=args.commission,
        slippage=args.slippage,
        stop_loss=args.stop_loss,
        take_profit=args.take_profit,
        position_size=args.position_size,
    )

    # 执行回测
    engine = BacktestEngine(config)
    result = engine.run(strategy, kline_data)

    # 生成报告
    if args.tui:
        dashboard = TUIDashboard(result)
        print("\n" + dashboard.show_dashboard())
    else:
        reporter = ReportGenerator(result)
        fmt = args.format

        if fmt == "terminal":
            print("\n" + reporter.generate_terminal())
        elif fmt == "json":
            output = args.output or "backtest_report.json"
            reporter.generate_json(output)
            print("JSON报告已保存: {}".format(output))
        elif fmt == "html":
            output = args.output or "backtest_report.html"
            reporter.generate_html(output)
            print("HTML报告已保存: {}".format(output))
        elif fmt == "markdown":
            output = args.output or "backtest_report.md"
            reporter.generate_markdown(output)
            print("Markdown报告已保存: {}".format(output))

    # 如果指定了输出路径且格式为terminal
    if args.output and args.format == "terminal":
        reporter = ReportGenerator(result)
        reporter.generate_markdown(args.output)
        print("报告已保存: {}".format(args.output))

    return 0


def cmd_indicators(args):
    """执行指标计算子命令。"""
    # 加载数据
    try:
        kline_data = KLineData.from_csv(args.file)
    except (FileNotFoundError, ValueError) as e:
        print("错误: {}".format(e))
        return 1

    closes = kline_data.get_closes()
    highs = kline_data.get_highs()
    lows = kline_data.get_lows()
    volumes = kline_data.get_volumes()

    # 计算指标
    indicator_name = args.indicator.upper()
    try:
        if indicator_name in ("MA", "EMA", "SMA", "RSI", "ROC", "TRIX"):
            result = compute_indicator(indicator_name, closes, args.period)
            values = result
        elif indicator_name == "MACD":
            dif, dea, hist = compute_indicator(indicator_name, closes)
            values = dif
            print("MACD指标 (DIF/DEA/HIST):")
        elif indicator_name == "BOLL":
            upper, middle, lower = compute_indicator(indicator_name, closes)
            values = middle
            print("布林带 (Upper/Middle/Lower):")
        elif indicator_name in ("ATR", "WR", "CCI", "DMI"):
            if indicator_name == "ATR":
                values = compute_indicator(indicator_name, highs, lows, closes, args.period)
            elif indicator_name == "WR":
                values = compute_indicator(indicator_name, highs, lows, closes, args.period)
            elif indicator_name == "CCI":
                values = compute_indicator(indicator_name, highs, lows, closes, args.period)
            elif indicator_name == "DMI":
                pdi, ndi, adx = compute_indicator(indicator_name, highs, lows, closes)
                values = adx
                print("DMI指标 (+DI/-DI/ADX):")
        elif indicator_name == "KDJ":
            k_vals, d_vals, j_vals = compute_indicator(indicator_name, highs, lows, closes)
            values = k_vals
            print("KDJ指标 (K/D/J):")
        elif indicator_name == "OBV":
            values = compute_indicator(indicator_name, closes, volumes)
        elif indicator_name == "MFI":
            values = compute_indicator(indicator_name, highs, lows, closes, volumes, args.period)
        elif indicator_name == "STOCH":
            k_vals, d_vals = compute_indicator(indicator_name, highs, lows, closes)
            values = k_vals
            print("STOCH指标 (%K/%D):")
        elif indicator_name == "VWAP":
            values = compute_indicator(indicator_name, highs, lows, closes, volumes)
        else:
            print("错误: 不支持的指标 '{}'".format(indicator_name))
            return 1
    except ValueError as e:
        print("错误: {}".format(e))
        return 1

    # 显示最近N条
    last_n = args.last
    dates = kline_data.get_dates()
    start_idx = max(0, len(values) - last_n)

    print("\n{} 指标 (最近{}条):".format(indicator_name, last_n))
    print("-" * 50)
    for i in range(start_idx, len(values)):
        date_str = dates[i] if i < len(dates) else "N/A"
        val = values[i]
        val_str = "{:.4f}".format(val) if val is not None else "N/A"
        print("  {} : {}".format(date_str, val_str))

    return 0


def cmd_report(args):
    """执行报告生成子命令。"""
    # 加载数据
    try:
        kline_data = KLineData.from_csv(args.file)
    except (FileNotFoundError, ValueError) as e:
        print("错误: {}".format(e))
        return 1

    # 创建策略
    try:
        strategy = create_strategy(args.strategy)
    except ValueError as e:
        print("错误: {}".format(e))
        return 1

    # 执行回测
    config = BacktestConfig()
    engine = BacktestEngine(config)
    result = engine.run(strategy, kline_data)

    # 生成报告
    reporter = ReportGenerator(result)
    fmt = args.format

    if fmt == "terminal":
        print(reporter.generate_terminal())
    elif fmt == "json":
        output = args.output or "report.json"
        reporter.generate_json(output)
        print("JSON报告已保存: {}".format(output))
    elif fmt == "html":
        output = args.output or "report.html"
        reporter.generate_html(output)
        print("HTML报告已保存: {}".format(output))
    elif fmt == "markdown":
        output = args.output or "report.md"
        reporter.generate_markdown(output)
        print("Markdown报告已保存: {}".format(output))

    return 0


def cmd_list_strategies(args):
    """列出可用策略。"""
    strategies = list_strategies()
    print("\n可用策略列表:")
    print("=" * 70)
    for s in strategies:
        print("\n  名称: {}".format(s["name"]))
        print("  描述: {}".format(s["desc"]))
        print("  参数: {}".format(s["params"]))
    print("\n" + "=" * 70)
    return 0


def cmd_list_indicators(args):
    """列出可用指标。"""
    indicators = list_indicators()
    print("\n可用技术指标列表:")
    print("=" * 70)
    for ind in indicators:
        params_str = ", ".join(ind["params"]) if ind["params"] else "无"
        print("  {:<8} | {:<40} | 参数: {}".format(
            ind["name"], ind["desc"], params_str
        ))
    print("\n" + "=" * 70)
    return 0


def main(args=None):
    """
    CLI主入口函数。

    Args:
        args: 命令行参数，为None时使用sys.argv

    Returns:
        int: 退出码
    """
    parsed = parse_args(args)

    # 版本信息
    if parsed.version:
        print("QuantPilot v{}".format(__version__))
        return 0

    # 子命令分发
    command_handlers = {
        "backtest": cmd_backtest,
        "indicators": cmd_indicators,
        "report": cmd_report,
        "list-strategies": cmd_list_strategies,
        "list-indicators": cmd_list_indicators,
    }

    handler = command_handlers.get(parsed.command)
    if handler is None:
        print("QuantPilot v{}".format(__version__))
        print("使用 'quantpilot -h' 查看帮助信息")
        return 0

    return handler(parsed)


if __name__ == "__main__":
    sys.exit(main())
