# src/algorithms/tripartite_meta_predictor.py

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# --- Core Component Imports (no changes) ---
from src.database.database_manager import DatabaseManager
from src.llm.llm_call_service import LLMCallService
from src.prompt_templates import (
    build_strategy_A_prompt, build_strategy_B_prompt, build_final_allocation_prompt
)
from src.model.lottery_models import LotteryHistory
from src.algorithms.dynamic_ensemble_optimizer import DynamicEnsembleOptimizer
from src.config.database_config import DB_CONFIG


class TripartiteMetaPredictor:
    """
    [V7 - Definitive Fix]
    - Corrects the "Data too long for column 'risk_level'" error.
    - Ensures all data correctly fits the database schema.
    """

    def __init__(self, db_config: Dict[str, Any]):
        self.db_manager = DatabaseManager(**db_config)
        self.ensemble_predictor = DynamicEnsembleOptimizer()
        self.name = "TripartiteMetaPredictor"
        self.version = "V18.0_SchemaCompliant"

    def _run_local_algorithms(self, history: List[LotteryHistory]) -> Dict[str, Any]:
        print("\n--- [HELPER] Running local algorithm integrator ---")
        try:
            self.ensemble_predictor.train(history)
            return self.ensemble_predictor.predict(history)
        except Exception as e:
            return {"error": str(e)}

    def _save_intermediate_strategy(self, data: Dict[str, Any], stage_name: str, llm_service: LLMCallService) -> bool:
        """Saves intermediate results for stages A and B."""
        print(f"  [DB] Saving intermediate result for {stage_name}...")
        model_full_name = f"{llm_service.model_name}_{stage_name}"
        meta_data = {
            'period_number': data.get("issue"), 'recommend_time': datetime.now(),
            'algorithm_version': self.version, 'confidence_score': 0.5,
            'risk_level': 'Analysis',  # This is a safe, short value
            'llm_cognitive_details': json.dumps(data, ensure_ascii=False),
            'models': model_full_name
        }
        rows = self.db_manager.insert_algorithm_recommendation_root(**meta_data)
        return rows and rows > 0

    def _save_final_mandate_with_details(self, data: Dict[str, Any], llm_service: LLMCallService) -> bool:
        """Saves the final Stage C master record AND links all detail records."""
        print(f"  [DB] Saving final mandate and linking details...")
        model_full_name = f"{llm_service.model_name}_Strategy_C"

        # --- THIS IS THE CRITICAL FIX ---
        # Instead of the long 'commander_ruling', we use a short, descriptive status.
        # The full details are already being saved in 'llm_cognitive_details'.
        risk_level_status = "Portfolio-VC-Model"
        # --------------------------------

        meta_data = {
            'period_number': data.get("issue"), 'recommend_time': datetime.now(),
            'algorithm_version': self.version, 'confidence_score': 0.98,
            'risk_level': risk_level_status,  # Use the safe, short value here
            'llm_cognitive_details': json.dumps(data, ensure_ascii=False),
            'models': model_full_name
        }

        rows_master = self.db_manager.insert_algorithm_recommendation_root(**meta_data)
        if not (rows_master and rows_master > 0):
            # If this fails, the error will now be logged from the DatabaseManager
            raise RuntimeError("Failed to save final mandate master record. Check DB logs for details.")

        recommendation_id = self.db_manager.get_last_insert_id()
        if not recommendation_id:
            raise RuntimeError("Failed to retrieve ID after saving final mandate.")

        print(f"  [DB] ✅ Saved final master record (ID: {recommendation_id}). Now linking details...")

        final_portfolio = data.get('final_portfolio', {})
        combos = []
        if isinstance(final_portfolio, dict):
            for key, value in final_portfolio.items():
                if isinstance(value, list):
                    combos.extend(value)
                elif isinstance(value, dict):
                    combos.append(value)

        if not combos: return True

        details_to_insert = [
            {
                "recommend_type": rec.get('combo_name'), "strategy_logic": rec.get('strategy_focus'),
                "front_numbers": ','.join(map(str, rec.get('front_numbers', []))),
                "back_numbers": ','.join(map(str, rec.get('back_numbers', []))),
                "win_probability": 0.0
            } for rec in combos if isinstance(rec, dict)
        ]

        return self.db_manager.insert_recommendation_details_batch(root_id=recommendation_id,
                                                                   details_list=details_to_insert)

    def generate_prediction(self, model_name: str) -> Optional[Dict[str, Any]]:
        """The main API-callable workflow function."""
        # ... The rest of this function remains unchanged as its logic is now correct ...
        print(f"\n{'=' * 20} Orchestrator Started for Model: {model_name} {'=' * 20}")
        llm_service = LLMCallService(model_name)

        if not self.db_manager.connect():
            return {"status": "error", "message": "Database connection failed."}

        try:
            next_issue = self.db_manager.get_next_period_number()
            print(f"[ORCHESTRATOR] Target Period: {next_issue}")

            final_model_identifier = f"{model_name}_Strategy_C"
            existing_final_record = self.db_manager.get_recommendation_by_period_and_model(next_issue,
                                                                                           final_model_identifier)
            if existing_final_record:
                print(f"  [ORCHESTRATOR] ✅ Complete result already exists. Operation finished.")
                return json.loads(existing_final_record['llm_cognitive_details'])

            print(f"  [ORCHESTRATOR] Cleaning up any partial results for '{model_name}'...")
            self.db_manager.delete_recommendations_by_period_and_model_base(next_issue, model_name)

            historical_data = self.db_manager.get_all_lottery_history(limit=200)
            ensemble_output = self._run_local_algorithms(historical_data)
            if 'error' in ensemble_output: raise RuntimeError("Local algorithm execution failed.")

            # Stage A
            print("\n--- Stage A: Generating & Saving ---")
            context_A = {'ensemble_output': ensemble_output, 'recent_draws': historical_data,
                         'next_issue_hint': next_issue}
            strategy_A_data = llm_service.execute_strategy(build_strategy_A_prompt, context_A)
            if not strategy_A_data or not self._save_intermediate_strategy(strategy_A_data, "Strategy_A", llm_service):
                raise RuntimeError("Stage A failed: Could not generate or save intermediate data.")

            # Stage B
            print("\n--- Stage B: Generating & Saving ---")
            context_B = {'recent_draws': historical_data, 'next_issue_hint': next_issue}
            strategy_B_data = llm_service.execute_strategy(build_strategy_B_prompt, context_B)
            if not strategy_B_data or not self._save_intermediate_strategy(strategy_B_data, "Strategy_B", llm_service):
                raise RuntimeError("Stage B failed: Could not generate or save intermediate data.")

            # Stage C
            print("\n--- Stage C: Generating Final Ruling & Saving with Details ---")
            context_C = {
                'strategy_A_json': json.dumps(strategy_A_data, ensure_ascii=False, indent=2),
                'strategy_B_json': json.dumps(strategy_B_data, ensure_ascii=False, indent=2),
                'next_issue_hint': next_issue
            }
            final_data = llm_service.execute_strategy(build_final_allocation_prompt, context_C)
            if not final_data: raise RuntimeError("Stage C failed to generate final data.")

            if not self._save_final_mandate_with_details(final_data, llm_service):
                raise RuntimeError("Failed to save final mandate with details.")

            print(f"\n--- ✅ Workflow Succeeded for {model_name} ---")
            return final_data

        except Exception as e:
            print(f"\n[ORCHESTRATOR] ❌ WORKFLOW FAILED for model '{model_name}': {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self.db_manager.disconnect()
            print("[ORCHESTRATOR] Workflow finished.")


# ==============================================================================
# --- API Simulation Block (no changes needed) ---
# ==============================================================================
if __name__ == "__main__":
    # qwen-plus-2025-09-11 qwen3-max gemini-2.5-flash gpt-4o deepseek-chat deepseek-v3.1 qwen3-max-2025-09-23 qwen-flash-2025-07-28
    model_to_run = "gpt-4o"  # qwen-plus-2025-09-11Change this to test different models
    print(f"\n{'=' * 25} API Call Simulation {'=' * 25}")
    print(f"Simulating request to generate prediction for model: '{model_to_run}'")
    try:
        predictor = TripartiteMetaPredictor(db_config=DB_CONFIG)
        final_result = predictor.generate_prediction(model_name=model_to_run)
        print("\n\n=============== Simulated API Response ===============")
        if final_result:
            print(json.dumps(final_result, indent=4, ensure_ascii=False))
        else:
            print({"status": "error", "message": "The orchestrator did not return a final result."})
        print("=" * 54)
    except Exception as e:
        print(f"\n❌ A critical error occurred during the API simulation: {e}")
        import traceback

        traceback.print_exc()