"""
  @Author:lining-lo
  @Time:2026/8/21
  @Desc: 
"""
from dataclasses import dataclass
from typing import TypeAlias


@dataclass
class TaskRef:
    task_id: str
    flow_id: str

# 开始任务变化
@dataclass
class TaskStarted:
    task: TaskRef

# 切换任务变化
@dataclass
class TaskSwitched:
    previous: TaskRef
    current: TaskRef

# 恢复任务变化
@dataclass
class TaskResumed:
    task: TaskRef

# 取消任务变化
@dataclass
class TaskCanceled:
    task: TaskRef

# def test() -> TaskStarted | TaskSwitched | TaskResumed | TaskCanceled:
#     pass
#
# def test1() -> TaskEvent:
#     pass

TaskEvent: TypeAlias = (
        TaskStarted
        | TaskSwitched
        | TaskResumed
        | TaskCanceled
)