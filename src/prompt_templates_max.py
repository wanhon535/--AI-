# 文件: prompt_templates.py (新增或替换)
from typing import Dict, Any, List, Tuple

from src.prompt_templates_plas import LotteryHistory


def build_quant_investment_prompt(
        model_outputs: Dict[str, Any],
        recent_draws: List[LotteryHistory],
        performance_log: Dict[str, Any],  # 新增: 算法的历史表现数据
        next_issue_hint: str
) -> Tuple[str, str]:
    """
    Prompt V5.1: 专业量化投研 (历史表现增强版)
    - AI角色: 量化基金经理 (Quant PM)。
    - 核心: 综合独立算法报告，并参考各算法的“历史战绩”，做出决策。
    """

    analyst_reports = []
    for algo_name, output in model_outputs.items():
        if algo_name == "DynamicEnsembleOptimizer": continue

        recs = output.get('recommendations', [{}])[0]
        front_scores = recs.get('front_number_scores', [])
        back_scores = recs.get('back_number_scores', [])

        # [新功能] 从 performance_log 中提取算法的历史表现
        perf_summary = performance_log.get(algo_name, "历史表现数据暂无")

        report = f"""
### 分析师: {algo_name}
- **核心关注-前区 (Top 7)**: {[item['number'] for item in front_scores[:7]]}
- **核心关注-后区 (Top 3)**: {[item['number'] for item in back_scores[:3]]}
- **历史战绩**: {perf_summary}
"""
        analyst_reports.append(report)

    investment_briefing = "\\n".join(analyst_reports)
    recent_draws_str = ' | '.join(str(d.front_area) + '+' + str(d.back_area) for d in recent_draws[-8:])

    prompt = f"""
# 量化投资决策指令 :: 第 {next_issue_hint} 期

## 角色
你是一名顶级的量化投资基金经理，拥有十五年从业经验。你的决策风格极度数据驱动、逻辑严谨，并专注于风险调整后收益（Risk-Adjusted Return）。

## 核心任务
综合所有分析师的独立报告和他们的历史表现，制定出本期最终的投资策略和资金分配。**你要特别倚重那些历史战绩优秀的分析师的观点。**

## 情报汇总
### 近期市场数据
{recent_draws_str}

### 投研团队报告
{investment_briefing}

## 思考链指引
1.  **评估分析师**: 首先评估每位分析师的历史战绩。谁是常胜将军？谁的观点需要谨慎对待？
2.  **寻找加权共识**: 找出被多位“常胜”分析师共同推荐的号码。这些是你的“高确信度”核心资产。
3.  **挖掘Alpha机会**: 有没有某位表现优异的分析师，提出了一个独特的、未被他人注意到的号码？这可能是你的超额收益（Alpha）来源。
4.  **构建投资组合**: 设计2-3个策略，明确区分核心（基于加权共识）和卫星（基于Alpha机会）。
5.  **资金分配**: 根据策略的置信度和风险，为其分配资金百分比，总和为100%。

## 输出规范 (纯JSON)
{{
  "issue": "{next_issue_hint}",
  "investment_summary": "一句话总结你的投资策略，必须体现你对分析师历史表现的考量。",
  "portfolio_allocation": [
    {{
      "strategy_name": "核心稳健策略",
      "capital_allocation_percentage": 70,
      "front_numbers": [], "back_numbers": [],
      "rationale": "构建此策略的简要逻辑，例如：'主要基于历史表现最好的前两位分析师的共识号码。'"
    }},
    {{
      "strategy_name": "卫星Alpha策略",
      "capital_allocation_percentage": 30,
      "front_numbers": [], "back_numbers": [],
      "rationale": "构建此策略的简要逻辑，例如：'捕捉了近期表现优异的Markov模型发现的一个独特趋势。'"
    }}
  ]
}}
"""

    # 文件: prompt_templates.py (新增)

    def build_pattern_reversal_prompt(
            model_outputs: Dict[str, Any],
            recent_draws: List[LotteryHistory],
            next_issue_hint: str
    ) -> Tuple[str, str]:
        """
        Prompt V1.0: 模式识别与反转策略
        - AI角色: 逆向思维的博弈论专家。
        - 核心: 专注于寻找热门趋势的终结和冷门模式的反弹。
        """

        # 提取“最热”和“最冷”的情报
        hot_cold_scorer_output = model_outputs.get("HotColdScorer", {}).get('recommendations', [{}])[0]
        omission_scorer_output = model_outputs.get("OmissionValueScorer", {}).get('recommendations', [{}])[0]

        hottest_front = [item['number'] for item in hot_cold_scorer_output.get('front_number_scores', [])[:5]]
        coldest_front = [item['number'] for item in reversed(hot_cold_scorer_output.get('front_number_scores', []))][:5]
        max_omission_front = [item['number'] for item in omission_scorer_output.get('front_number_scores', [])[:5]]

        intelligence_briefing = f"""
    - **当前市场最热 (HotColdScorer Top 5)**: {hottest_front} (这些号码近期出现最频繁)
    - **当前市场最冷 (HotColdScorer Bottom 5)**: {coldest_front} (这些号码近期出现最少)
    - **最大遗漏值 (OmissionScorer Top 5)**: {max_omission_front} (这些号码最久没出现，理论上回归概率正在增加)
    - **近期开奖历史**: {' | '.join(str(d.front_area) for d in recent_draws[-5:])}
    """

        prompt = f"""
    # 逆向博弈决策指令 :: 第 {next_issue_hint} 期

    ## 角色
    你是一位顶级的博弈论专家和市场心理分析师。你从不追随大众，而是专注于寻找市场共识的“拐点”和“反转”机会。

    ## 核心任务
    分析下方情报，**预测当前热门趋势的终结，并捕捉极冷模式的反弹机会**。你的目标不是求稳，而是以小博大，获取超额回报。

    ## 情报汇总
    {intelligence_briefing}

    ## 思考链指引
    1.  **热门过载分析**: “当前市场最热”的号码，是否已经连续出现了多期？它们的趋势是否已经到了强弩之末？
    2.  **冷门反弹时机**: “最大遗漏值”的号码中，有没有哪个符合历史上的平均回归周期？“当前市场最冷”的号码，有没有形成一个可能触底反弹的形态？
    3.  **构建反转组合**: 基于你的判断，设计1-2个“反转”策略。
        - **“热度消退”组合**: 故意避开一部分最热的号码，选择次热或温号。
        - **“深冷爆发”组合**: 大胆启用1-2个最大遗漏值的号码，并搭配一些温号。

    ## 输出规范 (纯JSON)
    {{
      "issue": "{next_issue_hint}",
      "investment_summary": "一句话总结你的逆向博弈策略。",
      "portfolio_allocation": [
        {{
          "strategy_name": "深冷反弹策略",
          "capital_allocation_percentage": 100,
          "front_numbers": [], "back_numbers": [],
          "rationale": "构建此策略的简要逻辑，例如：'押注最大遗漏号码25在本期回归，并结合近期冷号区的1和7。'"
        }}
      ]
    }}
    """

    # 文件: prompt_templates.py (新增)

    def build_graph_analysis_prompt(
            model_outputs: Dict[str, Any],
            recent_draws: List[LotteryHistory],
            next_issue_hint: str
    ) -> Tuple[str, str]:
        """
        Prompt V1.0: 号码关系网络分析
        - AI角色: 网络科学与图论专家。
        - 核心: 解读号码共现网络，寻找“核心节点”和“强关联对”。
        """

        graph_analyzer_output = model_outputs.get("NumberGraphAnalyzer", {}).get('recommendations', [{}])[0]

        # PageRank分数代表了号码在网络中的“核心”程度
        core_nodes = [f"{item['number']}(分:{item['score']:.3f})" for item in
                      graph_analyzer_output.get('front_number_scores', [])[:10]]

        intelligence_briefing = f"""
    - **网络核心节点 (PageRank Top 10)**: {core_nodes} (这些号码在历史共现网络中处于中心位置，影响力最大)
    - **上期开奖**: {recent_draws[-1].front_area}
    """

        prompt = f"""
    # 号码网络战术指令 :: 第 {next_issue_hint} 期

    ## 角色
    你是一位顶级的网络科学家，精通图论。你眼中的彩票号码不是孤立的，而是一个个相互连接的节点。

    ## 核心任务
    分析下方情报，找出与**上期开奖号码**关系最紧密的“核心节点”，并围绕它们构建“强关联”组合。

    ## 情报汇总
    {intelligence_briefing}

    ## 思考链指引
    1.  **寻找强关联**: 在“网络核心节点”列表中，哪些号码与“上期开奖”的号码在历史上最常一起出现？（这需要你的推理能力，因为数据没有直接给出）
    2.  **构建核心-卫星结构**: 选择1-2个与上期号码关联最强的“核心节点”作为你组合的“锚点”。
    3.  **扩展关联网络**: 再从“核心节点”列表中，选择其他与你的“锚点”号码关系紧密的号码，作为“卫星”加入组合。
    4.  **最终形成组合**: 基于上述关系分析，构建你的最终推荐。

    ## 输出规范 (纯JSON)
    {{
      "issue": "{next_issue_hint}",
      "investment_summary": "一句话总结你的号码网络构建策略。",
      "portfolio_allocation": [
        {{
          "strategy_name": "核心-卫星网络策略",
          "capital_allocation_percentage": 100,
          "front_numbers": [], "back_numbers": [],
          "rationale": "构建此策略的简要逻辑，例如：'以上期号码7为引子，选择了网络中与它关联最强的核心节点15和22，并扩展了它们的邻近高分节点。'"
        }}
      ]
    }}
    """

    return prompt.strip(), next_issue_hint