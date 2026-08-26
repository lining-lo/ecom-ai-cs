"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:封装MySQL异步客户端，
        初始化SQLAlchemy异步引擎与会话工厂，
        统一管理数据库连接生命周期
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from app.conf.config import settings

# mysql实例
engine: AsyncEngine | None = None

# 会话工厂，用来创建session
session_factory: async_sessionmaker[AsyncSession] | None = None


def init_database():
    """创建全局异步数据库引擎 + 会话工厂"""
    global engine, session_factory
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def close_database():
    """销毁连接、释放资源"""
    if engine:
        await engine.dispose()


if __name__ == '__main__':
    init_database()


    async def test():
        async with session_factory() as session:
            result = await session.execute(text("select 1"))
            print(result.fetchall())

        await close_database()


    asyncio.run(test())
