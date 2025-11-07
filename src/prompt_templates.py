import json
from typing import List, Tuple, Dict, Any

# ... (LotteryHistory 和类型提示保持不变) ...
try:
    from src.model.lottery_models import LotteryHistory
except ImportError:
    class LotteryHistory:
        front_area: List[int] = []
        back_area: List[int] = []
        period_number: str = "N/A"
        pass
AlgoOutput = Dict[str, Any]
HistoryList = List[LotteryHistory]


# ==============================================================================
# === 阶段 A (V13.0 A): 本地算法直接生成完整投注组合 ===
# ==============================================================================
def build_strategy_A_prompt(
        ensemble_output: AlgoOutput,
        recent_draws: HistoryList,
        next_issue_hint: str
) -> Tuple[str, str]:
    """
    [已升级] 角色：本地算法策略师
    任务：基于本地算法的数字评分，直接构建一套完整的、多样化的投注组合。
    """
    front_scores = ensemble_output.get('recommendations', [{}])[0].get('front_number_scores', [])
    back_scores = ensemble_output.get('recommendations', [{}])[0].get('back_number_scores', [])
    ensemble_info = ensemble_output.get('analysis', {}).get('ensemble_info', {})

    top_front_scores = "\n".join([f"- 号码 {item['number']:2d}: 评分 {item['score']:.4f}" for item in front_scores[:15]])
    top_back_scores = "\n".join([f"- 号码 {item['number']:2d}: 评分 {item['score']:.4f}" for item in back_scores[:8]])
    weights_str = "\n".join([f"- {algo}: {weight:.3f}" for algo, weight in ensemble_info.get('optimal_weights', {}).items()])

    prompt = f"""
# 本地算法策略师指令 :: 阶段 A：生成完整投注组合

## 角色
你是**本地算法策略师**。你的任务是深度解读 DynamicEnsembleOptimizer 提供的**数字评分**，并基于这些纯粹的数学结果，构建一个**完整的、结构化的投注组合**，以最大化中奖概率。

## 核心数据输入 (来自 DynamicEnsembleOptimizer)

### 前区Top 15评分
{top_front_scores}

### 后区Top 8评分
{top_back_scores}

### 算法权重
{weights_str}

## 深度思考链与组合构建指引
1.  **识别核心胆码**: 从前区Top 5和后区Top 3中，选出最稳定的1-2个前区胆码和1个后区胆码。这些是所有组合的基石。
2.  **构建高增长组合 (7+3)**: 围绕核心胆码，加入评分高且近期活跃的号码，构成一个最具潜力的组合。
3.  **构建平衡型组合 (7+2)**: 在7+3的基础上，用一个评分稍低但更稳健的后区号码替换掉风险最高的那个，形成覆盖面广的平衡组合。
4.  **构建高确定性组合 (6+3)**: 精选前区Top 8中的6个号码，组合后区Top 4中的3个，目标是保本和稳定命中。
5.  **设计单注对冲 (可选)**: 如果你发现评分接近但特性（如冷热、奇偶）相反的号码，可以设计几注单式来对冲风险。

## 输出规范 (纯JSON - 策略A的完整方案)
你的回答必须是**纯粹的JSON格式**，严格遵循以下结构，不要有任何额外文字。
{{{{
  "issue": "{next_issue_hint}",
  "source": "Strategy_A_Local_Algorithms",
  "reasoning_summary": "总结你是如何根据数字评分和算法权重，构建出以下这套组合的。",
  "portfolio_A": {{
    "high_growth_7_3": {{
      "combo_name": "高增长型复式 (7+3)",
      "front_numbers": [], "back_numbers": [],
      "strategy_focus": "基于本地算法评分最高的号码，追求最大回报。"
    }},
    "balanced_7_2": {{
      "combo_name": "平衡型复式 (7+2)",
      "front_numbers": [], "back_numbers": [],
      "strategy_focus": "平衡高评分与号码分布的广度。"
    }},
    "high_certainty_6_3": {{
      "combo_name": "高确定型复式 (6+3)",
      "front_numbers": [], "back_numbers": [],
      "strategy_focus": "核心高分号码的强力组合，目标是稳定命中。"
    }},
    "hedge_5_2_set": [
      {{
        "combo_name": "单注对冲A",
        "front_numbers": [], "back_numbers": [],
        "strategy_focus": "对冲特定风险点，如奇偶失衡。"
      }}
    ]
  }}
}}}}
"""
    return prompt.strip(), next_issue_hint


