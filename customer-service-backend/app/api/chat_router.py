"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:对话聊天接口路由层，
        负责接收前端聊天请求、参数模型转换、调用对话业务服务，
        并返回标准化聊天响应数据
"""
import uuid
from dataclasses import asdict
from fastapi import APIRouter, Depends
from app.api.depend import get_dialogue_service
from app.api.schemas import ChatRequest, ChatResponse, ChatMessage, ChatObject, HistoryResponse, HistoryMessage
from app.domain.message import UserMessage, MessageType, MessageObject, ProcessResult
from app.domain.state import DialogueState, Session, Turn
from app.service.dialogue_service import DialogueService

# 创建路由实例
chat_router = APIRouter()


@chat_router.post("/api/chat")
async def chat(chat_request: ChatRequest,
               dialogue_service: DialogueService = Depends(get_dialogue_service)
               ) -> ChatResponse:
    """
    前端调用的聊天接口
    :param chat_request:前端发送的数据
    :param dialogue_service:业务服务实例，路由层不 new 对象，解耦
    :return ChatResponse: 响应数据
    """
    # 构建service需要的参数
    user_message: UserMessage = _build_user_message(chat_request)

    # 调用service方法，返回结果
    process_result: ProcessResult = await dialogue_service.process_message(user_message)

    # 将结果返回给前端
    return _build_chat_response(process_result)


def _build_user_message(chat_request: ChatRequest) -> UserMessage:
    """
    将前端传来的数据对象封装成service的参数对象
    :param chat_request:前端传来的数据
    :return: UserMessage：service需要的参数
    """
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


def _build_chat_response(process_result: ProcessResult) -> ChatResponse:
    """
    将service返回的结果封装成前端需要的数据格式
    :param process_result: service返回的结果
    :return: ChatResponse: 前端需要的数据格式
    """
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


@chat_router.get("/api/chat/history")
async def chat_history(
        sender_id: str,
        dialogue_service: DialogueService = Depends(get_dialogue_service)
) -> HistoryResponse:
    """
    获取当前用户历史记录
    :param sender_id: 用户id
    :param dialogue_service: 业务服务实例，路由层不 new 对象，解耦
    :return: HistoryResponse: 历史记录
    """
    # 调用service方法,返回 查询出来的DialogueState对象
    history_session: DialogueState = (
        await dialogue_service.get_history_session_send_id(sender_id))

    # history_session:DialogueState 获取出来，封装到 HistoryResponse
    sessions: list[Session] = history_session.shared.sessions

    # 类型HistoryMessage变量，封装多个HistoryMessage数据
    messages: list[HistoryMessage] = []
    # sessions:list[Session]遍历，得到每个Session
    for session in sessions:
        # 每个session获取多轮对话
        turns: list[Turn] = session.turns
        # turns:list[Turn]遍历
        for turn in turns:
            # 封装用户提问问题
            messages.append(
                HistoryMessage(
                    role="user",
                    text=turn.user_message.text,
                    object=ChatObject(
                        **asdict(turn.user_message.object))
                    if turn.user_message.object else None,
                )
            )
            # 封装客服回复数据
            messages.extend([
                HistoryMessage(
                    role="bot",
                    text=bo_msg.text,
                    object=ChatObject(
                        **asdict(bo_msg.object))
                    if bo_msg.object else None,
                )
                for bo_msg in turn.bot_message
            ])

    return HistoryResponse(sender_id=sender_id,
                           messages=messages)
