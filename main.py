# main.py (V7.1 - 完整数据库初始化版本)

import json
import os
import sys
import traceback
from datetime import datetime, timedelta

# --- 1. 项目环境设置 ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 2. 导入所有核心组件 ---
from src.database.database_manager import DatabaseManager
from src.engine.performance_logger import PerformanceLogger
from src.engine.recommendation_engine import RecommendationEngine
from src.llm.clients import get_llm_client
from src.prompt_templates import build_lotto_pro_prompt_v14_omega
from src.engine.system_orchestrator import SystemOrchestrator
from run_backtest_simulation import BacktestRunner
from src.utils.logger import log_system_event

# --- 3. 算法导入 ---
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.algorithms.statistical_algorithms import (
    FrequencyAnalysisAlgorithm, HotColdNumberAlgorithm, OmissionValueAlgorithm
)
from src.algorithms.advanced_algorithms.bayesian_number_predictor import BayesianNumberPredictor
from src.algorithms.advanced_algorithms.markov_transition_model import MarkovTransitionModel
from src.algorithms.advanced_algorithms.number_graph_analyzer import NumberGraphAnalyzer

# --- 4. 全局配置 ---
DB_CONFIG = dict(
    host='localhost', user='root', password='123456789',
    database='lottery_analysis_system', port=3309
)


