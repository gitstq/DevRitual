"""DevRitual 命令行解析模块

使用argparse构建完整的CLI命令体系，支持多级子命令。
所有命令都有--help说明，支持中文帮助信息。
"""

import argparse
import sys

from devritual import __version__
from devritual.utils import (
    Color, colored, bold, success_msg, error_msg,
    info_msg, title_msg, is_initialized
)
from devritual.storage import init_storage, export_data, import_data, backup_data
from devritual.rituals import (
    cmd_ritual_create, cmd_ritual_list, cmd_ritual_show,
    cmd_ritual_edit, cmd_ritual_delete, cmd_ritual_start,
    cmd_ritual_complete, cmd_ritual_skip, cmd_ritual_templates
)
from devritual.habits import (
    cmd_habit_create, cmd_habit_list, cmd_habit_streak,
    cmd_habit_edit, cmd_habit_delete, cmd_habit_checkin,
    cmd_habit_skip, cmd_habit_templates
)
from devritual.stats import cmd_stats, cmd_stats_calendar, cmd_stats_trend
from devritual.dashboard import cmd_dashboard


def _check_init():
    """检查是否已初始化，未初始化则提示并退出

    Returns:
        bool: 如果已初始化返回True
    """
    if not is_initialized():
        error_msg("DevRitual 尚未初始化")
        info_msg("请先运行 'devritual init' 进行初始化")
        return False
    return True


