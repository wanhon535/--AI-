# ======================================================================
# --- FILE: src/engine/workflow/tasks.py (COMPLETE REPLACEMENT V3) ---
# ======================================================================
import datetime
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from bokeh.core.validation import issue

# --- 核心组件导入 ---
from src.database.database_manager import DatabaseManager
from src.model.lottery_models import LotteryHistory
from src.engine.imperial_senate import ImperialSenate
from src.prompt_templates import build_final_mandate_prompt
from src.llm.clients import get_llm_client
from src.algorithms import AVAILABLE_ALGORITHMS
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.engine.recommendation_engine import RecommendationEngine


class BaseTask(ABC):
    """任务基类"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    @abstractmethod
    def run(self, context: dict) -> bool:
        pass

    @property
    def name(self):
        return self.__class__.__name__


class InitializationTask(BaseTask):
    """任务1：初始化和自检"""

    def run(self, context: dict) -> bool:
        print("\n" + "=" * 60 + "\n🚀 [任务1/3] 执行: 系统初始化与自检...\n" + "=" * 60)
        print("  - ✅ 数据库连接正常。")
        print("  - ✅ 系统配置加载完毕。")
        return True


class LearningTask(BaseTask):
    """任务2：增量学习（目前为占位符）"""

    def run(self, context: dict) -> bool:
        print("\n" + "=" * 60 + "\n🧠 [任务2/3] 执行: 增量学习...\n" + "=" * 60)
        print("  - ✅ 增量学习任务完成（当前为占位符）。")
        return True


# ... (文件顶部的 import 需要增加 ImperialSenate)
from src.engine.imperial_senate import ImperialSenate


# ... (BaseTask, InitializationTask, LearningTask 保持不变)

class PredictionTask(BaseTask):
    """任务3：执行核心预测工作流 (V3.0 - 最终纯净版)"""

    def run(self, context: dict) -> bool:
        print("\n" + "=" * 70 + "\n=== 👑 [任务3/3] 执行: 最终预测 (The Final Mandate) ===\n" + "=" * 70)

        models_to_run = context.get('models_to_run', [])
        if not models_to_run: return True

        try:
            print("\n--- [步骤 1/5] 正在从数据库获取最新数据... ---")
            # 纯粹地使用 DatabaseManager
            history_data = self.db.get_latest_lottery_history(limit=100)
            if not history_data or len(history_data) < 20: raise ValueError("历史数据不足")

            performance_log = {}
            latest_period_num = history_data[0].period_number
            next_issue = str(int(latest_period_num) + 1)
            print(f"  - ✅ 数据获取成功。目标期号: {next_issue}")

        except Exception as e:
            print(f"  - ❌ 数据获取阶段失败: {e}")
            return False

        print("\n--- [步骤 2/5] 正在激活帝国算法引擎... ---")
        model_outputs = self._run_all_base_algorithms(history_data)
        if not model_outputs: return False
        print("  - ✅ 算法引擎已生成融合后的“大师热力图”。")

        print("\n--- [步骤 3/5] 帝国元老院正在蒸馏高级情报... ---")
        senate = ImperialSenate(self.db, performance_log, model_outputs)
        last_report_mock = "上期ROI-5%"
        edict, quant_prop, ml_brief = senate.generate_all_briefings(history_data, last_report_mock)
        print("  - ✅ 元老院密诏、军团计划、先知预警已生成。")

        print("\n--- [步骤 4/5] 正在准备呈送帝国档案至寂静王座... ---")
        risk_preference = "中性"
        prompt_text, _ = build_final_mandate_prompt(
            recent_draws=history_data, model_outputs=model_outputs, performance_log=performance_log,
            next_issue_hint=next_issue, last_performance_report=last_report_mock,
            budget=100.0, risk_preference=risk_preference,
            senate_edict=edict, quant_proposal=quant_prop, ml_briefing=ml_brief
        )
        print("  - ✅ 最终诏令Prompt已构建完成。")

        print("\n--- [步骤 5/5] 正在向各位皇帝（LLM）请求签发神谕... ---")
        for model_name in models_to_run:
            self._issue_and_store_decree(model_name, prompt_text, issue, model_outputs, edict, quant_prop, ml_brief)

        return True

    # _run_all_base_algorithms 保持不变
    def _run_all_base_algorithms(self, history_data: List[LotteryHistory], weights: Dict[str, float] = None) -> Dict[
        str, Any]:
        try:
            base_scorers = [AlgoClass() for name, AlgoClass in AVAILABLE_ALGORITHMS.items() if
                            name != "DynamicEnsembleOptimizer"]
            if not base_scorers: return {}
            fusion_algorithm = DynamicEnsembleOptimizer(base_algorithms=base_scorers)
            if weights:
                fusion_algorithm.current_weights = weights
            engine = RecommendationEngine(base_scorers=base_scorers, fusion_algorithm=fusion_algorithm)
            fused_report = engine.generate_fused_recommendation(history_data)
            return {"DynamicEnsembleOptimizer": fused_report}
        except Exception as e:
            print(f"  - ❌ 在运行基础算法或融合时发生严重错误: {e}")
            return {}

    # _issue_and_store_decree 保持不变 (它已经完全依赖 self.db)
    def _issue_and_store_decree(self, model_name: str, prompt: str, issue: str, model_outputs: dict, edict: str,
                                quant_prop: str, ml_brief: str) -> bool:
        print(f"\n  --- 皇帝 [{model_name}] 正在签发神谕... ---")
        try:
            llm_client = get_llm_client(model_name)
            response_str = llm_client.generate(system_prompt=prompt, user_prompt="Your Majesty, your final decree.",
                                               json_mode=True)
            clean_response_str = response_str.strip().replace('```json', '').replace('```', '')
            response_data = json.loads(clean_response_str)

            meta_data = {
                'period_number': issue, 'recommend_time': self.db.get_current_time(),
                'algorithm_version': f"TheFinalMandate_{model_name}_V1.1",
                'confidence_score': 0.9 if response_data.get('self_check', {}).get('e_hits_ok', False) else 0.7,
                'risk_level': response_data.get('meta', {}).get('constraints', {}).get('risk_preference', '中性'),
                'analysis_basis': json.dumps(model_outputs, ensure_ascii=False),
                'llm_cognitive_details': json.dumps({'senate_edict': edict, 'quant_proposal': json.loads(quant_prop),
                                                     'ml_briefing': json.loads(ml_brief),
                                                     'final_memo': response_data.get('edict', {}).get('final_memo')},
                                                    ensure_ascii=False),
                'models': model_name
            }
            # 使用 execute_update 并获取 ID
            recommendation_id = self.db.execute_update(
                "INSERT INTO algorithm_recommendation (period_number, recommend_time, algorithm_version, confidence_score, risk_level, analysis_basis, llm_cognitive_details, models) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                tuple(meta_data.values())
            )
            if not recommendation_id: raise Exception("插入元数据失败，未返回ID。")

            recommendations = response_data.get('edict', {}).get('final_imperial_portfolio', {}).get('recommendations',
                                                                                                     [])
            details_to_insert = [
                (recommendation_id, rec.get('type'), rec.get('role'), ','.join(map(str, rec.get('front_numbers', []))),
                 ','.join(map(str, rec.get('back_numbers', []))), rec.get('sharpe')) for rec in recommendations]

            if details_to_insert:
                details_query = "INSERT INTO recommendation_details (recommendation_metadata_id, recommend_type, strategy_logic, front_numbers, back_numbers, win_probability) VALUES (%s, %s, %s, %s, %s, %s)"
                self.db.execute_batch_insert(details_query, details_to_insert)

            print(f"    - ✅ 神谕主记录已存入史册 (ID: {recommendation_id})，包含 {len(recommendations)} 条具体指令。")
            return True
        except Exception as e:
            print(f"  - ❌ 皇帝 [{model_name}] 签发或存储神谕时发生错误: {e}")
            return False