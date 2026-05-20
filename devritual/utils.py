"""DevRitual 工具函数模块

提供ANSI颜色输出、日期处理、格式化等通用工具函数。
"""

import os
import sys
import json
import shutil
from datetime import datetime, date, timedelta


# ============================================================
# ANSI 颜色常量定义
# ============================================================

class Color:
    """ANSI终端颜色常量类

    提供常用的终端颜色和样式常量，用于美化CLI输出。
    使用方法: f"{Color.RED}错误信息{Color.RESET}"
    """

    # 基础颜色
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 亮色
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def colored(text, color):
    """为文本添加ANSI颜色

    Args:
        text (str): 需要着色的文本
        color (str): ANSI颜色代码（如 Color.RED）

    Returns:
        str: 带有ANSI颜色代码的文本
    """
    return f"{color}{text}{Color.RESET}"


def bold(text):
    """将文本加粗显示

    Args:
        text (str): 需要加粗的文本

    Returns:
        str: 带有加粗ANSI代码的文本
    """
    return colored(text, Color.BOLD)


def success_msg(text):
    """输出成功信息（绿色）

    Args:
        text (str): 成功信息文本
    """
    print(colored(f"  {text}", Color.GREEN))


def error_msg(text):
    """输出错误信息（红色）

    Args:
        text (str): 错误信息文本
    """
    print(colored(f"  错误: {text}", Color.RED), file=sys.stderr)


def warning_msg(text):
    """输出警告信息（黄色）

    Args:
        text (str): 警告信息文本
    """
    print(colored(f"  警告: {text}", Color.YELLOW))


def info_msg(text):
    """输出信息提示（蓝色）

    Args:
        text (str): 信息文本
    """
    print(colored(f"  {text}", Color.CYAN))


def title_msg(text):
    """输出标题信息（加粗青色）

    Args:
        text (str): 标题文本
    """
    print()
    print(colored(f"  {text}", Color.BOLD + Color.CYAN))
    print(colored("  " + "─" * len(text), Color.CYAN))


def get_data_dir():
    """获取DevRitual数据目录路径

    默认为用户主目录下的 .devritual/ 目录。

    Returns:
        str: 数据目录的绝对路径
    """
    return os.path.join(os.path.expanduser("~"), ".devritual")


def ensure_data_dir():
    """确保数据目录存在

    如果数据目录不存在则创建它。

    Returns:
        str: 数据目录的绝对路径
    """
    data_dir = get_data_dir()
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def is_initialized():
    """检查DevRitual是否已初始化

    通过检查数据目录中是否存在 rituals.json 文件来判断。

    Returns:
        bool: 如果已初始化返回True，否则返回False
    """
    data_dir = get_data_dir()
    return os.path.exists(os.path.join(data_dir, "rituals.json"))


def get_date_range(days):
    """获取最近N天的日期列表

    Args:
        days (int): 天数

    Returns:
        list: 日期字符串列表，从最早到最近排序
    """
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]


def format_duration(seconds):
    """将秒数格式化为可读的时间字符串

    Args:
        seconds (int): 秒数

    Returns:
        str: 格式化后的时间字符串，如 "1h 23m" 或 "45s"
    """
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"{hours}h"
    return f"{hours}h {remaining_minutes}m"


def format_percentage(value, total):
    """计算并格式化百分比

    Args:
        value (int): 实际值
        total (int): 总数

    Returns:
        str: 格式化后的百分比字符串，如 "85.0%"
    """
    if total == 0:
        return "0.0%"
    return f"{(value / total) * 100:.1f}%"


def truncate_text(text, max_length=50):
    """截断过长的文本

    如果文本超过最大长度，则在末尾添加省略号。

    Args:
        text (str): 原始文本
        max_length (int): 最大长度，默认为50

    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def get_terminal_width():
    """获取终端宽度

    尝试获取终端的列数，如果获取失败则返回默认值80。

    Returns:
        int: 终端宽度（列数）
    """
    try:
        size = shutil.get_terminal_size()
        return size.columns
    except Exception:
        return 80


def print_separator(char="─", length=None):
    """打印分隔线

    Args:
        char (str): 分隔符字符，默认为 "─"
        length (int): 分隔线长度，默认为终端宽度
    """
    if length is None:
        length = get_terminal_width()
    print(colored(char * length, Color.DIM))


def parse_date(date_str):
    """解析日期字符串为date对象

    Args:
        date_str (str): 日期字符串，格式为 YYYY-MM-DD

    Returns:
        date: 解析后的日期对象

    Raises:
        ValueError: 如果日期格式无效
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"无效的日期格式: {date_str}，请使用 YYYY-MM-DD 格式")


def prompt_input(prompt_text, default=None):
    """交互式输入提示

    Args:
        prompt_text (str): 提示文本
        default (str): 默认值，如果用户直接回车则使用此值

    Returns:
        str: 用户输入的值，或默认值
    """
    if default is not None:
        prompt = f"  {prompt_text} [{default}]: "
    else:
        prompt = f"  {prompt_text}: "
    value = input(prompt).strip()
    if not value and default is not None:
        return default
    return value


def prompt_yes_no(prompt_text, default=True):
    """交互式是/否确认

    Args:
        prompt_text (str): 提示文本
        default (bool): 默认值

    Returns:
        bool: 用户选择的结果
    """
    default_str = "Y/n" if default else "y/N"
    prompt = f"  {prompt_text} [{default_str}]: "
    value = input(prompt).strip().lower()
    if not value:
        return default
    return value in ("y", "yes", "是")
