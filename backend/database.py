"""
用户数据库管理模块
使用SQLite数据库持久化存储用户信息
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# 数据库文件路径
DB_PATH = Path(__file__).parent / "data" / "users.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class UserDatabase:
    """用户数据库管理类"""
    
    def __init__(self, db_path: str = str(DB_PATH)):
        """初始化数据库连接"""
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典形式的行
        return conn
    
    def _init_db(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_first_login INTEGER DEFAULT 1,
                profile_completed INTEGER DEFAULT 0
            )
        """)
        
        # 创建token表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # 创建验证码表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                code TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def user_exists(self, email: str) -> bool:
        """检查用户是否存在"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def username_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def create_user(self, username: str, email: str, password_hash: str) -> bool:
        """创建新用户"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO users (username, email, password, created_at, updated_at, is_first_login, profile_completed)
                VALUES (?, ?, ?, ?, ?, 1, 0)
            """, (username, email, password_hash, now, now))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱获取用户"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取用户"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """根据ID获取用户"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def save_token(self, token: str, user_id: int, expires_at: str) -> bool:
        """保存token"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO tokens (token, user_id, expires_at, created_at)
                VALUES (?, ?, ?, ?)
            """, (token, user_id, expires_at, now))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_token_user(self, token: str) -> Optional[Dict]:
        """获取token关联的用户"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.* FROM users u
            JOIN tokens t ON u.id = t.user_id
            WHERE t.token = ?
        """, (token,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def delete_token(self, token: str) -> bool:
        """删除token"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tokens WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return True
    
    def save_verification_code(self, email: str, code: str, expires_at: str) -> bool:
        """保存验证码"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO verification_codes (email, code, expires_at, created_at)
                VALUES (?, ?, ?, ?)
            """, (email, code, expires_at, now))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_verification_code(self, email: str) -> Optional[Dict]:
        """获取验证码"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM verification_codes 
            WHERE email = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def delete_verification_code(self, email: str) -> bool:
        """删除验证码"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return True
    
    def update_user_password(self, email: str, password_hash: str) -> bool:
        """更新用户密码"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users 
                SET password = ?, updated_at = ?
                WHERE email = ?
            """, (password_hash, now, email))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def update_profile_status(self, email: str, completed: bool = True) -> bool:
        """更新用户资料完成状态"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users 
                SET profile_completed = ?, updated_at = ?
                WHERE email = ?
            """, (1 if completed else 0, now, email))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def update_first_login_status(self, email: str, is_first_login: bool = False) -> bool:
        """更新首次登录状态"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users 
                SET is_first_login = ?, updated_at = ?
                WHERE email = ?
            """, (1 if is_first_login else 0, now, email))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """清理过期的token"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("DELETE FROM tokens WHERE expires_at < ?", (now,))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected
    
    def cleanup_expired_verification_codes(self) -> int:
        """清理过期的验证码"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("DELETE FROM verification_codes WHERE expires_at < ?", (now,))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected


# 全局数据库实例
db = UserDatabase()
