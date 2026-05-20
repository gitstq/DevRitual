"""DevRitual 数据模型模块

定义所有核心数据结构，包括仪式(Ritual)、习惯(Habit)、
习惯记录(HabitRecord)和仪式执行记录(RitualExecution)。
所有模型均使用字典结构，便于JSON序列化。
"""

import time
import uuid
from datetime import datetime, date


def generate_id():
    """生成唯一的ID标识符

    使用UUID4生成全局唯一标识符，用于仪式和习惯的唯一标识。

    Returns:
        str: 32位十六进制字符串形式的UUID
    """
    return uuid.uuid4().hex


def now_iso():
    """获取当前时间的ISO格式字符串

    Returns:
        str: ISO 8601格式的当前时间字符串
    """
    return datetime.now().isoformat()


def today_str():
    """获取今天的日期字符串（YYYY-MM-DD格式）

    Returns:
        str: 今天的日期字符串
    """
    return date.today().isoformat()


def create_ritual(name, description="", steps=None, estimated_time=0,
                  tags=None, frequency="daily"):
    """创建一个新的仪式对象

    Args:
        name (str): 仪式名称
        description (str): 仪式描述，默认为空
        steps (list): 仪式步骤列表，每个步骤为字符串，默认为空列表
        estimated_time (int): 预估执行时间（分钟），默认为0
        tags (list): 标签列表，默认为空列表
        frequency (str): 频率，可选值: daily/weekly/custom，默认为daily

    Returns:
        dict: 仪式数据字典，包含所有字段和元数据
    """
    if steps is None:
        steps = []
    if tags is None:
        tags = []

    return {
        "id": generate_id(),
        "name": name,
        "description": description,
        "steps": steps,
        "estimated_time": estimated_time,
        "tags": tags,
        "frequency": frequency,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "is_active": True,
    }


def create_habit(name, description="", frequency_target="daily",
                 reminder_time=None):
    """创建一个新的习惯对象

    Args:
        name (str): 习惯名称
        description (str): 习惯描述，默认为空
        frequency_target (str): 频率目标，可选值: daily/weekly/custom，
                                默认为daily
        reminder_time (str): 提醒时间（HH:MM格式），默认为None

    Returns:
        dict: 习惯数据字典，包含所有字段和元数据
    """
    return {
        "id": generate_id(),
        "name": name,
        "description": description,
        "frequency_target": frequency_target,
        "reminder_time": reminder_time,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "is_active": True,
        "streak": 0,
        "best_streak": 0,
        "total_completions": 0,
    }


def create_habit_record(habit_id, date_str=None, status="completed"):
    """创建一条习惯打卡记录

    Args:
        habit_id (str): 关联的习惯ID
        date_str (str): 日期字符串，默认为今天
        status (str): 记录状态，可选值: completed/skipped，默认为completed

    Returns:
        dict: 习惯记录数据字典
    """
    if date_str is None:
        date_str = today_str()

    return {
        "id": generate_id(),
        "habit_id": habit_id,
        "date": date_str,
        "status": status,
        "created_at": now_iso(),
    }


def create_ritual_execution(ritual_id, status="completed",
                            duration_seconds=0, notes=""):
    """创建一条仪式执行记录

    Args:
        ritual_id (str): 关联的仪式ID
        status (str): 执行状态，可选值: completed/paused/skipped，
                      默认为completed
        duration_seconds (int): 实际执行时长（秒），默认为0
        notes (str): 执行备注，默认为空

    Returns:
        dict: 仪式执行记录数据字典
    """
    return {
        "id": generate_id(),
        "ritual_id": ritual_id,
        "date": today_str(),
        "status": status,
        "duration_seconds": duration_seconds,
        "notes": notes,
        "started_at": now_iso(),
        "completed_at": now_iso(),
    }


def create_ritual_execution_started(ritual_id):
    """创建一条仪式开始执行的记录

    与 create_ritual_execution 不同，此方法标记仪式为进行中状态，
    started_at 和 completed_at 使用相同值，后续完成时更新 completed_at。

    Args:
        ritual_id (str): 关联的仪式ID

    Returns:
        dict: 仪式执行记录数据字典（进行中状态）
    """
    now = now_iso()
    return {
        "id": generate_id(),
        "ritual_id": ritual_id,
        "date": today_str(),
        "status": "in_progress",
        "duration_seconds": 0,
        "notes": "",
        "started_at": now,
        "completed_at": now,
    }
