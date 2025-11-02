# ======================================================================
# --- FILE: src/algorithms/base_algorithm.py (COMPLETE REPLACEMENT V2) ---
# ======================================================================
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.model.lottery_models import LotteryHistory

class BaseAlgorithm(ABC):
    """
    算法基类 V2
    - 改进: __init__不再需要参数，name 和 version 作为类属性定义。
      这解决了工作流中无法传递参数进行实例化的问题。
    """
    name: str = "BaseAlgorithm"
    version: str = "0.0"

    def __init__(self):
        """构造函数不再需要参数。"""
        self.parameters: Dict[str, Any] = {}
        self.is_trained: bool = False

    @abstractmethod
    def train(self, history_data: List[LotteryHistory]) -> bool:
        """训练模型"""
        pass

    @abstractmethod
    def predict(self, history_data: List[LotteryHistory]) -> Dict[str, Any]:
        """进行预测"""
        pass

    def set_parameters(self, parameters: Dict[str, Any]):
        """设置算法参数"""
        self.parameters.update(parameters)

    def get_parameters(self) -> Dict[str, Any]:
        """获取算法参数"""
        return self.parameters.copy()

    def get_algorithm_info(self) -> Dict[str, Any]:
        """获取算法信息"""
        return {
            'name': self.name,
            'version': self.version,
            'is_trained': self.is_trained,
            'parameters': self.parameters
        }