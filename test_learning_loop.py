# scripts/fixed_backtrack_test.py
# !/usr/bin/env python3
"""
完全修复的回溯测试 - 解决所有已知问题
"""

import sys
import os
import json
from datetime import datetime
from decimal import Decimal

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)


class DecimalEncoder(json.JSONEncoder):
    """处理Decimal类型的JSON编码器"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def test_fixed_backtracking():
    """测试修复版回溯功能"""
    print("=" * 60)
    print("🔧 测试修复版回溯分析功能")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # 导入修复版回溯引擎
        from src.engine.fixed_backtracking_engine import FixedBacktrackingEngine

        # 创建回溯引擎实例
        print("🔧 初始化修复版回溯引擎...")
        backtrack_engine = FixedBacktrackingEngine()

        print("\n1. 🎯 测试算法回溯...")
        algo_results = backtrack_engine.run_algorithm_backtracking(period_count=10)

        if algo_results.get('status') == 'success':
            print(f"✅ 算法回溯成功!")
            summary = algo_results['summary_metrics']
            print(f"   📅 分析期数: {algo_results['total_periods_analyzed']}")
            print(f"   🎯 平均得分: {summary['avg_hit_score_per_recommendation']}")
            print(f"   📊 胜率: {summary['win_rate']:.2%}")
            print(f"   📋 总推荐数: {summary['total_recommendations_analyzed']}")
        else:
            print(f"❌ 算法回溯失败: {algo_results.get('message')}")

        print("\n2. 📊 获取回溯摘要...")
        summary = backtrack_engine.get_backtracking_summary()

        if summary.get('status') == 'success':
            print("✅ 回溯摘要获取成功!")
            print(f"   🔢 跟踪算法数量: {summary['summary']['total_algorithms_tracked']}")
            if summary['reward_statistics']:
                stats = summary['reward_statistics']
                print(f"   📈 平均命中得分: {stats.get('avg_hit_score', 0):.2f}")
        else:
            print(f"❌ 回溯摘要获取失败: {summary.get('message')}")

        # 输出完整结果 - 使用自定义编码器处理Decimal
        print("\n" + "=" * 60)
        print("📋 完整回溯结果:")
        print("=" * 60)

        full_results = {
            'algorithm_backtracking': algo_results,
            'summary': summary,
            'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 使用自定义编码器确保Decimal能被序列化
        try:
            result_json = json.dumps(full_results, indent=2, ensure_ascii=False, cls=DecimalEncoder)
            print(result_json)
        except Exception as e:
            print(f"❌ JSON序列化失败: {e}")

            # 手动转换所有Decimal为float
            def convert_decimals(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                elif isinstance(obj, dict):
                    return {k: convert_decimals(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_decimals(item) for item in obj]
                else:
                    return obj

            safe_results = convert_decimals(full_results)
            print(json.dumps(safe_results, indent=2, ensure_ascii=False))

        # 保存结果到文件
        output_dir = os.path.join(project_root, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'fixed_backtracking_results.json')

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(full_results, f, indent=2, ensure_ascii=False, cls=DecimalEncoder)
        print(f"\n💾 结果已保存到: {output_file}")

        return full_results

    except Exception as e:
        print(f"❌ 回溯测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    test_fixed_backtracking()