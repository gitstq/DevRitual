"""DevRitual 统计分析模块

提供多维度的统计分析功能，包括：
- 每日/每周/每月完成率
- 习惯连续天数排行
- 仪式执行时间统计
- 热力图日历（终端ASCII渲染）
- 趋势分析
"""

from datetime import date, timedelta

from devritual.storage import (
    load_habits, load_habit_records, load_rituals, load_ritual_executions
)
from devritual.utils import (
    Color, colored, bold, success_msg, error_msg, warning_msg,
    info_msg, title_msg, print_separator, format_duration,
    format_percentage, get_date_range, truncate_text
)
from devritual.models import today_str


def cmd_stats(args):
    """查看总体统计命令处理函数

    显示所有习惯和仪式的汇总统计数据。

    Args:
        args: 命令行参数对象
    """
    habits = load_habits()
    rituals = load_rituals()
    records = load_habit_records()
    executions = load_ritual_executions()

    title_msg("DevRitual 统计概览")
    print()

    # 基本统计
    active_habits = [h for h in habits if h.get("is_active", True)]
    active_rituals = [r for r in rituals if r.get("is_active", True)]

    print(f"  活跃习惯: {colored(str(len(active_habits)), Color.BOLD + Color.GREEN)}")
    print(f"  活跃仪式: {colored(str(len(active_rituals)), Color.BOLD + Color.CYAN)}")
    print(f"  总打卡次数: {len([r for r in records if r['status'] == 'completed'])}")
    print(f"  仪式执行次数: {len([e for e in executions if e['status'] == 'completed'])}")
    print()

    # 今日完成情况
    _print_today_summary(records, executions, habits, rituals)
    print()

    # 本周完成情况
    _print_week_summary(records, executions, habits, rituals)
    print()

    # 习惯连续天数排行
    _print_streak_ranking(habits)
    print()

    # 仪式执行时间统计
    _print_ritual_time_stats(executions, rituals)


def cmd_stats_calendar(args):
    """热力图日历命令处理函数

    在终端中渲染最近N天的热力图日历，显示每日的完成情况。
    使用Unicode方块字符表示不同的完成程度。

    Args:
        args: 命令行参数对象，包含 days 属性
    """
    days = getattr(args, "days", 90)
    habits = load_habits()
    records = load_habit_records()

    title_msg(f"习惯热力图日历 (最近 {days} 天)")
    print()

    if not habits:
        warning_msg("还没有创建任何习惯")
        return

    # 计算每天的完成率
    date_completion = {}
    active_habit_ids = [h["id"] for h in habits if h.get("is_active", True)]
    active_count = len(active_habit_ids)

    if active_count == 0:
        warning_msg("没有活跃的习惯")
        return

    date_list = get_date_range(days)
    for d in date_list:
        day_records = [
            r for r in records
            if r["date"] == d and r["habit_id"] in active_habit_ids
            and r["status"] == "completed"
        ]
        completed = len(set(r["habit_id"] for r in day_records))
        date_completion[d] = completed / active_count

    # 渲染热力图
    _render_heatmap(date_list, date_completion)

    # 图例
    print()
    print("  图例: ")
    _print_legend()

    # 统计信息
    total_days = len(date_list)
    active_days = sum(1 for d in date_list if date_completion.get(d, 0) > 0)
    perfect_days = sum(
        1 for d in date_list if date_completion.get(d, 0) >= 1.0
    )
    avg_rate = sum(date_completion.get(d, 0) for d in date_list) / total_days

    print()
    print(f"  活跃天数: {colored(str(active_days), Color.GREEN)}/{total_days}")
    print(f"  完美天数: {colored(str(perfect_days), Color.BOLD + Color.GREEN)}/{total_days}")
    print(f"  平均完成率: {colored(format_percentage(avg_rate * active_count, active_count), Color.CYAN)}")
    print()


