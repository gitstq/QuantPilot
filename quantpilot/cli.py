"""
QuantPilot 命令行参数解析模块

支持子命令:
    backtest       - 运行策略回测
    indicators     - 计算并显示技术指标
    report         - 生成回测报告
    list-strategies - 列出可用策略
    list-indicators - 列出可用指标
    version        - 显示版本信息
"""

import argparse
import sys


def create_parser():
    """
    创建命令行参数解析器。

    Returns:
        argparse.ArgumentParser: 参数解析器
    """
    parser = argparse.ArgumentParser(
        prog="quantpilot",
        description="QuantPilot - 轻量级终端AI量化策略回测引擎",
        epilog="示例: quantpilot backtest -f data.csv -s dual_ma_cross",
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="显示版本信息",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用子命令")

    # backtest 子命令
    bt_parser = subparsers.add_parser(
        "backtest",
        help="运行策略回测",
        description="使用指定策略对K线数据进行回测",
    )
    bt_parser.add_argument(
        "-f", "--file",
        type=str,
        required=True,
        help="K线数据CSV文件路径",
    )
    bt_parser.add_argument(
        "-s", "--strategy",
        type=str,
        default="dual_ma_cross",
        help="策略名称 (默认: dual_ma_cross)",
    )
    bt_parser.add_argument(
        "--capital",
        type=float,
        default=1000000,
        help="初始资金 (默认: 1000000)",
    )
    bt_parser.add_argument(
        "--commission",
        type=float,
        default=0.0003,
        help="手续费率 (默认: 0.0003)",
    )
    bt_parser.add_argument(
        "--slippage",
        type=float,
        default=0.01,
        help="滑点 (默认: 0.01)",
    )
    bt_parser.add_argument(
        "--stop-loss",
        type=float,
        default=None,
        help="止损比例 (如 0.05 表示5%%)",
    )
    bt_parser.add_argument(
        "--take-profit",
        type=float,
        default=None,
        help="止盈比例 (如 0.10 表示10%%)",
    )
    bt_parser.add_argument(
        "--position-size",
        type=float,
        default=0.9,
        help="仓位比例 (默认: 0.9)",
    )
    bt_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="报告输出路径 (根据扩展名自动选择格式: .json/.html/.md)",
    )
    bt_parser.add_argument(
        "--format",
        type=str,
        choices=["terminal", "json", "html", "markdown"],
        default="terminal",
        help="报告格式 (默认: terminal)",
    )
    bt_parser.add_argument(
        "--tui",
        action="store_true",
        help="显示TUI仪表板",
    )

    # indicators 子命令
    ind_parser = subparsers.add_parser(
        "indicators",
        help="计算技术指标",
        description="计算并显示指定技术指标",
    )
    ind_parser.add_argument(
        "-f", "--file",
        type=str,
        required=True,
        help="K线数据CSV文件路径",
    )
    ind_parser.add_argument(
        "-i", "--indicator",
        type=str,
        default="MA",
        help="指标名称 (默认: MA)",
    )
    ind_parser.add_argument(
        "--period",
        type=int,
        default=20,
        help="指标周期 (默认: 20)",
    )
    ind_parser.add_argument(
        "--last",
        type=int,
        default=10,
        help="显示最近N条数据 (默认: 10)",
    )

    # report 子命令
    rpt_parser = subparsers.add_parser(
        "report",
        help="生成回测报告",
        description="从回测结果生成报告",
    )
    rpt_parser.add_argument(
        "-f", "--file",
        type=str,
        required=True,
        help="K线数据CSV文件路径",
    )
    rpt_parser.add_argument(
        "-s", "--strategy",
        type=str,
        default="dual_ma_cross",
        help="策略名称 (默认: dual_ma_cross)",
    )
    rpt_parser.add_argument(
        "--format",
        type=str,
        choices=["terminal", "json", "html", "markdown"],
        default="terminal",
        help="报告格式 (默认: terminal)",
    )
    rpt_parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出文件路径",
    )

    # list-strategies 子命令
    subparsers.add_parser(
        "list-strategies",
        help="列出可用策略",
    )

    # list-indicators 子命令
    subparsers.add_parser(
        "list-indicators",
        help="列出可用技术指标",
    )

    return parser


def parse_args(args=None):
    """
    解析命令行参数。

    Args:
        args: 参数列表，为None时使用sys.argv

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = create_parser()
    return parser.parse_args(args)
