"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc: 
"""
import time
import uuid
from app.domain.message import UserMessage, ProcessResult, MessageType, BotMessage
from app.domain.state import DialogueState, Turn
from app.plan.models import TurnPlan, TurnPlanValidationResult
from app.plan.turn_plan_validation import TurnPlanValidation
from app.task.handler import TaskHandler


# 处理消息
class DialogueEngine:
    def __init__(self,
                 turn_plan: TurnPlan,
                 turn_plan_validation: TurnPlanValidation,
                 task_handler: TaskHandler):
        self._turn_plan = turn_plan
        self._turn_plan_validation = turn_plan_validation
        self._task_handler = task_handler

    async def process_mesasge(self, state: DialogueState,
                              user_message: UserMessage) -> ProcessResult:
        # 1 准备当前会话
        self._prepare_session(state)

        # 2 准备本轮Turn
        turn = Turn(turn_id=str(uuid.uuid4()), user_message=user_message)

        # 3 判断消息类型
        # 文本类型消息
        if user_message.type == MessageType.TEXT:
            messages: list[BotMessage] = await self._execute_text_message(user_message, state)
        else:  # 对象类型消息
            messages: list[BotMessage] = self._execute_object_message(user_message, state)

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

    # 1 准备当前session会话
    def _prepare_session(self, state: DialogueState):
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

    # 2 处理文本类型消息
    async def _execute_text_message(self,
                                    user_message: UserMessage,
                                    state: DialogueState) -> list[BotMessage]:
        # 1 根据user_message文本提问信息，调用llm，进行意图识别
        # 识别执行哪个轨道：任务流程、知识检索、闲聊；
        # 如果任务流程，识别流程id
        turnPlan: TurnPlan = await self._turn_plan.plan(user_message=user_message,
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

    # 处理对象类型消息
    def _execute_object_message(self, user_message, state) -> list[BotMessage]:
        pass
