"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc: SQLAlchemy ORM基类，
        全部数据库模型继承于此，管理ORM元数据
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy ORM基类，全部数据库模型继承于此，管理ORM元数据"""
    pass
