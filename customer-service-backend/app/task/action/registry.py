"""
  @Author:lining-lo
  @Time:2026/8/24
  @Desc:Action动作注册中心，
        管理全部业务动作实例，支持动作注册与按名称检索，
        用于流程调度时查找对应业务动作
"""
from app.task.action.base import Action


class ActionRegistry:
    """Action动作注册中心"""

    def __init__(self):
        self._actions: dict[str, Action] = {}

    def register_action(self, action: Action):
        """注册action动作的方法"""
        self._actions[action.name] = action

    def get_action(self, name: str) -> Action:
        """获取action动作的方法"""
        return self._actions[name]
