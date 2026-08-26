"""
  @Author:lining-lo
  @Time:2026/8/24
  @Desc:
"""
from app.domain.message import UserMessage, BotMessage
from app.domain.state import DialogueState
from app.task.command.models import Command
from app.task.command.processor import CommandProcessor
from app.task.flow.executor import FlowExecutor
from app.task.flow.models import FlowCatalog
from app.task.lifecycle.models import TaskEvent
from app.task.lifecycle.responder import TaskLifecycleResponder


# TaskHander有三个组件，调用
class TaskHandler:
    def __init__(self,
                 command_processor: CommandProcessor,
                 task_lifecycle: TaskLifecycleResponder,
                 flow_executor: FlowExecutor,
                 flow_catalog: FlowCatalog):
        self._command_processor = command_processor
        self._task_lifecycle = task_lifecycle
        self._flow_executor = flow_executor
        self._flow_catalog = flow_catalog

    # commands:list[Command]: llm意图识别结果
    # DialogueState: CommandProcessor更新里面数据
    async def handle(self, commands: list[Command],
                     state: DialogueState,
                     user_message: UserMessage) -> list[BotMessage]:
        # 1 接受意图识别结果，根据结果使用CommandProcessor更新DialogueState
        task_events: list[TaskEvent] = await self._command_processor.run(commands=commands,
                                                                   state=state,
                                                                   flows=self._flow_catalog)

        # 2 根据CommandProcessor返回状态变化数据，调用TaskLifecycleResponder，生成中文提示
        messages: list[BotMessage] = await self._task_lifecycle.respond(task_events)

        # 3 调用FlowExecutor推进流程的步骤
        result: list[BotMessage] = await self._flow_executor.run_task(state=state,
                                                                      user_message=user_message,
                                                                      flows=self._flow_catalog)
        messages.extend(result)
        return messages