# ==============================================================================
# === 阶段 B (V13.0 B): LLM 独立生成完整投注组合 ===
# ==============================================================================
def build_strategy_B_prompt(
        recent_draws: HistoryList,
        next_issue_hint: str
) -> Tuple[str, str]:
    """
    [已升级] 角色：LLM 独立策略师
    任务：基于对历史数据的“脑补”算法分析，直接构建一套完整的、多样化的投注组合。
    """
    recent_draws_str = '\n'.join(
        f"期号:{d.period_number} - 前区:{d.front_area} - 后区:{d.back_area}" for d in recent_draws[-100:])

    prompt = f"""
# LLM 独立策略师指令 :: 阶段 B：生成完整投注组合

## 角色
你是**LLM 独立策略师**。你的任务是**完全忽略任何外部算法评分**，仅凭你对下方提供的**纯历史数据**的深度理解，在思维中模拟运行高级预测算法（如BSTS, 因果森林等），并基于你的模拟结果，直接构建一个**完整的、结构化的投注组合**。

## 纯历史开奖数据 (最新100期 - 你的唯一输入)
{recent_draws_str}

## 深度思考链与组合构建指引
1.  **识别核心模式**: 通过模拟，你认为下一期最可能出现的宏观模式是什么？（例如：大号回补、连号再现、奇数主导）。这是你所有组合的战略基础。
2.  **构建高增长组合 (7+3)**: 基于你识别的核心模式，大胆选择最符合该模式的号码，构建最具想象空间的7+3组合。
3.  **构建平衡型组合 (7+2)**: 在你的核心模式基础上，加入一些历史高频号码作为“压舱石”，形成攻守兼备的7+2。
4.  **构建高确定性组合 (6+3)**: 精选那些在多种模拟算法中都表现出稳定趋势的号码，构成一个最不容易“跑偏”的6+3组合。
5.  **设计单注对冲 (可选)**: 如果你的核心模式有备选方案（例如，如果大号不回补，而是小号继续热出），设计几注单式来覆盖这种可能性。

## 输出规范 (纯JSON - 策略B的完整方案)
你的回答必须是**纯粹的JSON格式**，严格遵循以下结构，不要有任何额外文字。
{{{{
  "issue": "{next_issue_hint}",
  "source": "Strategy_B_LLM_Internal",
  "reasoning_summary": "总结你是如何通过内部算法模拟和模式判断，构建出以下这套组合的。",
  "portfolio_B": {{
    "high_growth_7_3": {{
      "combo_name": "高增长型复式 (7+3)",
      "front_numbers": [], "back_numbers": [],
      "strategy_focus": "基于LLM识别的核心趋势，追求最大回报。"
    }},
    "balanced_7_2": {{
      "combo_name": "平衡型复式 (7+2)",
      "front_numbers": [], "back_numbers": [],
      "strategy_focus": "核心趋势与历史高频的平衡。"
    }},
    "high_certainty_6_3": {{
      "combo_name": "高确定型复式 (6+3)",
      "front_numbers": [], "back_numbers": [],
      "strategy_focus": "跨多种模拟算法的共识号码，目标是稳定。"
    }},
    "hedge_5_2_set": [
      {{
        "combo_name": "单注对冲B",
        "front_numbers": [], "back_numbers": [],
        "strategy_focus": "对冲核心模式的替补方案。"
      }}
    ]
  }}
}}}}
"""
    return prompt.strip(), next_issue_hint


