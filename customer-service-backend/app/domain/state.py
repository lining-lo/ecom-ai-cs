"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc: 
"""
import time
import uuid
from dataclasses import dataclass, field
from app.domain.message import UserMessage, BotMessage
from app.task.lifecycle.models import TaskEvent, TaskSwitched, TaskStarted, TaskRef, TaskCanceled, TaskResumed


# 一轮对话，一个问题对应一个或者多个回答
@dataclass
class Turn:
    turn_id: str
    # 用户提问
    user_message: UserMessage
    # 客服回复
    bot_message: list[BotMessage] = field(default_factory=list)


# 会话对象
@dataclass
class Session:
    # session的id，区别不同session
    session_id: str
    # session创建时间戳
    started_at: float
    # session最后一次活跃时间
    last_activity_at: float
    # 关闭时间
    closed_at: float
    # 每个session会话多轮对话
    turns: list[Turn] = field(default_factory=list)


# 对象类型消息
@dataclass
class FocusedObject:
    type: str
    id: str
    title: str | None = None
    attributes: dict = field(default_factory=dict)


# 三种能力都有数据：任务流程、知识问答、闲聊
@dataclass
class SharedState:
    # 对象类型消息
    focused_object: FocusedObject | None = None
    # 多个会话数据
    sessions: list[Session] | None = None

    # 创建新session
    def create_session(self):
        now = time.time()
        session = Session(
            session_id=str(uuid.uuid4()),
            started_at=now,
            last_activity_at=now,
        )
        # 创建session对象放到state里面
        self.sessions.append(session)

    # 关闭当前session
    def close_current_session(self):
        self.sessions[-1].closed_at = time.time()


# 某个任务流程步骤相关数据
@dataclass
class TaskInstance:
    # 流程id，对应yaml文件  refund_request
    flow_id: str
    # 步骤id ,比如 start
    step_id: str | None
    # 当前任务id
    task_id: str
    # 槽位数据字典  {order_number : a10098765}
    slots: dict = field(default_factory=dict)

    # task_id: str
    # flow_id: str
    def to_ref(self) -> TaskRef:
        return TaskRef(task_id=self.task_id,
                       flow_id=self.flow_id, )


# 任务流程特有数据，流程步骤数据
@dataclass
class TaskState:
    # 当前正在运行（活跃）的任务
    active: TaskInstance | None = None
    # 中断（暂停）的任务
    paused: list[TaskInstance] = field(default_factory=list)

    # 把数据封装DialogueState里面
    # TaskInstance =》 TaskState =》 DialogueState
    def start(self, task: TaskInstance) -> TaskEvent:
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
    # 用户id
    sender_id: str
    # 三种能力都有数据：任务流程、知识问答、闲聊
    shared: SharedState = field(default_factory=SharedState)
    # 任务流程特有数据，流程步骤数据
    tasks: TaskState = field(default_factory=TaskState)
