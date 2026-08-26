"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc:意图识别模型，
        封装任务、知识、闲聊三类规划数据，
        支持解析LLM输出的结构化计划，配套计划校验结果与澄清错误枚举
"""
from dataclasses import dataclass, field
from enum import Enum
from app.task.command.models import Command


@dataclass
class TaskTurnPlan:
    """任务意图"""
    # 任务类型列表 开始任务|取消任务|设置槽位数据|恢复任务
    commands: list[Command] = field(default_factory=list)

    @classmethod
    def from_dict(cls, task_data: dict) -> "TaskTurnPlan":
        """构建任务意图的方法"""
        return cls(commands=[Command.from_dict(command_data)
                             for command_data in task_data['commands']])


@dataclass
class KnowledgeTurnPlan:
    """知识查询意图"""
    # 查询的东西列表
    intents: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, knowledge_data: dict) -> "KnowledgeTurnPlan":
        """构建知识查询意图的方法"""
        return KnowledgeTurnPlan(knowledge_data['intents'])


@dataclass
class ChitchatTurnPlan:
    """闲聊意图"""
    pass


@dataclass
class TurnPlan:
    """意图识别模型类"""
    task: TaskTurnPlan | None = None # 任务
    knowledge: KnowledgeTurnPlan | None = None # 知识查询
    chitchat: ChitchatTurnPlan | None = None #闲聊

    @classmethod
    def from_dict(cls, plan_data: dict) -> "TurnPlan":
        """构建意图识别模型类的方法"""
        return cls(
            task=TaskTurnPlan.from_dict(plan_data['task'])
            if plan_data['task'] is not None else None,

            knowledge=KnowledgeTurnPlan.from_dict(plan_data['knowledge'])
            if plan_data['knowledge'] is not None else None,

            chitchat=ChitchatTurnPlan()
            if plan_data['chitchat'] is not None else None
        )


class ClarifyReason(Enum):
    """失败原因枚举类"""
    MISSING_TRACK = "missing_track"
    MULTIPLE_TRACKS = "multiple_tracks"
    MISSING_TASK_COMMANDS = "missing_task_commands"
    MISSING_KNOWLEDGE_INTENT = "missing_knowledge_intent"
    MISSING_FOCUSED_OBJECT = "missing_focused_object"
    OBJECT_REQUIRES_INTENT = "object_requires_intent"
    INVALID_TASK_COMMAND = "invalid_task_command"
    UNKNOWN_KNOWLEDGE_INTENT = "unknown_knowledge_intent"


@dataclass
class TurnPlanValidationResult:
    """意图识别的结果模型类"""
    valid: bool  # 是否校验成功
    reason: ClarifyReason | None = None  # 失败原因
