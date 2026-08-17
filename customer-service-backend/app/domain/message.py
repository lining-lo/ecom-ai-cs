"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc: 
"""
from dataclasses import dataclass, field
from enum import Enum


# 对象类型消息
@dataclass
class MessageObject:
    type: str  # order  product
    id: str
    title: str | None = None
    attributes: dict = field(default_factory=dict)


# 枚举
class MessageType(Enum):
    TEXT = "text"
    OBJECT = "object"


# 用户输入信息
@dataclass
class UserMessage:
    sender_id: str
    message_id: str
    # 消息类型： 文本 和 对象
    type: MessageType
    text: str | None = None
    object: MessageObject | None = None


# 客服回复信息
@dataclass
class BotMessage:
    text: str | None = None
    object: MessageObject | None = None


# service方法返回类型
@dataclass
class ProcessResult:
    sender_id: str
    message_id: str
    messages: list[BotMessage]
