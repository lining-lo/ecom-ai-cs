"""
  @Author:lining-lo
  @Time:2026/8/24
  @Desc: 
"""
from app.domain.state import DialogueState
from app.plan.models import TurnPlan, TurnPlanValidationResult, ClarifyReason, TaskTurnPlan
from app.task.command.models import StartFlowCommand, ResumeTaskCommand, CancelTaskCommand
from app.task.flow.models import FlowCatalog


# 意图识别校验
class TurnPlanValidation:
    def validate(self,
                 turn_plan: TurnPlan,
                 state: DialogueState,
                 flow_catalog: FlowCatalog) -> TurnPlanValidationResult:
        # 判断是否多个轨道
        active_tracks: list[str] = []
        if turn_plan.task is not None:
            active_tracks.append("task")

        if turn_plan.knowledge is not None:
            active_tracks.append("knowledge")

        if turn_plan.chitchat is not None:
            active_tracks.append("chitchat")
        # 没有识别到
        if not active_tracks:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MISSING_TRACK)

        # 识别多个轨道
        if len(active_tracks) > 1:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MULTIPLE_TRACKS)

        # 只有一个轨道
        active_track = active_tracks[0]
        # 根据不同轨道做不同校验
        if active_track == "task":
            self._validate_task_plan()
        if active_track == "knowledge":
            self._validate_knowledge_plan()

        return TurnPlanValidationResult(valid=True)

    # 对task意图识别校验
    # commands: list[Command]
    def _validate_task_plan(self, task: TaskTurnPlan,
                            state: DialogueState,
                            flow_catalog: FlowCatalog):
        # task:TaskTurnPlan => commands: list[Command]
        if not task.commands:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MISSING_TASK_COMMANDS
            )
        # 根据不同类型command做不同校验

        for command in task.commands:
            # 1 start_flow 校验flow_id是否存在于当前流程里面yaml里面
            if isinstance(command, StartFlowCommand):
                # 获取start_flow流程id
                flow_id = command.flow
                # 校验flow_id是否存在于当前流程里面yaml里面
                if flow_id not in flow_catalog.flows:
                    return TurnPlanValidationResult(
                        valid=False,
                        reason=ClarifyReason.INVALID_TASK_COMMAND
                    )

            # 2 resume_task 校验task_id是否存在于中断列表
            if isinstance(command, ResumeTaskCommand):
                # 判断恢复任务id 在中断列表是否存在
                # 获取中断列表索引任务id
                # [1 ,2 ,3 ]
                paused_task_ids = [paused_task.task_id
                                   for paused_task in state.tasks.paused]
                # 当前command任务id和所有中断列表任务id比较
                if command.task_id not in paused_task_ids:
                    return TurnPlanValidationResult(
                        valid=False,
                        reason=ClarifyReason.INVALID_TASK_COMMAND
                    )

            # 3 cancal_task 校验task_id是否存在于 中断列表 或者 当前任务里面
            if isinstance(command, CancelTaskCommand):
                # 获取中断列表所有任务id
                all_task_ids = [paused_task.task_id
                                for paused_task in state.tasks.paused]
                # 获取当前活跃任务id
                if state.tasks.active:
                    all_task_ids.append(state.tasks.active.task_id)

                # 判断
                if command.task_id not in all_task_ids:
                    return TurnPlanValidationResult(
                        valid=False,
                        reason=ClarifyReason.INVALID_TASK_COMMAND
                    )

        return TurnPlanValidationResult(valid=True)

    def _validate_knowledge_plan(self):
        pass
