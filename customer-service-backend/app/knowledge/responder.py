"""
  @Author:lining-lo
  @Time:2026/8/28
  @Desc:知识应答组件，
        将检索出的知识片段交给大模型，
        结合对话上下文生成客服回复
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from app.domain.message import BotMessage, UserMessage
from app.domain.state import Turn
from app.knowledge.provider import KnowledgeChunk
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import load_prompt
from app.utils.llm_client import llm


class KnowledgeResponder:
    """知识应答组件"""

    async def respond(self,
                      chunks: list[KnowledgeChunk],
                      user_message: UserMessage,
                      turns: list[Turn]
                      ) -> BotMessage:
        """
        把查询得到答案，提交llm，由llm整理后返回最终答案
        :param chunks: provider查询答案
        :param user_message: 用户输入信息
        :param turns: 历史记录
        :return: BotMessage：客服答复
        """
        # 加载提示词模版
        prompt_text = load_prompt("knowledge_respond")
        prompt = PromptTemplate.from_template(
            prompt_text, template_format="jinja2",
        )

        # 调用链
        chain = prompt | llm | StrOutputParser()

        # 调用方法
        result = await chain.ainvoke(input={
            "user_message": HistoryBuilder.render_user_message(user_message),
            "history": HistoryBuilder.build(turns),
            "knowledge_content": '\n'.join(
                [
                    chunk.content
                    for chunk in chunks
                ])
        })
        return BotMessage(text=result)
