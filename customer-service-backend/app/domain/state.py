"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc:对话运行状态模型，
        定义会话、轮次、焦点对象、任务实例与任务状态，
        管理会话历史以及任务启动、切换、暂停、取消、恢复的状态流转
"""
import time
import uuid
from dataclasses import dataclass, field
from app.domain.message import UserMessage, BotMessage
from app.task.lifecycle.models import TaskEvent, TaskSwitched, TaskStarted, TaskRef, TaskCanceled, TaskResumed


@dataclass
class Turn:
    """一轮对话信息，一个问题对应一个或者多个回答"""
    turn_id: str
    user_message: UserMessage  # 用户提问
    bot_message: list[BotMessage] = field(default_factory=list)  # 客服回复


@dataclass
class Session:
    """会话对象"""
    session_id: str  # session的id，区别不同session
    started_at: float  # session创建时间戳
    last_activity_at: float  # session最后一次活跃时间
    closed_at: float | None = None  # 关闭时间
    turns: list[Turn] = field(default_factory=list)  # 每个session会话多轮对话


@dataclass
class FocusedObject:
    """对象类型消息"""
    type: str
    id: str
    title: str | None = None
    attributes: dict = field(default_factory=dict)


@dataclass
class SharedState:
    """三种能力都有数据：任务流程、知识问答、闲聊"""
    focused_object: FocusedObject | None = None  # 对象类型消息
    sessions: list[Session] = field(default_factory=list)  # 多个会话数据

    def create_session(self):
        """创建会话对象的方法"""
        now = time.time()
        session = Session(
            session_id=str(uuid.uuid4()),
            started_at=now,
            last_activity_at=now,
        )
        # 创建session对象放到state里面
        self.sessions.append(session)

    def close_current_session(self):
        """关闭当前会话"""
        self.sessions[-1].closed_at = time.time()


@dataclass
class TaskInstance:
    """某个任务流程步骤相关数据"""
    flow_id: str  # 流程id，对应yaml文件  refund_request
    step_id: str | None = None  # 步骤id ,比如 start
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 当前任务id
    slots: dict = field(default_factory=dict)  # 槽位数据字典  {order_number : a10098765}

    def to_ref(self) -> TaskRef:
        """将TaskInstance转化为TaskRef"""
        return TaskRef(task_id=self.task_id,
                       flow_id=self.flow_id, )


@dataclass
class TaskState:
    """任务流程特有数据，流程步骤数据"""
    active: TaskInstance | None = None  # 当前正在运行（活跃）的任务
    paused: list[TaskInstance] = field(default_factory=list)  # 中断（暂停）的任务

    def start(self, task: TaskInstance) -> TaskEvent:
        """启动任务流程的方法"""
        # 判断当前是否有活跃任务
        if self.active:  # 有活跃
            # 任务变化 TaskSwitched
            previous = self.active.to_ref()
            # 暂停活跃任务
            self.paused.append(self.active)
            # 当前执行任务设置活跃任务
            self.active = task
            current = self.active.to_ref()
            return TaskSwitched(previous=previous,
                                current=current)
        else:
            # 任务变化 TaskStarted
            self.active = task
            return TaskStarted(task=self.active.to_ref())

    def cancel(self, task_id: str) -> TaskEvent:
        """取消任务流程的方法"""
        # 判断当前取消任务 是否 当前活跃任务，根据task_id判断
        # 是
        if self.active.task_id == task_id:
            target_task = self.active.to_ref()
            # 活跃任务取消
            self.active = None
            return TaskCanceled(task=target_task)
        else:  # 不是
            # 从中断列表获取
            for pause_task in self.paused:
                if pause_task.task_id == task_id:
                    target_task = pause_task.to_ref()
                    # 从中断列表删除任务
                    self.paused.remove(pause_task)
                    return TaskCanceled(task=target_task)
            raise ValueError("任务不存在")

    def resume(self, task_id: str) -> TaskEvent:
        """恢复任务流程的方法"""
        target_task_ref = None
        target_task = None
        # 把中断列表遍历，从中断列表找到恢复任务，从中断列表取出来
        for index, task in enumerate(self.paused):
            # 从中断列表找到恢复任务，从中断列表取出来
            if task.task_id == task_id:
                target_task_ref = task.to_ref()
                target_task = self.paused.pop(index)
                break

        # 判断中断列表有恢复任务
        if target_task is None:
            raise ValueError("恢复任务不存在")

        # 判断当前是否有活跃任务
        if self.active:
            previous_task_ref = self.active.to_ref()
            # 当前active暂停
            self.paused.append(self.active)

            # 设置中断列表获取任务是active
            self.active = target_task
            return TaskSwitched(previous=previous_task_ref,
                                current=target_task_ref)
        else:
            self.active = target_task
            return TaskResumed(task=target_task_ref)


@dataclass
class DialogueState:
    """对话运行状态类"""
    sender_id: str  # 用户id
    shared: SharedState = field(default_factory=SharedState)  # 三种能力都有数据：任务流程、知识问答、闲聊
    tasks: TaskState = field(default_factory=TaskState)  # 任务流程特有数据，流程步骤数据
