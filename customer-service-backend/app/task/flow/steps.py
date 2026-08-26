"""
  @Author:lining-lo
  @Time:2026/8/19
  @Desc:流程步骤数据模型，
        定义各类流程步骤实体，实现YAML字典到步骤对象的反序列化，
        处理静态、条件、兜底跳转链接解析
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from app.task.flow.links import FlowStepLink, StaticLink, ConditionalLink, FallbackLink
from app.task.response.models import ResponseTemplate


@dataclass
class SlotValidation:
    condition: str | None = None
    failure_template: ResponseTemplate | None = None


class FlowStepType(Enum):
    """流程步骤枚举类"""
    START = "start"
    ACTION = "action"
    RESPONSE = "response"
    COLLECT = "collect"
    END = "end"


@dataclass
class FlowStep:
    """流程步骤数据模型"""
    id: str
    type: FlowStepType
    next: list[FlowStepLink] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "FlowStep":
        """转化为流程步骤数据模型方法"""
        flow_type = flow_step_data['type']
        # type= action   得到类 ActionFlowStep
        clz = TYPE_TO_STEP_CLASS[flow_type]

        # ActionFlowStep.from_dict(flow_step_data)
        return clz.from_dict(flow_step_data)

    @classmethod
    def base_fields(cls, flow_step_data: dict[str, Any]) -> dict[str, Any]:
        return {
            'id': flow_step_data['id'],
            'type': FlowStepType(flow_step_data['type']),
            'description': flow_step_data.get('description', ''),
            'next': cls._build_links(flow_step_data['next'])
        }

    @classmethod
    def _build_links(cls, next_data: str | list[dict]) -> list[FlowStepLink]:
        """构建下一步流程方法"""
        # next值字符串，无条件跳转
        if isinstance(next_data, str):
            return [StaticLink(target=next_data)]
        else:  # 有条件跳转
            link_list: list[FlowStepLink] = []
            for link_data in next_data:
                if 'if' in link_data:
                    link_list.append(ConditionalLink(condition=link_data['if'], target=link_data['then']))
                else:
                    link_list.append(FallbackLink(target=link_data['else']))
            return link_list


@dataclass
class StartFlowStep(FlowStep):
    """开始步骤"""

    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "StartFlowStep":
        return cls(**FlowStep.base_fields(flow_step_data))


@dataclass
class ActionFlowStep(FlowStep):
    """业务动作步骤"""
    action: str = ""
    args: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "ActionFlowStep":
        return cls(
            **FlowStep.base_fields(flow_step_data),
            action=flow_step_data['action'],
            args=flow_step_data.get('args', {})
        )


@dataclass
class ResponseFlowStep(FlowStep):
    """回复步骤"""
    template: ResponseTemplate = field(default_factory=ResponseTemplate)

    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "ResponseFlowStep":
        # todo: 加载逻辑
        # pass
        return cls(
            **FlowStep.base_fields(flow_step_data),
            template=ResponseTemplate.from_dict(
                flow_step_data['template'])
        )


@dataclass
class CollectSlotStep(FlowStep):
    """收集槽位数据步骤"""
    slot_name: str = ""
    template: ResponseTemplate = field(default_factory=ResponseTemplate)
    validation: SlotValidation | None = None

    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "CollectSlotStep":
        # todo: 加载逻辑
        # pass
        validation = None
        if 'validation' in flow_step_data:
            validation = SlotValidation(
                condition=flow_step_data['validation']['condition'],
                failure_template=ResponseTemplate.from_dict(
                    flow_step_data['validation']
                    ['failure_template'])
            )

        return cls(
            **FlowStep.base_fields(flow_step_data),
            slot_name=flow_step_data['slot_name'],
            template=ResponseTemplate.from_dict(flow_step_data['template']),
            validation=validation
        )


@dataclass
class EndFlowStep(FlowStep):
    """结束步骤"""
    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "EndFlowStep":
        return cls(**FlowStep.base_fields(flow_step_data))

# 步骤集合
TYPE_TO_STEP_CLASS = {
    'start': StartFlowStep,
    'collect': CollectSlotStep,
    'response': ResponseFlowStep,
    'action': ActionFlowStep,
    'end': EndFlowStep
}
