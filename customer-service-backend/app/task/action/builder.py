"""
  @Author:lining-lo
  @Time:2026/8/24
  @Desc:业务动作注册入口，
        将自定义Action实例注册到动作注册中心，
        后续可改为包扫描自动注册
"""
from app.task.action.custom.logistics_tracking import LookupTracking
from app.task.action.custom.lookup_order_status import LookupOrderStatus
from app.task.action.registry import ActionRegistry


# todo 根据包扫描规则实现自动注册
def register_service_action(registry: ActionRegistry):
    """业务动作统一注册入口"""
    registry.register_action(LookupTracking())
    registry.register_action(LookupOrderStatus())
