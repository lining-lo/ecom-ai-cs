"""
  @Author:lining-lo
  @Time:2026/8/19
  @Desc:任务流程与槽位数据模型类，
        Flow代表单个任务流程，FlowCatalog管理全部流程集合，
        提供按ID查找流程、步骤、获取起始步骤的查询能力
"""
from dataclasses import dataclass, field
from app.task.flow.steps import FlowStep, StartFlowStep


@dataclass
class FlowSlot:
    """槽位数据模型类"""
    name: str
    type: str = "any"
    label: str = ""
    description: str = ""


@dataclass
class Flow:
    """任务流程类"""
    id: str
    description: str = ""
    steps: list[FlowStep] = field(default_factory=list)
    slots: list[FlowSlot] = field(default_factory=list)
    name: str | None = None

    def get_start_step(self) -> StartFlowStep:
        """获取开始类型步骤数据"""
        for step in self.steps:
            # 判断 开始类型
            if isinstance(step, StartFlowStep):
                return step
        raise Exception("Flow not found")

    def get_step_by_id(self, step_id) -> FlowStep:
        """根据步骤id获取步骤对应数据"""
        for step in self.steps:
            if step.id == step_id:
                return step
        raise Exception("step not found")


@dataclass
class FlowCatalog:
    """任务流程与槽位数据模型类"""
    flows: dict[str, Flow] = field(default_factory=dict)
    slots: dict[str, FlowSlot] = field(default_factory=dict)

    def get_flow_by_id(self, flow_id):
        """根据流程id查询流程的方法"""
        return self.flows[flow_id]
