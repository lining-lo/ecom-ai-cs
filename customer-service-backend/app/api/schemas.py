"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:对话接口Pydantic数据模型
        定义聊天对象、消息、请求体、响应体结构
"""
from pydantic import BaseModel, Field


class ChatObject(BaseModel):
    type: str
    id: str
    title: str | None = None
    attributes: dict = Field(default_factory={})


class ChatMessage(BaseModel):
    text: str | None = None
    object: ChatObject | None = None


# 封装请求数据
class ChatRequest(BaseModel):
    sender_id: str  # 用户id
    text: str | None = None  # 文本消息
    object: ChatObject | None = None
    message_id: str | None = None  # 消息唯一标识，需要自己生成 使用uuid


# 封装响应数据
class ChatResponse(BaseModel):
    sender_id: str
    message_id: str
    messages: list[ChatMessage]
