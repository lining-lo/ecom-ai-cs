"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc:对话模型类，
        使用dataclass定义消息枚举、用户消息、机器人消息、
        对象卡片、业务处理结果等内部业务实体
"""
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class MessageObject:
    """对象类型消息"""
    type: str  # order  product
    id: str
    title: str | None = None
    attributes: dict = field(default_factory=dict)


class MessageType(Enum):
    """消息类型枚举"""
    TEXT = "text"
    OBJECT = "object"


@dataclass
class UserMessage:
    """用户输入信息"""
    sender_id: str
    message_id: str
    type: MessageType  # 消息类型： 文本 和 对象
    text: str | None = None
    object: MessageObject | None = None


@dataclass
class BotMessage:
    """客服回复信息"""
    text: str | None = None
    object: MessageObject | None = None


@dataclass
class ProcessResult:
    """service方法返回类型"""
    sender_id: str
    message_id: str
    messages: list[BotMessage]
