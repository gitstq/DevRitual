"""DevRitual 数据存储模块测试

测试数据的增删改查、导入导出和备份恢复功能。
使用临时目录进行测试，避免污染用户数据。
"""

import unittest
import sys
import os
import json
import tempfile
import shutil

# 将项目根目录添加到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from devritual.models import create_ritual, create_habit, create_habit_record
from devritual import storage


class BaseStorageTest(unittest.TestCase):
    """存储测试基类

    在临时目录中运行测试，测试结束后自动清理。
    """

    def setUp(self):
        """每个测试前创建临时数据目录"""
        self.test_dir = tempfile.mkdtemp()
        # 临时替换数据目录
        self.original_data_dir = storage.get_data_dir
        storage.get_data_dir = lambda: self.test_dir
        # 确保目录存在
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """每个测试后清理临时目录"""
        storage.get_data_dir = self.original_data_dir
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


class TestStorageInit(BaseStorageTest):
    """测试存储初始化"""

    def test_init_creates_files(self):
        """测试初始化创建所有必要文件"""
        storage.init_storage()
        expected_files = [
            "rituals.json", "habits.json",
            "habit_records.json", "ritual_executions.json",
            "config.json",
        ]
        for filename in expected_files:
            filepath = os.path.join(self.test_dir, filename)
            self.assertTrue(os.path.exists(filepath),
                            f"文件 {filename} 未创建")

    def test_init_creates_config(self):
        """测试初始化创建配置文件"""
        storage.init_storage()
        config = storage.get_config()
        self.assertEqual(config["version"], "1.0.0")
        self.assertIn("created_at", config)


class TestRitualStorage(BaseStorageTest):
    """测试仪式数据存储"""

    def setUp(self):
        super().setUp()
        storage.init_storage()

    def test_add_and_load_ritual(self):
        """测试添加和加载仪式"""
        ritual = create_ritual("测试仪式", description="测试描述")
        storage.add_ritual(ritual)
        rituals = storage.load_rituals()
        self.assertEqual(len(rituals), 1)
        self.assertEqual(rituals[0]["name"], "测试仪式")

    def test_get_ritual_by_name(self):
        """测试按名称查找仪式"""
        ritual = create_ritual("唯一名称")
        storage.add_ritual(ritual)
        found = storage.get_ritual_by_name("唯一名称")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "唯一名称")

    def test_get_ritual_by_name_not_found(self):
        """测试查找不存在的仪式"""
        found = storage.get_ritual_by_name("不存在")
        self.assertIsNone(found)

    def test_get_ritual_by_id(self):
        """测试按ID查找仪式"""
        ritual = create_ritual("ID测试")
        storage.add_ritual(ritual)
        found = storage.get_ritual_by_id(ritual["id"])
        self.assertIsNotNone(found)
        self.assertEqual(found["id"], ritual["id"])

    def test_update_ritual(self):
        """测试更新仪式"""
        ritual = create_ritual("更新前")
        storage.add_ritual(ritual)
        updated = storage.update_ritual(ritual["id"], {"name": "更新后"})
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "更新后")
        # 验证持久化
        found = storage.get_ritual_by_id(ritual["id"])
        self.assertEqual(found["name"], "更新后")

    def test_delete_ritual(self):
        """测试删除仪式"""
        ritual = create_ritual("待删除")
        storage.add_ritual(ritual)
        result = storage.delete_ritual(ritual["id"])
        self.assertTrue(result)
        found = storage.get_ritual_by_id(ritual["id"])
        self.assertIsNone(found)

    def test_delete_nonexistent_ritual(self):
        """测试删除不存在的仪式"""
        result = storage.delete_ritual("nonexistent_id")
        self.assertFalse(result)


