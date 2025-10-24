import mysql.connector
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class AllDAO:
    """基础数据访问对象类"""

    def __init__(self, connection_config: Dict[str, Any]):
        self.connection_config = connection_config
        self.connection = None

    def connect(self) -> bool:
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(**self.connection_config)
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False

    def disconnect(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询语句"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            print(f"查询执行失败: {e}")
            return []

    def execute_update(self, query: str, params: tuple = None) -> bool:
        """执行更新语句"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            print(f"✅ SQL 执行成功: {query}")
            cursor.close()
            return True
        except Exception as e:
            print(f"更新执行失败: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """批量执行更新语句"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"批量更新执行失败: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def get_last_insert_id(self) -> Optional[int]:
        """获取最后插入的ID - 修复版本"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute("SELECT LAST_INSERT_ID()")
            result = cursor.fetchone()
            cursor.close()

            if result and result[0]:
                return result[0]
            return None
        except Exception as e:
            print(f"获取最后插入ID失败: {e}")
            return None