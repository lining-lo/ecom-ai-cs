"""
  @Author:lining-lo
  @Time:2026/8/19
  @Desc:YAML流程配置加载器，
        解析配置文件生成FlowCatalog流程目录，
        支持单文件、多文件加载合并，完成配置到领域对象的转换
"""
from pathlib import Path
import yaml
from app.task.flow.models import FlowCatalog, FlowSlot, Flow
from app.task.flow.steps import FlowStep


class FlowLoader:
    """YAML流程配置加载器"""

    def load(self, path: Path) -> FlowCatalog:
        """加载YAML流程配置的方法"""
        # 使用pyyaml的方法读取yaml文件
        flow_data = path.read_text(encoding="utf-8")
        flow_dict = yaml.safe_load(flow_data)

        # 获取slots数据  dict[str,Any] => dict[str, FlowSlot]
        slots: dict[str, FlowSlot] = self._load_slots(flow_dict['slots'])

        # 获取flows流程数据
        flows: dict[str, Flow] = self._load_flows(flow_dict['flows'], slots)

        return FlowCatalog(flows=flows, slots=slots)

    def _load_slots(self, slots_data: dict[str, dict]) -> dict[str, FlowSlot]:
        """槽位数据封装方法"""
        slots: dict[str, FlowSlot] = {}
        # 遍历
        for slot_name, slot_data in slots_data.items():
            slots[slot_name] = FlowSlot(
                name=slot_name,
                **slot_data
            )
        return slots

    def _load_flows(self, flows_data: dict[str, dict],
                    slots: dict[str, FlowSlot]) -> dict[str, Flow]:
        """流程数据封装方法"""
        flows: dict[str, Flow] = {}
        # 遍历
        for flow_id, flow_data in flows_data.items():
            # 封装Flow对象
            # 封装每个Flow里面slots
            flow_slots: list[FlowSlot] = [
                # slots['order_number']
                slots[collect_step['slot_name']]
                for collect_step in flow_data['steps']
                if collect_step['type'] == 'collect'
            ]

            # 步骤列表
            steps: list[FlowStep] = [
                FlowStep.from_dict(flow_step)
                for flow_step in flow_data['steps']
            ]

            # 封装Flow对象
            flow: Flow = Flow(
                id=flow_id,
                description=flow_data['description'],
                steps=steps,
                slots=flow_slots,
                name=flow_data['name'],
            )
            # flows
            flows[flow_id] = flow
        return flows

    def load_many(self, paths: list[Path]) -> FlowCatalog:
        """加载多个yaml流程配置文件"""
        flows: dict[str, Flow] = {}
        slots: dict[str, FlowSlot] = {}

        # path遍历
        for path in paths:
            # 调用load方法
            catalog = self.load(path)
            # 封装数据
            # {a:1} .update ( {b:2}) =>  {a:1,b:2,}
            flows.update(catalog.flows)
            slots.update(catalog.slots)
        return FlowCatalog(flows=flows, slots=slots)


if __name__ == "__main__":
    loader = FlowLoader()
    path = Path(__file__).parents[3] / 'flow_config' / 'user_flows.yml'
    result = loader.load(path)
    print(result)
