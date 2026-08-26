"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc:会话状态ORM实体，
        保存用户sender_id与序列化后的对话状态JSON，用于对话状态持久化存储
"""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.repository.orm.base import Base


class DialogueStateRecord(Base):
    """
    会话状态ORM实体类
    1. 表名：`dialogue_states`
    2. `sender_id`：发送方 ID，主键，区分不同用户 / 会话
    3. `state_json`：Text 大文本字段，把内存里 `DialogueState` dataclass 序列化为 JSON 字符串存入数据库
    """
    __tablename__ = "dialogue_states"

    sender_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    state_json: Mapped[str] = mapped_column(Text, nullable=False)
