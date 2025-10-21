# config/logging_config.py
import logging
import os

class LoggingConfig:
    """日志配置类"""

    @staticmethod
    def setup_logging(log_file: str = "logs/lottery_system.log",
                     log_level: str = "INFO"):
        """设置日志配置"""
        # 创建日志目录
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 配置日志格式
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        return logging.getLogger(__name__)
