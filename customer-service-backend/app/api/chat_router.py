"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:对话聊天接口路由
"""
import uuid
from dataclasses import asdict
from fastapi import APIRouter, Depends
from app.api.depend import get_dialogue_service
from app.api.schemas import ChatRequest, ChatResponse, ChatMessage, ChatObject
from app.domain.message import UserMessage, MessageType, MessageObject, ProcessResult
from app.service.dialogue_service import DialogueService

# 创建路由
chat_router = APIRouter()


@chat_router.post("/api/chat")
async def chat(chat_request: ChatRequest,
               dialogue_service: DialogueService = Depends(get_dialogue_service)
               ) -> ChatResponse:
    # 1 接受前端传递问题数据，封装ChatRequest里面
    # 2 把api的ChatRequest转换service对象类型 UserMessage
    user_message: UserMessage = _build_user_message(chat_request)

    # 3 调用service方法，返回结果ProcessResult
    # 在当前方法获取service对象，把service对象注入进来
    process_result: ProcessResult = await dialogue_service.process_message(user_message)

    # 4 把service返回结果ProcessResult ，封装ChatResponse对象，返回
    return _build_chat_response(process_result)


# ChatRequest转换 UserMessage
def _build_user_message(chat_request: ChatRequest) -> UserMessage:
    return UserMessage(
        sender_id=chat_request.sender_id,
        message_id=chat_request.message_id
        if chat_request.message_id else str(uuid.uuid4()),
        type=MessageType.TEXT
        if chat_request.text else MessageType.OBJECT,

        text=chat_request.text,

        object=MessageObject(
            type=chat_request.object.type,
            id=chat_request.object.id,
            title=chat_request.object.title,
            attributes=chat_request.object.attributes
        ) if chat_request.object else None,
    )


# ProcessResult => ChatResponse
def _build_chat_response(process_result: ProcessResult) -> ChatResponse:
    # list[BotMessage] = process_result.messages
    # list[BotMessage] => list[ChatMessage]
    return ChatResponse(
        sender_id=process_result.sender_id,
        message_id=process_result.message_id,
        messages=[
            ChatMessage(
                text=message.text,
                object=ChatObject(
                    **asdict(message.object)
                ) if message.object else None,
            ) for message in process_result.messages
        ]
    )
