"""
  @Author:lining-lo
  @Time:2026/8/21
  @Desc: 
"""
from app.domain.message import BotMessage
from app.task.flow.models import FlowCatalog, Flow
from app.task.lifecycle.models import TaskEvent, TaskStarted, TaskSwitched, TaskResumed, TaskCanceled


class TaskLifecycleResponder:
    def __init__(self, flows: FlowCatalog) -> None:
        self.flows = flows

    def respond(self, events: list[TaskEvent]) -> list[BotMessage]:
        messages: list[BotMessage] = []
        # 遍历
        for event in events:
            messages.append(self._execute_event_data(event))
        return messages

    # 根据流程id获取对应名称
    def _get_flow_name(self, flow_id: str) -> str:
        flow: Flow = self.flows.get_flow_by_id(flow_id)
        return flow.name

    def _execute_event_data(self, event: TaskEvent) -> BotMessage:
        if isinstance(event, TaskStarted):
            flow_name = self._get_flow_name(event.task.flow_id)
            return BotMessage(text=f"好的，我现在开始处理{flow_name}")

        if isinstance(event, TaskSwitched):
            # 暂停流程名称
            previous_flow_name = self._get_flow_name(event.previous.flow_id)
            # 开始流程名称
            current_flow_name = self._get_flow_name(event.current.flow_id)

            return BotMessage(text=f"好的，先把 {previous_flow_name} 暂停 "
                                   f"先处理 {current_flow_name} ")

        if isinstance(event, TaskResumed):
            # 开始流程名称
            resumed_flow_name = self._get_flow_name(event.task.flow_id)
            return BotMessage(text=f"好的，继续刚才{resumed_flow_name}")

        if isinstance(event, TaskCanceled):
            # 开始流程名称
            canceled_flow_name = self._get_flow_name(event.task.flow_id)
            return BotMessage(text=f"好的，{canceled_flow_name}取消操作")

        raise ValueError("Unknown event")