def cmd_stats_trend(args):
    """趋势分析命令处理函数

    显示最近N天的完成趋势，包括每日完成数量和完成率的变化。

    Args:
        args: 命令行参数对象，包含 days 属性
    """
    days = getattr(args, "days", 30)
    habits = load_habits()
    records = load_habit_records()
    executions = load_ritual_executions()

    title_msg(f"趋势分析 (最近 {days} 天)")
    print()

    if not habits:
        warning_msg("还没有创建任何习惯")
        return

    active_habit_ids = [h["id"] for h in habits if h.get("is_active", True)]
    active_count = len(active_habit_ids)

    date_list = get_date_range(days)

    # 计算每天的数据
    daily_data = []
    for d in date_list:
        habit_completed = len([
            r for r in records
            if r["date"] == d and r["habit_id"] in active_habit_ids
            and r["status"] == "completed"
        ])
        ritual_completed = len([
            e for e in executions
            if e["date"] == d and e["status"] == "completed"
        ])
        rate = habit_completed / active_count if active_count > 0 else 0
        daily_data.append({
            "date": d,
            "habits": habit_completed,
            "rituals": ritual_completed,
            "rate": rate,
        })

    # 习惯完成趋势图
    _print_trend_chart(daily_data, "习惯完成趋势", "habits", active_count)
    print()

    # 完成率趋势图
    _print_trend_chart(daily_data, "完成率趋势 (%)", "rate", 100)
    print()

    # 周对比
    _print_week_comparison(daily_data)
    print()


# ============================================================
# 内部辅助函数
# ============================================================

def _print_today_summary(records, executions, habits, rituals):
    """打印今日完成情况汇总

    Args:
        records: 所有习惯记录
        executions: 所有仪式执行记录
        habits: 所有习惯
        rituals: 所有仪式
    """
    today = today_str()
    active_habits = [h for h in habits if h.get("is_active", True)]
    active_rituals = [r for r in rituals if r.get("is_active", True)]

    # 今日习惯完成情况
    today_records = [
        r for r in records
        if r["date"] == today and r["status"] == "completed"
    ]
    completed_habit_ids = set(r["habit_id"] for r in today_records)
    today_habit_count = len([
        h for h in active_habits if h["id"] in completed_habit_ids
    ])

    # 今日仪式完成情况
    today_executions = [
        e for e in executions
        if e["date"] == today and e["status"] == "completed"
    ]
    completed_ritual_ids = set(e["ritual_id"] for e in today_executions)
    today_ritual_count = len([
        r for r in active_rituals if r["id"] in completed_ritual_ids
    ])

    print(colored("  今日完成情况:", Color.BOLD))
    habit_pct = format_percentage(today_habit_count, len(active_habits)) \
        if active_habits else "N/A"
    ritual_pct = format_percentage(today_ritual_count, len(active_rituals)) \
        if active_rituals else "N/A"

    print(f"    习惯: {today_habit_count}/{len(active_habits)} "
          f"({habit_pct})")
    print(f"    仪式: {today_ritual_count}/{len(active_rituals)} "
          f"({ritual_pct})")


def _print_week_summary(records, executions, habits, rituals):
    """打印本周完成情况汇总

    Args:
        records: 所有习惯记录
        executions: 所有仪式执行记录
        habits: 所有习惯
        rituals: 所有仪式
    """
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # 本周一

    active_habits = [h for h in habits if h.get("is_active", True)]
    active_rituals = [r for r in rituals if r.get("is_active", True)]

    # 本周习惯完成情况
    week_dates = [(week_start + timedelta(days=i)).isoformat()
                  for i in range(7)]
    week_records = [
        r for r in records
        if r["date"] in week_dates and r["status"] == "completed"
    ]

    # 计算本周每天的习惯完成数
    total_possible = len(active_habits) * 7
    unique_completions = set()
    for r in week_records:
        unique_completions.add((r["habit_id"], r["date"]))
    week_habit_completions = len(unique_completions)

    # 本周仪式完成情况
    week_executions = [
        e for e in executions
        if e["date"] in week_dates and e["status"] == "completed"
    ]
    week_ritual_completions = len(set(
        e["ritual_id"] for e in week_executions
    ))

    print(colored("  本周完成情况:", Color.BOLD))
    habit_pct = format_percentage(
        week_habit_completions, total_possible
    ) if total_possible > 0 else "N/A"
    ritual_pct = format_percentage(
        week_ritual_completions, len(active_rituals) * 7
    ) if active_rituals else "N/A"

    print(f"    习惯: {week_habit_completions}/{total_possible} "
          f"({habit_pct})")
    print(f"    仪式: {week_ritual_completions}/{len(active_rituals) * 7} "
          f"({ritual_pct})")


