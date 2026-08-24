"""
  @Author:lining-lo
  @Time:2026/8/24
  @Desc: 
"""
from app.domain.state import DialogueState
from app.plan.models import TurnPlan, TurnPlanValidationResult, ClarifyReason
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
    def _validate_task_plan(self):
        # 根据不同类型command做不同校验
        # 1 start_flow 校验flow_id是否存在于当前流程里面yaml里面
        # 2 resume_task 校验task_id是否存在于中断列表
        # 3 cancal_task 校验task_id是否存在于 中断列表 或者当前任务里面
        pass

    def _validate_knowledge_plan(self):
        pass
