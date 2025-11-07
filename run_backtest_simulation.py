# scripts/test_backtracking.py
# !/usr/bin/env python3
"""
独立的回溯测试脚本 - 不依赖其他模块
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)


def test_backtracking():
    """测试回溯功能"""
    print("=" * 60)
    print("测试回溯分析功能")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # 尝试导入回溯引擎
        from src.engine.backtracking_engine import BacktrackingEngine

        # 创建回溯引擎实例
        backtrack_engine = BacktrackingEngine()

        print("1. 测试算法回溯...")
        algo_results = backtrack_engine.run_algorithm_backtracking(period_count=50)

        if algo_results.get('status') == 'success':
            print(f"✅ 算法回溯成功!")
            summary = algo_results['summary_metrics']
            print(f"   分析期数: {algo_results['total_periods_analyzed']}")
            print(f"   平均得分: {summary['avg_hit_score_per_recommendation']}")
            print(f"   胜率: {summary['win_rate']:.2%}")
        else:
            print(f"❌ 算法回溯失败: {algo_results.get('message')}")

        print("\n2. 测试LLM回溯...")
        llm_results = backtrack_engine.run_llm_backtracking(period_count=30)

        if llm_results.get('status') == 'success':
            print(f"✅ LLM回溯成功!")
            metrics = llm_results['llm_metrics']
            print(f"   分析期数: {llm_results['total_periods_analyzed']}")
            print(f"   准确率: {metrics['accuracy_rate']:.2%}")
        else:
            print(f"❌ LLM回溯失败: {llm_results.get('message')}")

        print("\n3. 获取回溯摘要...")
        summary = backtrack_engine.get_backtracking_summary()

        if summary.get('status') == 'success':
            print("✅ 回溯摘要获取成功!")
        else:
            print(f"❌ 回溯摘要获取失败: {summary.get('message')}")

        # 输出完整结果
        print("\n" + "=" * 60)
        print("完整回溯结果:")
        print("=" * 60)
        full_results = {
            'algorithm_backtracking': algo_results,
            'llm_backtracking': llm_results,
            'summary': summary,
            'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        print(json.dumps(full_results, indent=2, ensure_ascii=False))

        # 保存结果到文件
        output_file = os.path.join(project_root, 'outputs', 'backtracking_test_results.json')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(full_results, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到: {output_file}")

        return full_results

    except Exception as e:
        print(f"❌ 回溯测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    test_backtracking()