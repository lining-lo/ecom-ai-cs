"""
  @Author:lining-lo
  @Time:2026/8/21
  @Desc:llm识别出的意图数据模型，
        各类业务意图继承Command基类；
        通过COMMAND_NAME_TO_CLASS映射实现dict到意图对象的反序列化
"""
from dataclasses import dataclass
from typing import Any


# | command       | 完整形式
# 我的订单号1101，我现在想退单，但是我暂时不想退了，我想订单物流信息

# | 作用                      |
# | ------------- | ------------------------------------------------------------ | ------------------------- |
# | `start_flow`  | `{"command": "start_flow", "flow": "<flow_id>"}`             | 启动指定 Flow。           |
# | `set_slots`   | `{"command": "set_slots", "slots": {"<slot_name>": "<value>"}}` | 向当前活动任务写入 Slot。 |
# | `cancel_task` | `{"command": "cancel_task", "task_id": "<task_id>"}`         | 取消指定任务。            |
# | `resume_task` | `{"command": "resume_task", "task_id": "<task_id>"}`         | 恢复指定的暂停任务。      |

@dataclass
class Command:
    """llm识别出的意图数据模型"""
    command: str

    @classmethod
    def from_dict(cls, command_data: dict) -> "Command":
        """构建不同类型llm识别出的意图数据模型"""
        clz = COMMAND_NAME_TO_CLASS[command_data["command"]]
        return clz(**command_data)


@dataclass
class StartFlowCommand(Command):
    """开始任务意图"""
    flow: str


@dataclass
class SetSlotsCommand(Command):
    """设置槽位数据意图"""
    slots: dict[str, Any]


@dataclass
class CancelTaskCommand(Command):
    """取消任务意图"""
    task_id: str


@dataclass
class ResumeTaskCommand(Command):
    """恢复任务意图"""
    task_id: str


# 意图对象字典
COMMAND_NAME_TO_CLASS: dict[str, type[Command]] = {
    "start_flow": StartFlowCommand,
    "set_slots": SetSlotsCommand,
    "cancel_task": CancelTaskCommand,
    "resume_task": ResumeTaskCommand,
}
