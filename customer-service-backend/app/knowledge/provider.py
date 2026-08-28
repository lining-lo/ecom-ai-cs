"""
  @Author:lining-lo
  @Time:2026/8/28
  @Desc:知识检索组件，
        抽象KnowledgeProvider，
        实现商品、订单、FAQ、RAG多源知识查询
"""
import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.conf.config import settings
from app.domain.message import UserMessage
from app.domain.state import DialogueState
from app.utils import http_client


@dataclass
class KnowledgeChunk:
    """知识检索最终结果"""
    content: str = ""


class KnowledgeProvider(ABC):
    """知识检索基类"""
    provider_id: str = ""

    @abstractmethod
    async def retrieve(self,
                       user_message: UserMessage,
                       state: DialogueState, ) -> list[KnowledgeChunk]:
        """
        知识检索的抽象方法
        :param user_message: 用户输入信息
        :param state: 对话运行状态
        :return:  list[KnowledgeChunk]: 知识检索结果列表
        """
        pass


class ApiProductProvider(KnowledgeProvider):
    """知识检索-商品信息咨询"""
    provider_id = "api.product"

    async def retrieve(self,
                       user_message: UserMessage,
                       state: DialogueState, ) -> list[KnowledgeChunk]:
        """
        知识检索-商品信息咨询方法
        :param user_message: 用户输入信息
        :param state: 对话运行状态
        :return:  list[KnowledgeChunk]: 知识检索结果列表
        """
        # 设计：页面中直接发送商品类型对象，执行当前这条线
        # 获取商品id
        product_id = state.shared.focused_object.id
        # 调用中台接口实现
        url = (f"{settings.commerce_api_base_url}"
               f"/products/{product_id}")
        # http调用
        response = await http_client.http_client.get(url)
        # todo 完善空值处理
        data = response.json()["data"]

        # KnowledgeChunk
        chunk = json.dumps(data, ensure_ascii=False)
        return [KnowledgeChunk(content=chunk)]


class ApiOrderProvider(KnowledgeProvider):
    """知识检索-订单信息咨询"""
    provider_id = "api.order"

    async def retrieve(self,
                       user_message: UserMessage,
                       state: DialogueState, ) -> list[KnowledgeChunk]:
        """
        知识检索-订单信息咨询方法
        :param user_message: 用户输入信息
        :param state: 对话运行状态
        :return:  list[KnowledgeChunk]: 知识检索结果列表
        """
        order_id = state.shared.focused_object.id
        # 得到订单信息，调用两个中台接口
        # 调用查询订单详情接口
        order_url = (f"{settings.commerce_api_base_url}"
                     f"/orders/{order_id}")
        # 调用查询订单物流接口
        logis_url = (f"{settings.commerce_api_base_url}"
                     f"/orders/{order_id}/logistics")
        order_info, logis_info = await asyncio.gather(
            http_client.http_client.get(order_url),
            http_client.http_client.get(logis_url),
        )

        # list[KnowledgeChunk]
        chunk = json.dumps({
            "order_detail": order_info.json()["data"],
            "logis_detail": logis_info.json()["data"],
        }, ensure_ascii=False
        )
        return [KnowledgeChunk(content=chunk)]


# 5 faq
# 6 rag
class FAQProvider(KnowledgeProvider):
    provider_id = 'faq.default'

    async def retrieve(self,
                       user_message: UserMessage,
                       state: DialogueState, ) -> list[KnowledgeChunk]:
        # TODO
        return [KnowledgeChunk(content="未检索到相关问题")]


class RAGProvider(KnowledgeProvider):
    provider_id = 'rag.default'

    async def retrieve(self,
                       user_message: UserMessage,
                       state: DialogueState, ) -> list[KnowledgeChunk]:
        # RAG知识库查询知识接口（TODO）
        return [KnowledgeChunk(content="未检索到相关信息")]
