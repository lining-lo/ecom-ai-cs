"""
  @Author:lining-lo
  @Time:2026/8/26
  @Desc:加载prompt提示词的工具
"""
from pathlib import Path


def load_prompt(name: str) -> str:
    """
    加载prompt提示词的方法
    :param name: prompt提示词文件名
    :return: 加载的结果字符串
    """
    file = Path(__file__).parent / 'jinja2' / f'{name}.jinja2'
    return file.read_text(encoding='utf-8')
