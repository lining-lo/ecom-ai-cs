"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc: 
"""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.repository.orm.base import Base


class DialogueStateRecord(Base):
    __tablename__ = "dialogue_states"

    sender_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    state_json: Mapped[str] = mapped_column(Text, nullable=False)
