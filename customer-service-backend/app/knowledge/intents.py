"""
  @Author:lining-lo
  @Time:2026/8/28
  @Desc:知识意图配置，
        维护意图与知识提供者映射关系，
        配置检索所需业务对象约束
"""
from dataclasses import dataclass, field


@dataclass
class KnowledgeIntent:
    """知识意图配置"""
    id: str  # 意图识别值    product_info
    description: str  # llm更好理解id含义  "商品信息咨询"
    provider_ids: list[str] = field(default_factory=list)  # 问题答案位置 provider类里面属性值对应
    requires_object: str | None = None  # 规则：查询商品 、 订单 信息都需要从对象获取值


# 2 创建字典   product_info
KNOWLEDGE_INTENTS: dict[str, KnowledgeIntent] = {
    "product_info": KnowledgeIntent(
        id="product_info", description="商品信息咨询",
        provider_ids=["api.product"], requires_object="product",
    ),
    "order_info": KnowledgeIntent(
        id="order_info", description="订单信息咨询",
        provider_ids=["api.order"], requires_object="order",
    ),

    "refund_policy": KnowledgeIntent(
        id="refund_policy", description="退款政策咨询",
        provider_ids=["faq.default", "rag.default"],
    ),
    "return_policy": KnowledgeIntent(
        id="return_policy", description="退货政策咨询",
        provider_ids=["faq.default", "rag.default"],
    ),
    "shipping_policy": KnowledgeIntent(
        id="shipping_policy", description="配送政策咨询",
        provider_ids=["faq.default", "rag.default"],
    ),
    "platform_rule": KnowledgeIntent(
        id="platform_rule", description="平台规则咨询",
        provider_ids=["rag.default"],
    ),
    "general_ecommerce_info": KnowledgeIntent(
        id="general_ecommerce_info", description="电商通用信息咨询",
        provider_ids=["faq.default", "rag.default"],
    ),
}
