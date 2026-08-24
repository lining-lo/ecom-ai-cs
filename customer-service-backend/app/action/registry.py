"""
  @Author:lining-lo
  @Time:2026/8/24
  @Desc:
"""
from app.action.base import Action


class ActionRegistry:

    def __init__(self):
        self._actions: dict[str, Action] = {}

    # 注册方法，向字典放数据
    def register_action(self, action: Action):
        self._actions[action.name] = action

    # 从字典获取action对象方法
    def get_action(self, name: str) -> Action:
        return self._actions[name]
