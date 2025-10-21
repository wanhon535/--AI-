# main.py
from src.config.database_config import DatabaseConfig

from src.config.system_config import SystemConfig
from src.database.database_manager import DatabaseManager
from src.engine.recommendation_engine import RecommendationEngine
from src.engine.evaluation_system import EvaluationSystem
from src.algorithms.statistical_algorithms import (
    FrequencyAnalysisAlgorithm,
    HotColdNumberAlgorithm,
    OmissionValueAlgorithm
)
import logging

def main():
    """主函数"""
    # 初始化日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("乐透智能分析系统启动")

    # 初始化数据库连接
    db_config = DatabaseConfig.get_config()
    db_manager = DatabaseManager(**db_config)

    if not db_manager.connect():
        logger.error("数据库连接失败")
        return

    logger.info("数据库连接成功")

    # 初始化推荐引擎
    recommendation_engine = RecommendationEngine()

    # 添加统计学算法
    recommendation_engine.add_algorithm(FrequencyAnalysisAlgorithm(), 0.3)
    recommendation_engine.add_algorithm(HotColdNumberAlgorithm(), 0.25)
    recommendation_engine.add_algorithm(OmissionValueAlgorithm(), 0.2)

    # 获取历史数据
    history_data = db_manager.get_lottery_history(limit=100)
    logger.info(f"获取到 {len(history_data)} 条历史数据")

    # 训练所有算法
    train_results = recommendation_engine.train_all_algorithms(history_data)
    logger.info(f"算法训练结果: {train_results}")

    # 生成推荐
    recommendations = recommendation_engine.generate_recommendations(history_data)
    logger.info(f"生成推荐结果: {recommendations}")

    # 保存推荐结果到数据库
    # 这里需要实现保存逻辑

    # 关闭数据库连接
    db_manager.disconnect()
    logger.info("系统运行完成")

if __name__ == "__main__":
    main()
