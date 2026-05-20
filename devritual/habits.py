"""DevRitual 习惯追踪模块

提供习惯的创建、编辑、删除、列表查看、每日打卡和连续天数追踪功能。
支持从预设模板创建习惯，也支持自定义创建。
"""

from datetime import datetime, date, timedelta

from devritual.models import create_habit, create_habit_record, now_iso
from devritual.storage import (
    load_habits, save_habits, add_habit, update_habit, delete_habit,
    get_habit_by_name, get_habit_by_id,
    load_habit_records, save_habit_records, add_habit_record,
    get_habit_records, get_records_by_date
)
from devritual.templates import (
    get_habit_template, list_habit_templates
)
from devritual.utils import (
    Color, colored, bold, success_msg, error_msg, warning_msg,
    info_msg, title_msg, print_separator, prompt_input, prompt_yes_no,
    truncate_text
)
from devritual.models import today_str


def cmd_habit_create(args):
    """创建新习惯命令处理函数

    支持两种创建方式：
    1. 从预设模板创建（--template 参数）
    2. 交互式创建（逐步引导用户输入信息）

    Args:
        args: 命令行参数对象，包含 name, description, template 等属性
    """
    # 从模板创建
    if getattr(args, "template", None):
        habit = get_habit_template(args.template)
        if habit is None:
            error_msg(f"未找到模板: {args.template}")
            print("  可用模板:")
            for tid, tname, tdesc in list_habit_templates():
                print(f"    {colored(tid, Color.CYAN)} - {tname}: {tdesc}")
            return
        if args.name:
            habit["name"] = args.name
        add_habit(habit)
        success_msg(f"已从模板创建习惯: {habit['name']}")
        return

    # 交互式创建
    name = getattr(args, "name", None) or prompt_input("习惯名称")
    if not name:
        error_msg("习惯名称不能为空")
        return

    # 检查名称是否已存在
    existing = get_habit_by_name(name)
    if existing:
        error_msg(f"习惯 '{name}' 已存在")
        return

    description = getattr(args, "description", None) or prompt_input(
        "描述", ""
    )

    frequency_target = getattr(args, "frequency", "daily") or "daily"

    reminder_time = getattr(args, "reminder", None) or prompt_input(
        "提醒时间（HH:MM，留空不提醒）", ""
    )
    if not reminder_time:
        reminder_time = None

    habit = create_habit(
        name=name,
        description=description,
        frequency_target=frequency_target,
        reminder_time=reminder_time,
    )

    add_habit(habit)
    success_msg(f"习惯 '{name}' 创建成功！")
    _print_habit_detail(habit)


def cmd_habit_list(args):
    """列出所有习惯命令处理函数

    显示所有已创建的习惯，包括名称、连续天数、完成率等信息。

    Args:
        args: 命令行参数对象
    """
    habits = load_habits()

    if not habits:
        warning_msg("还没有创建任何习惯")
        info_msg("使用 'devritual habit create' 创建你的第一个习惯")
        return

    title_msg(f"习惯列表 ({len(habits)})")
    print()

    for i, habit in enumerate(habits, 1):
        # 状态标记
        if habit.get("is_active", True):
            status = colored("活跃", Color.GREEN)
        else:
            status = colored("停用", Color.DIM)

        # 连续天数
        streak = habit.get("streak", 0)
        best_streak = habit.get("best_streak", 0)
        total = habit.get("total_completions", 0)

        # 检查今天是否已打卡
        today_records = get_habit_records(habit["id"], today_str())
        checked_today = any(
            r["status"] == "completed" for r in today_records
        )
        if checked_today:
            check_mark = colored("[v]", Color.GREEN)
        else:
            check_mark = colored("[ ]", Color.DIM)

        print(f"  {check_mark} {colored(str(i).rjust(2), Color.DIM)}. "
              f"{bold(habit['name'])}  {status}")
        if habit.get("description"):
            print(f"        {truncate_text(habit['description'], 50)}")
        print(f"        连续: {colored(str(streak) + '天', Color.YELLOW)}  |  "
              f"最长: {best_streak}天  |  "
              f"累计: {total}次")
        print()


