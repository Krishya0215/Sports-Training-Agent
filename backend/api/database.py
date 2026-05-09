"""
用户与训练业务数据库管理模块
使用SQLite数据库持久化存储用户、训练与记忆信息
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

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
                role TEXT DEFAULT 'user',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_first_login INTEGER DEFAULT 1,
                profile_completed INTEGER DEFAULT 0
            )
        """)

        # 迁移：为旧数据库补充 avatar 列
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT NULL")
        except Exception:
            pass  # 列已存在则忽略

        # 迁移：为 training_plans 补充 conversation_id 列
        try:
            cursor.execute("ALTER TABLE training_plans ADD COLUMN conversation_id TEXT DEFAULT NULL")
        except Exception:
            pass  # 列已存在则忽略

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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                goal TEXT,
                preferred_method TEXT,
                weekly_days INTEGER,
                daily_duration INTEGER,
                intensity_level TEXT,
                injury_status TEXT,
                injury_detail TEXT,
                fitness_level TEXT,
                age_range TEXT,
                gender TEXT,
                height_cm REAL,
                weight_kg REAL,
                profile_source TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                goal TEXT,
                start_date TEXT,
                end_date TEXT,
                created_from_ai INTEGER DEFAULT 0,
                metadata_json TEXT,
                selected_weekdays_json TEXT,
                source_prompt TEXT,
                ai_response TEXT,
                status TEXT DEFAULT 'active',
                version INTEGER DEFAULT 1,
                based_on_memory INTEGER DEFAULT 0,
                conversation_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_id INTEGER,
                plan_session_key TEXT,
                date TEXT NOT NULL,
                training_type TEXT NOT NULL,
                duration INTEGER,
                intensity TEXT,
                feedback TEXT,
                fatigue_level INTEGER,
                pain_level INTEGER,
                completion_status TEXT DEFAULT 'completed',
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (plan_id) REFERENCES training_plans(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_episodic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                event_time TEXT NOT NULL,
                conversation_id TEXT,
                plan_id INTEGER,
                record_id INTEGER,
                question TEXT,
                answer_summary TEXT,
                event_summary TEXT,
                trigger_source TEXT,
                payload_json TEXT,
                importance_score REAL DEFAULT 0,
                tags_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (plan_id) REFERENCES training_plans(id),
                FOREIGN KEY (record_id) REFERENCES training_records(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_semantic_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fact_category TEXT NOT NULL,
                fact_key TEXT NOT NULL,
                fact_value TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                source_event_id INTEGER,
                source_type TEXT,
                is_active INTEGER DEFAULT 1,
                valid_from TEXT,
                valid_to TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (source_event_id) REFERENCES memory_episodic_events(id),
                UNIQUE(user_id, fact_category, fact_key)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_working_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_id TEXT NOT NULL,
                source TEXT,
                status TEXT DEFAULT 'active',
                max_rounds INTEGER DEFAULT 5,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_working_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT,
                sequence_no INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES memory_working_sessions(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_perceptual_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                asset_type TEXT NOT NULL,
                source_path TEXT NOT NULL,
                source_name TEXT,
                chunk_id TEXT,
                page_no INTEGER,
                title TEXT,
                description TEXT,
                feature_tags_json TEXT,
                body_part TEXT,
                movement_type TEXT,
                risk_level TEXT,
                contraindications_json TEXT,
                embedding_ref TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 聊天消息持久化表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                thinking TEXT,
                mode TEXT DEFAULT 'single_agent',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_user_conv
            ON chat_messages(user_id, conversation_id)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                food_content TEXT NOT NULL,
                calories REAL,
                protein REAL,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                weight REAL NOT NULL,
                body_fat REAL,
                chest_circumference REAL,
                waist_circumference REAL,
                hip_circumference REAL,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.commit()
        conn.close()

    def _serialize_json(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False)

    def _deserialize_json(self, value: Optional[str], default):
        if not value:
            return default
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return default

    def _row_to_training_plan(self, row: sqlite3.Row) -> Dict[str, Any]:
        item = dict(row)
        item["created_from_ai"] = bool(item.get("created_from_ai", 0))
        item["based_on_memory"] = bool(item.get("based_on_memory", 0))
        item["metadata"] = self._deserialize_json(item.pop("metadata_json", None), {})
        item["selected_weekdays"] = self._deserialize_json(item.pop("selected_weekdays_json", None), [])
        return item

    def _row_to_episode(self, row: sqlite3.Row) -> Dict[str, Any]:
        item = dict(row)
        item["payload"] = self._deserialize_json(item.pop("payload_json", None), {})
        item["tags"] = self._deserialize_json(item.pop("tags_json", None), [])
        return item

    def _row_to_perceptual_asset(self, row: sqlite3.Row) -> Dict[str, Any]:
        item = dict(row)
        item["feature_tags"] = self._deserialize_json(item.pop("feature_tags_json", None), [])
        item["contraindications"] = self._deserialize_json(item.pop("contraindications_json", None), [])
        return item
    
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
    
    def create_user(self, username: str, email: str, password_hash: str, role: str = "user") -> bool:
        """创建新用户"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO users (username, email, password, role, created_at, updated_at, is_first_login, profile_completed)
                VALUES (?, ?, ?, ?, ?, ?, 1, 0)
            """, (username, email, password_hash, role, now, now))
            
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

    def get_user_by_email_or_username(self, account: str) -> Optional[Dict]:
        user = self.get_user_by_email(account)
        if user:
            return user
        return self.get_user_by_username(account)
    
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

    def get_user_by_token(self, token: str) -> Optional[Dict]:
        return self.get_token_user(token)
    
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

    def update_username(self, user_id: int, new_username: str) -> bool:
        """更新用户名"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users
                SET username = ?, updated_at = ?
                WHERE id = ?
            """, (new_username, now, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def update_account(self, user_id: int, new_username: str, new_email: str) -> bool:
        """同时更新用户名和邮箱"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users
                SET username = ?, email = ?, updated_at = ?
                WHERE id = ?
            """, (new_username, new_email, now, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_user_avatar(self, user_id: int) -> Optional[str]:
        """获取用户头像文件名"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT avatar FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            return row["avatar"] if row else None
        except Exception:
            return None

    def update_avatar(self, user_id: int, filename: str) -> bool:
        """更新用户头像"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users SET avatar = ?, updated_at = ? WHERE id = ?
            """, (filename, now, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def update_profile_status(self, email: str, completed: bool = True) -> bool:
        """更新用户资料完成状态，同时清除首次登录标记"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users
                SET profile_completed = ?, is_first_login = 0, updated_at = ?
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

    def upsert_user_profile(self, user_id: int, profile: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        current = self.get_user_profile(user_id)
        payload = {
            "goal": profile.get("goal"),
            "preferred_method": profile.get("preferred_method"),
            "weekly_days": profile.get("weekly_days"),
            "daily_duration": profile.get("daily_duration"),
            "intensity_level": profile.get("intensity_level"),
            "injury_status": profile.get("injury_status"),
            "injury_detail": profile.get("injury_detail"),
            "fitness_level": profile.get("fitness_level"),
            "age_range": profile.get("age_range"),
            "gender": profile.get("gender"),
            "height_cm": profile.get("height_cm"),
            "weight_kg": profile.get("weight_kg"),
            "profile_source": profile.get("profile_source", "manual")
        }

        if current:
            merged = {**current, **{k: v for k, v in payload.items() if v is not None}}
            cursor.execute("""
                UPDATE user_profiles
                SET goal = ?, preferred_method = ?, weekly_days = ?, daily_duration = ?,
                    intensity_level = ?, injury_status = ?, injury_detail = ?, fitness_level = ?,
                    age_range = ?, gender = ?, height_cm = ?, weight_kg = ?, profile_source = ?,
                    updated_at = ?
                WHERE user_id = ?
            """, (
                merged.get("goal"),
                merged.get("preferred_method"),
                merged.get("weekly_days"),
                merged.get("daily_duration"),
                merged.get("intensity_level"),
                merged.get("injury_status"),
                merged.get("injury_detail"),
                merged.get("fitness_level"),
                merged.get("age_range"),
                merged.get("gender"),
                merged.get("height_cm"),
                merged.get("weight_kg"),
                merged.get("profile_source"),
                now,
                user_id
            ))
        else:
            cursor.execute("""
                INSERT INTO user_profiles (
                    user_id, goal, preferred_method, weekly_days, daily_duration,
                    intensity_level, injury_status, injury_detail, fitness_level,
                    age_range, gender, height_cm, weight_kg, profile_source,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                payload.get("goal"),
                payload.get("preferred_method"),
                payload.get("weekly_days"),
                payload.get("daily_duration"),
                payload.get("intensity_level"),
                payload.get("injury_status"),
                payload.get("injury_detail"),
                payload.get("fitness_level"),
                payload.get("age_range"),
                payload.get("gender"),
                payload.get("height_cm"),
                payload.get("weight_kg"),
                payload.get("profile_source"),
                now,
                now
            ))

        conn.commit()
        conn.close()
        return self.get_user_profile(user_id) or {}

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def create_training_plan(self, user_id: int, plan: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO training_plans (
                user_id, title, content, goal, start_date, end_date, created_from_ai,
                metadata_json, selected_weekdays_json, source_prompt, ai_response,
                status, version, based_on_memory, conversation_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            plan.get("title"),
            plan.get("content"),
            plan.get("goal"),
            plan.get("start_date"),
            plan.get("end_date"),
            1 if plan.get("created_from_ai") else 0,
            self._serialize_json(plan.get("metadata")),
            self._serialize_json(plan.get("selected_weekdays") or []),
            plan.get("source_prompt"),
            plan.get("ai_response"),
            plan.get("status", "active"),
            plan.get("version", 1),
            1 if plan.get("based_on_memory") else 0,
            plan.get("conversation_id"),
            now,
            now
        ))
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_training_plan_by_id(user_id, plan_id)

    def list_training_plans(self, user_id: int) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM training_plans WHERE user_id = ? ORDER BY created_at DESC, id DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_training_plan(row) for row in rows]

    def get_training_plan_by_id(self, user_id: int, plan_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM training_plans WHERE id = ? AND user_id = ?",
            (plan_id, user_id)
        )
        row = cursor.fetchone()
        conn.close()
        return self._row_to_training_plan(row) if row else None

    def update_training_plan(self, user_id: int, plan_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self.get_training_plan_by_id(user_id, plan_id)
        if not current:
            return None

        merged = {**current, **updates}
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE training_plans
            SET title = ?, content = ?, goal = ?, start_date = ?, end_date = ?,
                created_from_ai = ?, metadata_json = ?, selected_weekdays_json = ?,
                source_prompt = ?, ai_response = ?, status = ?, version = ?,
                based_on_memory = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (
            merged.get("title"),
            merged.get("content"),
            merged.get("goal"),
            merged.get("start_date"),
            merged.get("end_date"),
            1 if merged.get("created_from_ai") else 0,
            self._serialize_json(merged.get("metadata")),
            self._serialize_json(merged.get("selected_weekdays") or []),
            merged.get("source_prompt"),
            merged.get("ai_response"),
            merged.get("status", "active"),
            merged.get("version", 1),
            1 if merged.get("based_on_memory") else 0,
            datetime.now().isoformat(),
            plan_id,
            user_id
        ))
        conn.commit()
        conn.close()
        return self.get_training_plan_by_id(user_id, plan_id)

    def delete_training_plan(self, user_id: int, plan_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM training_plans WHERE id = ? AND user_id = ?", (plan_id, user_id))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def create_training_record(self, user_id: int, record: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO training_records (
                user_id, plan_id, plan_session_key, date, training_type, duration, intensity,
                feedback, fatigue_level, pain_level, completion_status, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            record.get("plan_id"),
            record.get("plan_session_key"),
            record.get("date"),
            record.get("training_type"),
            record.get("duration"),
            record.get("intensity"),
            record.get("feedback"),
            record.get("fatigue_level"),
            record.get("pain_level"),
            record.get("completion_status", "completed"),
            record.get("notes"),
            now,
            now
        ))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_training_record_by_id(user_id, record_id)

    def list_training_records(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        training_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM training_records WHERE user_id = ?"
        params: List[Any] = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if training_type:
            query += " AND training_type = ?"
            params.append(training_type)

        query += " ORDER BY date DESC, id DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_training_record_by_id(self, user_id: int, record_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM training_records WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_training_record(self, user_id: int, record_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM training_records WHERE id = ? AND user_id = ?", (record_id, user_id))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    # ==================== 饮食记录操作 ====================

    def create_daily_record(self, user_id: int, record: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO daily_records (
                user_id, date, meal_type, food_content, calories, protein, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            record.get("date"),
            record.get("meal_type"),
            record.get("food_content"),
            record.get("calories"),
            record.get("protein"),
            record.get("notes"),
            now,
            now
        ))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_daily_record_by_id(user_id, record_id)

    def list_daily_records(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM daily_records WHERE user_id = ?"
        params: List[Any] = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC, id DESC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_daily_record_by_id(self, user_id: int, record_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM daily_records WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_daily_record(self, user_id: int, record_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_records WHERE id = ? AND user_id = ?", (record_id, user_id))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    # ==================== 体重记录操作 ====================

    def create_weight_record(self, user_id: int, record: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO weight_records (
                user_id, date, weight, body_fat, chest_circumference, waist_circumference, hip_circumference, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            record.get("date"),
            record.get("weight"),
            record.get("body_fat"),
            record.get("chest_circumference"),
            record.get("waist_circumference"),
            record.get("hip_circumference"),
            record.get("notes"),
            now,
            now
        ))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_weight_record_by_id(user_id, record_id)

    def list_weight_records(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM weight_records WHERE user_id = ?"
        params: List[Any] = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC, id DESC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_weight_record_by_id(self, user_id: int, record_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM weight_records WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_weight_record(self, user_id: int, record_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weight_records WHERE id = ? AND user_id = ?", (record_id, user_id))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def create_episodic_event(self, user_id: int, event: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO memory_episodic_events (
                user_id, event_type, event_time, conversation_id, plan_id, record_id,
                question, answer_summary, event_summary, trigger_source, payload_json,
                importance_score, tags_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            event.get("event_type"),
            event.get("event_time", now),
            event.get("conversation_id"),
            event.get("plan_id"),
            event.get("record_id"),
            event.get("question"),
            event.get("answer_summary"),
            event.get("event_summary"),
            event.get("trigger_source"),
            self._serialize_json(event.get("payload") or {}),
            event.get("importance_score", 0),
            self._serialize_json(event.get("tags") or []),
            now
        ))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_episodic_event_by_id(user_id, event_id)

    def get_episodic_event_by_id(self, user_id: int, event_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM memory_episodic_events WHERE id = ? AND user_id = ?",
            (event_id, user_id)
        )
        row = cursor.fetchone()
        conn.close()
        return self._row_to_episode(row) if row else None

    def list_episodic_events(
        self,
        user_id: int,
        event_type: Optional[str] = None,
        plan_id: Optional[int] = None,
        limit: int = 20,
        target_user_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()

        # 如果 target_user_ids 为 None，表示管理员查看所有用户
        if target_user_ids is None:
            query = "SELECT * FROM memory_episodic_events WHERE 1=1"
            params: List[Any] = []
        else:
            query = "SELECT * FROM memory_episodic_events WHERE user_id IN ({})".format(
                ",".join(["?"] * len(target_user_ids))
            )
            params: List[Any] = list(target_user_ids)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if plan_id is not None:
            query += " AND plan_id = ?"
            params.append(plan_id)

        query += " ORDER BY event_time DESC, id DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_episode(row) for row in rows]

    def count_episodic_events(self, user_id: int, target_user_ids: Optional[List[int]] = None) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()

        # 如果 target_user_ids 为 None，表示管理员查看所有用户
        if target_user_ids is None:
            cursor.execute("SELECT COUNT(*) AS count FROM memory_episodic_events")
        else:
            query = "SELECT COUNT(*) AS count FROM memory_episodic_events WHERE user_id IN ({})".format(
                ",".join(["?"] * len(target_user_ids))
            )
            cursor.execute(query, tuple(target_user_ids))

        row = cursor.fetchone()
        conn.close()
        return int(row["count"]) if row else 0

    def upsert_semantic_fact(
        self,
        user_id: int,
        fact_category: str,
        fact_key: str,
        fact_value: str,
        confidence: float = 0.8,
        source_event_id: Optional[int] = None,
        source_type: Optional[str] = None,
        is_active: bool = True
    ) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO memory_semantic_facts (
                user_id, fact_category, fact_key, fact_value, confidence,
                source_event_id, source_type, is_active, valid_from, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, fact_category, fact_key)
            DO UPDATE SET
                fact_value = excluded.fact_value,
                confidence = excluded.confidence,
                source_event_id = excluded.source_event_id,
                source_type = excluded.source_type,
                is_active = excluded.is_active,
                updated_at = excluded.updated_at
        """, (
            user_id,
            fact_category,
            fact_key,
            fact_value,
            confidence,
            source_event_id,
            source_type,
            1 if is_active else 0,
            now,
            now,
            now
        ))
        conn.commit()
        conn.close()
        return self.get_semantic_fact(user_id, fact_category, fact_key) or {}

    def get_semantic_fact(self, user_id: int, fact_category: str, fact_key: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM memory_semantic_facts
            WHERE user_id = ? AND fact_category = ? AND fact_key = ?
        """, (user_id, fact_category, fact_key))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def list_semantic_facts(
        self,
        user_id: int,
        fact_category: Optional[str] = None,
        target_user_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()

        # 如果 target_user_ids 为 None，表示管理员查看所有用户
        if target_user_ids is None:
            base_query = "SELECT * FROM memory_semantic_facts WHERE is_active = 1"
            params: List[Any] = []
            if fact_category:
                base_query += " AND fact_category = ?"
                params.append(fact_category)
        else:
            base_query = "SELECT * FROM memory_semantic_facts WHERE user_id IN ({}) AND is_active = 1".format(
                ",".join(["?"] * len(target_user_ids))
            )
            params: List[Any] = list(target_user_ids)
            if fact_category:
                base_query += " AND fact_category = ?"
                params.append(fact_category)

        query = base_query + " ORDER BY updated_at DESC, id DESC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def count_semantic_facts(self, user_id: int, target_user_ids: Optional[List[int]] = None) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()

        # 如果 target_user_ids 为 None，表示管理员查看所有用户
        if target_user_ids is None:
            cursor.execute("SELECT COUNT(*) AS count FROM memory_semantic_facts WHERE is_active = 1")
        else:
            query = "SELECT COUNT(*) AS count FROM memory_semantic_facts WHERE user_id IN ({}) AND is_active = 1".format(
                ",".join(["?"] * len(target_user_ids))
            )
            cursor.execute(query, tuple(target_user_ids))

        row = cursor.fetchone()
        conn.close()
        return int(row["count"]) if row else 0

    def create_perceptual_asset(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO memory_perceptual_assets (
                user_id, asset_type, source_path, source_name, chunk_id, page_no, title, description,
                feature_tags_json, body_part, movement_type, risk_level,
                contraindications_json, embedding_ref, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset.get("user_id"),
            asset.get("asset_type"),
            asset.get("source_path"),
            asset.get("source_name"),
            asset.get("chunk_id"),
            asset.get("page_no"),
            asset.get("title"),
            asset.get("description"),
            self._serialize_json(asset.get("feature_tags") or []),
            asset.get("body_part"),
            asset.get("movement_type"),
            asset.get("risk_level"),
            self._serialize_json(asset.get("contraindications") or []),
            asset.get("embedding_ref"),
            now,
            now
        ))
        asset_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_perceptual_asset(asset_id) or {}

    def get_perceptual_asset(self, asset_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memory_perceptual_assets WHERE id = ?", (asset_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_perceptual_asset(row) if row else None

    def count_perceptual_assets(self) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM memory_perceptual_assets")
        row = cursor.fetchone()
        conn.close()
        return int(row["count"]) if row else 0

    # ==================== 工作记忆方法 ====================

    def create_working_session(
        self,
        user_id: int,
        conversation_id: str,
        source: Optional[str] = None,
        max_rounds: int = 5
    ) -> Dict[str, Any]:
        """创建工作记忆会话"""
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO memory_working_sessions (
                user_id, conversation_id, source, status, max_rounds, created_at, updated_at
            ) VALUES (?, ?, ?, 'active', ?, ?, ?)
        """, (user_id, conversation_id, source, max_rounds, now, now))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"id": session_id, "user_id": user_id, "conversation_id": conversation_id}

    def get_working_session(
        self,
        user_id: int,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取工作记忆会话"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM memory_working_sessions
            WHERE user_id = ? AND conversation_id = ? AND status = 'active'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id, conversation_id))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_working_session(
        self,
        session_id: int,
        status: Optional[str] = None
    ) -> bool:
        """更新工作记忆会话状态"""
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        updates = ["updated_at = ?"]
        params = [now]

        if status:
            updates.append("status = ?")
            params.append(status)

        params.append(session_id)

        cursor.execute(f"""
            UPDATE memory_working_sessions
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        conn.commit()
        conn.close()
        return True

    def add_working_message(
        self,
        session_id: int,
        role: str,
        content: str,
        message_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """添加工作记忆消息"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 获取当前最大序列号
        cursor.execute("""
            SELECT MAX(sequence_no) AS max_seq FROM memory_working_messages
            WHERE session_id = ?
        """, (session_id,))
        result = cursor.fetchone()
        next_seq = (result["max_seq"] or 0) + 1

        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO memory_working_messages (
                session_id, role, content, message_type, sequence_no, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, role, content, message_type, next_seq, now))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"id": message_id, "session_id": session_id}

    def get_working_messages(
        self,
        session_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取工作记忆消息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        query = """
            SELECT * FROM memory_working_messages
            WHERE session_id = ?
            ORDER BY sequence_no ASC
        """
        if limit:
            query += " LIMIT ?"
            cursor.execute(query, (session_id, limit))
        else:
            cursor.execute(query, (session_id,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_working_context(
        self,
        user_id: int,
        conversation_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """获取完整的工作记忆上下文"""
        # 获取或创建会话
        session = self.get_working_session(user_id, conversation_id)
        if not session:
            return {"session_id": None, "messages": []}

        messages = self.get_working_messages(session["id"], limit=limit)

        return {
            "session_id": session["id"],
            "conversation_id": conversation_id,
            "source": session.get("source"),
            "status": session.get("status"),
            "max_rounds": session.get("max_rounds"),
            "messages": messages
        }

    # ── 聊天消息持久化 ──────────────────────────────────────

    def save_chat_message(self, user_id: int, conversation_id: str,
                          question: str, answer: str,
                          thinking: str = "", mode: str = "single_agent") -> Optional[int]:
        """保存一条聊天消息，返回 id"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO chat_messages
                    (user_id, conversation_id, question, answer, thinking, mode, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, conversation_id, question, answer, thinking or "", mode, now))
            msg_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return msg_id
        except Exception:
            return None

    def get_chat_history(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """获取用户聊天历史（按时间倒序，最新的在前）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, conversation_id, question, answer, thinking, mode, created_at
            FROM chat_messages
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_chat_conversations(self, user_id: int, limit: int = 50) -> List[Dict]:
        """获取用户的对话列表（每个 conversation 取最新一条消息作为摘要）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT conversation_id,
                   question,
                   answer,
                   MAX(created_at) AS last_time
            FROM chat_messages
            WHERE user_id = ?
            GROUP BY conversation_id
            ORDER BY last_time DESC
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_conversation_messages(self, user_id: int, conversation_id: str) -> List[Dict]:
        """获取某个对话的所有消息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, question, answer, thinking, mode, created_at
            FROM chat_messages
            WHERE user_id = ? AND conversation_id = ?
            ORDER BY created_at ASC
        """, (user_id, conversation_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def end_working_session(
        self,
        user_id: int,
        conversation_id: str
    ) -> bool:
        """结束工作记忆会话"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE memory_working_sessions
            SET status = 'ended', updated_at = ?
            WHERE user_id = ? AND conversation_id = ? AND status = 'active'
        """, (datetime.now().isoformat(), user_id, conversation_id))
        conn.commit()
        conn.close()
        return True


# 全局数据库实例
db = UserDatabase()
