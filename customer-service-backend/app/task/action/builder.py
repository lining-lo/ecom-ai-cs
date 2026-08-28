"""
  @Author:lining-lo
  @Time:2026/8/24
  @Desc:业务动作注册入口，
        将自定义Action实例注册到动作注册中心，
        后续可改为包扫描自动注册
"""
import importlib
import inspect
import pkgutil
from app.task.action.base import Action
from app.task.action.custom.logistics_tracking import LookupTracking
from app.task.action.custom.lookup_order_status import LookupOrderStatus
from app.task.action.registry import ActionRegistry


# todo 根据包扫描规则实现自动注册
# def register_service_action(registry: ActionRegistry):
#     """业务动作统一注册入口"""
#     registry.register_action(LookupTracking())
#     registry.register_action(LookupOrderStatus())

def register_service_action(
        registry: ActionRegistry,
) -> None:
    # 1 加载当前扫描包路径
    package = importlib.import_module(
        "app.task.action.custom")

    # 2 找到包下面所有模块，对所有模块遍历
    for _, module_name, is_package in pkgutil.iter_modules(package.__path__,
                                                           prefix=f"{package.__name__}.", ):
        # 如果 app.task.action.custom包下面，还有包，
        if is_package:
            continue

        # 如果不是包，就是模块，加载模块处理
        module = importlib.import_module(module_name)

        # 获取每个模块所有成员： 方法、属性、类（获取）
        for _, action_class in inspect.getmembers(module, inspect.isclass):
            # 类的类型必须Action类型
            # 类不能是Action基类
            if not issubclass(action_class, Action) or action_class is Action:
                continue

            # action必须是当前模块定义，不能是其他模块import进来的
            if action_class.__module__ != module.__name__:
                continue

            # 注册
            registry.register_action(action_class())
