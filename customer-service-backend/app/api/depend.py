"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc:依赖注入工厂，
        提供FastAPI Depends所需的各个对象生成函数，
        管理数据库会话、仓储、对话引擎、业务服务实例
"""
from fastapi import Depends
from app.engine.builder import build_dialogue_engine
from app.engine.dialogue_engine import DialogueEngine
from app.repository.dialogue_repository import DialogueRepository
from app.service.dialogue_service import DialogueService
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import database_client


async def get_session():
    """创建session实例"""
    async with database_client.session_factory() as session:
        yield session


async def get_dialogue_repository(session: AsyncSession = Depends(get_session)):
    """
    创建数据访问层实例
    :param session: session实例，负责数据库操作
    :return: dialogue_repository: 数据访问层实例
    """
    return DialogueRepository(session=session)


def init_dialogue_engine():
    """
    创建对话处理实例
    全局单例，服务启动初始化一次，全部请求共享
    """
    global _dialogue_engine
    _dialogue_engine = build_dialogue_engine()


def get_dialogue_engine():
    """获取对话处理实例"""
    return _dialogue_engine


async def get_dialogue_service(
        dialogue_repository: DialogueRepository = Depends(get_dialogue_repository),
        dialogue_engine: DialogueEngine = Depends(get_dialogue_engine)):
    """
    创建service实例
    :param dialogue_repository:数据访问层实例
    :param dialogue_engine:对话处理实例
    :return: DialogueService: service实例
    """
    return DialogueService(dialogue_repository=dialogue_repository,
                           dialogue_engine=dialogue_engine)
