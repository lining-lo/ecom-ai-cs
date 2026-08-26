"""
  @Author:lining-lo
  @Time:2026/8/16
  @Desc:全局httpx异步http客户端封装，
        维护单例连接池，提供初始化与关闭方法，
        供业务action调用第三方接口
"""
import asyncio
from httpx import AsyncClient

# http客户端实例
http_client: AsyncClient | None = None


def init_http_client():
    """创建http客户端实例"""
    global http_client
    http_client = AsyncClient()


async def close_http_client():
    """释放http客户端实例"""
    if http_client:
        await http_client.aclose()


if __name__ == '__main__':
    init_http_client()


    async def test():
        response = await http_client.get('http://localhost:18081/users/u1001/orders')
        print(response.json()['data']['orders'])

        await close_http_client()


    asyncio.run(test())
