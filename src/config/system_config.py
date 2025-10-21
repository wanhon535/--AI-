# config/system_config.py
class SystemConfig:
    """系统配置类"""
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/lottery_system.log"

    # 数据更新配置
    DATA_UPDATE_INTERVAL = 3600  # 1小时更新一次数据

    # 算法权重配置
    DEFAULT_ALGORITHM_WEIGHTS = {
        "frequency_analysis": 0.3,
        "hot_cold_number": 0.25,
        "omission_value": 0.2,
        "time_series": 0.15,
        "association_rules": 0.1
    }

    # 推荐配置
    RECOMMENDATION_COUNT = 5  # 默认推荐组合数

    # A/B测试配置
    AB_TEST_MIN_SAMPLE = 100
    AB_TEST_SIGNIFICANCE = 0.95
