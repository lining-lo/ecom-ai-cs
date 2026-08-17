"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc: 
"""
from app.domain.message import ProcessResult, UserMessage
from app.domain.state import DialogueState
from app.engine.dialogue_engine import DialogueEngine
from app.repository.dialogue_repository import DialogueRepository


class DialogueService:

    # 初始化方式
    def __init__(self, dialogue_repository: DialogueRepository,
                 dialogue_engine: DialogueEngine):
        self.dialogue_repository = dialogue_repository
        self.dialogue_engine = dialogue_engine

    async def process_message(self, user_message: UserMessage) -> ProcessResult:
        # 1.根据用户ID 加载对话状态。
        sender_id = user_message.sender_id
        # 调用repository方法查询
        state: DialogueState = await self.dialogue_repository.load(sender_id)

        # 2.将用户消息和对话状态交给`DialogueEngine`处理。
        process_result: ProcessResult = await self.dialogue_engine.process_mesasge(state, user_message)

        # 3.保存处理后的对话状态。
        # 规则：只保留前一次处理记录，如果存在更新
        await self.dialogue_repository.save(state)

        # 4.返回本轮处理结果。
        return process_result
