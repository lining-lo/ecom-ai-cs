"""
  @Author:lining-lo
  @Time:2026/8/21
  @Desc: 
"""
from app.domain.state import DialogueState, TaskInstance
from app.task.command.models import Command, StartFlowCommand, SetSlotsCommand, CancelTaskCommand, ResumeTaskCommand
from app.task.flow.models import FlowCatalog, Flow
from app.task.flow.steps import StartFlowStep
from app.task.lifecycle.models import TaskEvent


class CommandProcessor:
    # commands 意图识别返回结果
    # state：状态数据
    # flows：流程数据
    def run(self,
            commands: list[Command],
            state: DialogueState,
            flows: FlowCatalog,
    ) -> list[TaskEvent]:
        # 定义遍历，封装最终数据
        events: list[TaskEvent] = []
        # 遍历commands，得到每个command，根据不同类型分别不同处理
        for command in commands:
            # 调用方法
            event = self._apply(command=command,
                                state=state,
                                flows=flows)
            if event:
                events.append(event)
        return events

    # 处理每个command
    def _apply(self,
            command: Command,
            state: DialogueState,
            flow_catalog: FlowCatalog
    )-> TaskEvent:
        # 判断command类型
        # start_flow 开始流程
        if isinstance(command, StartFlowCommand):
            # 获取StartFlowCommand里面流程id
            # {"command": "start_flow", "flow": "<flow_id>"}
            flow_id = command.flow
            # 根据flow_id获取对应flow数据
            # 在FlowCatalog增加根据流程id查询流程的方法
            flow:Flow = flow_catalog.get_flow_by_id(flow_id)

            # 从Flow里面找到类型是start步骤，把对应id获取到
            # Flow类增加 获取开始步骤数据
            start_step:StartFlowStep = flow.get_start_step()

            # 封装数据到TaskInstance
            task = TaskInstance(
                flow_id=flow_id,
                step_id=start_step.id
            )

            # 把数据封装DialogueState里面
            # TaskInstance =》 TaskState =》 DialogueState
            # 把TaskInstance封装方法
            # TaskState增加start方法
            event:TaskEvent = state.tasks.start(task)
            return event

        # {"command": "set_slots", "slots": {"<slot_name>": "<value>"}}
        # 设置槽数据，当前必须有运行任务
        # 因为设置槽数据，没有任务状态变化，都是在当前运行任务里面设置，必须要返回变化对象
        if isinstance(command, SetSlotsCommand):
            state.tasks.active.slots.update(command.slots)
            return None

        # {"command": "cancel_task", "task_id": "<task_id>"}
        if isinstance(command, CancelTaskCommand):
            # # TaskState增加cancel方法
            event: TaskEvent = state.tasks.cancel(command.task_id)
            return event

        # {"command": "resume_task", "task_id": "<task_id>"}
        if isinstance(command, ResumeTaskCommand):
            # # TaskState增加resume方法
            event: TaskEvent = state.tasks.resume(command.task_id)
            return event
