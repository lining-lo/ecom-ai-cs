"""
  @Author:lining-lo
  @Time:2026/8/19
  @Desc:机器人回复模板模型，
        定义static/rephrase/generate三种输出模式，
        封装文本与prompt，支持从字典反序列化加载配置
"""
from dataclasses import dataclass
from enum import Enum


class ResponseMode(Enum):
    """回复类型枚举"""
    # 直接返回text内容
    STATIC = "static"

    # 基于text内容，调用llm，把text修改返回
    REPHRASE = "rephrase"

    # 直接llm生成内容 返回
    GENERATE = "generate"


@dataclass
class ResponseTemplate:
    """机器人回复模板模型"""
    mode: ResponseMode = ResponseMode.STATIC
    text: str | None = None
    prompt: str | None = None

    @classmethod
    def from_dict(cls, template_data: dict
                  ) -> "ResponseTemplate":
        return cls(
            mode=ResponseMode(template_data['mode'])
            if 'mode' in template_data
            else ResponseMode.STATIC,
            text=template_data.get('text'),
            prompt=template_data.get('prompt'))
