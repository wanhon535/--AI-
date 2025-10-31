# scripts/generate_backtest_data.py (完整字段版本)
import os
import sys
import json
from datetime import datetime

# 环境设置
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.algorithms.statistical_algorithms import (
    FrequencyAnalysisAlgorithm, HotColdNumberAlgorithm, OmissionValueAlgorithm
)
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer
from src.model.lottery_models import LotteryHistory
from src.engine.performance_logger import PerformanceLogger

DB_CONFIG = dict(
    host='localhost', user='root', password='123456789',
    database='lottery_analysis_system', port=3309
)


def generate_backtest_data():
    """为历史期号生成完整的回测数据"""
    db_manager = DatabaseManager(**DB_CONFIG)
    if not db_manager.connect():
        print("❌ 数据库连接失败")
        return

    print("\n" + "=" * 60)
    print("🚀 开始生成完整历史回测数据...")
    print("=" * 60)

    try:
        # 1. 获取所有需要回测的历史期号
        all_history_dicts = db_manager.get_all_lottery_history(200)
        if not all_history_dicts or len(all_history_dicts) < 50:
            print("❌ 历史数据不足，无法生成回测数据")
            return

        # 转换为 LotteryHistory 对象
        all_history_data = []
        for record_dict in all_history_dicts:
            lottery_record = LotteryHistory()
            lottery_record.period_number = record_dict['period_number']
            lottery_record.draw_date = record_dict['draw_date']
            lottery_record.front_area = [
                record_dict['front_area_1'],
                record_dict['front_area_2'],
                record_dict['front_area_3'],
                record_dict['front_area_4'],
                record_dict['front_area_5']
            ]
            lottery_record.back_area = [
                record_dict['back_area_1'],
                record_dict['back_area_2']
            ]
            all_history_data.append(lottery_record)

        # 2. 获取需要回测的期号
        periods_to_process = []
        for i in range(50, len(all_history_data)):
            period = all_history_data[i].period_number
            periods_to_process.append(period)

        if not periods_to_process:
            print("✅ 所有历史期号都已存在回测数据")
            return

        print(f"📊 发现 {len(periods_to_process)} 个需要生成回测数据的期号")

        # 3. 初始化算法列表和性能记录器
        base_algorithms = [
            FrequencyAnalysisAlgorithm(),
            HotColdNumberAlgorithm(),
            OmissionValueAlgorithm(),
            BayesianNumberPredictor(),
            MarkovTransitionModel(),
            NumberGraphAnalyzer(),
        ]

        performance_logger = PerformanceLogger(db_manager=db_manager)

        # 4. 为每个期号生成完整的回测数据
        for i, period in enumerate(periods_to_process, 1):
            print(f"\n--- 正在处理期号: {period} ({i}/{len(periods_to_process)}) ---")

            try:
                # 获取该期号之前的历史数据
                current_index = next((idx for idx, record in enumerate(all_history_data)
                                      if record.period_number == period), -1)

                if current_index == -1 or current_index < 30:
                    print(f"  - ⏸️ 跳过: 期号 {period} 的历史数据不足")
                    continue

                training_data = all_history_data[:current_index]

                # 运行所有算法生成预测
                individual_predictions = {}
                algorithm_parameters = {}

                for algorithm in base_algorithms:
                    try:
                        algorithm.train(training_data)
                        prediction = algorithm.predict(training_data)
                        individual_predictions[algorithm.name] = prediction

                        # 收集算法参数
                        algorithm_parameters[algorithm.name] = {
                            'version': getattr(algorithm, 'version', '1.0'),
                            'parameters': getattr(algorithm, 'get_parameters', lambda: {})(),
                            'trained_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }

                        # 插入 algorithm_performance 表
                        performance_data = {
                            'algorithm_version': f"{algorithm.name}_{getattr(algorithm, 'version', '1.0')}",
                            'period_number': period,
                            'predictions': json.dumps(prediction, ensure_ascii=False),
                            'confidence_score': prediction.get('confidence', 0.5),
                            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        performance_logger.dao.insert_algorithm_performance(performance_data)
                        print(f"  - ✅ {algorithm.name} 预测完成并存储性能数据")

                    except Exception as e:
                        print(f"  - ❌ {algorithm.name} 预测失败: {e}")
                        continue

                # 生成集成预测和模型权重
                ensemble_optimizer = DynamicEnsembleOptimizer(base_algorithms)
                ensemble_optimizer.train(training_data)
                ensemble_prediction = ensemble_optimizer.predict(training_data)

                # 获取模型权重
                model_weights = ensemble_optimizer.current_weights

                # 提取关键模式
                key_patterns = {
                    'hot_numbers': individual_predictions.get('HotColdNumberAlgorithm', {}).get('hot_numbers', []),
                    'high_frequency': individual_predictions.get('FrequencyAnalysisAlgorithm', {}).get(
                        'high_frequency_numbers', []),
                    'high_omission': individual_predictions.get('OmissionValueAlgorithm', {}).get(
                        'high_omission_numbers', []),
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                # 构建完整的分析基础数据
                analysis_basis = {
                    'period_number': period,
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'individual_predictions': individual_predictions,  # 这应该是字典，不是字符串
                    'ensemble_prediction': ensemble_prediction,
                    'algorithms_used': [algo.name for algo in base_algorithms],
                    'history_data_count': len(training_data),
                    'training_period_range': {
                        'start': training_data[0].period_number if training_data else None,
                        'end': training_data[-1].period_number if training_data else None
                    }
                }

                # 插入到 algorithm_recommendation 表（完整字段）
                root_id = db_manager.insert_algorithm_recommendation_root(
                    period_number=period,
                    recommend_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    algorithm_version="backtest_data_generator_v2.0",
                    algorithm_parameters=json.dumps(algorithm_parameters, ensure_ascii=False),
                    model_weights=json.dumps(model_weights, ensure_ascii=False),
                    confidence_score=ensemble_prediction.get('confidence', 0.7),
                    risk_level=ensemble_prediction.get('risk_level', 'medium'),
                    analysis_basis=json.dumps(analysis_basis, ensure_ascii=False),  # 确保是JSON字符串
                    key_patterns=json.dumps(key_patterns, ensure_ascii=False),
                    models=','.join([algo.name for algo in base_algorithms])
                )

                if root_id:
                    # 插入推荐详情到 recommendation_details 表
                    details_to_insert = []

                    # 添加集成推荐
                    ensemble_details = {
                        "recommend_type": "ensemble_prediction",
                        "strategy_logic": "动态集成优化算法综合推荐",
                        "front_numbers": ','.join(map(str, ensemble_prediction.get('front_area', []))),
                        "back_numbers": ','.join(map(str, ensemble_prediction.get('back_area', []))),
                        "win_probability": ensemble_prediction.get('confidence', 0.7)
                    }
                    details_to_insert.append(ensemble_details)

                    # 添加各算法推荐
                    for algo_name, prediction in individual_predictions.items():
                        algo_details = {
                            "recommend_type": f"{algo_name}_prediction",
                            "strategy_logic": f"{algo_name}算法独立推荐",
                            "front_numbers": ','.join(map(str, prediction.get('front_area', []))),
                            "back_numbers": ','.join(map(str, prediction.get('back_area', []))),
                            "win_probability": prediction.get('confidence', 0.5)
                        }
                        details_to_insert.append(algo_details)

                    # 批量插入详情
                    db_manager.insert_recommendation_details_batch(root_id, details_to_insert)

                    print(f"  - ✅ 成功生成完整回测数据，记录ID: {root_id}")
                    print(f"  - 📊 存储了 {len(details_to_insert)} 条推荐详情")
                else:
                    print(f"  - ❌ 插入回测数据失败")

            except Exception as e:
                print(f"  - ❌ 处理期号 {period} 时出错: {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"\n✨ 完整回测数据生成完成！共处理 {len(periods_to_process)} 个期号")

    except Exception as e:
        print(f"❌ 生成回测数据过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    generate_backtest_data()