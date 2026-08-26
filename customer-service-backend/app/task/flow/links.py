"""
  @Author:lining-lo
  @Time:2026/8/19
  @Desc:流程步骤跳转链路实体，
        定义静态跳转、条件跳转、兜底跳转三种链接类型，
        承载步骤间的分支配置
"""
from dataclasses import dataclass


@dataclass
class FlowStepLink:
    """流程步骤跳转链路"""
    target: str


@dataclass
class StaticLink(FlowStepLink):
    """普通流程步骤跳转链路"""
    pass


@dataclass
class ConditionalLink(FlowStepLink):
    """条件流程步骤跳转链路"""
    condition: str


@dataclass
class FallbackLink(FlowStepLink):
    """兜底流程步骤跳转链路"""
    pass
