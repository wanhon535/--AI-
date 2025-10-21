# algorithms/base_algorithm.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.model.lottery_models import LotteryHistory

class BaseAlgorithm(ABC):
    """算法基类"""

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.parameters = {}
        self.is_trained = False

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
