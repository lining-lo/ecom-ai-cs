"""
  @Author:lining-lo
  @Time:2026/8/24
  @Desc:
"""
from app.task.action.custom.logistics_tracking import LookupTracking
from app.task.action.custom.lookup_order_status import LookupOrderStatus
from app.task.action.registry import ActionRegistry


# todo 根据包扫描规则实现自动注册
def register_service_action(registry: ActionRegistry):
    registry.register_action(LookupTracking())
    registry.register_action(LookupOrderStatus())
