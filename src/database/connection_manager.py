# src/database/connection_manager.py
from typing import Dict, Any
from .AllDao import AllDAO


class DatabaseConnectionManager:
    """数据库连接管理器"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    # def __init__(self, host: str, user: str, password: str, database: str, port: int = 3309):
    #     if not hasattr(self, '_initialized'):
    #         self.connection_config = {
    #             'host': host,
    #             'user': user,
    #             'password': password,
    #             'database': database,
    #             'port': port,
    #             'charset': 'utf8mb4'
    #         }
    #         self._daos = {}
    #         self._initialized = True
    def __init__(self, **connection_kwargs: Any):
        """
        (V2 - 升级版)
        直接接收所有数据库连接参数。
        """
        if not hasattr(self, '_initialized'):
            # 直接将所有传入的参数作为连接配置
            self.connection_config = connection_kwargs
            self._daos = {}
            self._initialized = True

    def get_dao(self, dao_class) -> AllDAO:
        """获取DAO实例"""
        if dao_class not in self._daos:
            self._daos[dao_class] = dao_class(self.connection_config)
            # 建立连接
            self._daos[dao_class].connect()
        return self._daos[dao_class]

    def disconnect_all(self):
        """断开所有DAO的连接"""
        for dao in self._daos.values():
            dao.disconnect()
        self._daos.clear()