"""
  @Author:lining-lo
  @Time:2026/8/21
  @Desc:任务生命周期事件数据模型，
        定义启动、切换、恢复、取消任务事件，
        统一用TaskEvent聚合，承载任务状态变更消息
"""
from dataclasses import dataclass
from typing import TypeAlias


@dataclass
class TaskRef:
    """任务生命周期事件数据模型"""
    task_id: str
    flow_id: str

@dataclass
class TaskStarted:
    """开始任务变化"""
    task: TaskRef

@dataclass
class TaskSwitched:
    """切换任务变化"""
    previous: TaskRef
    current: TaskRef

@dataclass
class TaskResumed:
    """恢复任务变化"""
    task: TaskRef

@dataclass
class TaskCanceled:
    """取消任务变化"""
    task: TaskRef

# 取别名
TaskEvent: TypeAlias = (
        TaskStarted
        | TaskSwitched
        | TaskResumed
        | TaskCanceled
)