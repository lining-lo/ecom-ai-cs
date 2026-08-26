"""
  @Author:lining-lo
  @Time:2026/8/23
  @Desc:业务动作抽象模型，
        ActionCall描述待执行动作，ActionResult封装执行后的槽位更新，
        Action抽象类定义所有业务动作统一执行接口
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from app.domain.state import DialogueState


@dataclass
class ActionCall:
    """动作调用描述实体"""
    action_name: str
    action_kwargs: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ActionResult:
    """执行业务动作的的返回结果"""
    slot_updates: dict[str, Any] = field(default_factory=dict)


class Action(ABC):
    """业务动作抽象模型"""
    name: str = ""

    @abstractmethod
    async def run(
            self,
            state: DialogueState,
            action_kwargs: dict[str, Any],
    ) -> ActionResult:
        """执行业务动作的统一抽象方法（由子类实现）"""
        pass
