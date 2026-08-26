"""
  @Author:lining-lo
  @Time:2026/8/23
  @Desc:机器人回复渲染组件，
        分别处理static静态渲染、rephrase改写、generate大模型生成三种模式，
        支持jinja2槽位变量替换与LLM链路调用，产出BotMessa
"""
from jinja2 import Template
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from app.domain.message import UserMessage, BotMessage
from app.domain.state import DialogueState
from app.prompts.history_builder import HistoryBuilder
from app.task.response.models import ResponseTemplate, ResponseMode
from app.utils.llm_client import llm


class ResponseRenderer:
    """机器人回复渲染组件"""

    # template： mode text  prompt
    async def render(self, template: ResponseTemplate,
                     state: DialogueState,
                     user_message: UserMessage) -> BotMessage:
        """机器人回复渲染组件的方法"""
        # 判断不同mode做不同处理
        # static渲染text内容，直接返回text内容
        if template.mode == ResponseMode.STATIC:
            # jinja2渲染
            template = Template(template.text)
            render_text = template.render(slots=state.tasks.active.slots)
            return BotMessage(text=render_text)

        # rephrase：有text文本，调用llm，根据提示词 和 text文本，llm修改内容返回
        if template.mode == ResponseMode.REPHRASE:
            # text内容渲染
            render_text = Template(template.text).render(
                slots=state.tasks.active.slots)

            # 加载提示词模版，使用langchain
            prompt = PromptTemplate.from_template(
                template.prompt, template_format='jinja2', )

            # 调用llm，返回结果
            chain = prompt | llm | StrOutputParser()
            res = await chain.ainvoke({
                "history": HistoryBuilder.build(
                    state.shared.sessions[-1].turns
                ),
                "user_message": HistoryBuilder.render_user_message(user_message),
                "current_response": render_text
            }
            )
            # 封装BotMessage
            return BotMessage(text=res)

        # generate: 根据提示词,调用llm生成结果，没有text文本
        if template.mode == ResponseMode.GENERATE:
            prompt = PromptTemplate.from_template(
                template.prompt, template_format='jinja2',
            )
            chain = prompt | llm | StrOutputParser()
            res = await chain.ainvoke({
                "history": HistoryBuilder.build(
                    state.shared.sessions[-1].turns
                ),
                "user_message": HistoryBuilder.render_user_message(user_message)
            })
            return BotMessage(text=res)
