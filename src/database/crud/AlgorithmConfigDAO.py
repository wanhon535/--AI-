# 算法配置操作
from typing import List
import json
from ..AllDao import AllDAO
from src.model.lottery_models import AlgorithmConfig


class AlgorithmConfigDAO(AllDAO):
    """算法配置数据访问对象"""

    def get_algorithm_configs(self, is_active: bool = True) -> List[AlgorithmConfig]:
        """获取算法配置"""
        query = "SELECT * FROM algorithm_configs"
        if is_active:
            query += " WHERE is_active = 1"

        results = self.execute_query(query)
        config_list = []
        for row in results:
            config = AlgorithmConfig(
                id=row['id'],
                algorithm_name=row['algorithm_name'],
                algorithm_type=row['algorithm_type'],
                parameters=json.loads(row['parameters']),
                description=row['description'],
                version=row['version'],
                is_active=bool(row['is_active']),
                is_default=bool(row['is_default']),
                min_data_required=row['min_data_required'],
                expected_accuracy=float(row['expected_accuracy']) if row['expected_accuracy'] else None,
                computation_complexity=row['computation_complexity'],
                memory_requirements=row['memory_requirements']
            )
            config_list.append(config)
        return config_list

    def insert(self, config: AlgorithmConfig) -> bool:
        """插入算法配置"""
        query = """
        INSERT INTO algorithm_configs (
            algorithm_name, algorithm_type, parameters, description,
            version, is_active, is_default, min_data_required,
            expected_accuracy, computation_complexity, memory_requirements
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            config.algorithm_name,
            config.algorithm_type,
            json.dumps(config.parameters),
            config.description,
            config.version,
            config.is_active,
            config.is_default,
            config.min_data_required,
            config.expected_accuracy,
            config.computation_complexity,
            config.memory_requirements
        )
        return self.execute_update(query, params)