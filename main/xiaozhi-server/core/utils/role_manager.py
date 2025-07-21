"""
音色识别和角色管理工具类
用于处理对话中的音色识别、角色分配和记忆生成
"""
import mysql.connector
from mysql.connector import Error
import logging
from typing import Dict, List, Optional, Any
from config.config_loader import load_config

logger = logging.getLogger(__name__)


class VoiceRoleManager:
    """音色角色管理器"""
    
    def __init__(self):
        self.connection = None
        self.user_counter = 0  # 用户计数器，用于生成用户1、用户2等
        self._connect_to_db()
        
    def _connect_to_db(self):
        """连接到数据库"""
        try:
            config = load_config()
            db_config = {
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root', 
                'password': '123456',
                'database': 'xiaozhi_esp32_server',
                'charset': 'utf8mb4'
            }
            
            self.connection = mysql.connector.connect(**db_config)
            logger.info("Successfully connected to MySQL for role management")
            
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise
    
    def _execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """执行SQL查询"""
        try:
            if not self.connection or not self.connection.is_connected():
                self._connect_to_db()
                
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
                
        except Error as e:
            logger.error(f"MySQL query error: {e}")
            raise
    
    def get_or_create_role_by_voice(self, voice_hash: str, message_role: str) -> Dict[str, Any]:
        """根据音色获取或创建角色"""
        if not voice_hash:
            # 如果没有音色信息，返回默认角色
            return self._get_default_role(message_role)
        
        # 查找现有角色
        existing_role = self._find_role_by_voice_hash(voice_hash)
        if existing_role:
            return existing_role
            
        # 创建新角色
        return self._create_new_role(voice_hash, message_role)
    
    def _find_role_by_voice_hash(self, voice_hash: str) -> Optional[Dict[str, Any]]:
        """通过音色哈希查找角色"""
        query = "SELECT id, name, voice_hash FROM role WHERE voice_hash = %s"
        result = self._execute_query(query, (voice_hash,), fetch=True)
        return result[0] if result else None
    
    def _get_default_role(self, message_role: str) -> Dict[str, Any]:
        """获取默认角色"""
        if message_role == "assistant":
            role_name = "助手"
        else:
            role_name = "用户"
            
        # 查找或创建默认角色
        query = "SELECT id, name, voice_hash FROM role WHERE name = %s"
        result = self._execute_query(query, (role_name,), fetch=True)
        
        if result:
            return result[0]
        else:
            # 创建默认角色
            query = "INSERT INTO role (name, voice_hash) VALUES (%s, %s)"
            role_id = self._execute_query(query, (role_name, None))
            return {
                'id': role_id,
                'name': role_name,
                'voice_hash': None
            }
    
    def _create_new_role(self, voice_hash: str, message_role: str) -> Dict[str, Any]:
        """创建新角色"""
        if message_role == "assistant":
            role_name = "助手"
        else:
            # 为用户生成递增的名称
            self.user_counter += 1
            # 检查已存在的用户数量来确定正确的编号
            query = "SELECT COUNT(*) as count FROM role WHERE name LIKE '用户%'"
            result = self._execute_query(query, fetch=True)
            user_count = result[0]['count'] if result else 0
            role_name = f"用户{user_count + 1}"
        
        # 插入新角色
        query = "INSERT INTO role (name, voice_hash) VALUES (%s, %s)"
        role_id = self._execute_query(query, (role_name, voice_hash))
        
        logger.info(f"Created new role: {role_name} (ID: {role_id}) with voice_hash: {voice_hash}")
        
        return {
            'id': role_id,
            'name': role_name,
            'voice_hash': voice_hash
        }
    
    def assign_roles_to_messages(self, messages: List) -> List:
        """为消息列表分配角色信息"""
        enhanced_messages = []
        
        for message in messages:
            # 获取音色哈希（如果存在）
            voice_hash = getattr(message, 'voice_hash', None)
            
            # 根据音色获取或创建角色
            role_info = self.get_or_create_role_by_voice(voice_hash, message.role)
            
            # 更新消息的角色信息
            message.role_id = role_info['id']
            message.role_name = role_info['name']
            
            enhanced_messages.append(message)
            
        return enhanced_messages
    
    def get_participants_from_messages(self, messages: List) -> Dict[int, Dict[str, Any]]:
        """从消息列表中获取所有参与者"""
        participants = {}
        
        for message in messages:
            if hasattr(message, 'role_id') and message.role_id:
                participants[message.role_id] = {
                    'role_id': message.role_id,
                    'role_name': message.role_name,
                    'voice_hash': getattr(message, 'voice_hash', None)
                }
                
        return participants
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Voice role manager MySQL connection closed")
    
    def __del__(self):
        self.close()