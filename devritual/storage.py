"""DevRitual 数据存储模块

负责所有数据的持久化操作，包括仪式、习惯、记录的增删改查，
以及数据的导入导出和备份恢复。
所有数据以JSON格式存储在用户主目录的 ~/.devritual/ 下。
"""

import os
import json
import shutil
from datetime import datetime

from devritual.utils import (
    ensure_data_dir, get_data_dir, error_msg, success_msg
)


# ============================================================
# 数据文件名常量
# ============================================================

FILE_RITUALS = "rituals.json"           # 仪式数据文件
FILE_HABITS = "habits.json"             # 习惯数据文件
FILE_HABIT_RECORDS = "habit_records.json"  # 习惯打卡记录文件
FILE_RITUAL_EXECUTIONS = "ritual_executions.json"  # 仪式执行记录文件
FILE_CONFIG = "config.json"             # 配置文件


def _read_json_file(filepath):
    """读取JSON文件内容

    如果文件不存在或内容为空，返回空列表。

    Args:
        filepath (str): JSON文件的完整路径

    Returns:
        list or dict: 解析后的JSON数据
    """
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data is None:
                return []
            return data
    except (json.JSONDecodeError, IOError):
        return []


def _write_json_file(filepath, data):
    """将数据写入JSON文件

    使用UTF-8编码，缩进2个空格，确保中文正常显示。

    Args:
        filepath (str): JSON文件的完整路径
        data: 要写入的数据（必须可JSON序列化）
    """
    ensure_data_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_filepath(filename):
    """获取数据文件的完整路径

    Args:
        filename (str): 文件名

    Returns:
        str: 文件的完整路径
    """
    return os.path.join(get_data_dir(), filename)


# ============================================================
# 初始化与配置
# ============================================================

def init_storage():
    """初始化数据存储

    创建数据目录和所有必要的数据文件。
    如果数据已存在，则跳过创建。

    Returns:
        bool: 如果初始化成功返回True
    """
    ensure_data_dir()

    # 创建所有数据文件（如果不存在）
    files = [FILE_RITUALS, FILE_HABITS, FILE_HABIT_RECORDS,
             FILE_RITUAL_EXECUTIONS]

    for filename in files:
        filepath = _get_filepath(filename)
        if not os.path.exists(filepath):
            _write_json_file(filepath, [])

    # 写入默认配置
    config_path = _get_filepath(FILE_CONFIG)
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        _write_json_file(config_path, {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "theme": "default",
        })

    return True


def get_config():
    """读取配置信息

    Returns:
        dict: 配置字典
    """
    filepath = _get_filepath(FILE_CONFIG)
    data = _read_json_file(filepath)
    if isinstance(data, dict):
        return data
    return {}


# ============================================================
# 仪式数据操作
# ============================================================

def load_rituals():
    """加载所有仪式数据

    Returns:
        list: 仪式字典列表
    """
    return _read_json_file(_get_filepath(FILE_RITUALS))


def save_rituals(rituals):
    """保存所有仪式数据

    Args:
        rituals (list): 仪式字典列表
    """
    _write_json_file(_get_filepath(FILE_RITUALS), rituals)


def add_ritual(ritual):
    """添加一个新仪式

    Args:
        ritual (dict): 仪式数据字典
    """
    rituals = load_rituals()
    rituals.append(ritual)
    save_rituals(rituals)


def update_ritual(ritual_id, updates):
    """更新指定仪式的数据

    Args:
        ritual_id (str): 仪式ID
        updates (dict): 需要更新的字段字典

    Returns:
        dict or None: 更新后的仪式数据，如果未找到则返回None
    """
    rituals = load_rituals()
    for i, ritual in enumerate(rituals):
        if ritual["id"] == ritual_id:
            rituals[i].update(updates)
            save_rituals(rituals)
            return rituals[i]
    return None


def delete_ritual(ritual_id):
    """删除指定仪式

    Args:
        ritual_id (str): 仪式ID

    Returns:
        bool: 如果删除成功返回True，未找到返回False
    """
    rituals = load_rituals()
    original_len = len(rituals)
    rituals = [r for r in rituals if r["id"] != ritual_id]
    if len(rituals) < original_len:
        save_rituals(rituals)
        return True
    return False


