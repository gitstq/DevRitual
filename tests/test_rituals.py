"""DevRitual 仪式管理模块测试

测试仪式的创建、列表、执行追踪等功能。
使用临时目录避免污染用户数据。
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 将项目根目录添加到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from devritual.models import create_ritual
from devritual import storage, rituals


class BaseRitualTest(unittest.TestCase):
    """仪式测试基类"""

    def setUp(self):
        """每个测试前创建临时数据目录并初始化"""
        self.test_dir = tempfile.mkdtemp()
        storage.get_data_dir = lambda: self.test_dir
        storage.init_storage()

    def tearDown(self):
        """每个测试后清理临时目录"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


class TestRitualCreate(BaseRitualTest):
    """测试仪式创建"""

    def test_create_with_name_arg(self):
        """测试使用命令行参数创建仪式"""
        args = MagicMock()
        args.name = "测试仪式"
        args.description = "测试描述"
        args.steps = ["步骤1", "步骤2"]
        args.estimated_time = 15
        args.tags = ["测试"]
        args.frequency = "daily"
        args.template = None

        rituals.cmd_ritual_create(args)

        found = storage.get_ritual_by_name("测试仪式")
        self.assertIsNotNone(found)
        self.assertEqual(found["description"], "测试描述")
        self.assertEqual(found["steps"], ["步骤1", "步骤2"])

    def test_create_from_template(self):
        """测试从模板创建仪式"""
        args = MagicMock()
        args.template = "morning-code-review"
        args.name = None

        rituals.cmd_ritual_create(args)

        found = storage.get_ritual_by_name("晨间代码审查")
        self.assertIsNotNone(found)
        self.assertTrue(len(found["steps"]) > 0)

    def test_create_from_template_with_custom_name(self):
        """测试从模板创建并自定义名称"""
        args = MagicMock()
        args.template = "pre-commit-check"
        args.name = "我的提交检查"

        rituals.cmd_ritual_create(args)

        found = storage.get_ritual_by_name("我的提交检查")
        self.assertIsNotNone(found)

    def test_create_duplicate_name(self):
        """测试创建重名仪式"""
        ritual = create_ritual("重复名称")
        storage.add_ritual(ritual)

        args = MagicMock()
        args.name = "重复名称"
        args.description = None
        args.steps = None
        args.estimated_time = 0
        args.tags = None
        args.frequency = "daily"
        args.template = None

        # 应该不会报错，因为交互模式下会提示
        # 但在非交互模式下（name已提供），应该检测到重复
        rituals.cmd_ritual_create(args)

        # 应该仍然只有一个
        found_list = storage.load_rituals()
        self.assertEqual(len([r for r in found_list if r["name"] == "重复名称"]), 1)


class TestRitualList(BaseRitualTest):
    """测试仪式列表"""

    def test_list_empty(self):
        """测试空列表"""
        args = MagicMock()
        args.tag = None

        # 不应该抛出异常
        rituals.cmd_ritual_list(args)

    def test_list_with_rituals(self):
        """测试有仪式时的列表"""
        storage.add_ritual(create_ritual("仪式1", tags=["标签A"]))
        storage.add_ritual(create_ritual("仪式2", tags=["标签B"]))

        args = MagicMock()
        args.tag = None

        # 不应该抛出异常
        rituals.cmd_ritual_list(args)

    def test_list_filter_by_tag(self):
        """测试按标签过滤"""
        storage.add_ritual(create_ritual("仪式A", tags=["Python"]))
        storage.add_ritual(create_ritual("仪式B", tags=["Java"]))

        args = MagicMock()
        args.tag = "Python"

        # 不应该抛出异常
        rituals.cmd_ritual_list(args)


class TestRitualExecution(BaseRitualTest):
    """测试仪式执行"""

    def test_start_ritual(self):
        """测试开始仪式"""
        storage.add_ritual(create_ritual("测试仪式"))

        args = MagicMock()
        args.name = "测试仪式"

        rituals.cmd_ritual_start(args)

        executions = storage.get_ritual_executions(
            storage.get_ritual_by_name("测试仪式")["id"]
        )
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["status"], "in_progress")

    def test_complete_ritual(self):
        """测试完成仪式"""
        ritual = create_ritual("完成测试")
        storage.add_ritual(ritual)

        # 先开始
        args_start = MagicMock()
        args_start.name = "完成测试"
        rituals.cmd_ritual_start(args_start)

        # 再完成
        args_complete = MagicMock()
        args_complete.name = "完成测试"
        rituals.cmd_ritual_complete(args_complete)

        executions = storage.get_ritual_executions(ritual["id"])
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["status"], "completed")

    def test_skip_ritual(self):
        """测试跳过仪式"""
        storage.add_ritual(create_ritual("跳过测试"))

        args = MagicMock()
        args.name = "跳过测试"

        rituals.cmd_ritual_skip(args)

        executions = storage.get_ritual_executions(
            storage.get_ritual_by_name("跳过测试")["id"]
        )
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["status"], "skipped")

    def test_start_nonexistent_ritual(self):
        """测试开始不存在的仪式"""
        args = MagicMock()
        args.name = "不存在"

        # 不应该抛出异常
        rituals.cmd_ritual_start(args)


class TestRitualDelete(BaseRitualTest):
    """测试仪式删除"""

    def test_delete_existing(self):
        """测试删除存在的仪式"""
        storage.add_ritual(create_ritual("待删除"))

        args = MagicMock()
        args.name = "待删除"

        with patch("devritual.rituals.prompt_yes_no", return_value=True):
            rituals.cmd_ritual_delete(args)

        found = storage.get_ritual_by_name("待删除")
        self.assertIsNone(found)

    def test_delete_cancelled(self):
        """测试取消删除"""
        storage.add_ritual(create_ritual("保留"))

        args = MagicMock()
        args.name = "保留"

        with patch("devritual.rituals.prompt_yes_no", return_value=False):
            rituals.cmd_ritual_delete(args)

        found = storage.get_ritual_by_name("保留")
        self.assertIsNotNone(found)


class TestRitualTemplates(BaseRitualTest):
    """测试仪式模板"""

    def test_list_templates(self):
        """测试列出模板"""
        args = MagicMock()
        # 不应该抛出异常
        rituals.cmd_ritual_templates(args)


if __name__ == "__main__":
    unittest.main()
