"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc:会话状态数据访问层，
        异步读写dialogue_states表；
        通过TypeAdapter实现Domain对象与JSON序列化，实现会话状态加载与upsert保存
"""
from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from app.domain.state import DialogueState
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.orm.dialogue_state import DialogueStateRecord

# TypeAdapter类型适配器
# 方便进行 序列化 和 反序列化操作
# 对象 =》 json字符串   dump_json
# json字符串 =》 对象   validate_json
DIALOGUE_STATE_ADAPTER = TypeAdapter(DialogueState)


class DialogueRepository:
    """会话状态数据访问层"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def load(self, sender_id: str) -> DialogueState:
        """
        根据sender_id查询历史会话状态数据的方法
        :param sender_id: 发送人id
        :return: DialogueState: 对话运行状态
        """
        # 1 创建sql语句，使用方法创建
        # SELECT * FROM dialogue_states  WHERE send_id =?
        # sql1 = "SELECT * FROM dialogue_states  WHERE send_id =:sid"
        # await self.session.execute(sql1,{"sid":sender_id})

        sql = select(DialogueStateRecord).where(
            DialogueStateRecord.sender_id == sender_id)
        # 2 执行sql语句
        result = await self.session.execute(sql)

        # 3 从查询result对象获取结果
        record = result.scalar_one_or_none()
        if record:
            # record不是DialogueState对象，转换DialogueState对象
            state = DIALOGUE_STATE_ADAPTER.validate_json(record.state_json)
            return state
        else:  # 没有查询数据
            return DialogueState(sender_id=sender_id)

    async def save(self, state: DialogueState):
        """
        新增|更改历史会话的方法
        :param state: 对话运行状态
        """
        # 1 把DialogueState对象类型数据转换字符串
        state_json = DIALOGUE_STATE_ADAPTER.dump_json(state).decode(encoding='utf-8')

        # 2 创建sql语句
        # from sqlalchemy.dialects.mysql import insert
        statement = insert(DialogueStateRecord).values(
            sender_id=state.sender_id,
            state_json=state_json)

        # 判断当前用户是否存在会话状态数据，如果不存在添加，如果存在更新
        # 方言的mysql的insert语句有方法，根据主键判断，如果主键存在更新，不存在添加
        on_duplicate_key = statement.on_duplicate_key_update(
            state_json=state_json
        )

        await self.session.execute(on_duplicate_key)
        await self.session.commit()
