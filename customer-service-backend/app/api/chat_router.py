"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:对话聊天接口路由
"""
import uuid

from fastapi import APIRouter

from app.api.schemas import ChatRequest, ChatResponse, ChatMessage

# 创建路由
chat_router = APIRouter()


@chat_router.post("/api/chat")
def chat(chat_request: ChatRequest) -> ChatResponse:
    # 接受前端传递问题，封装ChatRequest里面
    # todo 调用service方法

    return ChatResponse(
        sender_id=chat_request.sender_id,
        message_id=chat_request.message_id if chat_request.message_id else str(uuid.uuid4()),
        messages=[ChatMessage(text="hello")]
    )
