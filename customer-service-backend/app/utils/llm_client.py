"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:封装LLM大模型客户端，
        基于langchain初始化dashscope兼容OpenAI协议的对话模型，
        全局生成llm单例对象，供上游各模块直接调用
"""
import os
from langchain.chat_models import init_chat_model
from app.conf.config import settings

# LM大模型客户端实例
llm = init_chat_model(
    model=settings.llm_model,
    model_provider='openai',
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0,
    base_url=settings.llm_base_url
)

if __name__ == '__main__':
    print(llm.invoke("你好！"))