def get_ritual_by_name(name):
    """根据名称查找仪式

    Args:
        name (str): 仪式名称

    Returns:
        dict or None: 找到的仪式数据，未找到返回None
    """
    rituals = load_rituals()
    for ritual in rituals:
        if ritual["name"] == name:
            return ritual
    return None


def get_ritual_by_id(ritual_id):
    """根据ID查找仪式

    Args:
        ritual_id (str): 仪式ID

    Returns:
        dict or None: 找到的仪式数据，未找到返回None
    """
    rituals = load_rituals()
    for ritual in rituals:
        if ritual["id"] == ritual_id:
            return ritual
    return None


# ============================================================
# 习惯数据操作
# ============================================================

def load_habits():
    """加载所有习惯数据

    Returns:
        list: 习惯字典列表
    """
    return _read_json_file(_get_filepath(FILE_HABITS))


def save_habits(habits):
    """保存所有习惯数据

    Args:
        habits (list): 习惯字典列表
    """
    _write_json_file(_get_filepath(FILE_HABITS), habits)


def add_habit(habit):
    """添加一个新习惯

    Args:
        habit (dict): 习惯数据字典
    """
    habits = load_habits()
    habits.append(habit)
    save_habits(habits)


def update_habit(habit_id, updates):
    """更新指定习惯的数据

    Args:
        habit_id (str): 习惯ID
        updates (dict): 需要更新的字段字典

    Returns:
        dict or None: 更新后的习惯数据，如果未找到则返回None
    """
    habits = load_habits()
    for i, habit in enumerate(habits):
        if habit["id"] == habit_id:
            habits[i].update(updates)
            save_habits(habits)
            return habits[i]
    return None


def delete_habit(habit_id):
    """删除指定习惯

    Args:
        habit_id (str): 习惯ID

    Returns:
        bool: 如果删除成功返回True，未找到返回False
    """
    habits = load_habits()
    original_len = len(habits)
    habits = [h for h in habits if h["id"] != habit_id]
    if len(habits) < original_len:
        save_habits(habits)
        return True
    return False


def get_habit_by_name(name):
    """根据名称查找习惯

    Args:
        name (str): 习惯名称

    Returns:
        dict or None: 找到的习惯数据，未找到返回None
    """
    habits = load_habits()
    for habit in habits:
        if habit["name"] == name:
            return habit
    return None


def get_habit_by_id(habit_id):
    """根据ID查找习惯

    Args:
        habit_id (str): 习惯ID

    Returns:
        dict or None: 找到的习惯数据，未找到返回None
    """
    habits = load_habits()
    for habit in habits:
        if habit["id"] == habit_id:
            return habit
    return None


# ============================================================
# 习惯记录操作
# ============================================================

def load_habit_records():
    """加载所有习惯打卡记录

    Returns:
        list: 习惯记录字典列表
    """
    return _read_json_file(_get_filepath(FILE_HABIT_RECORDS))


def save_habit_records(records):
    """保存所有习惯打卡记录

    Args:
        records (list): 习惯记录字典列表
    """
    _write_json_file(_get_filepath(FILE_HABIT_RECORDS), records)


def add_habit_record(record):
    """添加一条习惯打卡记录

    Args:
        record (dict): 习惯记录数据字典
    """
    records = load_habit_records()
    records.append(record)
    save_habit_records(records)


def get_habit_records(habit_id, date_str=None):
    """获取指定习惯的打卡记录

    Args:
        habit_id (str): 习惯ID
        date_str (str): 日期字符串，如果为None则返回所有记录

    Returns:
        list: 匹配的习惯记录列表
    """
    records = load_habit_records()
    if date_str is None:
        return [r for r in records if r["habit_id"] == habit_id]
    return [r for r in records
            if r["habit_id"] == habit_id and r["date"] == date_str]


def get_records_by_date(date_str):
    """获取指定日期的所有习惯记录

    Args:
        date_str (str): 日期字符串

    Returns:
        list: 该日期的所有习惯记录列表
    """
    records = load_habit_records()
    return [r for r in records if r["date"] == date_str]


