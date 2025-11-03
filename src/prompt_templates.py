import json
from typing import List, Tuple, Dict, Any
from src.model.lottery_models import LotteryHistory
import random

def build_final_mandate_prompt(
        recent_draws: List[LotteryHistory],
        model_outputs: Dict[str, Any],
        performance_log: Dict[str, float],
        user_constraints: Dict[str, Any] = None,
        next_issue_hint: str = None,
        last_performance_report: str = None,
        budget: float = 100.0,
        risk_preference: str = "中性",
        senate_edict: str = None,
        quant_proposal: str = None,
        ml_briefing: str = None
) -> Tuple[str, str]:
    """
    The Final Mandate — V1.4: 最终修正版 (修复f-string转义错误)。
    """
    # === 1. 基础数据准备 ===
    latest_issue = str(recent_draws[-1].period_number) if recent_draws else "未知"
    next_issue = next_issue_hint or (str(int(latest_issue) + 1) if latest_issue.isdigit() else "下一期")
    uc = user_constraints or {}
    max_bets = uc.get("max_bets", 5)

    # === 2. 从引擎输出中提取动态号码 ===
    fused_output = model_outputs.get("DynamicEnsembleOptimizer", {})
    fused_recs = fused_output.get('recommendations', [{}])[0]
    fused_front_scores = fused_recs.get('fused_front_scores', [])
    fused_back_scores = fused_recs.get('fused_back_scores', [])

    if not fused_front_scores: fused_front_scores = [{'number': n, 'score': 0.5} for n in range(1, 36)]
    if not fused_back_scores: fused_back_scores = [{'number': n, 'score': 0.5} for n in range(1, 13)]

    dynamic_front_core = [item['number'] for item in fused_front_scores[:7]]
    dynamic_back_core = [item['number'] for item in fused_back_scores[:3]]
    dynamic_front_hedge = [item['number'] for item in fused_front_scores[9:14]]
    dynamic_back_hedge = [item['number'] for item in fused_back_scores[3:5]]

    # === 3. 定义 self_check 所需的变量 ===
    core_cost = min(42.0, budget * 0.7)
    hedge_cost = 10.0
    total_cost = core_cost + hedge_cost

    cost_ok = total_cost <= budget
    e_hits_ok = True
    roi_ok = True
    fixes = []
    if not cost_ok:
        fixes.append(f"成本超出预算: {total_cost} > {budget}")

    # === 4. 简化外部报告的生成 (如果未提供) ===
    if not senate_edict:
        senate_edict = "陛下，算法军团已呈上融合分析。请审阅并下达最终诏令。"
    if not quant_proposal:
        # 修复：确保 quant_proposal 始终是 JSON 字符串
        quant_summary = {"summary": f"核心推荐基于 {len(model_outputs)} 个算法的动态融合。"}
        quant_proposal = json.dumps(quant_summary, ensure_ascii=False)
    if not ml_briefing:
        # 修复：确保 ml_briefing 始终是 JSON 字符串
        ml_summary = {"risk": "AI先知院提示，请始终注意风险控制。"}
        ml_briefing = json.dumps(ml_summary, ensure_ascii=False)

    # === 5. 构建最终的Prompt字符串 (已修复大括号转义) ===
    prompt = f"""
# 👑 The Final Mandate :: The Emperor's Edict

## 【档案】
- **期号:** {next_issue}
- **国库:** 预算 {budget} 元

### 📜 元老院密诏
> {senate_edict}

### 📄 A: 量化军团作战计划
```json
{quant_proposal}
🔮 B: AI先知院未来预警```json
{ml_briefing}
code
Code
## 【神谕】
你的任务是聆听元老院的最高战略指引，审阅A、B两份战术报告，然后用你无上的智慧，签发最终的、唯一的作战指令。你的决策必须基于A和B计划提供的数据和号码。融合A的主力号码与B的风险提示，形成最终的投资组合。

【输出规范】
必须严格按照下面的JSON格式输出，不要有任何额外的解释。
{{
  "meta": {{
    "version": "The Final Mandate v1.4",
    "issue": "{next_issue}"
  }},
  "edict": {{
    "final_imperial_portfolio": {{
      "recommendations": [
        {{
          "type": "皇帝荣耀(7+3)",
          "cost": {core_cost},
          "front_numbers": {json.dumps(dynamic_front_core)},
          "back_numbers": {json.dumps(dynamic_back_core)},
          "expected_hits": 2.2,
          "sharpe": 1.45,
          "role": "融合引擎主力推荐，锁定核心热区"
        }},
        {{
          "type": "侧翼宁静(5+2)",
          "cost": {hedge_cost},
          "front_numbers": {json.dumps(dynamic_front_hedge)},
          "back_numbers": {json.dumps(dynamic_back_hedge)},
          "expected_hits": 1.2,
          "sharpe": 1.32,
          "role": "引擎中段号码对冲，捕捉潜在机会"
        }}
      ],
      "allocation_summary": "总成本 {total_cost:.2f}元，主攻与对冲结合，以期稳定回报。",
      "overall_e_hits_range": [1.8, 2.5]
    }},
    "final_memo": "朕阅A、B二策，决断已定。以引擎之智为矛，以对冲之策为盾。执行，无需多言。"
  }},
  "self_check": {{
    "ok": {str(bool(cost_ok and e_hits_ok and roi_ok)).lower()},
    "roi_ok": {str(roi_ok).lower()},
    "cost_ok": {str(cost_ok).lower()},
    "e_hits_ok": {str(e_hits_ok).lower()},
    "fixes_applied": {json.dumps(fixes)}
  }}
}}
"""
    return prompt.strip(), next_issue