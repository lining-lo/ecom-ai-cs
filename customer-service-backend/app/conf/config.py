"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:项目全局配置类，
        基于pydantic‑settings读取项目根目录.env文件，
        统一管理LLM、数据库、商城接口、服务启动参数，对外提供settings单例
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 配置文件路径
ENV_FILE = Path(__file__).parents[2] / ".env"


class Settings(BaseSettings):
    """项目全局配置类"""
    # LLM
    llm_api_key: str
    llm_model: str
    llm_base_url: str

    # 数据库
    database_url: str

    # 商城 API
    commerce_api_base_url: str

    # 服务器
    app_host: str
    app_port: int

    # 配置：指定env文件路径，自动从.env加载环境变量赋值给类字段
    model_config = SettingsConfigDict(env_file=ENV_FILE)


# 全局配置类实例
settings = Settings()

if __name__ == '__main__':
    print(settings.llm_model)
