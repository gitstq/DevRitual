"""DevRitual 仪式管理模块

提供仪式的创建、编辑、删除、列表查看和执行追踪功能。
支持从预设模板创建仪式，也支持自定义创建。
"""

import time
from datetime import datetime

from devritual.models import (
    create_ritual, create_ritual_execution_started, now_iso
)
from devritual.storage import (
    load_rituals, save_rituals, add_ritual, update_ritual, delete_ritual,
    get_ritual_by_name, get_ritual_by_id,
    load_ritual_executions, save_ritual_executions, add_ritual_execution,
    get_ritual_executions
)
from devritual.templates import (
    get_ritual_template, list_ritual_templates
)
from devritual.utils import (
    Color, colored, bold, success_msg, error_msg, warning_msg,
    info_msg, title_msg, print_separator, prompt_input, prompt_yes_no,
    truncate_text, format_duration
)


def cmd_ritual_create(args):
    """创建新仪式命令处理函数

    支持两种创建方式：
    1. 从预设模板创建（--template 参数）
    2. 交互式创建（逐步引导用户输入信息）

    Args:
        args: 命令行参数对象，包含 name, description, steps, template 等属性
    """
    # 从模板创建
    if getattr(args, "template", None):
        ritual = get_ritual_template(args.template)
        if ritual is None:
            error_msg(f"未找到模板: {args.template}")
            print("  可用模板:")
            for tid, tname, tdesc in list_ritual_templates():
                print(f"    {colored(tid, Color.CYAN)} - {tname}: {tdesc}")
            return
        # 允许用户修改名称
        if args.name:
            ritual["name"] = args.name
        add_ritual(ritual)
        success_msg(f"已从模板创建仪式: {ritual['name']}")
        return

    # 交互式创建
    name = getattr(args, "name", None) or prompt_input("仪式名称")
    if not name:
        error_msg("仪式名称不能为空")
        return

    # 检查名称是否已存在
    existing = get_ritual_by_name(name)
    if existing:
        error_msg(f"仪式 '{name}' 已存在")
        return

    description = getattr(args, "description", None) or prompt_input(
        "描述", ""
    )

    # 输入步骤
    steps = []
    if getattr(args, "steps", None):
        steps = args.steps
    else:
        info_msg("输入仪式步骤（每行一个，空行结束）:")
        while True:
            step = prompt_input(f"  步骤 {len(steps) + 1}")
            if not step:
                break
            steps.append(step)
        if not steps:
            warning_msg("未添加任何步骤")

    estimated_time = getattr(args, "estimated_time", 0) or 0
    if not estimated_time:
        try:
            time_str = prompt_input("预估时间（分钟）", "10")
            estimated_time = int(time_str)
        except ValueError:
            estimated_time = 10

    # 输入标签
    tags = []
    if getattr(args, "tags", None):
        tags = args.tags
    else:
        tags_str = prompt_input("标签（逗号分隔）", "")
        if tags_str:
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]

    frequency = getattr(args, "frequency", "daily") or "daily"

    ritual = create_ritual(
        name=name,
        description=description,
        steps=steps,
        estimated_time=estimated_time,
        tags=tags,
        frequency=frequency,
    )

    add_ritual(ritual)
    success_msg(f"仪式 '{name}' 创建成功！")
    _print_ritual_detail(ritual)


def cmd_ritual_list(args):
    """列出所有仪式命令处理函数

    显示所有已创建的仪式，包括名称、描述、频率和状态信息。
    支持按标签过滤（--tag 参数）。

    Args:
        args: 命令行参数对象，包含 tag 属性
    """
    rituals = load_rituals()

    if not rituals:
        warning_msg("还没有创建任何仪式")
        info_msg("使用 'devritual ritual create' 创建你的第一个仪式")
        return

    # 按标签过滤
    tag_filter = getattr(args, "tag", None)
    if tag_filter:
        rituals = [r for r in rituals if tag_filter in r.get("tags", [])]
        if not rituals:
            warning_msg(f"没有找到标签为 '{tag_filter}' 的仪式")
            return

    title_msg(f"仪式列表 ({len(rituals)})")
    print()

    for i, ritual in enumerate(rituals, 1):
        # 状态标记
        if ritual.get("is_active", True):
            status = colored("活跃", Color.GREEN)
        else:
            status = colored("停用", Color.DIM)

        # 频率显示
        freq_map = {"daily": "每日", "weekly": "每周", "custom": "自定义"}
        freq = freq_map.get(ritual.get("frequency", "daily"), ritual["frequency"])

        print(f"  {colored(str(i).rjust(2), Color.DIM)}. "
              f"{bold(ritual['name'])}  {status}")
        if ritual.get("description"):
            print(f"      {truncate_text(ritual['description'], 60)}")
        print(f"      频率: {freq}  |  "
              f"预估: {ritual.get('estimated_time', 0)}分钟  |  "
              f"步骤: {len(ritual.get('steps', []))}个")
        if ritual.get("tags"):
            tags_str = " ".join(
                colored(f"[{t}]", Color.YELLOW) for t in ritual["tags"]
            )
            print(f"      标签: {tags_str}")
        print()


