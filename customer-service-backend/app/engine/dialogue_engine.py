"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc:对话处理类，对话系统顶层入口；
        管理会话过期，处理文本/对象两类消息，完成意图规划、计划校验，
        调度任务处理器执行业务流程，输出机器人回复
"""
import time
import uuid
from dataclasses import asdict
from app.chitchat.handler import ChitchatHandler
from app.clarify.handler import ClarifyResponder
from app.domain.message import UserMessage, ProcessResult, MessageType, BotMessage
from app.domain.state import DialogueState, Turn, FocusedObject
from app.knowledge.handler import KnowledgeHandler
from app.plan.models import TurnPlan, TurnPlanValidationResult
from app.plan.turn_plan import TurnPlanner
from app.plan.turn_plan_validation import TurnPlanValidation
from app.task.command.models import SetSlotsCommand
from app.task.flow.models import Flow
from app.task.flow.steps import FlowStep, CollectSlotStep
from app.task.handler import TaskHandler


class DialogueEngine:
    """对话处理类"""

    def __init__(self,
                 turn_planner: TurnPlanner,
                 turn_plan_validation: TurnPlanValidation,
                 task_handler: TaskHandler,
                 knowledge_handler: KnowledgeHandler,
                 chitchat_handler: ChitchatHandler,
                 clarify_responder: ClarifyResponder):
        self._turn_planner = turn_planner
        self._turn_plan_validation = turn_plan_validation
        self._task_handler = task_handler
        self._knowledge_handler = knowledge_handler
        self._chitchat_handler = chitchat_handler
        self._clarify_responder = clarify_responder

    async def process_message(self, state: DialogueState,
                              user_message: UserMessage) -> ProcessResult:
        """
        处理对话的方法
        :param state: 对话运行状态
        :param user_message: 用户输入信息
        :return: ProcessResult: service方法返回类型
        """
        # 1 准备当前会话
        self._prepare_session(state)

        # 2 准备本轮Turn
        turn = Turn(turn_id=str(uuid.uuid4()), user_message=user_message)

        # 3 判断消息类型
        # 文本类型消息
        if user_message.type == MessageType.TEXT:
            messages: list[BotMessage] = await self._execute_text_message(user_message, state)
        else:  # 对象类型消息
            messages: list[BotMessage] = await self._execute_object_message(user_message, state)

        # 4 提交本轮对话记录
        ## 封装list[BotMessage]到turn对象
        turn.bot_message.extend(messages)
        # 放到当前session里面
        state.shared.sessions[-1].turns.append(turn)

        # 5 返回本轮回复
        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            messages=messages
        )

    def _prepare_session(self, state: DialogueState):
        """
        准备当前session会话的方法
        :param state: 对话运行状态类
        """
        # 判断当前session存在
        # 不存在session
        if not state.shared.sessions:
            # 创建session
            state.shared.create_session()

        else:  # 存在session
            # 判断session是否过期,
            current_session = state.shared.sessions[-1]
            # 获取当前时间戳
            now = time.time()
            # 60分钟不活跃过期
            if now - current_session.last_activity_at > 60 * 60:
                # 手动session过期
                state.shared.close_current_session()
                # 创建新session
                state.shared.create_session()
            else:  # session没有过期
                # 更新最后活跃时间当前时间
                current_session.last_activity_at = now

    async def _execute_text_message(self,
                                    user_message: UserMessage,
                                    state: DialogueState) -> list[BotMessage]:
        """
        处理文本类型消息的方法
        :param user_message: 用户输入信息
        :param state: 对话运行状态类
        :return: list[BotMessage]: 客服回复信息列表
        """
        # 1 根据user_message文本提问信息，调用llm，进行意图识别
        # 识别执行哪个轨道：任务流程、知识检索、闲聊；
        # 如果任务流程，识别流程id
        turnPlan: TurnPlan = await self._turn_planner.plan(user_message=user_message,
                                                           state=state,
                                                           flow_catalog=self._task_handler._flow_catalog)

        # 2 对llm意图识别结果校验
        ## 比如识别有两个轨道，任务流程识别流程id不存在......
        validation: TurnPlanValidationResult = self._turn_plan_validation.validate(
            turn_plan=turnPlan,
            state=state,
            flow_catalog=self._task_handler._flow_catalog)

        # 3 校验失败，调用反问澄清组件
        if not validation.valid:
            # todo 反问澄清组件
            pass

        # 4 校验成功，根据识别不同轨道，调用不同handler处理，
        # 识别任务流程，调用TaskHandler方法执行
        if turnPlan.task:
            return await self._task_handler.handle(
                commands=turnPlan.task.commands,
                state=state,
                user_message=user_message,
            )

        # todo 知识检索
        if turnPlan.knowledge:
            pass
        # todo 闲聊
        if turnPlan.chitchat:
            pass

    async def _execute_object_message(self, user_message, state):
        """处理对象类型消息的方法"""
        # 1 把对象消息放到state里面 focused_object
        state.shared.focused_object = FocusedObject(
            **asdict(user_message.object)
        )

        # 2 判断，是否填充槽位数据
        if self._can_fill_slots(state):
            if user_message.object.type == 'order':
                slots = {'order_number': user_message.object.id}
            else:
                slots = {'product_id': user_message.object.id}

            # 最终调用TaskHandler里面方法，传入command对象，对象类型消息处理
            # 没有调用意图识别组件，没有command
            # 手动构建command对象，设置对应类型
            # {"command": "set_slots", "slots": {"<slot_name>": "<value>"}}`
            command = SetSlotsCommand(
                command='set_slots',
                slots=slots
            )
            # 调用TaskHandler方法执行
            return await self._task_handler.handle(
                commands=[command],
                state=state,
                user_message=user_message,
            )
        else:
            # 反问澄清
            pass

    def _can_fill_slots(self, state: DialogueState) -> bool:
        """校验是否允许填充槽数据的方法"""
        # 1 判断当前是否有活跃任务
        active_task = state.tasks.active
        if not active_task:
            return False

        # 2 有活跃任务
        # 根据当前任务流程id，获取流程对象
        flow_id = active_task.flow_id
        flow: Flow = self._task_handler._flow_catalog.get_flow_by_id(flow_id)

        # 从流程对象获取所有步骤列表，当前任务步骤id到列表找到步骤对应数据
        step: FlowStep = flow.get_step_by_id(active_task.step_id)

        # # 判断当前步骤是否collect类型
        if not isinstance(step, CollectSlotStep):
            return False

        if (step.slot_name == 'order_number') and (state.shared.focused_object.type == 'order'):
            return True

        if (step.slot_name == 'product_id') and (state.shared.focused_object.type == 'product'):
            return True

        return False
