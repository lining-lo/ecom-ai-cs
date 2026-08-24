"""
  @Author:lining-lo
  @Time:2026/8/24
  @Desc:
"""
import json
from dataclasses import asdict
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from app.domain.message import UserMessage
from app.domain.state import DialogueState
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import load_prompt
from app.task.flow.models import FlowCatalog, Flow
from app.utils.llm_client import llm


# 意图识别组件
class TurnPlan:

    async def plan(self, user_message: UserMessage,
                   state: DialogueState,
                   flow_catalog: FlowCatalog) -> "TurnPlan":
        # 1 加载提示词模版
        prompt_text = load_prompt('turn_plan')
        prompt = PromptTemplate.from_template(
            prompt_text, template_format='jinja2',
        )

        # 2 创建调用链
        chain = prompt | llm | JsonOutputParser()

        # 3 获取提示词模版需要数据，调用ainvoke方法执行，把这些数据传递到方法里面
        # 用户信息
        user_message = HistoryBuilder.render_user_message(user_message)
        # 历史多轮对话
        conversation_history = HistoryBuilder.build(state.shared.sessions[-1].turns)
        # 聚焦对象数据
        focused_object_json = json.dumps(
            asdict(state.shared.focused_object)
            if state.shared.focused_object else None, ensure_ascii=False)
        # task_state_json
        task_state_json = json.dumps(asdict(state.tasks)
                                     if state.tasks else None, ensure_ascii=False)
        # flows_json 流程数据
        # 获取所有流程中，每个流程不包含步骤数据
        flows: dict[str, Flow] = flow_catalog.flows
        # items() k，v
        # .values()   Flow
        flows_json = [
            {k: v for k, v in asdict(flow).items()
             if k != 'steps'
             }
            for flow in flows.values()
        ]
        # 调用方得到结果
        res = await chain.ainvoke({
            "flows_json": flows_json,
            "task_state_json": task_state_json,
            "focused_object_json": focused_object_json,
            "conversation_history": conversation_history,
            "user_message": user_message,
            # todo 后面完善，目前{}
            "knowledge_intents_json": {},
        })

        # 4 把llm返回结果封装TurnPlan
        return TurnPlan.from_dict(res)
