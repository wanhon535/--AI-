# 文件: prompt_templates.py (V6.0 - 命中率导向终极版)

import json
from typing import List, Tuple, Dict, Any
import numpy as np

# 临时定义，以防IDE报错，请确保您项目中实际导入了正确的类
try:
    from src.model.lottery_models import LotteryHistory
except ImportError:
    class LotteryHistory:
        pass


# ==============================================================================
# === 全局唯一Prompt: “金选组合”生成器 (Hit-Rate Focused) ===
# ==============================================================================
def build_gold_standard_prompt(
        model_outputs: Dict[str, Any],
        recent_draws: List[LotteryHistory],
        next_issue_hint: str
) -> Tuple[str, str]:
    """
    Prompt V6.0: 命中率导向的“金选组合”生成器
    - AI角色: 冷酷的概率猎人 (Probability Hunter)。
    - 核心任务: 寻找多个算法的“共识核心”，并进行智能补全，以最大化命中3-4个号码的概率。
    """

    # === 步骤 1: 生成标准化的“数据摘要”，包含所有算法的精华 ===
    all_front_recommendations = []
    all_back_recommendations = []

    report_sections = []
    for algo_name, output in model_outputs.items():
        if algo_name == "DynamicEnsembleOptimizer": continue
        recs = output.get('recommendations', [{}])[0]
        front_scores = recs.get('front_number_scores', [])
        back_scores = recs.get('back_number_scores', [])

        top_front = [item['number'] for item in front_scores[:7]]
        top_back = [item['number'] for item in back_scores[:3]]

        all_front_recommendations.extend(top_front)
        all_back_recommendations.extend(top_back)

        report_sections.append(f"- **{algo_name}**: 前区推荐 {top_front} | 后区推荐 {top_back}")

    # 将所有算法的推荐汇总成一份情报
    intelligence_briefing = "\\n".join(report_sections)

    # [核心] 计算所有算法推荐的“重叠宇宙”
    front_consensus = sorted(
        [num for num, count in np.unique(all_front_recommendations, return_counts=True) if count > 1], reverse=True)
    back_consensus = sorted(
        [num for num, count in np.unique(all_back_recommendations, return_counts=True) if count > 1], reverse=True)

    # 近期市场回顾
    recent_draws_str = ' | '.join(
        str(getattr(d, 'front_area', [])) + '+' + str(getattr(d, 'back_area', [])) for d in recent_draws[-8:])

    # === 步骤 2: 构建终极的、专注的Prompt ===
    prompt = f"""
# 概率猎人指令 :: 第 {next_issue_hint} 期“金选组合”构建

## 角色
你是一名冷酷、理性的概率猎人。你的唯一目标是**最大化命中3-4个号码的概率**。忽略所有无关的情感、故事和复杂的策略，只相信数据和概率。

## 核心任务
你的任务是分析下方由多个独立算法（你的“探针”）提供的数据，找出最有可能出现的“**共识核心**”，并围绕它构建1-2组最高概率的“**金选组合 (Gold-Standard Combo)**”。

## 数据摘要 (Data Digest)

### 算法探针报告
{intelligence_briefing}

### [关键情报] 算法共识区
- **前区共识 (被多个算法同时推荐)**: {front_consensus}
- **后区共识 (被多个算法同时推荐)**: {back_consensus}

### 近期市场回顾
{recent_draws_str}

## 思考链指引 (Chain of Thought)
1.  **确立基石**: “共识区”的号码是本次行动的绝对核心，因为它们得到了多重验证。你的最终组合里**必须**包含这些号码中的绝大部分。
2.  **分析缺口**: “共识区”通常只有2-4个号码。你需要决定还需要补充几个号码来组成一个完整的组合 (5个前区，2个后区)。
3.  **智能补全**: 仔细审阅“算法探针报告”和“近期市场回顾”。从那些**未进入共识区、但被高分推荐**的号码中，挑选出与你的“基石”号码最可能形成**协同模式**（例如，构成连号、邻号、同尾、奇偶平衡等）的号码，来填补缺口。
4.  **最终组合**: 构建出你认为概率最高的1-2组最终组合。

## 输出规范 (纯JSON)
你的回答必须是**纯粹的JSON格式**，严格遵循以下结构，不要有任何额外的文本。
{{{{
  "issue": "{next_issue_hint}",
  "reasoning_summary": "一句话总结你的选号逻辑。例如：'以高共识度的12和24为核心，并补充了频率算法推荐的邻号11和图算法推荐的同尾号34。'",
  "gold_standard_combos": [
    
    {{{{
      "combo_name": "主攻金选复式组合 (7+3)",
      "front_numbers": [], // 你选择的7个前区号码
      "back_numbers": [],  // 你选择的3个后区号码
      "confidence_level": "High"
    }}}},
    {{{{
      "combo_name": "备选对冲复式组合 (6+3)",
      "front_numbers": [], // 你选择的6个前区号码
      "back_numbers": [],  // 你选择的3个后区号码
      "confidence_level": "Medium"
    }}}},
    {{{{
      "combo_name": "备选对冲组合 (5+2)",
      "front_numbers": [], // 另一组你认为可能的5个前区号码
      "back_numbers": [],  // 另一组可能的2个后区号码
      "confidence_level": "Medium"
    }}}},
    {{{{
      "combo_name": "主攻金选组合 (5+2)",
      "front_numbers": [], // 你选择的5个前区号码
      "back_numbers": [],  // 你选择的2个后区号码
      "confidence_level": "High"
    }}}}
  ]
}}}}
"""
    return prompt.strip(), next_issue_hint