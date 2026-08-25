"""
  @Author:lining-lo
  @Time:2026/8/23
  @Desc: 
"""
from app.task.action.base import ActionCall, ActionResult
from app.task.action.runner import ActionRunner
from app.domain.message import UserMessage, BotMessage
from app.domain.state import DialogueState
# from app.task.action.base import ActionCall
from app.task.flow.links import FlowStepLink, ConditionalLink, FallbackLink
from app.task.flow.models import FlowCatalog, Flow
from app.task.flow.steps import FlowStep, StartFlowStep, ResponseFlowStep, CollectSlotStep, ActionFlowStep, \
    EndFlowStep
from app.task.response.renderer import ResponseRenderer


# TaskHandler组件，推进业务里面步骤
class FlowExecutor:
    def __init__(self,response_renderer:ResponseRenderer,
                 action_runner:ActionRunner):
        self._response_renderer = response_renderer
        self._action_runner = action_runner

    async def run_task(self,
                       state: DialogueState,
                       user_message: UserMessage,
                       flows: FlowCatalog) -> list[BotMessage]:
        bot_messages: list[BotMessage] = []

        # 判断当前是否有活跃任务,没有
        if not state.tasks.active:
            return bot_messages

        # 当前有活跃任务
        # while True:
        for _ in range(100):
            # 推进步骤实现，获取步骤是什么
            # 1 根据流程id获取流程对象
            flow:Flow = flows.get_flow_by_id(
                state.tasks.active.flow_id)
            # 2 在获取流程对象里面，根据步骤id获取步骤对应数据
            step:FlowStep = flow.get_step_by_id(
                    state.tasks.active.step_id)
            # 3 判断步骤类型，不同类型进行不同处理
            """
                start类型步骤处理流程：
                * 本身不做什么事情，就是推进到下一步
                * 推进到下一步：
                ** 到下一步：无条件跳转 StaticLink，
                **         有条件跳转，条件成立 ConditionalLink
                **         有条件跳转，条件不成立 FallbackLink
            """
            if isinstance(step, StartFlowStep):
                self._run_step(step, state)
                continue

            """
                response类型步骤处理流程
                * 渲染数据
                * 返回内容
            """
            if isinstance(step, ResponseFlowStep):
                # 调用ResponseRenderer方法实现渲染数据
                bot_message: BotMessage = await self._response_renderer.render(
                    step.template, state, user_message
                )
                # 把渲染之后数据放到list里面
                bot_messages.append(bot_message)
                # 推进下一步
                self._run_step(step,state)
                continue

            """
                收集槽位数据步骤类型
            """
            if isinstance(step, CollectSlotStep):
                # need_input是bool  true:需要用户输入，没有槽位数据   false：有槽位数据
                need_input = self._run_collect_step(step,state,
                                       user_message,
                                       bot_messages)
                if need_input: # true需要用户输入，没有槽位数据
                    return bot_messages
                else: # 有槽位数据，推进下一步
                    self._run_step(step,state)
                    continue

            """
                处理action类型步骤
                * 调用中台系统接口实现具体业务，比如查询订单状态

            """
            if isinstance(step, ActionFlowStep):
                # 1 从action步骤里面获取action值
                action_name = step.action
                action_kwargs = step.args
                action_call = ActionCall(action_name, action_kwargs)

                # 2 根据action值找到对应action业务对象
                # 3 调用action业务对象里面的方法调用中台接口
                # 4 把action返回结果
                action_result: ActionResult = await self._action_runner.run(
                    action_call=action_call,
                    state=state)

                # 5 封装处理,封装state里面slots里面
                state.tasks.active.slots.update(
                    action_result.slot_updates)

                # 5 推进下一步
                self._run_step(step, state)
                continue

            """
                处理结束end步骤
            """
            if isinstance(step, EndFlowStep):
                state.tasks.active = None
                return bot_messages

        return bot_messages

    def _run_step(self,step:FlowStep,state:DialogueState):
        """往后推进步骤"""
        # 把当前步骤的next值设置当前active里面步骤id
        # next_step_id = step.next
        # step.next有两种情况 字符串  列表 if then else
        next_step_id = self._select_next_step(step.next, state)
        state.tasks.active.step_id = next_step_id

    def _select_next_step(self,
                          next:list[FlowStepLink],
                          state:DialogueState)->str:
        # 如果next是一个字符串
        if len(next) == 1:
            return next[0].target

        for link in next:
            if isinstance(link, ConditionalLink):
                # 从state里面获取需要数据，和if条件比较，条件是否成立
                # 返回bool
                result = bool(eval(link.condition,
                                   {},
                                   {"slots":state.tasks.active.slots}))
                if result:
                    return link.target
                continue
            if isinstance(link, FallbackLink):
                return link.target

    # 处理collect类型步骤
    async def _run_collect_step(self,
                          step:CollectSlotStep,
                          state:DialogueState,
                          user_message:UserMessage,
                          bot_messages:list[BotMessage])->bool:
        # 1 从当前活跃任务获取槽位数据
        slots:dict = state.tasks.active.slots
        slot_value = slots.get(step.slot_name)

        # 2 如果当前活跃任务获取不到槽位数据，从聚焦对象获取槽位数据
        if not slot_value:
            # 从聚焦对象获取槽位数据
            self.get_slot_data_focused_object(step,state)

        # 3 如果上面两个步骤执行之后，槽位数据都获取不到，给用户返回信息
        # true需要用户输入，没有槽位数据
        slots_value = state.tasks.active.slots.get(step.slot_name)
        if not slots_value:
            bot_message = await self._response_renderer.render(
                step.template,state,user_message)
            bot_messages.append(bot_message)
            return True

        # 4 如果上面两步获取槽位数据
        else:
            # 5 判断配置文件是否有validation校验
            if not step.validation:
                # 推进下一步
                return False

            # 6 如果没有validation校验，直接推进到下一步
            else:
                # 7 如果有validation校验，判断校验条件是否成立，方法eval
                result = bool(eval(step.validation.condition,{},
                          {'slots':state.tasks.active.slots}))

                # 8 如果校验成立，推进下一步
                if result:
                    return False

                # 9 如果校验不成立，回复提示信息 failure_response
                else:
                    # 从槽删除数据
                    state.tasks.active.slots.pop(step.slot_name)
                    bot_message = self._response_renderer.render(
                        step.validation.failure_template, state, user_message)
                    bot_messages.append(bot_message)
                    return True

    # 从state聚焦对象获取槽位数据
    def get_slot_data_focused_object(self, step, state):
        # 1 判断focused_object对象是否为空
        if not state.shared.focused_object:
            return

        # 2 focused_object对象不为空
        # focused_object 目前有两种  order  product
        # 对象类型 order
        if (step.slot_name=='order_number'
                and state.shared.focused_object.type=='order'):
            state.tasks.active.slots.update(
                {step.slot_name: state.shared.focused_object.id})
            return

        if (step.slot_name=='product_id'
                and state.shared.focused_object.type=='product'):
            state.tasks.active.slots.update(
                {step.slot_name: state.shared.focused_object.id})
            return