def _print_streak_ranking(habits):
    """打印习惯连续天数排行榜

    Args:
        habits: 所有习惯列表
    """
    active_habits = [h for h in habits if h.get("is_active", True)]

    if not active_habits:
        return

    # 按连续天数排序
    sorted_habits = sorted(
        active_habits,
        key=lambda h: h.get("streak", 0),
        reverse=True,
    )

    print(colored("  习惯连续天数排行:", Color.BOLD))

    for i, habit in enumerate(sorted_habits[:10], 1):
        streak = habit.get("streak", 0)
        best = habit.get("best_streak", 0)

        # 排名标记
        if i == 1 and streak > 0:
            rank = colored("1.", Color.YELLOW + Color.BOLD)
        elif i == 2 and streak > 0:
            rank = colored("2.", Color.BRIGHT_WHITE)
        elif i == 3 and streak > 0:
            rank = colored("3.", Color.RED)
        else:
            rank = colored(f"{i}.", Color.DIM)

        # 连续天数进度条
        bar_len = min(streak, 20)
        bar = colored("█" * bar_len, Color.GREEN) + \
              colored("░" * (20 - bar_len), Color.DIM)

        name = truncate_text(habit["name"], 20)
        print(f"    {rank} {name.ljust(22)} "
              f"{bar} {colored(str(streak), Color.GREEN)}天"
              f" (最长{best}天)")


def _print_ritual_time_stats(executions, rituals):
    """打印仪式执行时间统计

    Args:
        executions: 所有仪式执行记录
        rituals: 所有仪式列表
    """
    completed = [e for e in executions if e["status"] == "completed"]

    if not completed:
        return

    print(colored("  仪式执行时间统计:", Color.BOLD))

    # 按仪式分组统计
    ritual_map = {r["id"]: r["name"] for r in rituals}
    ritual_stats = {}

    for e in completed:
        rid = e["ritual_id"]
        if rid not in ritual_stats:
            ritual_stats[rid] = {
                "name": ritual_map.get(rid, "未知仪式"),
                "count": 0,
                "total_time": 0,
            }
        ritual_stats[rid]["count"] += 1
        ritual_stats[rid]["total_time"] += e.get("duration_seconds", 0)

    for rid, stats in sorted(ritual_stats.items(),
                             key=lambda x: x[1]["total_time"],
                             reverse=True):
        avg_time = stats["total_time"] // stats["count"] \
            if stats["count"] > 0 else 0
        name = truncate_text(stats["name"], 20)
        print(f"    {name.ljust(22)} "
              f"执行{stats['count']}次  "
              f"平均{format_duration(avg_time)}  "
              f"总计{format_duration(stats['total_time'])}")


def _render_heatmap(date_list, date_completion):
    """渲染热力图日历

    使用Unicode方块字符在终端中渲染热力图。
    每周一行，共显示最近N天的数据。

    Args:
        date_list (list): 日期字符串列表
        date_completion (dict): 日期到完成率的映射
    """
    # 热力图颜色级别
    levels = [
        (0.0, Color.DIM),        # 无数据 - 暗灰
        (0.01, "\033[48;5;22m"),  # 1-25% - 深绿
        (0.26, "\033[48;5;28m"),  # 26-50% - 绿色
        (0.51, "\033[48;5;34m"),  # 51-75% - 亮绿
        (0.76, "\033[48;5;46m"),  # 76-99% - 更亮绿
        (1.0, "\033[48;5;82m"),   # 100% - 最亮绿
    ]

    def get_level_color(rate):
        """根据完成率获取对应的颜色代码"""
        if rate <= 0:
            return levels[0][1]
        for threshold, color in reversed(levels):
            if rate >= threshold:
                return color
        return levels[0][1]

    def get_block(rate):
        """根据完成率获取对应的方块字符"""
        if rate <= 0:
            return "░"
        elif rate < 0.25:
            return "▒"
        elif rate < 0.5:
            return "▓"
        elif rate < 0.75:
            return "▒"
        else:
            return "█"

    # 按周分组
    weeks = []
    current_week = []

    for d in date_list:
        current_week.append(d)
        dt = date.fromisoformat(d)
        if dt.weekday() == 6:  # 周日
            weeks.append(current_week)
            current_week = []

    if current_week:
        weeks.append(current_week)

    # 月份标签
    month_labels = {}
    for i, d in enumerate(date_list):
        dt = date.fromisoformat(d)
        month_key = dt.strftime("%Y-%m")
        if month_key not in month_labels:
            month_labels[month_key] = i

    # 打印月份标签
    print("    ", end="")
    last_month = ""
    for d in date_list:
        dt = date.fromisoformat(d)
        month = dt.strftime("%m月")
        if month != last_month:
            print(colored(month, Color.DIM), end=" ")
            last_month = month
        else:
            print("   ", end="")
    print()

    # 打印星期标签
    weekday_names = ["一", "", "三", "", "五", "", "日"]
    print("    ", end="")
    for name in weekday_names:
        if name:
            print(colored(name, Color.DIM), end="  ")
        else:
            print("   ", end="")
    print()

    # 打印热力图
    for week in weeks:
        # 周标签
        if week:
            first_dt = date.fromisoformat(week[0])
            week_label = f"{first_dt.strftime('%m/%d')}"
            print(f"  {colored(week_label, Color.DIM)} ", end="")
        else:
            print("         ", end="")

        for d in week:
            rate = date_completion.get(d, 0)
            color = get_level_color(rate)
            block = get_block(rate)

            # 使用背景色
            print(f"{color} {block} {Color.RESET}", end="")

        print()