def cmd_habit_checkin(args):
    """习惯打卡命令处理函数

    为指定习惯记录一次打卡。如果今天已经打过卡，则提示用户。

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    habit = get_habit_by_name(args.name)
    if not habit:
        error_msg(f"未找到习惯: {args.name}")
        return

    # 检查今天是否已打卡
    today_records = get_habit_records(habit["id"], today_str())
    completed_today = [
        r for r in today_records if r["status"] == "completed"
    ]

    if completed_today:
        warning_msg(f"习惯 '{habit['name']}' 今天已经打卡过了")
        return

    # 创建打卡记录
    record = create_habit_record(
        habit_id=habit["id"],
        date_str=today_str(),
        status="completed",
    )
    add_habit_record(record)

    # 更新习惯统计
    _update_habit_streak(habit)

    success_msg(f"习惯 '{habit['name']}' 打卡成功！")
    info_msg(f"当前连续天数: {habit.get('streak', 0)} 天")


def cmd_habit_skip(args):
    """跳过习惯打卡命令处理函数

    记录一次跳过，不影响连续天数（连续天数会被重置）。

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    habit = get_habit_by_name(args.name)
    if not habit:
        error_msg(f"未找到习惯: {args.name}")
        return

    # 检查今天是否已有记录
    today_records = get_habit_records(habit["id"], today_str())
    if today_records:
        warning_msg(f"习惯 '{habit['name']}' 今天已有记录")
        return

    record = create_habit_record(
        habit_id=habit["id"],
        date_str=today_str(),
        status="skipped",
    )
    add_habit_record(record)

    # 重置连续天数
    update_habit(habit["id"], {
        "streak": 0,
        "updated_at": now_iso(),
    })

    info_msg(f"习惯 '{habit['name']}' 已标记为跳过")


def cmd_habit_streak(args):
    """查看习惯连续天数命令处理函数

    显示指定习惯的当前连续天数、最长连续天数和完成统计。

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    habit = get_habit_by_name(args.name)
    if not habit:
        error_msg(f"未找到习惯: {args.name}")
        return

    # 重新计算连续天数以确保准确
    streak = _calculate_streak(habit["id"])
    best_streak = _calculate_best_streak(habit["id"])

    # 更新习惯数据
    update_habit(habit["id"], {
        "streak": streak,
        "best_streak": max(best_streak, habit.get("best_streak", 0)),
        "updated_at": now_iso(),
    })

    title_msg(f"习惯连续天数: {habit['name']}")
    print()

    # 当前连续天数 - 用进度条显示
    current = streak
    bar_length = 20
    filled = min(current, bar_length)
    bar = colored("█" * filled, Color.GREEN) + \
          colored("░" * (bar_length - filled), Color.DIM)
    print(f"  当前连续: {colored(str(current), Color.BOLD + Color.GREEN)} 天")
    print(f"  {bar}")
    print()

    # 最长连续天数
    best = max(best_streak, habit.get("best_streak", 0))
    print(f"  最长连续: {colored(str(best), Color.YELLOW)} 天")
    print(f"  累计完成: {habit.get('total_completions', 0)} 次")
    print(f"  创建时间: {habit.get('created_at', 'N/A')[:10]}")
    print()

    # 最近7天打卡情况
    _print_recent_checkins(habit["id"], 7)


def cmd_habit_edit(args):
    """编辑习惯命令处理函数

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    habit = get_habit_by_name(args.name)
    if not habit:
        error_msg(f"未找到习惯: {args.name}")
        return

    print(f"  当前名称: {habit['name']}")

    new_name = prompt_input("新名称（留空保持不变）", habit["name"])
    if new_name != habit["name"]:
        existing = get_habit_by_name(new_name)
        if existing and existing["id"] != habit["id"]:
            error_msg(f"名称 '{new_name}' 已被使用")
            return

    new_desc = prompt_input("新描述（留空保持不变）",
                            habit.get("description", ""))

    freq_map = {"daily": "每日", "weekly": "每周", "custom": "自定义"}
    current_freq = habit.get("frequency_target", "daily")
    print(f"  当前频率: {freq_map.get(current_freq, current_freq)}")
    new_freq = prompt_input("新频率 (daily/weekly/custom)", current_freq)

    reminder = habit.get("reminder_time", "") or ""
    new_reminder = prompt_input("提醒时间（HH:MM，留空不提醒）", reminder)
    if not new_reminder:
        new_reminder = None

    updates = {
        "name": new_name,
        "description": new_desc,
        "frequency_target": new_freq,
        "reminder_time": new_reminder,
        "updated_at": now_iso(),
    }

    update_habit(habit["id"], updates)
    success_msg(f"习惯 '{new_name}' 更新成功！")


