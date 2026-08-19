"""
  @Author:lining-lo
  @Time:2026/8/19
  @Desc:
"""
from dataclasses import dataclass, field
from app.task.flow.steps import FlowStep


@dataclass
class FlowSlot:
    name: str
    type: str = "any"
    label: str = ""
    description: str = ""


@dataclass
class Flow:
    id: str
    description: str = ""
    steps: list[FlowStep] = field(default_factory=list)
    slots: list[FlowSlot] = field(default_factory=list)
    name: str | None = None


@dataclass
class FlowCatalog:
    flows: dict[str, Flow] = field(default_factory=dict)
    slots: dict[str, FlowSlot] = field(default_factory=dict)


