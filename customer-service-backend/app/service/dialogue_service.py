"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc:会话业务层，
        协调对话处理类和会话状态数据访问层；
        完成会话状态加载、消息处理、状态持久化，对外提供消息处理入口
"""
from app.domain.message import ProcessResult, UserMessage
from app.domain.state import DialogueState
from app.engine.dialogue_engine import DialogueEngine
from app.repository.dialogue_repository import DialogueRepository


class DialogueService:
    """会话业务层"""

    def __init__(self, dialogue_repository: DialogueRepository,
                 dialogue_engine: DialogueEngine):
        self.dialogue_repository = dialogue_repository
        self.dialogue_engine = dialogue_engine

    async def process_message(self, user_message: UserMessage) -> ProcessResult:
        """
        service推进业务流程的方法
        :param user_message: 用户输入信息
        :return: ProcessResult service方法返回类型
        """
        # 1.根据用户ID 加载对话状态。
        sender_id = user_message.sender_id
        # 调用repository方法查询
        state: DialogueState = await self.dialogue_repository.load(sender_id)

        # 2.将用户消息和对话状态交给`DialogueEngine`处理。
        process_result: ProcessResult = await self.dialogue_engine.process_message(state, user_message)

        # 3.保存处理后的对话状态。
        # 规则：只保留前一次处理记录，如果存在更新
        await self.dialogue_repository.save(state)

        # 4.返回本轮处理结果。
        return process_result
