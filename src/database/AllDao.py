import mysql.connector
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class AllDAO:
    """基础数据访问对象类"""

    def __init__(self, connection_config):
        if hasattr(connection_config, "get_config"):
            # 如果传入 DatabaseManager，就自动取出配置字典
            self.connection_config = connection_config.get_config()
        elif isinstance(connection_config, dict):
            self.connection_config = connection_config
        else:
            raise TypeError(f"无效的数据库配置类型: {type(connection_config)}")

        self.connection: Optional[mysql.connector.MySQLConnection] = None

    def connect(self) -> bool:
        """建立数据库连接"""
        try:
            if not self.is_connected():
                self.connection = mysql.connector.connect(**self.connection_config)
                self._connected = True
            return True
        except mysql.connector.Error as e:
            print(f"数据库连接失败: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self._connected = False

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询语句"""
        if not self.connect(): return []
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"查询执行失败: {e}")
            return []

    def execute_update(self, query: str, params: tuple = None) -> Optional[int]:
        """执行更新/插入语句，返回影响的行数或最后插入的ID"""
        if not self.connect(): return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                # 如果是INSERT，lastrowid是新ID；如果是UPDATE，rowcount是影响行数
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        except mysql.connector.Error as e:
            print(f"更新/插入执行失败: {e}")
            if self.connection: self.connection.rollback()
            return None

    def execute_many(self, query: str, params_list: List[tuple]) -> Optional[int]:
        """批量执行更新语句"""
        if not self.connect(): return None
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(query, params_list)
                self.connection.commit()
                return cursor.rowcount
        except mysql.connector.Error as e:
            print(f"批量更新执行失败: {e}")
            if self.connection: self.connection.rollback()
            return None

    def get_last_insert_id(self, cursor) -> Optional[int]:
        """获取指定游标的最后插入ID"""
        return cursor.lastrowid

    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.connection and self.connection.is_connected()