def _print_legend():
    """打印热力图图例"""
    print("    ", end="")
    labels = ["无", "少", "中", "多", "全"]
    colors = [
        Color.DIM,
        "\033[48;5;22m",
        "\033[48;5;28m",
        "\033[48;5;34m",
        "\033[48;5;82m",
    ]
    blocks = ["░", "▒", "▓", "▒", "█"]

    for label, color, block in zip(labels, colors, blocks):
        print(f"{color} {block} {Color.RESET} {label}  ", end="")
    print()


def _print_trend_chart(daily_data, title, key, max_val):
    """打印简单的终端趋势图

    使用Unicode字符绘制竖向柱状图。

    Args:
        daily_data (list): 每日数据列表
        title (str): 图表标题
        key (str): 数据键名
        max_val (int): 最大值（用于归一化）
    """
    print(colored(f"  {title}:", Color.BOLD))

    if not daily_data:
        print("    暂无数据")
        return

    # 计算图表高度
    chart_height = 10
    chart_width = min(len(daily_data), 50)

    # 取最近的数据
    data = daily_data[-chart_width:]

    # 归一化数据
    values = []
    for d in data:
        if key == "rate":
            values.append(int(d[key] * 100))
        else:
            values.append(d[key])

    actual_max = max(values) if values else 1
    if actual_max == 0:
        actual_max = 1

    # 绘制图表
    for row in range(chart_height, 0, -1):
        threshold = (row / chart_height) * actual_max
        line = f"    {str(int(threshold)).rjust(4)} │ "

        for val in values:
            if val >= threshold:
                # 根据值选择颜色
                ratio = val / actual_max
                if ratio >= 0.8:
                    line += colored("█", Color.GREEN)
                elif ratio >= 0.5:
                    line += colored("█", Color.YELLOW)
                else:
                    line += colored("█", Color.CYAN)
            else:
                line += colored("░", Color.DIM)
            line += " "

        print(line)

    # X轴
    print("        └" + "─" * (chart_width * 2 - 1))

    # 日期标签（只显示首尾）
    if len(data) >= 2:
        first_date = data[0]["date"][5:]  # MM-DD
        last_date = data[-1]["date"][5:]
        print(f"         {first_date}{' ' * (chart_width * 2 - 12)}{last_date}")


def _print_week_comparison(daily_data):
    """打印周对比数据

    Args:
        daily_data (list): 每日数据列表
    """
    if len(daily_data) < 14:
        return

    print(colored("  周对比:", Color.BOLD))

    # 将数据按周分组
    weeks = []
    for i in range(0, len(daily_data), 7):
        week_data = daily_data[i:i + 7]
        if week_data:
            avg_rate = sum(d["rate"] for d in week_data) / len(week_data)
            total_habits = sum(d["habits"] for d in week_data)
            weeks.append({
                "start": week_data[0]["date"],
                "avg_rate": avg_rate,
                "total_habits": total_habits,
            })

    if len(weeks) >= 2:
        this_week = weeks[-1]
        last_week = weeks[-2]

        rate_change = this_week["avg_rate"] - last_week["avg_rate"]
        habit_change = this_week["total_habits"] - last_week["total_habits"]

        if rate_change > 0:
            change_str = colored(f"+{rate_change:.1%}", Color.GREEN)
        elif rate_change < 0:
            change_str = colored(f"{rate_change:.1%}", Color.RED)
        else:
            change_str = colored("持平", Color.DIM)

        if habit_change > 0:
            habit_str = colored(f"+{habit_change}", Color.GREEN)
        elif habit_change < 0:
            habit_str = colored(f"{habit_change}", Color.RED)
        else:
            habit_str = colored("持平", Color.DIM)

        print(f"    完成率: {change_str}  "
              f"(上周 {last_week['avg_rate']:.0%} → "
              f"本周 {this_week['avg_rate']:.0%})")
        print(f"    习惯数: {habit_str}  "
              f"(上周 {last_week['total_habits']} → "
              f"本周 {this_week['total_habits']})")
