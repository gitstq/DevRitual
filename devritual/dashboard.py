"""DevRitual TUI仪表盘模块

在终端中渲染一个综合性的仪表盘界面，展示：
- 今日待办（习惯打卡和仪式执行）
- 习惯连续天数概览
- 最近活动记录
- 快速统计信息
"""

from datetime import date, timedelta

from devritual.storage import (
    load_habits, load_rituals, load_habit_records, load_ritual_executions
)
from devritual.utils import (
    Color, colored, bold, success_msg, error_msg, warning_msg,
    info_msg, title_msg, print_separator, format_duration,
    format_percentage, get_terminal_width
)
from devritual.models import today_str


def cmd_dashboard(args):
    """TUI仪表盘命令处理函数

    渲染一个综合性的终端仪表盘，展示所有关键信息。

    Args:
        args: 命令行参数对象
    """
    habits = load_habits()
    rituals = load_rituals()
    records = load_habit_records()
    executions = load_ritual_executions()

    width = get_terminal_width()
    today = today_str()

    # 清屏效果
    print()
    _print_header(width)
    print()

    # 今日概览
    _print_today_overview(habits, rituals, records, executions, today)
    print()

    # 待办事项
    _print_todo_list(habits, rituals, records, executions, today)
    print()

    # 习惯连续天数
    _print_habit_streaks(habits)
    print()

    # 最近活动
    _print_recent_activity(records, executions)
    print()

    # 快速统计
    _print_quick_stats(habits, rituals, records, executions)
    print()

    # 底部提示
    _print_footer(width)


def _print_header(width):
    """打印仪表盘头部

    Args:
        width (int): 终端宽度
    """
    header = " DevRitual 仪表盘 "
    padding = (width - len(header) - 4) // 2
    left_pad = "═" * padding
    right_pad = "═" * (width - len(header) - 4 - padding)

    print(colored(f"  ╔{left_pad}{header}{right_pad}╗", Color.CYAN))

    today_str_display = date.today().strftime("%Y年%m月%d日 %A")
    weekday_map = {
        "Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三",
        "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六",
        "Sunday": "星期日",
    }
    for en, zh in weekday_map.items():
        today_str_display = today_str_display.replace(en, zh)

    display = f"  ║ {today_str_display.center(width - 6)} ║"
    print(colored(display, Color.CYAN))
    print(colored(f"  ╚{'═' * (width - 4)}╝", Color.CYAN))


def _print_today_overview(habits, rituals, records, executions, today):
    """打印今日概览

    Args:
        habits: 所有习惯列表
        rituals: 所有仪式列表
        records: 所有习惯记录
        executions: 所有仪式执行记录
        today (str): 今天的日期字符串
    """
    active_habits = [h for h in habits if h.get("is_active", True)]
    active_rituals = [r for r in rituals if r.get("is_active", True)]

    # 今日习惯完成情况
    today_habit_records = [
        r for r in records
        if r["date"] == today and r["status"] == "completed"
    ]
    completed_habit_ids = set(r["habit_id"] for r in today_habit_records)
    habit_done = len([
        h for h in active_habits if h["id"] in completed_habit_ids
    ])
    habit_total = len(active_habits)

    # 今日仪式完成情况
    today_ritual_execs = [
        e for e in executions
        if e["date"] == today and e["status"] == "completed"
    ]
    completed_ritual_ids = set(e["ritual_id"] for e in today_ritual_execs)
    ritual_done = len([
        r for r in active_rituals if r["id"] in completed_ritual_ids
    ])
    ritual_total = len(active_rituals)

    # 计算总体进度
    total_items = habit_total + ritual_total
    done_items = habit_done + ritual_done
    progress = done_items / total_items if total_items > 0 else 0

    title_msg("今日进度")
    print()

    # 进度条
    bar_width = 40
    filled = int(bar_width * progress)
    empty = bar_width - filled

    if progress >= 1.0:
        bar_color = Color.GREEN
    elif progress >= 0.5:
        bar_color = Color.YELLOW
    else:
        bar_color = Color.RED

    bar = colored("█" * filled, bar_color) + \
          colored("░" * empty, Color.DIM)
    pct = colored(f"{progress:.0%}", Color.BOLD)

    print(f"  {bar} {pct}")
    print()

    # 分项统计
    print(f"  {colored('习惯', Color.CYAN)}: "
          f"{colored(str(habit_done), Color.GREEN)}/"
          f"{habit_total} 已完成")
    print(f"  {colored('仪式', Color.CYAN)}: "
          f"{colored(str(ritual_done), Color.GREEN)}/"
          f"{ritual_total} 已完成")

    if progress >= 1.0:
        print()
        success_msg("今日目标已全部完成！")


