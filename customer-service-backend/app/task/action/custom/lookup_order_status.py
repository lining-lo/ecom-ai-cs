"""
  @Author:lining-lo
  @Time:2026/8/23
  @Desc:
"""
from typing import Any
from app.task.action.base import Action, ActionResult
from app.conf.config import settings
from app.domain.state import DialogueState
from app.utils import http_client


# 查询订单状态
class LookupOrderStatus(Action):
    name="action_lookup_order_status"

    async def run(
            self,
            state: DialogueState,
            action_kwargs: dict[str, Any],
    ) -> ActionResult:
        # 1 获取订单编号，从state里面槽位获取到
        order_number = state.tasks.active.slots.get("order_number")

        # 2 httpx调用中台接口，路径+参数+提交方式get
        url = f"{settings.commerce_api_base_url}/orders/{order_number}/status"
        response = await http_client.http_client.get(url)
        data = response.json()["data"]

        # 封装到ActionResult
        return ActionResult(
            slot_updates={
                "order_status": data["status"],
                "order_summary": data["status_desc"],
            }
        )