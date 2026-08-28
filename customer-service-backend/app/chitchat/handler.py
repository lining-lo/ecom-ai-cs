"""
  @Author:lining-lo
  @Time:2026/8/28
  @Desc:闲聊业务处理器，
        处理闲聊类意图，
        基于上下文调用LLM直接输出闲聊回复。
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from app.domain.message import UserMessage, BotMessage
from app.domain.state import DialogueState
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import load_prompt
from app.utils.llm_client import llm


class ChitchatHandler:

    async def handle(
            self,
            state: DialogueState,
            user_message: UserMessage,
    ) -> list[BotMessage]:
        """
        闲聊业务处理器
        :param state: 对话运行状态
        :param user_message: 用户输入信息
        :return: list[BotMessage]: 客服回复列表
        """
        # 加载提示词模版
        prompt_text = load_prompt("chitchat_respond")
        prompt = PromptTemplate.from_template(
            prompt_text, template_format="jinja2")

        # 构建调用链
        chain = prompt | llm | StrOutputParser()

        # 调用
        result = await chain.ainvoke(input={
            "user_message": HistoryBuilder.render_user_message(user_message),
            "history": HistoryBuilder.build(state.shared.sessions[-1].turns)
        })

        return [BotMessage(text=result)]