def build_parser():
    """构建完整的命令行参数解析器

    创建多级子命令结构，包含所有CLI命令和对应的帮助信息。

    Returns:
        argparse.ArgumentParser: 配置好的参数解析器
    """
    parser = argparse.ArgumentParser(
        prog="devritual",
        description="DevRitual - 轻量级终端开发者仪式感与习惯养成引擎",
        epilog="使用 'devritual <command> --help' 查看子命令帮助",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ============================================================
    # init 命令
    # ============================================================
    init_parser = subparsers.add_parser(
        "init",
        help="初始化 DevRitual 配置",
        description="初始化 DevRitual，创建数据目录和配置文件",
    )

    # ============================================================
    # ritual 命令组
    # ============================================================
    ritual_parser = subparsers.add_parser(
        "ritual",
        help="仪式管理",
        description="管理开发者仪式（创建、执行、查看等）",
    )
    ritual_subparsers = ritual_parser.add_subparsers(
        dest="ritual_command", help="仪式子命令"
    )

    # ritual create
    ritual_create_parser = ritual_subparsers.add_parser(
        "create",
        help="创建新仪式",
        description="创建一个新的开发者仪式，可从模板创建或自定义",
    )
    ritual_create_parser.add_argument(
        "-n", "--name", type=str, help="仪式名称"
    )
    ritual_create_parser.add_argument(
        "-d", "--description", type=str, help="仪式描述"
    )
    ritual_create_parser.add_argument(
        "-s", "--steps", nargs="+", help="仪式步骤列表"
    )
    ritual_create_parser.add_argument(
        "-t", "--time", type=int, dest="estimated_time",
        help="预估时间（分钟）"
    )
    ritual_create_parser.add_argument(
        "--tags", nargs="+", help="标签列表"
    )
    ritual_create_parser.add_argument(
        "-f", "--frequency", choices=["daily", "weekly", "custom"],
        default="daily", help="频率（默认: daily）"
    )
    ritual_create_parser.add_argument(
        "--template", type=str, help="从模板创建（模板ID）"
    )

    # ritual list
    ritual_list_parser = ritual_subparsers.add_parser(
        "list",
        help="列出所有仪式",
        description="列出所有已创建的仪式",
    )
    ritual_list_parser.add_argument(
        "--tag", type=str, help="按标签过滤"
    )

    # ritual show
    ritual_show_parser = ritual_subparsers.add_parser(
        "show",
        help="查看仪式详情",
        description="查看指定仪式的详细信息",
    )
    ritual_show_parser.add_argument(
        "name", type=str, help="仪式名称"
    )

    # ritual edit
    ritual_edit_parser = ritual_subparsers.add_parser(
        "edit",
        help="编辑仪式",
        description="编辑指定仪式的信息",
    )
    ritual_edit_parser.add_argument(
        "name", type=str, help="仪式名称"
    )

    # ritual delete
    ritual_delete_parser = ritual_subparsers.add_parser(
        "delete",
        help="删除仪式",
        description="删除指定的仪式",
    )
    ritual_delete_parser.add_argument(
        "name", type=str, help="仪式名称"
    )

    # ritual start
    ritual_start_parser = ritual_subparsers.add_parser(
        "start",
        help="开始执行仪式",
        description="开始执行指定的仪式，创建执行记录",
    )
    ritual_start_parser.add_argument(
        "name", type=str, help="仪式名称"
    )

    # ritual complete
    ritual_complete_parser = ritual_subparsers.add_parser(
        "complete",
        help="完成仪式",
        description="标记指定的仪式为已完成",
    )
    ritual_complete_parser.add_argument(
        "name", type=str, help="仪式名称"
    )

    # ritual skip
    ritual_skip_parser = ritual_subparsers.add_parser(
        "skip",
        help="跳过仪式",
        description="跳过指定的仪式",
    )
    ritual_skip_parser.add_argument(
        "name", type=str, help="仪式名称"
    )

    # ritual templates
    ritual_templates_parser = ritual_subparsers.add_parser(
        "templates",
        help="查看仪式模板",
        description="列出所有可用的预设仪式模板",
    )

    # ============================================================
    # habit 命令组
    # ============================================================
    habit_parser = subparsers.add_parser(
        "habit",
        help="习惯追踪",
        description="管理开发者习惯（创建、打卡、统计等）",
    )
    habit_subparsers = habit_parser.add_subparsers(
        dest="habit_command", help="习惯子命令"
    )

    # habit create
    habit_create_parser = habit_subparsers.add_parser(
        "create",
        help="创建新习惯",
        description="创建一个新的开发者习惯，可从模板创建或自定义",
    )
    habit_create_parser.add_argument(
        "-n", "--name", type=str, help="习惯名称"
    )
    habit_create_parser.add_argument(
        "-d", "--description", type=str, help="习惯描述"
    )
    habit_create_parser.add_argument(
        "-f", "--frequency", choices=["daily", "weekly", "custom"],
        default="daily", dest="frequency", help="频率目标（默认: daily）"
    )
    habit_create_parser.add_argument(
        "-r", "--reminder", type=str, help="提醒时间（HH:MM）"
    )
    habit_create_parser.add_argument(
        "--template", type=str, help="从模板创建（模板ID）"
    )

    # habit list
    habit_list_parser = habit_subparsers.add_parser(
        "list",
        help="列出所有习惯",
        description="列出所有已创建的习惯及其状态",
    )

    # habit checkin
    habit_checkin_parser = habit_subparsers.add_parser(
        "checkin",
        help="习惯打卡",
        description="为指定习惯记录一次打卡",
    )
    habit_checkin_parser.add_argument(
        "name", type=str, help="习惯名称"
    )

    # habit skip
    habit_skip_parser = habit_subparsers.add_parser(
        "skip",
        help="跳过习惯",
        description="跳过今天的习惯打卡",
    )
    habit_skip_parser.add_argument(
        "name", type=str, help="习惯名称"
    )

    # habit streak
    habit_streak_parser = habit_subparsers.add_parser(
        "streak",
        help="查看连续天数",
        description="查看指定习惯的连续打卡天数统计",
    )
    habit_streak_parser.add_argument(
        "name", type=str, help="习惯名称"
    )

    # habit edit
    habit_edit_parser = habit_subparsers.add_parser(
        "edit",
        help="编辑习惯",
        description="编辑指定习惯的信息",
    )
    habit_edit_parser.add_argument(
        "name", type=str, help="习惯名称"
    )

    # habit delete
    habit_delete_parser = habit_subparsers.add_parser(
        "delete",
        help="删除习惯",
        description="删除指定的习惯",
    )
    habit_delete_parser.add_argument(
        "name", type=str, help="习惯名称"
    )

    # habit templates
    habit_templates_parser = habit_subparsers.add_parser(
        "templates",
        help="查看习惯模板",
        description="列出所有可用的预设习惯模板",
    )

    # ============================================================
    # stats 命令组
    # ============================================================
    stats_parser = subparsers.add_parser(
        "stats",
        help="统计分析",
        description="查看习惯和仪式的统计数据",
    )
    stats_subparsers = stats_parser.add_subparsers(
        dest="stats_command", help="统计子命令"
    )

    # stats (默认 - 总体统计)
    stats_default_parser = stats_subparsers.add_parser(
        "overview",
        help="总体统计概览",
        description="查看所有习惯和仪式的汇总统计",
    )

    # stats calendar
    stats_calendar_parser = stats_subparsers.add_parser(
        "calendar",
        help="热力图日历",
        description="查看习惯完成情况的热力图日历",
    )
    stats_calendar_parser.add_argument(
        "-d", "--days", type=int, default=90,
        help="显示天数（默认: 90）"
    )

    # stats trend
    stats_trend_parser = stats_subparsers.add_parser(
        "trend",
        help="趋势分析",
        description="查看完成趋势和周对比数据",
    )
    stats_trend_parser.add_argument(
        "-d", "--days", type=int, default=30,
        help="分析天数（默认: 30）"
    )

    # ============================================================
    # export 命令
    # ============================================================
    export_parser = subparsers.add_parser(
        "export",
        help="导出数据",
        description="将所有数据导出为JSON文件",
    )
    export_parser.add_argument(
        "-f", "--file", type=str, default="devritual_export.json",
        help="导出文件路径（默认: devritual_export.json）"
    )

    # ============================================================
    # import 命令
    # ============================================================
    import_parser = subparsers.add_parser(
        "import",
        help="导入数据",
        description="从JSON文件导入数据（会覆盖当前数据）",
    )
    import_parser.add_argument(
        "file", type=str, help="导入文件路径"
    )

    # ============================================================
    # backup 命令
    # ============================================================
    backup_parser = subparsers.add_parser(
        "backup",
        help="备份数据",
        description="创建数据备份",
    )

    # ============================================================
    # dashboard 命令
    # ============================================================
    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="TUI仪表盘",
        description="打开综合仪表盘，查看今日概览和统计数据",
    )

    return parser