class TestHabitStorage(BaseStorageTest):
    """测试习惯数据存储"""

    def setUp(self):
        super().setUp()
        storage.init_storage()

    def test_add_and_load_habit(self):
        """测试添加和加载习惯"""
        habit = create_habit("测试习惯", description="测试描述")
        storage.add_habit(habit)
        habits = storage.load_habits()
        self.assertEqual(len(habits), 1)
        self.assertEqual(habits[0]["name"], "测试习惯")

    def test_get_habit_by_name(self):
        """测试按名称查找习惯"""
        habit = create_habit("唯一习惯")
        storage.add_habit(habit)
        found = storage.get_habit_by_name("唯一习惯")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "唯一习惯")

    def test_update_habit(self):
        """测试更新习惯"""
        habit = create_habit("更新前")
        storage.add_habit(habit)
        updated = storage.update_habit(habit["id"], {"streak": 5})
        self.assertIsNotNone(updated)
        self.assertEqual(updated["streak"], 5)

    def test_delete_habit(self):
        """测试删除习惯"""
        habit = create_habit("待删除")
        storage.add_habit(habit)
        result = storage.delete_habit(habit["id"])
        self.assertTrue(result)
        found = storage.get_habit_by_id(habit["id"])
        self.assertIsNone(found)


class TestHabitRecordStorage(BaseStorageTest):
    """测试习惯记录存储"""

    def setUp(self):
        super().setUp()
        storage.init_storage()

    def test_add_and_load_records(self):
        """测试添加和加载记录"""
        record = create_habit_record("habit_1", "2025-01-15")
        storage.add_habit_record(record)
        records = storage.load_habit_records()
        self.assertEqual(len(records), 1)

    def test_get_records_by_habit_id(self):
        """测试按习惯ID获取记录"""
        for i in range(3):
            record = create_habit_record("habit_1", f"2025-01-{15+i:02d}")
            storage.add_habit_record(record)
        # 添加其他习惯的记录
        other = create_habit_record("habit_2", "2025-01-15")
        storage.add_habit_record(other)

        records = storage.get_habit_records("habit_1")
        self.assertEqual(len(records), 3)

    def test_get_records_by_date(self):
        """测试按日期获取记录"""
        r1 = create_habit_record("habit_1", "2025-01-15")
        r2 = create_habit_record("habit_2", "2025-01-15")
        r3 = create_habit_record("habit_3", "2025-01-16")
        storage.add_habit_record(r1)
        storage.add_habit_record(r2)
        storage.add_habit_record(r3)

        records = storage.get_records_by_date("2025-01-15")
        self.assertEqual(len(records), 2)


class TestExportImport(BaseStorageTest):
    """测试数据导入导出"""

    def setUp(self):
        super().setUp()
        storage.init_storage()

    def test_export_creates_file(self):
        """测试导出创建文件"""
        ritual = create_ritual("导出测试")
        storage.add_ritual(ritual)

        export_path = os.path.join(self.test_dir, "export.json")
        result = storage.export_data(export_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_path))

        # 验证导出内容
        with open(export_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data["rituals"]), 1)
        self.assertEqual(data["rituals"][0]["name"], "导出测试")

    def test_import_restores_data(self):
        """测试导入恢复数据"""
        # 创建并导出数据
        ritual = create_ritual("导入测试")
        storage.add_ritual(ritual)
        export_path = os.path.join(self.test_dir, "export.json")
        storage.export_data(export_path)

        # 清空数据
        storage.save_rituals([])
        self.assertEqual(len(storage.load_rituals()), 0)

        # 导入数据
        result = storage.import_data(export_path)
        self.assertTrue(result)
        rituals = storage.load_rituals()
        self.assertEqual(len(rituals), 1)
        self.assertEqual(rituals[0]["name"], "导入测试")


class TestBackup(BaseStorageTest):
    """测试数据备份"""

    def setUp(self):
        super().setUp()
        storage.init_storage()

    def test_backup_creates_directory(self):
        """测试备份创建目录"""
        ritual = create_ritual("备份测试")
        storage.add_ritual(ritual)

        backup_dir = storage.backup_data()
        self.assertTrue(os.path.exists(backup_dir))
        self.assertIn("backup_", os.path.basename(backup_dir))

        # 验证备份文件存在
        self.assertTrue(os.path.exists(
            os.path.join(backup_dir, "rituals.json")
        ))

    def test_restore_from_backup(self):
        """测试从备份恢复"""
        ritual = create_ritual("恢复测试")
        storage.add_ritual(ritual)

        backup_dir = storage.backup_data()

        # 修改数据
        storage.save_rituals([])
        self.assertEqual(len(storage.load_rituals()), 0)

        # 恢复
        result = storage.restore_data(backup_dir)
        self.assertTrue(result)
        rituals = storage.load_rituals()
        self.assertEqual(len(rituals), 1)
        self.assertEqual(rituals[0]["name"], "恢复测试")


if __name__ == "__main__":
    unittest.main()
