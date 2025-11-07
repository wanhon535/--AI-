# scripts/quick_backtrack_test.py
# !/usr/bin/env python3
"""
快速回溯测试 - 最小化依赖
"""

import sys
import os
import mysql.connector
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)


def quick_test():
    """快速测试数据库连接和基本功能"""
    print("🔍 快速回溯测试")
    print("=" * 50)

    try:
        # 直接测试数据库连接
        from src.config.database_config import DB_CONFIG

        print("1. 🗄️ 测试数据库连接...")
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("   ✅ 数据库连接成功!")

            # 检查关键表是否存在
            cursor = connection.cursor(dictionary=True)

            tables_to_check = [
                'lottery_history',
                'algorithm_recommendation',
                'recommendation_details',
                'reward_penalty_records',
                'algorithm_performance'
            ]

            print("2. 📊 检查数据库表...")
            for table in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table} LIMIT 1")
                    result = cursor.fetchone()
                    print(f"   ✅ {table}: 存在 ({result['count']} 条记录)")
                except Exception as e:
                    print(f"   ❌ {table}: 不存在或错误 - {e}")

            cursor.close()
            connection.close()

            print("\n3. 🚀 测试独立回溯引擎...")
            from src.engine.independent_backtracking_engine import IndependentBacktrackingEngine

            engine = IndependentBacktrackingEngine()
            results = engine.run_algorithm_backtracking(period_count=10)

            if results.get('status') == 'success':
                print("   ✅ 回溯分析成功!")
                summary = results['summary_metrics']
                print(f"      分析期数: {results['total_periods_analyzed']}")
                print(f"      平均得分: {summary['avg_hit_score_per_recommendation']}")
                print(f"      胜率: {summary['win_rate']:.2%}")
            else:
                print(f"   ❌ 回溯分析失败: {results.get('message')}")

        else:
            print("   ❌ 数据库连接失败!")

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    quick_test()