def cmd_ritual_show(args):
    """显示仪式详情命令处理函数

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    ritual = get_ritual_by_name(args.name)
    if not ritual:
        error_msg(f"未找到仪式: {args.name}")
        return

    _print_ritual_detail(ritual)


def cmd_ritual_edit(args):
    """编辑仪式命令处理函数

    交互式引导用户修改仪式的各个字段。

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    ritual = get_ritual_by_name(args.name)
    if not ritual:
        error_msg(f"未找到仪式: {args.name}")
        return

    print(f"  当前名称: {ritual['name']}")

    # 修改名称
    new_name = prompt_input("新名称（留空保持不变）", ritual["name"])
    if new_name != ritual["name"]:
        existing = get_ritual_by_name(new_name)
        if existing and existing["id"] != ritual["id"]:
            error_msg(f"名称 '{new_name}' 已被使用")
            return

    # 修改描述
    new_desc = prompt_input("新描述（留空保持不变）", ritual.get("description", ""))

    # 修改频率
    freq_map = {"daily": "每日", "weekly": "每周", "custom": "自定义"}
    current_freq = ritual.get("frequency", "daily")
    print(f"  当前频率: {freq_map.get(current_freq, current_freq)}")
    new_freq = prompt_input("新频率 (daily/weekly/custom)", current_freq)

    # 修改预估时间
    new_time = prompt_input(
        "新预估时间（分钟）", str(ritual.get("estimated_time", 0))
    )

    updates = {
        "name": new_name,
        "description": new_desc,
        "frequency": new_freq,
        "estimated_time": int(new_time) if new_time else 0,
        "updated_at": now_iso(),
    }

    update_ritual(ritual["id"], updates)
    success_msg(f"仪式 '{new_name}' 更新成功！")


def cmd_ritual_delete(args):
    """删除仪式命令处理函数

    删除前需要用户确认。

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    ritual = get_ritual_by_name(args.name)
    if not ritual:
        error_msg(f"未找到仪式: {args.name}")
        return

    if not prompt_yes_no(f"确定要删除仪式 '{ritual['name']}' 吗？", False):
        info_msg("已取消删除")
        return

    delete_ritual(ritual["id"])
    success_msg(f"仪式 '{ritual['name']}' 已删除")


def cmd_ritual_start(args):
    """开始执行仪式命令处理函数

    创建一条进行中的执行记录，并显示仪式步骤引导。

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    ritual = get_ritual_by_name(args.name)
    if not ritual:
        error_msg(f"未找到仪式: {args.name}")
        return

    # 检查是否有正在进行的执行
    executions = get_ritual_executions(ritual["id"])
    in_progress = [e for e in executions if e["status"] == "in_progress"]
    if in_progress:
        warning_msg(f"仪式 '{ritual['name']}' 已在进行中")
        info_msg("使用 'devritual ritual complete' 完成它")
        return

    # 创建执行记录
    execution = create_ritual_execution_started(ritual["id"])
    add_ritual_execution(execution)

    success_msg(f"仪式 '{ritual['name']}' 已开始！")
    print()

    # 显示步骤引导
    if ritual.get("steps"):
        print(colored("  执行步骤:", Color.BOLD + Color.CYAN))
        for i, step in enumerate(ritual["steps"], 1):
            checkbox = colored("[ ]", Color.YELLOW)
            print(f"    {checkbox} {colored(f'{i}.', Color.DIM)} {step}")
        print()
        info_msg(f"预估时间: {ritual.get('estimated_time', 0)} 分钟")
        info_msg("完成后使用 'devritual ritual complete "
                 f"{ritual['name']}' 标记完成")