def main():
    """CLI主入口函数

    解析命令行参数，分发到对应的命令处理函数。
    """
    parser = build_parser()
    args = parser.parse_args()

    # 没有指定命令时显示帮助
    if not args.command:
        parser.print_help()
        return

    # ============================================================
    # init 命令（不需要检查初始化状态）
    # ============================================================
    if args.command == "init":
        if is_initialized():
            info_msg("DevRitual 已经初始化过了")
            info_msg(f"数据目录: ~/.devritual/")
            return
        init_storage()
        success_msg("DevRitual 初始化完成！")
        info_msg("数据目录: ~/.devritual/")
        print()
        info_msg("快速开始:")
        print(colored("    devritual ritual create          ", Color.CYAN) +
              "# 创建仪式")
        print(colored("    devritual habit create           ", Color.CYAN) +
              "# 创建习惯")
        print(colored("    devritual dashboard              ", Color.CYAN) +
              "# 打开仪表盘")
        return

    # ============================================================
    # 其他命令都需要先检查初始化
    # ============================================================
    if not _check_init():
        sys.exit(1)

    # ============================================================
    # ritual 命令分发
    # ============================================================
    if args.command == "ritual":
        if not hasattr(args, "ritual_command") or not args.ritual_command:
            # 没有子命令，显示ritual帮助
            parser.parse_args(["ritual", "--help"])
            return

        ritual_commands = {
            "create": cmd_ritual_create,
            "list": cmd_ritual_list,
            "show": cmd_ritual_show,
            "edit": cmd_ritual_edit,
            "delete": cmd_ritual_delete,
            "start": cmd_ritual_start,
            "complete": cmd_ritual_complete,
            "skip": cmd_ritual_skip,
            "templates": cmd_ritual_templates,
        }

        handler = ritual_commands.get(args.ritual_command)
        if handler:
            handler(args)
        else:
            parser.parse_args(["ritual", "--help"])

    # ============================================================
    # habit 命令分发
    # ============================================================
    elif args.command == "habit":
        if not hasattr(args, "habit_command") or not args.habit_command:
            parser.parse_args(["habit", "--help"])
            return

        habit_commands = {
            "create": cmd_habit_create,
            "list": cmd_habit_list,
            "checkin": cmd_habit_checkin,
            "skip": cmd_habit_skip,
            "streak": cmd_habit_streak,
            "edit": cmd_habit_edit,
            "delete": cmd_habit_delete,
            "templates": cmd_habit_templates,
        }

        handler = habit_commands.get(args.habit_command)
        if handler:
            handler(args)
        else:
            parser.parse_args(["habit", "--help"])

    # ============================================================
    # stats 命令分发
    # ============================================================
    elif args.command == "stats":
        stats_command = getattr(args, "stats_command", None)

        if stats_command == "calendar":
            cmd_stats_calendar(args)
        elif stats_command == "trend":
            cmd_stats_trend(args)
        else:
            # 默认显示总体统计
            cmd_stats(args)

    # ============================================================
    # export 命令
    # ============================================================
    elif args.command == "export":
        filepath = getattr(args, "file", "devritual_export.json")
        if export_data(filepath):
            success_msg(f"数据已导出到: {filepath}")

    # ============================================================
    # import 命令
    # ============================================================
    elif args.command == "import":
        filepath = args.file
        if import_data(filepath):
            success_msg(f"数据已从 {filepath} 导入")

    # ============================================================
    # backup 命令
    # ============================================================
    elif args.command == "backup":
        backup_dir = backup_data()
        success_msg(f"数据已备份到: {backup_dir}")

    # ============================================================
    # dashboard 命令
    # ============================================================
    elif args.command == "dashboard":
        cmd_dashboard(args)
