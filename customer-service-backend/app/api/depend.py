"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc: 
"""
from fastapi import Depends
from app.engine.dialogue_engine import DialogueEngine
from app.repository.dialogue_repository import DialogueRepository
from app.service.dialogue_service import DialogueService
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import database_client


async def get_session():
    async with database_client.session_factory() as session:
        yield session

async def get_dialogue_repository(session: AsyncSession=Depends(get_session)):
    return DialogueRepository(session = session)

# todo 后面注入其他对象
async def get_dialogue_engine():
    return DialogueEngine()

async def get_dialogue_service(
        dialogue_repository:DialogueRepository=Depends(get_dialogue_repository),
        dialogue_engine:DialogueEngine=Depends(get_dialogue_engine)):

    return DialogueService(dialogue_repository=dialogue_repository,
                           dialogue_engine=dialogue_engine)
