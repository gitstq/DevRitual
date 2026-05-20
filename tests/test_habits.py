"""DevRitual 习惯追踪模块测试

测试习惯的创建、打卡、连续天数追踪等功能。
使用临时目录避免污染用户数据。
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch

# 将项目根目录添加到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from devritual.models import create_habit, create_habit_record
from devritual import storage, habits


class BaseHabitTest(unittest.TestCase):
    """习惯测试基类"""

    def setUp(self):
        """每个测试前创建临时数据目录并初始化"""
        self.test_dir = tempfile.mkdtemp()
        storage.get_data_dir = lambda: self.test_dir
        storage.init_storage()

    def tearDown(self):
        """每个测试后清理临时目录"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


class TestHabitCreate(BaseHabitTest):
    """测试习惯创建"""

    def test_create_with_name_arg(self):
        """测试使用命令行参数创建习惯"""
        args = MagicMock()
        args.name = "测试习惯"
        args.description = "测试描述"
        args.frequency = "daily"
        args.reminder = "09:00"
        args.template = None

        habits.cmd_habit_create(args)

        found = storage.get_habit_by_name("测试习惯")
        self.assertIsNotNone(found)
        self.assertEqual(found["description"], "测试描述")
        self.assertEqual(found["reminder_time"], "09:00")

    def test_create_from_template(self):
        """测试从模板创建习惯"""
        args = MagicMock()
        args.template = "daily-commit"
        args.name = None

        habits.cmd_habit_create(args)

        found = storage.get_habit_by_name("每日提交")
        self.assertIsNotNone(found)

    def test_create_from_template_with_custom_name(self):
        """测试从模板创建并自定义名称"""
        args = MagicMock()
        args.template = "code-review"
        args.name = "我的代码审查"

        habits.cmd_habit_create(args)

        found = storage.get_habit_by_name("我的代码审查")
        self.assertIsNotNone(found)


class TestHabitCheckin(BaseHabitTest):
    """测试习惯打卡"""

    def test_checkin_success(self):
        """测试成功打卡"""
        habit = create_habit("打卡测试")
        storage.add_habit(habit)

        args = MagicMock()
        args.name = "打卡测试"

        habits.cmd_habit_checkin(args)

        records = storage.get_habit_records(habit["id"])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], "completed")

    def test_checkin_updates_streak(self):
        """测试打卡更新连续天数"""
        habit = create_habit("连续测试")
        storage.add_habit(habit)

        args = MagicMock()
        args.name = "连续测试"

        habits.cmd_habit_checkin(args)

        updated = storage.get_habit_by_id(habit["id"])
        self.assertEqual(updated["streak"], 1)
        self.assertEqual(updated["total_completions"], 1)

    def test_checkin_duplicate(self):
        """测试重复打卡"""
        habit = create_habit("重复打卡")
        storage.add_habit(habit)

        args = MagicMock()
        args.name = "重复打卡"

        habits.cmd_habit_checkin(args)
        habits.cmd_habit_checkin(args)

        records = storage.get_habit_records(habit["id"])
        completed = [r for r in records if r["status"] == "completed"]
        self.assertEqual(len(completed), 1)

    def test_checkin_nonexistent(self):
        """测试为不存在的习惯打卡"""
        args = MagicMock()
        args.name = "不存在"

        # 不应该抛出异常
        habits.cmd_habit_checkin(args)


class TestHabitSkip(BaseHabitTest):
    """测试跳过习惯"""

    def test_skip_resets_streak(self):
        """测试跳过重置连续天数"""
        habit = create_habit("跳过测试")
        habit["streak"] = 5
        storage.add_habit(habit)

        args = MagicMock()
        args.name = "跳过测试"

        habits.cmd_habit_skip(args)

        updated = storage.get_habit_by_id(habit["id"])
        self.assertEqual(updated["streak"], 0)


class TestHabitStreak(BaseHabitTest):
    """测试连续天数计算"""

    def test_streak_calculation(self):
        """测试连续天数计算"""
        habit = create_habit("连续计算")
        storage.add_habit(habit)

        # 添加连续3天的记录
        from datetime import date, timedelta
        for i in range(3):
            d = (date.today() - timedelta(days=i)).isoformat()
            record = create_habit_record(habit["id"], d)
            storage.add_habit_record(record)

        args = MagicMock()
        args.name = "连续计算"

        habits.cmd_habit_streak(args)

        updated = storage.get_habit_by_id(habit["id"])
        self.assertEqual(updated["streak"], 3)

    def test_streak_broken(self):
        """测试连续天数中断"""
        habit = create_habit("中断测试")
        storage.add_habit(habit)

        from datetime import date, timedelta
        # 添加今天和3天前的记录（跳过了中间的2天）
        today = date.today()
        record1 = create_habit_record(habit["id"], today.isoformat())
        record2 = create_habit_record(
            habit["id"], (today - timedelta(days=3)).isoformat()
        )
        storage.add_habit_record(record1)
        storage.add_habit_record(record2)

        args = MagicMock()
        args.name = "中断测试"

        habits.cmd_habit_streak(args)

        updated = storage.get_habit_by_id(habit["id"])
        self.assertEqual(updated["streak"], 1)


class TestHabitDelete(BaseHabitTest):
    """测试习惯删除"""

    def test_delete_existing(self):
        """测试删除存在的习惯"""
        storage.add_habit(create_habit("待删除"))

        args = MagicMock()
        args.name = "待删除"

        with patch("devritual.habits.prompt_yes_no", return_value=True):
            habits.cmd_habit_delete(args)

        found = storage.get_habit_by_name("待删除")
        self.assertIsNone(found)

    def test_delete_cancelled(self):
        """测试取消删除"""
        storage.add_habit(create_habit("保留"))

        args = MagicMock()
        args.name = "保留"

        with patch("devritual.habits.prompt_yes_no", return_value=False):
            habits.cmd_habit_delete(args)

        found = storage.get_habit_by_name("保留")
        self.assertIsNotNone(found)


class TestHabitList(BaseHabitTest):
    """测试习惯列表"""

    def test_list_empty(self):
        """测试空列表"""
        args = MagicMock()
        habits.cmd_habit_list(args)

    def test_list_with_habits(self):
        """测试有习惯时的列表"""
        storage.add_habit(create_habit("习惯1"))
        storage.add_habit(create_habit("习惯2"))

        args = MagicMock()
        habits.cmd_habit_list(args)


class TestHabitTemplates(BaseHabitTest):
    """测试习惯模板"""

    def test_list_templates(self):
        """测试列出模板"""
        args = MagicMock()
        habits.cmd_habit_templates(args)


if __name__ == "__main__":
    unittest.main()
