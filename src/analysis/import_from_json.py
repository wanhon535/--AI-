# file: import_from_json.py

import json
import os
import sys
import traceback

# --- 1. Environment Setup ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 2. Imports ---
from src.database.database_manager import DatabaseManager
from src.database.crud.lottery_history_dao import LotteryHistoryDAO
from src.model.lottery_models import LotteryHistory

# --- 3. Configuration ---
JSON_DATA_FILENAME = "dlt_history_data.json"
DB_CONFIG = dict(
    host='127.0.0.1', user='root', password='123456789',
    database='lottery_analysis_system', port=3309
)


def calculate_consecutive_details(numbers: list[int]) -> tuple[list, int]:
    """
    A helper function to calculate consecutive numbers and their count from a sorted list.
    """
    if not numbers:
        return [], 0

    consecutive_numbers = []
    sorted_numbers = sorted(numbers)

    for i in range(len(sorted_numbers) - 1):
        if sorted_numbers[i + 1] - sorted_numbers[i] == 1:
            consecutive_numbers.extend([sorted_numbers[i], sorted_numbers[i + 1]])

    # Remove duplicates and sort
    unique_consecutive = sorted(list(set(consecutive_numbers)))
    count = len(unique_consecutive)

    return unique_consecutive, count


def import_json_to_database():
    """
    Reads the dlt_history_data.json file and inserts all new records into the database.
    """
    print("🚀 Starting JSON to Database Importer...")

    # --- Step 1: Load JSON file ---
    if not os.path.exists(JSON_DATA_FILENAME):
        print(f"❌ Error: JSON file not found at '{JSON_DATA_FILENAME}'.")
        print("   Please run your 'manager.py' or 'database_importer.py' first to generate the file.")
        return

    with open(JSON_DATA_FILENAME, 'r', encoding='utf-8') as f:
        try:
            json_data = json.load(f)
            print(f"✅ Successfully loaded {len(json_data)} records from '{JSON_DATA_FILENAME}'.")
        except json.JSONDecodeError as e:
            print(f"❌ Error: Could not parse JSON file. It might be corrupted. Details: {e}")
            return

    # --- Step 2: Connect to Database and prepare for import ---
    db = DatabaseManager(**DB_CONFIG)
    if not db.connect():
        print("❌ Database connection failed. Aborting import.")
        return

    history_dao = LotteryHistoryDAO(db)

    try:
        # --- Step 3: Get existing data to avoid duplicates ---
        print("🔎 Fetching existing period numbers from the database to prevent duplicates...")
        existing_periods = history_dao.get_all_period_numbers()
        print(f"   - Found {len(existing_periods)} existing records in the database.")

        # --- Step 4: Iterate and Insert New Records ---
        new_records_count = 0
        skipped_count = 0

        print("\n🔄 Processing records and inserting new ones...")
        for item in json_data:
            period_number = item.get('expect')
            if not period_number:
                print(f"  - 🟡 Skipping a record due to missing 'expect' field: {item}")
                continue

            if period_number in existing_periods:
                skipped_count += 1
                continue

            # This is a new record, let's process and insert it
            try:
                front_area = item.get('frontArea', [])
                consecutive_nums, consecutive_count = calculate_consecutive_details(front_area)

                lottery_record = LotteryHistory(
                    period_number=period_number,
                    draw_date=item.get('time', '1970-01-01 00:00:00').split(' ')[0],
                    draw_time=item.get('time', '1970-01-01 00:00:00').split(' ')[1],
                    front_area=front_area,
                    back_area=item.get('backArea', []),
                    sum_value=item.get('frontArea_Sum', 0),
                    span_value=item.get('frontArea_Span', 0),
                    odd_even_ratio=item.get('frontArea_OddEven', '0:0'),
                    consecutive_numbers=consecutive_nums,
                    consecutive_count=consecutive_count,
                    data_source="json_import",
                    data_quality="processed",
                    # Fill other fields with defaults if not present in JSON
                    ac_value=item.get('ac_value', 0),
                    size_ratio=item.get('size_ratio', ''),
                    prime_composite_ratio=item.get('prime_composite_ratio', ''),
                    tail_numbers=item.get('tail_numbers', [])
                )

                if history_dao.insert_lottery_history(lottery_record):
                    print(f"  - ✅ Inserted new record for period: {period_number}")
                    new_records_count += 1
                else:
                    print(f"  - 🔴 DAO failed to insert record for period: {period_number}")

            except Exception as e:
                print(f"  - 🔴 Error processing or inserting record for period {period_number}: {e}")
                traceback.print_exc()

        # --- Step 5: Final Report ---
        print("\n" + "=" * 50)
        print("📊 Import Summary:")
        print(f"   - Total records in JSON file: {len(json_data)}")
        print(f"   - Records already in database (skipped): {skipped_count}")
        print(f"   - New records successfully inserted: {new_records_count}")
        print("=" * 50)

    finally:
        db.disconnect()
        print("\n🔌 Database connection closed. Import process finished.")


if __name__ == "__main__":
    # You need to ensure your LotteryHistoryDAO has the `get_all_period_numbers` method.
    # If not, add this to your `src/database/crud/lottery_history_dao.py`:
    #
    # def get_all_period_numbers(self) -> set:
    #     """获取数据库中所有已存在的期号集合，用于快速去重检查。"""
    #     query = "SELECT period_number FROM lottery_history"
    #     rows = self.execute_query(query)
    #     return {str(r['period_number']) for r in rows}

    import_json_to_database()