def _print_todo_list(habits, rituals, records, executions, today):
    """打印今日待办事项

    Args:
        habits: 所有习惯列表
        rituals: 所有仪式列表
        records: 所有习惯记录
        executions: 所有仪式执行记录
        today (str): 今天的日期字符串
    """
    title_msg("今日待办")
    print()

    # 未完成的习惯
    active_habits = [h for h in habits if h.get("is_active", True)]
    today_records = [r for r in records if r["date"] == today]
    completed_habit_ids = set(
        r["habit_id"] for r in today_records if r["status"] == "completed"
    )

    pending_habits = [
        h for h in active_habits if h["id"] not in completed_habit_ids
    ]

    if pending_habits:
        print(colored("  待打卡习惯:", Color.BOLD))
        for habit in pending_habits:
            streak = habit.get("streak", 0)
            streak_info = f" (连续{streak}天)" if streak > 0 else ""
            print(f"    {colored('[ ]', Color.YELLOW)} "
                  f"{habit['name']}{colored(streak_info, Color.DIM)}")
    else:
        print(colored("  所有习惯已打卡!", Color.GREEN))

    print()

    # 未完成的仪式
    active_rituals = [r for r in rituals if r.get("is_active", True)]
    today_execs = [e for e in executions if e["date"] == today]
    completed_ritual_ids = set(
        e["ritual_id"] for e in today_execs
        if e["status"] in ("completed", "skipped")
    )
    in_progress_ids = set(
        e["ritual_id"] for e in today_execs if e["status"] == "in_progress"
    )

    pending_rituals = [
        r for r in active_rituals
        if r["id"] not in completed_ritual_ids and r["id"] not in in_progress_ids
    ]
    in_progress_rituals = [
        r for r in active_rituals if r["id"] in in_progress_ids
    ]

    if in_progress_rituals:
        print(colored("  进行中的仪式:", Color.BOLD))
        for ritual in in_progress_rituals:
            print(f"    {colored('[>]', Color.YELLOW)} "
                  f"{ritual['name']} (进行中)")
        print()

    if pending_rituals:
        print(colored("  待执行仪式:", Color.BOLD))
        for ritual in pending_rituals:
            freq_map = {"daily": "每日", "weekly": "每周", "custom": "自定义"}
            freq = freq_map.get(ritual.get("frequency", "daily"),
                                ritual["frequency"])
            print(f"    {colored('[ ]', Color.YELLOW)} "
                  f"{ritual['name']} ({freq})")
    elif not in_progress_rituals:
        print(colored("  所有仪式已完成!", Color.GREEN))


def _print_habit_streaks(habits):
    """打印习惯连续天数概览

    Args:
        habits: 所有习惯列表
    """
    active_habits = [h for h in habits if h.get("is_active", True)]

    if not active_habits:
        return

    sorted_habits = sorted(
        active_habits,
        key=lambda h: h.get("streak", 0),
        reverse=True,
    )

    title_msg("习惯连续天数")
    print()

    for habit in sorted_habits[:5]:
        streak = habit.get("streak", 0)
        best = habit.get("best_streak", 0)

        # 进度条
        bar_len = 15
        filled = min(streak, bar_len)
        bar = colored("█" * filled, Color.GREEN) + \
              colored("░" * (bar_len - filled), Color.DIM)

        name = habit["name"][:15].ljust(15)
        print(f"  {name} {bar} "
              f"{colored(str(streak), Color.BOLD + Color.GREEN):>3}天 "
              f"{colored(f'(最长{best})', Color.DIM)}")