# ============================================================
# 仪式执行记录操作
# ============================================================

def load_ritual_executions():
    """加载所有仪式执行记录

    Returns:
        list: 仪式执行记录字典列表
    """
    return _read_json_file(_get_filepath(FILE_RITUAL_EXECUTIONS))


def save_ritual_executions(executions):
    """保存所有仪式执行记录

    Args:
        executions (list): 仪式执行记录字典列表
    """
    _write_json_file(_get_filepath(FILE_RITUAL_EXECUTIONS), executions)


def add_ritual_execution(execution):
    """添加一条仪式执行记录

    Args:
        execution (dict): 仪式执行记录数据字典
    """
    executions = load_ritual_executions()
    executions.append(execution)
    save_ritual_executions(executions)


def get_ritual_executions(ritual_id, date_str=None):
    """获取指定仪式的执行记录

    Args:
        ritual_id (str): 仪式ID
        date_str (str): 日期字符串，如果为None则返回所有记录

    Returns:
        list: 匹配的仪式执行记录列表
    """
    executions = load_ritual_executions()
    if date_str is None:
        return [e for e in executions if e["ritual_id"] == ritual_id]
    return [e for e in executions
            if e["ritual_id"] == ritual_id and e["date"] == date_str]


def get_executions_by_date(date_str):
    """获取指定日期的所有仪式执行记录

    Args:
        date_str (str): 日期字符串

    Returns:
        list: 该日期的所有仪式执行记录列表
    """
    executions = load_ritual_executions()
    return [e for e in executions if e["date"] == date_str]


# ============================================================
# 数据导入导出
# ============================================================

def export_data(filepath):
    """导出所有数据到一个JSON文件

    将仪式、习惯、习惯记录、仪式执行记录和配置打包导出。

    Args:
        filepath (str): 导出文件的路径

    Returns:
        bool: 导出成功返回True
    """
    data = {
        "version": "1.0.0",
        "exported_at": datetime.now().isoformat(),
        "rituals": load_rituals(),
        "habits": load_habits(),
        "habit_records": load_habit_records(),
        "ritual_executions": load_ritual_executions(),
        "config": get_config(),
    }

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        error_msg(f"导出失败: {e}")
        return False


def import_data(filepath):
    """从JSON文件导入数据

    读取导出文件并覆盖当前数据。导入前会自动创建备份。

    Args:
        filepath (str): 导入文件的路径

    Returns:
        bool: 导入成功返回True
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        error_msg(f"导入失败: {e}")
        return False

    # 导入前创建备份
    backup_data()

    # 写入数据
    if "rituals" in data:
        save_rituals(data["rituals"])
    if "habits" in data:
        save_habits(data["habits"])
    if "habit_records" in data:
        save_habit_records(data["habit_records"])
    if "ritual_executions" in data:
        save_ritual_executions(data["ritual_executions"])

    return True


def backup_data():
    """创建数据备份

    在数据目录下创建 backup_<时间戳> 子目录，
    将所有数据文件复制到备份目录中。

    Returns:
        str: 备份目录的路径
    """
    data_dir = get_data_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(data_dir, f"backup_{timestamp}")

    os.makedirs(backup_dir, exist_ok=True)

    # 复制所有数据文件到备份目录
    for filename in [FILE_RITUALS, FILE_HABITS, FILE_HABIT_RECORDS,
                     FILE_RITUAL_EXECUTIONS, FILE_CONFIG]:
        src = os.path.join(data_dir, filename)
        dst = os.path.join(backup_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    return backup_dir


def restore_data(backup_dir):
    """从备份恢复数据

    Args:
        backup_dir (str): 备份目录的路径

    Returns:
        bool: 恢复成功返回True
    """
    if not os.path.exists(backup_dir):
        error_msg(f"备份目录不存在: {backup_dir}")
        return False

    data_dir = get_data_dir()

    for filename in [FILE_RITUALS, FILE_HABITS, FILE_HABIT_RECORDS,
                     FILE_RITUAL_EXECUTIONS, FILE_CONFIG]:
        src = os.path.join(backup_dir, filename)
        dst = os.path.join(data_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    return True
