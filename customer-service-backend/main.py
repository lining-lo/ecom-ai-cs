"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:程序入口
"""
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from app.api.chat_router import chat_router
from app.api.depend import init_dialogue_engine
from app.conf.config import settings
from app.utils.database_client import init_database, close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    init_dialogue_engine()
    yield
    await close_database()

# 创建API应用，并绑定生命周期函数
app = FastAPI(lifespan=lifespan)

# 添加路由器
app.include_router(chat_router)

if __name__ == "__main__":
    import asyncio
    import uvicorn

    config = uvicorn.Config(app, host="127.0.0.1", port=18082)
    server = uvicorn.Server(config)
    asyncio.run(server.serve())