# config/database_config.py
class DatabaseConfig:
    """数据库配置类"""
    HOST = "127.0.0.1"
    PORT = 3309
    USER = "root"
    PASSWORD = "123456789"
    DATABASE = "lottery_analysis_system"
    CHARSET = "utf8mb4"

    @classmethod
    def get_config(cls):
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': cls.DATABASE,
            'charset': cls.CHARSET
        }
