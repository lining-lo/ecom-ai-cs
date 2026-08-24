"""
  @Author:lining-lo
  @Time:2026/8/23
  @Desc:
"""
from app.action.base import ActionCall, ActionResult, Action
from app.action.registry import ActionRegistry
from app.domain.state import DialogueState


class ActionRunner:
    def __init__(self, registry: ActionRegistry):
        self._registry = registry

    # 对外提供的方法，根据action值找到action对象，调用中台接口返回数据
    # 1 action_call: action类型步骤里面action属性值和args属性值
    # 2 state: 如果查询物流状态，从state的槽位获取订单号
    async def run(self, action_call: ActionCall,
                  state: DialogueState) -> ActionResult:
        # 1 根据action值获取对应action对象
        action_name = action_call.action_name
        action: Action = self._registry.get_action(action_name)

        # 2 调用获取action对象的方法中台接口调用，得到结果
        return await action.run(state=state,
                                action_kwargs=action_call.action_kwargs)
