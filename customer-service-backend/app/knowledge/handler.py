"""
  @Author:lining-lo
  @Time:2026/8/28
  @Desc:知识查询处理器，
        根据知识意图路由多数据源检索，
        聚合检索结果后交由LLM生成客服回复
"""
from app.domain.message import UserMessage, BotMessage
from app.domain.state import DialogueState
from app.knowledge.intents import KnowledgeIntent, KNOWLEDGE_INTENTS
from app.knowledge.provider import KnowledgeChunk
from app.knowledge.registry import KnowledgeProviderRegistry
from app.knowledge.responder import KnowledgeResponder


class KnowledgeHandler:
    """知识查询处理器"""

    def __init__(self,
                 knowledge_intents: dict[str, KnowledgeIntent],
                 provider_registry: KnowledgeProviderRegistry,
                 knowledge_responder: KnowledgeResponder):
        self.knowledge_intents = knowledge_intents
        self.provider_registry = provider_registry
        self.knowledge_responder = knowledge_responder

    # 1 意图识别结果  ["return_policy","product_info"]
    # 2 user_message
    # 3 state
    async def handle(self,
                     knowledge_intents: list[str],
                     user_message: UserMessage,
                     state: DialogueState,
                     ) -> list[BotMessage]:
        """
        对外调用方法，负责处理知识检索过程
        :param knowledge_intents: 意图识别结果
        :param user_message: 用户输入信息
        :param state: 对话运行状态
        :return: list[BotMessage] 客服回答列表
        """
        # 1 获取上一步意图识别结果  ["return_policy","product_info",refund_policy]
        # 2 根据意图识别结果，找到答案位置  每个识别值对应 provider_ids
        ##  ["faq.default", "rag.default" , "api.product"]
        ## 去重处理 相同位置保留一个
        provider_ids: list[str] = self.get_provider_ids(knowledge_intents)

        # 3 根据上一步找到答案位置，根据位置值找到对应provider对象
        ## 把位置list遍历，得到每个位置名称，根据每个位置名称找到对应provider对象
        # ["faq.default", "rag.default" , "api.product"]
        final_result: list[KnowledgeChunk] = []
        for provider_id in provider_ids:
            provider_obj = self.provider_registry.get(provider_id)
            # 4 把对应provider对象的方法retrieve 执行得到结果
            result = await provider_obj.retrieve(
                state=state,
                user_message=user_message,
            )
            final_result.extend(result)

        # 5 把provider对象的方法执行得到结果，提交LLM，整理返回最终答案
        #  respond() -> BotMessage
        response = await self.knowledge_responder.respond(
            chunks=final_result,
            user_message=user_message,
            turns=state.shared.sessions[-1].turns,
        )
        return [response]

    # 根据意图识别结果 ["return_policy","product_info",refund_policy]
    # 找到答案位置    ["faq.default", "rag.default" , "api.product"]
    # 如果找到多个相同位置，保留一个

    def get_provider_ids(self,
                         knowledge_intents: list[str]) -> list[str]:
        """根据意图识别结果，找到答案位置  每个识别值对应 provider_ids"""
        final_provider_ids: list[str] = []
        # 遍历得到每个意图识别结果值
        for intent in knowledge_intents:
            # 拿着图识别结果值，到字典找到位置
            final_provider_ids.extend(KNOWLEDGE_INTENTS[intent].provider_ids)

        # final_provider_ids去重 ["faq.default", "faq.default" , "api.product"]
        # 第一种 set集合， 缺陷：无法保证数据顺序
        return list(set(final_provider_ids))

        # 第二种 dict方法 dict.fromkeys()，优点：保证数据顺序
        # return list(dict.fromkeys(final_provider_ids))
