"""DevRitual 数据模型模块测试

测试所有数据模型的创建函数，验证字段完整性和默认值。
"""

import unittest
import sys
import os

# 将项目根目录添加到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from devritual.models import (
    generate_id, now_iso, today_str,
    create_ritual, create_habit, create_habit_record,
    create_ritual_execution, create_ritual_execution_started
)


class TestGenerateId(unittest.TestCase):
    """测试ID生成函数"""

    def test_generate_id_returns_string(self):
        """测试ID生成为字符串"""
        result = generate_id()
        self.assertIsInstance(result, str)

    def test_generate_id_length(self):
        """测试ID长度为32个字符（UUID4 hex格式）"""
        result = generate_id()
        self.assertEqual(len(result), 32)

    def test_generate_id_unique(self):
        """测试多次生成的ID不重复"""
        ids = [generate_id() for _ in range(100)]
        self.assertEqual(len(set(ids)), 100)


class TestNowIso(unittest.TestCase):
    """测试ISO时间格式函数"""

    def test_now_iso_returns_string(self):
        """测试返回字符串"""
        result = now_iso()
        self.assertIsInstance(result, str)

    def test_now_iso_format(self):
        """测试返回ISO格式的时间字符串"""
        result = now_iso()
        # ISO格式应包含 'T' 分隔符
        self.assertIn("T", result)


class TestTodayStr(unittest.TestCase):
    """测试日期字符串函数"""

    def test_today_str_returns_string(self):
        """测试返回字符串"""
        result = today_str()
        self.assertIsInstance(result, str)

    def test_today_str_format(self):
        """测试返回 YYYY-MM-DD 格式"""
        result = today_str()
        parts = result.split("-")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[0]), 4)  # 年
        self.assertEqual(len(parts[1]), 2)  # 月
        self.assertEqual(len(parts[2]), 2)  # 日


class TestCreateRitual(unittest.TestCase):
    """测试仪式创建函数"""

    def test_create_ritual_basic(self):
        """测试基本仪式创建"""
        ritual = create_ritual("测试仪式")
        self.assertEqual(ritual["name"], "测试仪式")
        self.assertIsInstance(ritual["id"], str)
        self.assertEqual(len(ritual["id"]), 32)

    def test_create_ritual_with_all_params(self):
        """测试带所有参数的仪式创建"""
        ritual = create_ritual(
            name="完整仪式",
            description="这是一个测试仪式",
            steps=["步骤1", "步骤2", "步骤3"],
            estimated_time=30,
            tags=["测试", "开发"],
            frequency="weekly",
        )
        self.assertEqual(ritual["name"], "完整仪式")
        self.assertEqual(ritual["description"], "这是一个测试仪式")
        self.assertEqual(ritual["steps"], ["步骤1", "步骤2", "步骤3"])
        self.assertEqual(ritual["estimated_time"], 30)
        self.assertEqual(ritual["tags"], ["测试", "开发"])
        self.assertEqual(ritual["frequency"], "weekly")

    def test_create_ritual_defaults(self):
        """测试默认参数值"""
        ritual = create_ritual("默认仪式")
        self.assertEqual(ritual["description"], "")
        self.assertEqual(ritual["steps"], [])
        self.assertEqual(ritual["estimated_time"], 0)
        self.assertEqual(ritual["tags"], [])
        self.assertEqual(ritual["frequency"], "daily")
        self.assertTrue(ritual["is_active"])

    def test_create_ritual_has_timestamps(self):
        """测试仪式包含创建和更新时间"""
        ritual = create_ritual("时间测试")
        self.assertIn("created_at", ritual)
        self.assertIn("updated_at", ritual)
        self.assertIsInstance(ritual["created_at"], str)
        self.assertIsInstance(ritual["updated_at"], str)


class TestCreateHabit(unittest.TestCase):
    """测试习惯创建函数"""

    def test_create_habit_basic(self):
        """测试基本习惯创建"""
        habit = create_habit("测试习惯")
        self.assertEqual(habit["name"], "测试习惯")
        self.assertIsInstance(habit["id"], str)

    def test_create_habit_with_all_params(self):
        """测试带所有参数的习惯创建"""
        habit = create_habit(
            name="完整习惯",
            description="这是一个测试习惯",
            frequency_target="weekly",
            reminder_time="09:00",
        )
        self.assertEqual(habit["name"], "完整习惯")
        self.assertEqual(habit["description"], "这是一个测试习惯")
        self.assertEqual(habit["frequency_target"], "weekly")
        self.assertEqual(habit["reminder_time"], "09:00")

    def test_create_habit_defaults(self):
        """测试默认参数值"""
        habit = create_habit("默认习惯")
        self.assertEqual(habit["description"], "")
        self.assertEqual(habit["frequency_target"], "daily")
        self.assertIsNone(habit["reminder_time"])
        self.assertTrue(habit["is_active"])
        self.assertEqual(habit["streak"], 0)
        self.assertEqual(habit["best_streak"], 0)
        self.assertEqual(habit["total_completions"], 0)


class TestCreateHabitRecord(unittest.TestCase):
    """测试习惯记录创建函数"""

    def test_create_habit_record_basic(self):
        """测试基本记录创建"""
        record = create_habit_record("habit_123")
        self.assertEqual(record["habit_id"], "habit_123")
        self.assertEqual(record["status"], "completed")
        self.assertEqual(record["date"], today_str())

    def test_create_habit_record_with_date(self):
        """测试指定日期的记录创建"""
        record = create_habit_record("habit_456", "2025-01-15")
        self.assertEqual(record["date"], "2025-01-15")

    def test_create_habit_record_skipped(self):
        """测试跳过状态的记录创建"""
        record = create_habit_record("habit_789", status="skipped")
        self.assertEqual(record["status"], "skipped")


class TestCreateRitualExecution(unittest.TestCase):
    """测试仪式执行记录创建函数"""

    def test_create_ritual_execution_basic(self):
        """测试基本执行记录创建"""
        execution = create_ritual_execution("ritual_123")
        self.assertEqual(execution["ritual_id"], "ritual_123")
        self.assertEqual(execution["status"], "completed")
        self.assertEqual(execution["date"], today_str())

    def test_create_ritual_execution_with_duration(self):
        """测试带时长的执行记录创建"""
        execution = create_ritual_execution(
            "ritual_456",
            duration_seconds=600,
            notes="顺利完成"
        )
        self.assertEqual(execution["duration_seconds"], 600)
        self.assertEqual(execution["notes"], "顺利完成")

    def test_create_ritual_execution_started(self):
        """测试进行中状态的执行记录创建"""
        execution = create_ritual_execution_started("ritual_789")
        self.assertEqual(execution["status"], "in_progress")
        self.assertEqual(execution["started_at"], execution["completed_at"])


if __name__ == "__main__":
    unittest.main()