# ==============================================================================
# === 阶段 C (V13.0 C): 终极方案裁决与再平衡 ===
# ==============================================================================
def build_final_allocation_prompt(
        strategy_A_json: str,
        strategy_B_json: str,
        next_issue_hint: str
) -> Tuple[str, str]:
    """
    [VC MODEL UPGRADE] 角色：终极投资组合经理
    任务：将固定的投注模板，按照风险投资的原则进行填充，目标是长期正向ROI。
    """
    betting_template_info = """
- **1注 7+3 复式 (核心盈利)**
- **1注 7+2 复式 (稳健增长)**
- **1注 6+3 复式 (成本对冲/安全垫)**
- **6-7注 5+2 单式 (高风险/高回报的天使投资)**
"""

    prompt = f"""
# 终极投资组合经理指令 :: 阶段 C：构建风险投资型投注组合

## 角色
你是**终极投资组合经理**。你的任务是将A、B两份研究报告中的洞察，转化为一个结构化的、以**长期正向投资回报率（ROI）**为唯一目标的投注组合。你必须严格按照下方指定的模板及其财务角色进行号码分配。

## 战略情报输入

### 方案 A (由本地算法策略师提交)
{strategy_A_json}

### 方案 B (由LLM独立策略师提交)
{strategy_B_json}

## 最终投注模板及其财务角色 (必须严格遵守)
{betting_template_info}

## 投资组合的财务角色与构建指令 (CRITICAL)
你必须为每个模板分配符合其财务角色的号码，以构建一个健康的投资组合：

1.  **安全垫投注 (`6+3` 复式)**:
    *   **财务角色**: 这是你的“成本对冲”工具。它的首要目标是频繁命中中小奖（如3+1, 4+0, 4+1），从而**覆盖整个投资组合的大部分成本**。
    *   **构建指令**: **必须**使用A、B方案中**共识度最高**、最稳健、历史出现频率最稳定的号码来构建。**不要**在此处追求冷门。

2.  **稳健增长投注 (`7+2` 复式)**:
    *   **财务角色**: 这是你的“中盘股”。在安全垫的基础上，扩大前区覆盖，追求更高一些的奖金，是保本与盈利之间的平衡器。
    *   **构建指令**: 可以使用`6+3`的号码作为核心，加入一个共识度同样较高但近期有上升趋势的第7个前区号码。后区选择最稳健的2个。

3.  **核心盈利投注 (`7+3` 复式)**:
    *   **财务角色**: 这是你的“核心盈利引擎”。它承担着主要的盈利任务，追求较高的奖项。
    *   **构建指令**: 使用`7+2`的前区，但后区**必须**加入一个A或B方案中预测的、最具潜力的“黑马号码”，以博取更高回报。

4.  **天使投资投注 (6-7注 `5+2` 单式)**:
    *   **财务角色**: 这是你的“风险投资（VC）”部分。**你预计这部分的大多数投注会失败**，但它们的目标是捕捉到低概率、高回报的“黑天鹅”事件。一注命中，就足以覆盖所有成本并带来巨大利润。
    *   **构建指令**: 这些单式**必须体现与核心投注完全不同的逻辑**，以实现真正的风险对冲。例如：
        *   **2注**: 完全体现A方案的独特逻辑（使用A独有而B没有的号码）。
        *   **2注**: 完全体现B方案的独特逻辑（使用B独有而A没有的号码）。
        *   **1注**: 构建一个**纯冷号**组合，去博弈“热极必反”。
        *   **1注**: 构建一个**追逐极端遗漏**的组合（例如，包含当前遗漏值最高的1-2个号码）。
        *   **1注**: 构建一个**极端形态**的组合（例如，纯大号组合、纯奇数组合等）。

## 输出规范 (纯JSON - 填充后的最终方案)
你的回答必须是**纯粹的JSON格式**。`final_portfolio`的结构必须与下方完全一致，以体现你的投资策略。
{{{{
  "issue": "{next_issue_hint}",
  "reasoning_summary": "阐述你的投资组合构建策略：你是如何为每个财务角色分配号码的，特别是你的天使投资（单式）部分是如何对冲核心投注的风险的。",
  "fusion_analysis": {{
      "high_confidence_intersection": {{ "front_numbers": [], "back_numbers": [] }},
      "strategy_A_vs_B_conflict": "描述A和B的核心策略分歧。",
      "commander_ruling": "明确说明你的最终组合是如何将A和B的洞察，转化为一个多层次的风险投资组合的。"
  }},
  "final_portfolio": {{
    "safety_net_bet": {{
        "combo_name": "【安全垫】成本对冲型 (6+3)", "front_numbers": [], "back_numbers": [], "strategy_focus": "高共识号码，目标是频繁中小奖以覆盖成本。"
    }},
    "steady_growth_bet": {{
        "combo_name": "【稳健增长】平衡型 (7+2)", "front_numbers": [], "back_numbers": [], "strategy_focus": "扩大核心覆盖，追求稳定盈利。"
    }},
    "core_profit_bet": {{
        "combo_name": "【核心盈利】主攻型 (7+3)", "front_numbers": [], "back_numbers": [], "strategy_focus": "最强信号组合，承担主要盈利任务。"
    }},
    "vc_plays": [
        {{ "combo_name": "【VC-A逻辑】单式", "front_numbers": [], "back_numbers": [], "strategy_focus": "体现A方案独特逻辑。" }},
        {{ "combo_name": "【VC-B逻辑】单式", "front_numbers": [], "back_numbers": [], "strategy_focus": "体现B方案独特逻辑。" }},
        {{ "combo_name": "【VC-冷门】单式", "front_numbers": [], "back_numbers": [], "strategy_focus": "博弈热极必反，捕捉黑天鹅。" }},
        {{ "combo_name": "【VC-遗漏】单式", "front_numbers": [], "back_numbers": [], "strategy_focus": "追逐当前最大遗漏值号码。" }},
        {{ "combo_name": "【VC-形态】单式", "front_numbers": [], "back_numbers": [], "strategy_focus": "博弈极端号码形态（如全大/全奇）。" }},
        {{ "combo_name": "【VC-备用】单式", "front_numbers": [], "back_numbers": [], "strategy_focus": "备用对冲策略。" }}
    ]
  }}
}}}}
"""
    return prompt.strip(), next_issue_hint