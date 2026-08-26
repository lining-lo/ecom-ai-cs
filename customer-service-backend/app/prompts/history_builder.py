"""
  @Author:lining-lo
  @Time:2026/8/23
  @Desc:会话历史构建工具，
        把内存中的Turn对话轮次对象转换成LLM可用的历史文本，
        支持文本消息与对象类型消息格式化输出
"""
import json
from dataclasses import asdict
from app.domain.message import UserMessage, MessageType, BotMessage
from app.domain.state import Turn


class HistoryBuilder:
    """
    会话历史构建工具类，
    把内存中的Turn对话轮次对象转换成LLM可用的历史文本
    """

    @staticmethod
    def build(turns: list[Turn]) -> str:
        """
        执行会话历史构建的主方法
        :param turns: 对话信息列表
        :return: LLM可以识别的字符串
        """
        messages: list[str] = []
        for turn in turns:
            user_message = HistoryBuilder.render_user_message(turn.user_message)
            messages.append(user_message)
            for bot_message in turn.bot_message:
                bot_message = HistoryBuilder.render_bot_message(bot_message)
                messages.append(bot_message)
        return "\n".join(messages)

    @staticmethod
    def render_user_message(user_message: UserMessage) -> str:
        """
        执行会话历史构建“用户输入信息”的方法
        :param user_message: 用户输入信息
        :return: LLM可以识别的字符串
        """
        if user_message.type == MessageType.TEXT:
            return f"USER: {user_message.text}"
        else:
            return f"USER: {json.dumps(asdict(user_message.object), ensure_ascii=False)}"

    @staticmethod
    def render_bot_message(bot_message: BotMessage) -> str:
        """
        执行会话历史构建“客服回复信息”的方法
        :param bot_message: 客服回复信息
        :return: LLM可以识别的字符串
        """
        if bot_message.text:
            return f"BOT: {bot_message.text}"
        else:
            return f"BOT: {json.dumps(asdict(bot_message.object), ensure_ascii=False)}"
