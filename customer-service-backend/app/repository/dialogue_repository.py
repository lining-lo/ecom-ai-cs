"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc: 
"""
from app.domain.state import DialogueState
from sqlalchemy.ext.asyncio import AsyncSession

class DialogueRepository:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def load(self, sender_id:str) -> DialogueState:
        pass

    async def save(self, state:DialogueState):
        pass