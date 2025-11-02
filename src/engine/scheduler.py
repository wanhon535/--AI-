
# 文件: src/engine/scheduler.py (最终净化版)

from typing import List
from src.database.database_manager import DatabaseManager
from src.utils.logger import log_system_event
from src.engine.workflow.tasks import InitializationTask, LearningTask, PredictionTask


class Scheduler:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.workflow: List = []
        self.context = {}

    def setup_daily_workflow(self, models_to_run: List[str]):
        """配置一个最简化的每日工作流。"""
        # 将所有必要的依赖项放入初始 context
        self.context = {
            'db_manager': self.db,
            'models_to_run': models_to_run
        }
        self.workflow = [
            InitializationTask(self.db),
            LearningTask(self.db),
            PredictionTask(self.db)  # PredictionTask 自己处理 models_to_run
        ]
        print("✅ 每日标准工作流已配置完毕。")

    def run(self):
        """按顺序执行工作流中的所有任务。"""
        if not self.workflow:
            print("❌ 错误: 工作流为空，无法执行。")
            return

        print("\n" + "#" * 70 + "\n###         🚀 工作流调度器启动执行         ###\n" + "#" * 70)

        # 依次执行任务，传递context
        for task in self.workflow:
            try:
                # 任务的成功与否现在由任务自身决定
                if not task.run(self.context):
                    print(f"  - ⚠️ 任务 '{task.name}' 执行失败或返回False，工作流终止。")
                    log_system_event(self.db, 'system', 'TASK_FAILURE', 'FAILURE', {'task_name': task.name})
                    break  # 如果一个任务失败，可以选择终止整个流程
            except Exception as e:
                print(f"  - ❌ 任务 '{task.name}' 执行时发生严重错误: {e}")
                import traceback
                traceback.print_exc()
                log_system_event(self.db, 'system', 'TASK_FATAL_ERROR', 'FAILURE',
                                 {'task_name': task.name, 'error': str(e)})
                break  # 发生严重错误也终止

        print("\n" + "#" * 70 + "\n###         🏁 所有工作流任务执行完毕         ###\n" + "#" * 70)
        log_system_event(self.db, 'system', 'WORKFLOW_COMPLETE', 'SUCCESS', {'workflow_name': 'daily'})