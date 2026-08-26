"""
  @Author:lining-lo
  @Time:2026/8/23
  @Desc:查询物流动作，
        读取任务槽位订单号，调用电商接口获取物流信息，
        返回待更新的槽位数据
"""
from typing import Any
from app.task.action.base import Action, ActionResult
from app.conf.config import settings
from app.domain.state import DialogueState
from app.utils import http_client


# 查询物流
class LookupTracking(Action):
    """查询物流动作类"""
    name = "action_lookup_logistics"

    async def run(
            self,
            state: DialogueState,
            action_kwargs: dict[str, Any],
    ) -> ActionResult:
        """
        执行查询物流动作
        :param state: 对话运行状态
        :param action_kwargs: 动作调用参数
        :return:ActionResult: 执行业务动作的的返回结果
        """
        order_number = state.tasks.active.slots.get("order_number")
        url = f"{settings.commerce_api_base_url}/orders/{order_number}/logistics"
        response = await http_client.http_client.get(url)
        data = response.json()["data"]
        return ActionResult(
            slot_updates={
                "logistics_company": data["logistics_company"],
                "tracking_number": data["tracking_number"],
                "logistics_status": data["status_desc"],
            }
        )
