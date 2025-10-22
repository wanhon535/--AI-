# prediction.py
import mysql.connector
from datetime import datetime, timedelta
import json
import random

def predict_next_lottery():
    """预测下一期彩票号码"""

    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'port': 3307,
        'user': 'root',
        'password': 'root',
        'database': 'lottery_analysis_system',
        'charset': 'utf8mb4'
    }

    try:
        # 连接数据库
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # 获取最新的开奖记录
        cursor.execute("""
            SELECT period_number FROM lottery_history 
            ORDER BY period_number DESC 
            LIMIT 1
        """)

        latest_period = cursor.fetchone()

        if not latest_period:
            print("没有找到历史开奖记录")
            return

        current_period = latest_period[0]

        # 计算下一期期号
        next_period_number = str(int(current_period) + 1)

        # 模拟预测算法（这里使用简单的随机生成作为示例）
        front_numbers = sorted(random.sample(range(1, 36), 5))
        back_numbers = sorted(random.sample(range(1, 13), 2))

        # 根据您提供的格式构建推荐数据
        recommendation_data = {
            "stage_one": {
                "style_summary": "高跨度分散型，中高和值偏好"
            },
            "stage_two": {
                "strongest_pattern": "连号模式",
                "historical_percentage": "15%",
                "high_potential_pool": [6, 10, 12, 15, 21, 22, 25, 28, 30]
            },
            "stage_three": [
                {
                    "recommendation_type": "热号主攻",
                    "strategy_logic": "遵循最强模式 + 热号",
                    "front_numbers": [6, 10, 12, 21, 22],
                    "back_numbers": [1, 6],
                    "win_rate": "18%"
                },
                {
                    "recommendation_type": "冷号回补",
                    "strategy_logic": "模式+冷号突破",
                    "front_numbers": [15, 25, 28, 30, 33],
                    "back_numbers": [2, 8],
                    "win_rate": "15%"
                },
                {
                    "recommendation_type": "复式 (6+3)",
                    "strategy_logic": "遵循风格 + 最强模式强化",
                    "front_numbers": [6, 10, 12, 15, 21, 22],
                    "back_numbers": [1, 6, 8],
                    "win_rate": "22%"
                },
                {
                    "recommendation_type": "复式 (8+3)",
                    "strategy_logic": "综合高潜力池全覆盖",
                    "front_numbers": [6, 10, 12, 15, 21, 22, 25, 28],
                    "back_numbers": [1, 6, 8],
                    "win_rate": "25%"
                }
            ]
        }

        # 构建推荐组合
        recommendation_combinations = [
            {
                "front_numbers": front_numbers,
                "back_numbers": back_numbers,
                "confidence": 0.75,
                "analysis_basis": "基于历史数据分析"
            }
        ]

        # 生成推荐参数
        algorithm_parameters = {
            "prediction_method": "statistical_analysis",
            "data_range": "last_100_periods",
            "weighting_factors": {
                "frequency": 0.3,
                "hot_cold": 0.2,
                "pattern_recognition": 0.25,
                "trend_analysis": 0.25
            }
        }

        # 生成模型权重
        model_weights = {
            "statistical_model": 0.4,
            "ml_model": 0.3,
            "ensemble_model": 0.3
        }

        # 生成分析依据
        analysis_basis = {
            "recent_trends": "最近出现频率较高的号码",
            "hot_numbers": [6, 10, 12],
            "cold_numbers": [25, 30, 33],
            "patterns_detected": ["连号", "奇偶平衡"]
        }

        # 生成关键模式识别
        key_patterns = [
            {"type": "consecutive", "numbers": [12, 13], "confidence": 0.6},
            {"type": "odd_even_balance", "ratio": "3:2", "confidence": 0.7}
        ]

        # 插入推荐记录
        insert_query = """
        INSERT INTO algorithm_recommendation (
            period_number, recommend_time, algorithm_version,
            recommendation_combinations, algorithm_parameters,
            model_weights, confidence_score, risk_level,
            analysis_basis, key_patterns, recommend_type
        ) VALUES (
            %s, %s, %s,
            %s, %s,
            %s, %s, %s,
            %s, %s, %s
        )
        """

        cursor.execute(insert_query, (
            next_period_number,
            datetime.now(),
            "v3.0-ensemble",
            json.dumps(recommendation_data),
            json.dumps(algorithm_parameters),
            json.dumps(model_weights),
            0.75,
            "medium",
            json.dumps(analysis_basis),
            json.dumps(key_patterns),
            "primary"
        ))

        # 提交事务
        connection.commit()
        print(f"成功预测并插入期号 {next_period_number} 的推荐数据")

    except Exception as e:
        print(f"预测或插入数据时出错: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    predict_next_lottery()
