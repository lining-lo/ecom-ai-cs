"""
  @Author:lining-lo
  @Time:2026/8/23
  @Desc:
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.domain.state import DialogueState


@dataclass
class ActionCall:
    action_name: str
    action_kwargs: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ActionResult:
    slot_updates: dict[str, Any] = field(default_factory=dict)


class Action(ABC):
    name: str = ""

    @abstractmethod
    async def run(
            self,
            state: DialogueState,
            action_kwargs: dict[str, Any],
    ) -> ActionResult:
        pass
