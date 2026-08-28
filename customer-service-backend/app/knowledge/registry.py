"""
  @Author:lining-lo
  @Time:2026/8/28
  @Desc:知识库查询注册中心，
        维护provider_id与检索实例映射，提供实例查询能力
"""
from app.knowledge.provider import KnowledgeProvider


class KnowledgeProviderRegistry():
    """知识库查询注册中心"""

    # 初始化方法，传入所有的provider对象，进行注册
    def __init__(self, provider_objs: list[KnowledgeProvider]) -> None:
        # 把所有provider对象注册字典类型变量里面
        self._providers_by_id = {
            provider_obj.provider_id: provider_obj
            for provider_obj in provider_objs
        }

    def get(self, provider_id: str) -> KnowledgeProvider:
        """根据provider_id返回对应provider对象的方法"""
        return self._providers_by_id.get(provider_id)
