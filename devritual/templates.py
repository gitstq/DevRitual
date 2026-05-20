"""DevRitual 预设模板模块

提供内置的仪式和习惯模板，用户可以基于这些模板快速创建
自己的仪式和习惯。每个模板包含预定义的名称、描述、步骤等信息。
"""

from devritual.models import create_ritual, create_habit


# ============================================================
# 仪式模板
# ============================================================

RITUAL_TEMPLATES = {
    "morning-code-review": {
        "name": "晨间代码审查",
        "description": "每天早上开始编码前，快速审查昨天的代码变更",
        "steps": [
            "查看昨天的Git提交记录",
            "浏览未解决的Pull Request",
            "检查CI/CD构建状态",
            "阅读重要的代码评论",
            "规划今天的编码任务",
        ],
        "estimated_time": 15,
        "tags": ["代码质量", "团队协作"],
        "frequency": "daily",
    },
    "pre-commit-check": {
        "name": "提交前检查",
        "description": "在Git提交前执行的标准检查流程",
        "steps": [
            "运行代码格式化工具",
            "执行单元测试",
            "检查代码Lint警告",
            "确认提交信息格式正确",
            "验证功能完整性",
        ],
        "estimated_time": 10,
        "tags": ["Git", "代码质量"],
        "frequency": "daily",
    },
    "standup-prep": {
        "name": "每日站会准备",
        "description": "为每日站会准备汇报内容",
        "steps": [
            "回顾昨天完成的工作",
            "列出今天计划的任务",
            "标记遇到的阻碍和问题",
            "整理需要讨论的议题",
        ],
        "estimated_time": 5,
        "tags": ["团队协作", "敏捷"],
        "frequency": "daily",
    },
    "end-of-day-wrap": {
        "name": "下班前收尾",
        "description": "每天结束工作前的收尾仪式",
        "steps": [
            "提交当天所有代码变更",
            "编写或更新TODO注释",
            "更新任务看板状态",
            "记录今天学到的知识点",
            "清理工作环境（关闭标签页等）",
        ],
        "estimated_time": 10,
        "tags": ["效率", "工作流"],
        "frequency": "daily",
    },
    "weekly-retro": {
        "name": "周回顾与规划",
        "description": "每周五下午进行的回顾和下周规划",
        "steps": [
            "回顾本周完成的任务",
            "分析未完成任务的原因",
            "总结本周的技术收获",
            "规划下周的重点任务",
            "更新个人技术路线图",
        ],
        "estimated_time": 30,
        "tags": ["规划", "回顾"],
        "frequency": "weekly",
    },
    "deep-work-session": {
        "name": "深度工作准备",
        "description": "开始深度编码前的准备工作",
        "steps": [
            "关闭所有通知和消息应用",
            "设置番茄钟（25分钟）",
            "明确本次编码的具体目标",
            "准备必要的文档和参考资料",
            "进入专注状态",
        ],
        "estimated_time": 5,
        "tags": ["专注", "效率"],
        "frequency": "daily",
    },
    "learning-time": {
        "name": "技术学习时间",
        "description": "每天固定的技术学习和提升时间",
        "steps": [
            "选择今天的学习主题",
            "阅读技术文章或文档",
            "动手实践新知识",
            "记录学习笔记",
            "分享学到的新知识",
        ],
        "estimated_time": 30,
        "tags": ["学习", "成长"],
        "frequency": "daily",
    },
    "bug-fixing-ritual": {
        "name": "Bug修复流程",
        "description": "系统化的Bug修复流程",
        "steps": [
            "阅读Bug报告，理解问题",
            "复现Bug",
            "定位问题根因",
            "编写修复代码",
            "编写回归测试",
            "验证修复效果",
        ],
        "estimated_time": 20,
        "tags": ["Bug修复", "质量"],
        "frequency": "custom",
    },
}


# ============================================================
# 习惯模板
# ============================================================

HABIT_TEMPLATES = {
    "daily-commit": {
        "name": "每日提交",
        "description": "每天至少提交一次代码",
        "frequency_target": "daily",
        "reminder_time": "17:00",
    },
    "code-review": {
        "name": "代码审查",
        "description": "每天至少审查一个Pull Request",
        "frequency_target": "daily",
        "reminder_time": "14:00",
    },
    "write-tests": {
        "name": "编写测试",
        "description": "为新功能编写单元测试",
        "frequency_target": "daily",
        "reminder_time": "10:00",
    },
    "read-docs": {
        "name": "阅读文档",
        "description": "每天阅读技术文档或文章",
        "frequency_target": "daily",
        "reminder_time": "21:00",
    },
    "refactor": {
        "name": "代码重构",
        "description": "每周进行一次代码重构",
        "frequency_target": "weekly",
        "reminder_time": "15:00",
    },
    "blog-write": {
        "name": "技术写作",
        "description": "每周写一篇技术博客或笔记",
        "frequency_target": "weekly",
        "reminder_time": "20:00",
    },
    "open-source": {
        "name": "开源贡献",
        "description": "每周为开源项目做一次贡献",
        "frequency_target": "weekly",
        "reminder_time": "19:00",
    },
    "learn-new-lang": {
        "name": "学习新语言",
        "description": "每周学习一种新的编程语言或框架",
        "frequency_target": "weekly",
        "reminder_time": "10:00",
    },
}


def get_ritual_template(template_id):
    """获取仪式模板

    Args:
        template_id (str): 模板ID

    Returns:
        dict or None: 模板数据字典，未找到返回None
    """
    template = RITUAL_TEMPLATES.get(template_id)
    if template is None:
        return None
    return create_ritual(
        name=template["name"],
        description=template["description"],
        steps=template["steps"],
        estimated_time=template["estimated_time"],
        tags=template["tags"],
        frequency=template["frequency"],
    )


def get_habit_template(template_id):
    """获取习惯模板

    Args:
        template_id (str): 模板ID

    Returns:
        dict or None: 模板数据字典，未找到返回None
    """
    template = HABIT_TEMPLATES.get(template_id)
    if template is None:
        return None
    return create_habit(
        name=template["name"],
        description=template["description"],
        frequency_target=template["frequency_target"],
        reminder_time=template["reminder_time"],
    )


def list_ritual_templates():
    """列出所有可用的仪式模板

    Returns:
        list: 模板信息列表，每个元素为 (id, name, description) 元组
    """
    result = []
    for tid, template in RITUAL_TEMPLATES.items():
        result.append((tid, template["name"], template["description"]))
    return result


def list_habit_templates():
    """列出所有可用的习惯模板

    Returns:
        list: 模板信息列表，每个元素为 (id, name, description) 元组
    """
    result = []
    for tid, template in HABIT_TEMPLATES.items():
        result.append((tid, template["name"], template["description"]))
    return result
