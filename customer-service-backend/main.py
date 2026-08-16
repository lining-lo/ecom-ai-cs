"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:程序入口
"""
import uvicorn
from fastapi import FastAPI
from app.api.chat_router import chat_router
from app.conf.config import settings

# 创建API应用，并绑定生命周期函数
app = FastAPI()

# 添加路由器
app.include_router(chat_router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
    )