def _print_recent_activity(records, executions):
    """打印最近活动记录

    Args:
        records: 所有习惯记录
        executions: 所有仪式执行记录
    """
    title_msg("最近活动")
    print()

    # 合并并排序最近的记录
    activities = []

    for r in records[-10:]:
        activities.append({
            "type": "habit",
            "action": "完成打卡" if r["status"] == "completed" else "跳过",
            "name": _get_habit_name(r["habit_id"]),
            "time": r.get("created_at", ""),
            "status": r["status"],
        })

    for e in executions[-10:]:
        status_map = {
            "completed": "完成执行",
            "in_progress": "开始执行",
            "skipped": "跳过",
        }
        activities.append({
            "type": "ritual",
            "action": status_map.get(e["status"], e["status"]),
            "name": _get_ritual_name(e["ritual_id"]),
            "time": e.get("started_at", ""),
            "status": e["status"],
        })

    # 按时间排序，取最近5条
    activities.sort(key=lambda x: x["time"], reverse=True)

    if not activities:
        print(colored("  暂无活动记录", Color.DIM))
        return

    for activity in activities[:5]:
        time_str = activity["time"][:16] if activity["time"] else "N/A"

        if activity["status"] == "completed":
            icon = colored("●", Color.GREEN)
        elif activity["status"] == "skipped":
            icon = colored("○", Color.DIM)
        else:
            icon = colored("◐", Color.YELLOW)

        type_label = colored(
            "[习惯]" if activity["type"] == "habit" else "[仪式]",
            Color.DIM
        )
        name = activity["name"] or "未知"

        print(f"  {icon} {time_str} {type_label} "
              f"{name} - {activity['action']}")


def _print_quick_stats(habits, rituals, records, executions):
    """打印快速统计信息

    Args:
        habits: 所有习惯列表
        rituals: 所有仪式列表
        records: 所有习惯记录
        executions: 所有仪式执行记录
    """
    title_msg("快速统计")
    print()

    # 计算各项统计
    total_checkins = len([
        r for r in records if r["status"] == "completed"
    ])
    total_executions = len([
        e for e in executions if e["status"] == "completed"
    ])

    # 本周数据
    today = date.today()
    week_start = (today - timedelta(days=today.weekday())).isoformat()
    week_checkins = len([
        r for r in records
        if r["date"] >= week_start and r["status"] == "completed"
    ])
    week_executions = len([
        e for e in executions
        if e["date"] >= week_start and e["status"] == "completed"
    ])

    # 最长连续天数
    best_streak = 0
    for h in habits:
        if h.get("best_streak", 0) > best_streak:
            best_streak = h["best_streak"]

    # 总仪式执行时间
    total_time = sum(
        e.get("duration_seconds", 0)
        for e in executions
        if e["status"] == "completed"
    )

    stats = [
        ("累计打卡", f"{total_checkins} 次", Color.GREEN),
        ("本周打卡", f"{week_checkins} 次", Color.CYAN),
        ("仪式执行", f"{total_executions} 次", Color.MAGENTA),
        ("本周仪式", f"{week_executions} 次", Color.BRIGHT_CYAN),
        ("最长连续", f"{best_streak} 天", Color.YELLOW),
        ("仪式总时长", format_duration(total_time), Color.BRIGHT_WHITE),
    ]

    # 两列显示
    col_width = 30
    for i in range(0, len(stats), 2):
        line = "  "
        for j in range(2):
            if i + j < len(stats):
                label, value, color = stats[i + j]
                line += f"{label}: {colored(value, color)}"
                if j == 0:
                    line = line.ljust(col_width + 2)
        print(line)


def _print_footer(width):
    """打印仪表盘底部提示

    Args:
        width (int): 终端宽度
    """
    footer = " 使用 'devritual --help' 查看所有命令 "
    padding = (width - len(footer) - 4) // 2
    left_pad = "─" * padding
    right_pad = "─" * (width - len(footer) - 4 - padding)

    print(colored(f"  {left_pad}{footer}{right_pad}", Color.DIM))


def _get_habit_name(habit_id):
    """根据ID获取习惯名称

    Args:
        habit_id (str): 习惯ID

    Returns:
        str: 习惯名称，未找到返回"未知习惯"
    """
    habits = load_habits()
    for h in habits:
        if h["id"] == habit_id:
            return h["name"]
    return "未知习惯"


def _get_ritual_name(ritual_id):
    """根据ID获取仪式名称

    Args:
        ritual_id (str): 仪式ID

    Returns:
        str: 仪式名称，未找到返回"未知仪式"
    """
    rituals = load_rituals()
    for r in rituals:
        if r["id"] == ritual_id:
            return r["name"]
    return "未知仪式"