def initialize_system_tables(db_manager: DatabaseManager):
    """
    初始化系统中所有需要基础数据的表 (V8 - 最终对齐版)
    """
    print("\n" + "=" * 60)
    print("🔄 步骤1.5: 初始化系统基础数据表...")
    print("=" * 60)

    try:
        # --- 1. algorithm_configs (保持不变) ---
        print("  - 初始化算法配置表...")
        algorithm_configs = [
            {'algorithm_name': 'FrequencyAnalysisAlgorithm', 'algorithm_type': 'statistical', 'parameters': json.dumps({'window_size': 100, 'top_n': 10}), 'description': '频率分析算法：基于历史数据计算每个号码的出现频率', 'version': '1.0.0', 'is_active': 1, 'is_default': 1, 'min_data_required': 50, 'expected_accuracy': 0.65, 'computation_complexity': 'low'},
            {'algorithm_name': 'HotColdNumberAlgorithm', 'algorithm_type': 'statistical', 'parameters': json.dumps({'window_size': 50, 'hot_threshold': 0.7}), 'description': '热冷号算法：分析号码的热冷状态', 'version': '1.0.0', 'is_active': 1, 'is_default': 1, 'min_data_required': 50, 'expected_accuracy': 0.62, 'computation_complexity': 'low'},
            {'algorithm_name': 'OmissionValueAlgorithm', 'algorithm_type': 'statistical', 'parameters': json.dumps({'max_omission_threshold': 20}), 'description': '遗漏值算法：分析号码的遗漏情况', 'version': '1.0.0', 'is_active': 1, 'is_default': 1, 'min_data_required': 50, 'expected_accuracy': 0.58, 'computation_complexity': 'low'},
            {'algorithm_name': 'BayesianNumberPredictor', 'algorithm_type': 'ml', 'parameters': json.dumps({'prior_strength': 0.5, 'update_prior': True}), 'description': '贝叶斯预测器：基于贝叶斯定理的号码预测', 'version': '1.0.0', 'is_active': 1, 'is_default': 1, 'min_data_required': 100, 'expected_accuracy': 0.68, 'computation_complexity': 'medium'},
            {'algorithm_name': 'MarkovTransitionModel', 'algorithm_type': 'ml', 'parameters': json.dumps({'order': 2, 'smoothing': 0.1}), 'description': '马尔可夫转移模型：基于马尔可夫链的号码转移预测', 'version': '1.0.0', 'is_active': 1, 'is_default': 1, 'min_data_required': 100, 'expected_accuracy': 0.66, 'computation_complexity': 'medium'},
            {'algorithm_name': 'NumberGraphAnalyzer', 'algorithm_type': 'ml', 'parameters': json.dumps({'graph_type': 'co-occurrence', 'community_detection': True}), 'description': '号码图分析器：基于图网络的号码关联分析', 'version': '1.0.0', 'is_active': 1, 'is_default': 1, 'min_data_required': 150, 'expected_accuracy': 0.63, 'computation_complexity': 'high'}
        ]
        for config in algorithm_configs:
            db_manager.execute_insert('algorithm_configs', config)
        print("  - ✅ algorithm_configs 表初始化完成")

        # --- 2. 核心修复: 为 algorithm_performance 初始化数据添加 'issue' 和 'algorithm' 字段 ---
        print("  - 初始化算法性能表...")
        algorithm_performance_data = [
            {
                'issue': 'system_init',  # 正确提供 NOT NULL 字段 'issue' 的值
                'algorithm': name,       # 正确提供 NOT NULL 字段 'algorithm' 的值
                'algorithm_version': f"{name}_1.0",
                'period_number': '2024000',
                'predictions': json.dumps({'note': 'Initial placeholder'}),
                'confidence_score': 0.0,
                'hits': 0,
                'hit_rate': 0.0,
                'score': 0.0
            }
            for name in ['FrequencyAnalysisAlgorithm', 'HotColdNumberAlgorithm', 'OmissionValueAlgorithm',
                         'BayesianNumberPredictor', 'MarkovTransitionModel', 'NumberGraphAnalyzer']
        ]
        for performance in algorithm_performance_data:
            db_manager.execute_insert('algorithm_performance', performance)
        print("  - ✅ algorithm_performance 表初始化完成")

        # --- 3. 其他表的初始化保持不变 (代码折叠) ---
        print("  - 初始化A/B测试配置表...")
        ab_test_configs = [{'test_name': '基础算法对比测试', 'test_description': '对比统计算法与机器学习算法的表现', 'algorithm_a': 'FrequencyAnalysisAlgorithm_1.0', 'algorithm_b': 'BayesianNumberPredictor_1.0', 'split_ratio': 0.5, 'test_parameters': json.dumps({'test_duration': 30, 'min_periods': 20}), 'success_metrics': json.dumps({'primary': 'hit_rate', 'secondary': 'consistency'}), 'test_status': 'draft', 'start_date': datetime.now().date().isoformat(), 'min_sample_size': 50, 'created_by': 'system'}]
        for test_config in ab_test_configs: db_manager.execute_insert('ab_test_configs', test_config)
        print("  - ✅ ab_test_configs 表初始化完成")
        print("  - 初始化数据更新日志表...")
        update_log = {'update_type': 'automatic', 'data_source': 'system_initialization', 'period_range': 'system_setup', 'records_added': len(algorithm_configs) + len(algorithm_performance_data) + len(ab_test_configs), 'records_updated': 0, 'records_deleted': 0, 'update_status': 'success', 'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'execution_duration': 5, 'initiated_by': 'system'}
        db_manager.execute_insert('data_update_logs', update_log)
        print("  - ✅ data_update_logs 表初始化完成")
        print("  - 初始化财务报表...")
        financial_report = {'report_period': datetime.now().strftime('%Y-%m'), 'report_type': 'monthly', 'total_investment': 0.0, 'total_winnings': 0.0, 'net_profit': 0.0, 'return_rate': 0.0, 'total_bets': 0, 'winning_bets': 0, 'bet_success_rate': 0.0, 'algorithm_performance': json.dumps({}), 'max_drawdown': 0.0, 'generated_by': 'system'}
        db_manager.execute_insert('financial_reports', financial_report)
        print("  - ✅ financial_reports 表初始化完成")
        print("  - 初始化模型训练日志表...")
        training_logs = [{'algorithm_version': 'DynamicEnsembleOptimizer_1.0', 'training_date': datetime.now().date().isoformat(), 'data_start_period': '2024001', 'data_end_period': '2024100', 'training_samples': 100, 'training_parameters': json.dumps({'ensemble_method': 'weighted_average', 'update_frequency': 'weekly'}), 'feature_set': json.dumps(['frequency', 'omission', 'hot_cold', 'graph_relations']), 'training_accuracy': 0.72, 'validation_accuracy': 0.68, 'test_accuracy': 0.65, 'training_status': 'completed', 'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'training_duration': 120}]
        for log in training_logs: db_manager.execute_insert('model_training_logs', log)
        print("  - ✅ model_training_logs 表初始化完成")
        print("  - 初始化系统通知表...")
        notifications = [{'user_id': 'system', 'notification_type': 'system', 'title': '系统初始化完成', 'message': '彩票分析系统已完成基础数据初始化，可以开始使用。', 'related_entity_type': 'system', 'related_entity_id': 1}, {'user_id': 'admin', 'notification_type': 'system', 'title': '欢迎使用彩票分析系统', 'message': '系统已准备就绪，请开始您的分析之旅。', 'related_entity_type': 'system', 'related_entity_id': 1}]
        for notification in notifications: db_manager.execute_insert('notifications', notification)
        print("  - ✅ notifications 表初始化完成")
        print("  - 初始化模式识别表...")
        patterns = [{'pattern_type': 'hot_number_cluster', 'pattern_description': '热号聚集模式：连续多期出现热号聚集现象', 'pattern_features': json.dumps({'cluster_size': 3, 'persistence': 5}), 'pattern_signature': 'hot_cluster_v1', 'occurrence_count': 12, 'success_rate': 0.75, 'confidence_level': 0.82, 'first_occurrence_date': '2024-01-15', 'is_active': 1, 'validity_period': 30, 'related_algorithms': json.dumps(['HotColdNumberAlgorithm', 'FrequencyAnalysisAlgorithm'])}, {'pattern_type': 'omission_reversal', 'pattern_description': '遗漏反转模式：长期遗漏号码突然出现', 'pattern_features': json.dumps({'omission_threshold': 15, 'reversal_strength': 0.8}), 'pattern_signature': 'omission_reversal_v1', 'occurrence_count': 8, 'success_rate': 0.68, 'confidence_level': 0.71, 'first_occurrence_date': '2024-02-01', 'is_active': 1, 'validity_period': 45, 'related_algorithms': json.dumps(['OmissionValueAlgorithm', 'BayesianNumberPredictor'])}]
        for pattern in patterns: db_manager.execute_insert('pattern_recognition', pattern)
        print("  - ✅ pattern_recognition 表初始化完成")
        print("  - 初始化奖罚记录表...")
        reward_records = [{'period_number': '2024100', 'algorithm_version': 'FrequencyAnalysisAlgorithm_1.0', 'recommendation_id': 1, 'front_hit_count': 3, 'back_hit_count': 1, 'hit_score': 75.0, 'reward_points': 25.0, 'penalty_points': 0.0, 'net_points': 25.0, 'hit_details': json.dumps({'front_hits': [5, 12, 23], 'back_hits': [8]}), 'missed_numbers': json.dumps({'front_missed': [7, 18], 'back_missed': [3]}), 'performance_rating': 4, 'accuracy_deviation': 0.15, 'improvement_suggestions': '建议结合热冷号分析提高前区命中率'}]
        for record in reward_records: db_manager.execute_insert('reward_penalty_records', record)
        print("  - ✅ reward_penalty_records 表初始化完成")
        print("  - 初始化系统监控表...")
        monitoring_metrics = [{'metric_name': 'algorithm_accuracy', 'metric_category': 'accuracy', 'metric_value': 0.68, 'metric_unit': 'percentage', 'warning_threshold': 0.6, 'critical_threshold': 0.5, 'current_status': 'normal'}, {'metric_name': 'data_freshness', 'metric_category': 'performance', 'metric_value': 1.0, 'metric_unit': 'days', 'warning_threshold': 2.0, 'critical_threshold': 7.0, 'current_status': 'normal'}, {'metric_name': 'memory_usage', 'metric_category': 'resource', 'metric_value': 45.2, 'metric_unit': 'percentage', 'warning_threshold': 80.0, 'critical_threshold': 90.0, 'current_status': 'normal'}, {'metric_name': 'prediction_latency', 'metric_category': 'performance', 'metric_value': 2.3, 'metric_unit': 'seconds', 'warning_threshold': 5.0, 'critical_threshold': 10.0, 'current_status': 'normal'}]
        for metric in monitoring_metrics: db_manager.execute_insert('system_monitoring', metric)
        print("  - ✅ system_monitoring 表初始化完成")

        print("\n✨ 所有系统基础数据表初始化完成！")

    except Exception as e:
        print(f"❌ 系统表初始化失败: {e}")
        traceback.print_exc()


def check_system_initialization(db_manager: DatabaseManager):
    """
    检查系统是否需要初始化
    """
    tables_to_check = [
        'algorithm_configs', 'algorithm_performance', 'ab_test_configs',
        'data_update_logs', 'financial_reports', 'model_training_logs',
        'notifications', 'pattern_recognition', 'reward_penalty_records',
        'system_monitoring'
    ]

    need_initialization = False

    for table in tables_to_check:
        try:
            result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            if count == 0:
                print(f"  - ⚠️ {table} 表为空，需要初始化")
                need_initialization = True
            else:
                print(f"  - ✅ {table} 表已有数据")
        except Exception as e:
            print(f"  - ❌ 检查 {table} 表时出错: {e}")
            need_initialization = True

    return need_initialization


def run_prediction_pipeline(db_manager: DatabaseManager):
    """
    执行单次预测的管道 (V9 - 最终修复版)
    """
    print("\n" + "=" * 60)
    print("🚀  步骤5: 启动 [完整预测] 管道...")
    print("=" * 60)

    try:
        # 1. 数据获取
        performance_logger = PerformanceLogger(db_manager=db_manager)
        recent_draws = db_manager.get_latest_lottery_history(100)
        next_issue = db_manager.get_next_period_number()
        print(f"  - 目标期号: {next_issue}")

        # 2. 学习最新权重
        latest_weights = performance_logger.get_latest_adaptive_weights()
        if not latest_weights:
            print("  - ⚠️ 警告: 尚未学习到任何权重，使用默认值。")
        else:
            print(f"  - ✅ 已加载学习到的动态权重。")

        # 3. 算法引擎执行
        base_algorithms = [
            FrequencyAnalysisAlgorithm(), HotColdNumberAlgorithm(), OmissionValueAlgorithm(),
            BayesianNumberPredictor(), MarkovTransitionModel(), NumberGraphAnalyzer(),
        ]

        individual_predictions = {}
        algorithm_parameters = {}

        for algorithm in base_algorithms:
            try:
                algorithm.train(recent_draws)
                prediction = algorithm.predict(recent_draws)
                individual_predictions[algorithm.name] = prediction

                algorithm_parameters[algorithm.name] = {
                    'version': getattr(algorithm, 'version', '1.0'),
                    'parameters': getattr(algorithm, 'get_parameters', lambda: {})(),
                    'trained_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                # 插入每次的预测日志，这部分现在是正确的
                prediction_log_entry = {
                    'period_number': next_issue,
                    'algorithm_version': f"{algorithm.name}_{getattr(algorithm, 'version', '1.0')}",
                    'predictions': json.dumps(prediction, ensure_ascii=False),
                    'confidence_score': prediction.get('confidence', 0.5)
                }
                db_manager.execute_insert('algorithm_prediction_logs', prediction_log_entry)
                print(f"  - ✅ 存储 {algorithm.name} 预测日志到 'algorithm_prediction_logs' 表")

            except Exception as e:
                print(f"  - ❌ 算法 {algorithm.name} 执行失败: {e}")
                traceback.print_exc()

        # 集成优化逻辑
        chief_strategy_officer = DynamicEnsembleOptimizer(base_algorithms)
        if latest_weights:
            chief_strategy_officer.current_weights = latest_weights

        engine = RecommendationEngine()
        engine.set_meta_algorithm(chief_strategy_officer)
        final_report = engine.generate_final_recommendation(
            history_data=recent_draws,
            individual_predictions=individual_predictions
        )

        model_weights = chief_strategy_officer.current_weights
        key_patterns = {
            'hot_numbers': individual_predictions.get('HotColdNumberAlgorithm', {}).get('hot_numbers', []),
            'high_frequency': individual_predictions.get('FrequencyAnalysisAlgorithm', {}).get('high_frequency_numbers',
                                                                                               []),
            'high_omission': individual_predictions.get('OmissionValueAlgorithm', {}).get('high_omission_numbers', []),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 4. LLM最终裁决
        prompt_text, _ = build_lotto_pro_prompt_v14_omega(
            recent_draws=recent_draws, model_outputs=final_report,
            performance_log=model_weights, next_issue_hint=next_issue,
            last_performance_report="Weights auto-learned from history."
        )
        llm_client = get_llm_client("qwen3-max")
        response_str = llm_client.generate(
            system_prompt=prompt_text,
            user_prompt="Execute your final analysis and generate the complete JSON investment portfolio."
        )

        # 5. 存储完整结果
        response_data = json.loads(response_str)
        final_summary = response_data.get('final_summary', {})
        recommendations_from_llm = response_data['cognitive_cycle_outputs']['phase4_portfolio_construction'][
            'recommendations']

        cognitive_details = response_data.get('cognitive_cycle_outputs', {})
        # --- 核心修复: 在调用前，确保所有字典/列表都转换为JSON字符串 ---
        root_id = db_manager.insert_algorithm_recommendation_root(
            period_number=next_issue,
            algorithm_version="qwen3-max (V14.5-Pr)",
            algorithm_parameters=json.dumps(algorithm_parameters, ensure_ascii=False),
            model_weights=json.dumps(model_weights, ensure_ascii=False),
            confidence_score=final_summary.get('confidence_level', 0.8),
            risk_level=final_summary.get('risk_assessment', 'medium'),
            analysis_basis=json.dumps(final_report, ensure_ascii=False),
            llm_cognitive_details=json.dumps(cognitive_details, ensure_ascii=False),
            key_patterns=json.dumps(key_patterns, ensure_ascii=False),
            models=','.join([algo.name for algo in base_algorithms])
        )

        if not root_id:
            raise Exception("插入推荐主记录失败。")

        print(f"  - ✅ 成功为期号 {next_issue} 存储了完整预测主记录 (ID: {root_id})")

        details_to_insert = [
            {"recommend_type": rec.get('type', 'Unknown'), "strategy_logic": rec.get('role_in_portfolio', ''),
             "front_numbers": ','.join(map(str, rec.get('front_numbers', []))),
             "back_numbers": ','.join(map(str, rec.get('back_numbers', []))),
             "win_probability": rec.get('confidence_score', 0.0)}
            for rec in recommendations_from_llm
        ]
        db_manager.insert_recommendation_details_batch(root_id, details_to_insert)
        print(f"  - ✅ 成功存储了 {len(details_to_insert)} 条推荐详情到 recommendation_details 表")

    except Exception as e:
        print(f"\n❌ 预测管道执行期间发生意外错误: {e}")
        traceback.print_exc()

def main():
    """
    全自动智能管家主程序 - 完整初始化版本
    """
    print("\n" + "#" * 70)
    print("###       欢迎使用 Lotto-Pro 全自动智能管家 V7.1       ###")
    print("#" * 70)

    db_manager = DatabaseManager(**DB_CONFIG)
    log_system_event(db_manager, user_id='system', event_type='SYSTEM_START', status='INFO', details={'version': '7.1'})
    try:
        if not db_manager.connect():
            raise ConnectionError("数据库连接失败，程序终止。")

        orchestrator = SystemOrchestrator(db_manager)

        # --- 步骤1: 检查系统基础表是否需要初始化 ---
        print("\n" + "=" * 60)
        print("🔍 步骤1: 检查系统基础表初始化状态...")
        need_system_init = check_system_initialization(db_manager)

        if need_system_init:
            print("  - 开始初始化系统基础表...")
            initialize_system_tables(db_manager)
        else:
            print("  - ✅ 所有系统基础表已初始化，跳过。")

        # --- 步骤2: 检查号码统计表是否需要初始化 ---
        print("\n" + "=" * 60)
        print("🔍 步骤2: 检查号码统计表初始化状态...")
        stats_count_result = db_manager.execute_query("SELECT COUNT(*) as count FROM number_statistics")
        stats_count = stats_count_result[0]['count'] if stats_count_result else 0
        if stats_count == 0:
            print("  - 检测到系统首次运行，将执行号码统计初始化...")
            orchestrator.check_and_initialize_data()
        else:
            print("  - ✅ 号码统计表已初始化，跳过。")

        # --- 步骤3: 检查并回填缺失的历史分析数据 ---
        print("\n" + "=" * 60)
        print("🔍 步骤3: 检查是否有需要回填的历史分析...")
        missing_basis_result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM algorithm_recommendation WHERE analysis_basis IS NULL OR analysis_basis = ''")
        missing_basis_count = missing_basis_result[0]['count'] if missing_basis_result else 0
        if missing_basis_count > 0:
            print(f"  - 检测到 {missing_basis_count} 条记录缺少分析数据，开始回填...")
            orchestrator.backfill_analysis_basis()
        else:
            print("  - ✅ 所有历史记录的分析数据完整，跳过。")

        # --- 步骤4: 检查并运行历史学习流程 ---
        print("\n" + "=" * 60)
        print("🔍 步骤4: 检查是否有需要学习的新历史...")
        unlearned_query = """
                    SELECT COUNT(DISTINCT period_number) as count
                    FROM algorithm_recommendation
                    WHERE (analysis_basis IS NOT NULL AND analysis_basis != '')
                    AND period_number NOT IN (SELECT DISTINCT period_number FROM algorithm_performance)
                """
        unlearned_result = db_manager.execute_query(unlearned_query)
        unlearned_count = unlearned_result[0]['count'] if unlearned_result else 0
        if unlearned_count > 0:
            print(f"  - 检测到 {unlearned_count} 期已分析但未学习的历史，开始学习...")
            backtest_runner = BacktestRunner(DB_CONFIG)
            try:
                backtest_runner.connect()
                start, end = backtest_runner._get_issue_range_from_db()
                if start and end:
                    backtest_runner.run(start, end)
            finally:
                backtest_runner.disconnect()
        else:
            print("  - ✅ 所有历史均已学习，跳过。")

        # --- 步骤5: 执行今天的预测任务 ---
        run_prediction_pipeline(db_manager)
        log_system_event(db_manager, user_id='system', event_type='SYSTEM_SHUTDOWN', status='SUCCESS')
    except Exception as e:
        print(f"\n❌ 系统主流程发生严重错误: {e}")
        traceback.print_exc()
        log_system_event(db_manager, user_id='system', event_type='SYSTEM_FATAL_ERROR', status='FAILURE',
                         details={'error': str(e)})
    finally:
        if db_manager and getattr(db_manager, "_connected", False):
            db_manager.disconnect()
            print("\n" + "#" * 70)
            print("###                  系统所有任务执行完毕                  ###")
            print("#" * 70)


if __name__ == "__main__":
    main()