def cmd_habit_delete(args):
    """删除习惯命令处理函数

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    habit = get_habit_by_name(args.name)
    if not habit:
        error_msg(f"未找到习惯: {args.name}")
        return

    if not prompt_yes_no(f"确定要删除习惯 '{habit['name']}' 吗？", False):
        info_msg("已取消删除")
        return

    delete_habit(habit["id"])
    success_msg(f"习惯 '{habit['name']}' 已删除")


def cmd_habit_templates(args):
    """列出所有可用的习惯模板

    Args:
        args: 命令行参数对象（未使用）
    """
    templates = list_habit_templates()

    title_msg("可用习惯模板")
    print()

    for tid, tname, tdesc in templates:
        print(f"  {colored(tid, Color.CYAN)}")
        print(f"    {bold(tname)}")
        print(f"    {tdesc}")
        print()


# ============================================================
# 内部辅助函数
# ============================================================

def _update_habit_streak(habit):
    """更新习惯的连续天数和累计完成次数

    Args:
        habit (dict): 习惯数据字典
    """
    streak = _calculate_streak(habit["id"])
    best_streak = _calculate_best_streak(habit["id"])

    update_habit(habit["id"], {
        "streak": streak,
        "best_streak": max(best_streak, habit.get("best_streak", 0)),
        "total_completions": habit.get("total_completions", 0) + 1,
        "updated_at": now_iso(),
    })


def _calculate_streak(habit_id):
    """计算指定习惯的当前连续天数

    从今天开始往前逐天检查，直到找到未完成的日期为止。

    Args:
        habit_id (str): 习惯ID

    Returns:
        int: 当前连续天数
    """
    records = load_habit_records()
    habit_records = {
        r["date"]: r["status"]
        for r in records
        if r["habit_id"] == habit_id and r["status"] == "completed"
    }

    streak = 0
    today = date.today()

    for i in range(365):  # 最多检查一年
        check_date = (today - timedelta(days=i)).isoformat()
        if check_date in habit_records:
            streak += 1
        else:
            break

    return streak


def _calculate_best_streak(habit_id):
    """计算指定习惯的历史最长连续天数

    Args:
        habit_id (str): 习惯ID

    Returns:
        int: 历史最长连续天数
    """
    records = load_habit_records()
    habit_records = sorted(
        [r for r in records
         if r["habit_id"] == habit_id and r["status"] == "completed"],
        key=lambda r: r["date"],
    )

    if not habit_records:
        return 0

    best_streak = 1
    current_streak = 1

    for i in range(1, len(habit_records)):
        prev_date = date.fromisoformat(habit_records[i - 1]["date"])
        curr_date = date.fromisoformat(habit_records[i]["date"])

        if (curr_date - prev_date).days == 1:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        elif (curr_date - prev_date).days > 1:
            current_streak = 1

    return best_streak


def _print_recent_checkins(habit_id, days):
    """打印最近N天的打卡情况

    Args:
        habit_id (str): 习惯ID
        days (int): 显示天数
    """
    records = load_habit_records()
    habit_records = {
        r["date"]: r["status"]
        for r in records
        if r["habit_id"] == habit_id
    }

    today = date.today()
    print(colored("  最近打卡记录:", Color.BOLD))
    line = "    "
    for i in range(days - 1, -1, -1):
        check_date = (today - timedelta(days=i)).isoformat()
        weekday = (today - timedelta(days=i)).strftime("%a")
        status = habit_records.get(check_date)

        if status == "completed":
            mark = colored("●", Color.GREEN)
        elif status == "skipped":
            mark = colored("○", Color.DIM)
        else:
            mark = colored("○", Color.RED)

        line += f"{mark} {check_date[5:]}({weekday})  "
        if (days - i) % 4 == 0 and i > 0:
            print(line)
            line = "    "

    if line.strip():
        print(line)
    print()


def _print_habit_detail(habit):
    """打印习惯的详细信息

    Args:
        habit (dict): 习惯数据字典
    """
    freq_map = {"daily": "每日", "weekly": "每周", "custom": "自定义"}
    freq = freq_map.get(
        habit.get("frequency_target", "daily"),
        habit["frequency_target"]
    )

    title_msg(f"习惯详情: {habit['name']}")
    print()
    if habit.get("description"):
        print(f"  描述: {habit['description']}")
    print(f"  频率: {freq}")
    if habit.get("reminder_time"):
        print(f"  提醒时间: {habit['reminder_time']}")
    print(f"  创建时间: {habit.get('created_at', 'N/A')[:10]}")
    print()
