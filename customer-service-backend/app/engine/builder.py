"""
  @Author:lining-lo
  @Time:2026/8/17
  @Desc:DialogueEngine引擎构建工厂，
        加载流程YAML配置，实例并组装规划、校验、任务、动作、流程执行等全部内部组件，
        返回完整对话引擎实例
"""
from pathlib import Path
from app.engine.dialogue_engine import DialogueEngine
from app.plan.turn_plan import TurnPlanner
from app.plan.turn_plan_validation import TurnPlanValidation
from app.task.action.builder import register_service_action
from app.task.action.registry import ActionRegistry
from app.task.action.runner import ActionRunner
from app.task.command.processor import CommandProcessor
from app.task.flow.executor import FlowExecutor
from app.task.flow.loader import FlowLoader
from app.task.flow.models import FlowCatalog
from app.task.handler import TaskHandler
from app.task.lifecycle.responder import TaskLifecycleResponder
from app.task.response.renderer import ResponseRenderer


def build_dialogue_engine() -> DialogueEngine:
    """创建DialogueEngine实例的方法"""
    # 获取yaml文件所有数据，FlowCatalog
    flow_path = Path(__file__).parents[2] / "flow_config" / "user_flows.yml"
    flow_catalog: FlowCatalog = FlowLoader().load(flow_path)

    turn_planner = TurnPlanner()
    turn_plan_validator = TurnPlanValidation()

    command_processor = CommandProcessor()
    task_lifecycle = TaskLifecycleResponder(flows=flow_catalog)

    response_renderer = ResponseRenderer()
    registry = ActionRegistry()
    # 业务对应action，注册字典里面
    register_service_action(registry)
    action_runner = ActionRunner(registry=registry)

    flow_executor = FlowExecutor(
        response_renderer=response_renderer,
        action_runner=action_runner
    )

    task_handler = TaskHandler(
        command_processor=command_processor,
        task_lifecycle=task_lifecycle,
        flow_executor=flow_executor,
        flow_catalog=flow_catalog)

    return DialogueEngine(
        turn_planner=turn_planner,
        turn_plan_validation=turn_plan_validator,
        task_handler=task_handler
    )
