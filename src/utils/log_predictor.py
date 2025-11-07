# src/utils/log_predictor.py
import json
from functools import wraps
from datetime import datetime
from src.database.database_manager import DatabaseManager
from src.config.database_config import DB_CONFIG


def log_prediction(func):
    """
    This is our "Universal Listener" decorator.
    It intercepts the output of any 'predict' method it wraps,
    logs the result to the database, and then returns the original result.
    """

    @wraps(func)
    def wrapper(self, history_data, *args, **kwargs):
        # 1. Execute the original predict function to get the result
        prediction_result = func(self, history_data, *args, **kwargs)

        # 2. If the prediction was successful, log it
        if prediction_result and 'error' not in prediction_result:
            try:
                # Determine the next period for the log entry
                next_period = "UNKNOWN"
                if history_data:
                    try:
                        next_period = str(int(history_data[-1].period_number) + 1)
                    except (ValueError, IndexError):
                        pass

                log_entry = {
                    "period_number": next_period,
                    "algorithm_version": f"{self.name}_{self.version}",
                    "predictions": prediction_result,
                    "confidence_score": prediction_result.get('recommendations', [{}])[0].get('confidence', 0.5)
                }

                # Use a temporary DB manager instance for logging
                # This is robust for use anywhere in the system
                db_manager = DatabaseManager(**DB_CONFIG)
                if db_manager.connect():
                    query = """
                        INSERT INTO algorithm_prediction_logs 
                        (period_number, algorithm_version, predictions, confidence_score, created_at) 
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    params = (
                        log_entry['period_number'],
                        log_entry['algorithm_version'],
                        json.dumps(log_entry['predictions'], ensure_ascii=False),
                        log_entry['confidence_score'],
                        datetime.now()
                    )
                    db_manager.execute_update(query, params)
                    print(f"  [LOG LISTENER] ✅ Successfully logged prediction for '{log_entry['algorithm_version']}'.")
            except Exception as e:
                print(f"  [LOG LISTENER] ❌ ERROR: Failed to log prediction for '{self.name}': {e}")

        # 3. Return the original result, so the rest of the program works as normal
        return prediction_result

    return wrapper