def cmd_ritual_complete(args):
    """完成仪式命令处理函数

    将进行中的仪式标记为已完成，并记录执行时长。

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    ritual = get_ritual_by_name(args.name)
    if not ritual:
        error_msg(f"未找到仪式: {args.name}")
        return

    # 查找进行中的执行记录
    executions = get_ritual_executions(ritual["id"])
    in_progress = [e for e in executions if e["status"] == "in_progress"]

    if not in_progress:
        # 如果没有进行中的记录，直接创建一条完成记录
        execution = {
            "id": __import__("uuid").uuid4().hex,
            "ritual_id": ritual["id"],
            "date": __import__("datetime").date.today().isoformat(),
            "status": "completed",
            "duration_seconds": 0,
            "notes": "",
            "started_at": now_iso(),
            "completed_at": now_iso(),
        }
        add_ritual_execution(execution)
        success_msg(f"仪式 '{ritual['name']}' 已标记完成！")
        return

    # 更新执行记录为已完成
    execution = in_progress[-1]
    started = datetime.fromisoformat(execution["started_at"])
    now = datetime.now()
    duration = int((now - started).total_seconds())

    # 更新所有进行中的记录
    all_executions = load_ritual_executions()
    for i, e in enumerate(all_executions):
        if e["id"] == execution["id"]:
            all_executions[i]["status"] = "completed"
            all_executions[i]["duration_seconds"] = duration
            all_executions[i]["completed_at"] = now_iso()
            break
    save_ritual_executions(all_executions)

    success_msg(f"仪式 '{ritual['name']}' 已完成！")
    info_msg(f"本次用时: {format_duration(duration)}")


def cmd_ritual_skip(args):
    """跳过仪式命令处理函数

    将仪式标记为已跳过。

    Args:
        args: 命令行参数对象，包含 name 属性
    """
    ritual = get_ritual_by_name(args.name)
    if not ritual:
        error_msg(f"未找到仪式: {args.name}")
        return

    execution = {
        "id": __import__("uuid").uuid4().hex,
        "ritual_id": ritual["id"],
        "date": __import__("datetime").date.today().isoformat(),
        "status": "skipped",
        "duration_seconds": 0,
        "notes": "",
        "started_at": now_iso(),
        "completed_at": now_iso(),
    }
    add_ritual_execution(execution)
    info_msg(f"仪式 '{ritual['name']}' 已标记为跳过")


def cmd_ritual_templates(args):
    """列出所有可用的仪式模板

    Args:
        args: 命令行参数对象（未使用）
    """
    templates = list_ritual_templates()

    title_msg("可用仪式模板")
    print()

    for tid, tname, tdesc in templates:
        print(f"  {colored(tid, Color.CYAN)}")
        print(f"    {bold(tname)}")
        print(f"    {tdesc}")
        print()


def _print_ritual_detail(ritual):
    """打印仪式的详细信息

    Args:
        ritual (dict): 仪式数据字典
    """
    freq_map = {"daily": "每日", "weekly": "每周", "custom": "自定义"}
    freq = freq_map.get(ritual.get("frequency", "daily"), ritual["frequency"])

    title_msg(f"仪式详情: {ritual['name']}")
    print()
    if ritual.get("description"):
        print(f"  描述: {ritual['description']}")
    print(f"  频率: {freq}")
    print(f"  预估时间: {ritual.get('estimated_time', 0)} 分钟")
    print(f"  创建时间: {ritual.get('created_at', 'N/A')}")
    print(f"  状态: {'活跃' if ritual.get('is_active', True) else '停用'}")

    if ritual.get("tags"):
        tags_str = " ".join(
            colored(f"[{t}]", Color.YELLOW) for t in ritual["tags"]
        )
        print(f"  标签: {tags_str}")

    if ritual.get("steps"):
        print()
        print(colored("  执行步骤:", Color.BOLD))
        for i, step in enumerate(ritual["steps"], 1):
            print(f"    {colored(f'{i}.', Color.DIM)} {step}")

    print()
