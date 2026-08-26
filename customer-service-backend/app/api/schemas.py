"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:api接口层数据模型
"""
from pydantic import BaseModel, Field


class ChatObject(BaseModel):
    """订单对象信息"""
    type: str
    id: str
    title: str | None = None
    attributes: dict = Field(default_factory={})


class ChatMessage(BaseModel):
    """客服回复的信息"""
    text: str | None = None  # 文本消息
    object: ChatObject | None = None  # 订单对象信息


class ChatRequest(BaseModel):
    """请求数据"""
    sender_id: str  # 用户id
    text: str | None = None  # 文本消息
    object: ChatObject | None = None  # 订单对象信息
    message_id: str | None = None  # 消息唯一标识，需要自己生成 使用uuid


class ChatResponse(BaseModel):
    """响应数据"""
    sender_id: str  # 用户id
    message_id: str  # 消息唯一标识
    messages: list[ChatMessage]  # 返回的消息
