"""
用户认证模块
处理用户注册、登录、密码重置等功能
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import hashlib
import secrets
import re
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.api.database import db


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_token() -> str:
        """生成访问令牌"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_verification_code() -> str:
        """生成6位验证码"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        验证密码强度
        返回: (是否有效, 错误信息)
        """
        if len(password) < 6:
            return False, "密码长度至少6位"
        if len(password) > 20:
            return False, "密码长度不能超过20位"
        return True, ""
    
    @staticmethod
    def register(username: str, email: str, password: str, role: str = "user") -> Dict:
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            role: 用户角色
            
        Returns:
            注册结果
        """
        # 验证邮箱格式
        if not AuthService.validate_email(email):
            return {"success": False, "message": "邮箱格式不正确"}
        
        # 验证密码强度
        valid, msg = AuthService.validate_password(password)
        if not valid:
            return {"success": False, "message": msg}
        
        # 检查邮箱是否已注册
        if db.user_exists(email):
            return {"success": False, "message": "该邮箱已被注册"}
        
        # 检查用户名是否已存在
        if db.username_exists(username):
            return {"success": False, "message": "用户名已存在"}
        
        # 创建用户
        password_hash = AuthService.hash_password(password)
        if db.create_user(username, email, password_hash, role):
            return {
                "success": True,
                "message": "注册成功",
                "user": {
                    "username": username,
                    "email": email,
                    "role": role
                }
            }
        else:
            return {"success": False, "message": "注册失败，请稍后重试"}
    
    @staticmethod
    def login(account: str, password: str) -> Dict:
        """
        用户登录
        
        Args:
            account: 账号（用户名或邮箱）
            password: 密码
            
        Returns:
            登录结果
        """
        user = None
        user_email = None
        
        # 先尝试作为邮箱查找
        user = db.get_user_by_email(account)
        if user:
            user_email = account
        else:
            # 再尝试作为用户名查找
            user = db.get_user_by_username(account)
            if user:
                user_email = user["email"]
        
        if not user:
            return {"success": False, "message": "账号不存在"}
        
        # 验证密码
        if user["password"] != AuthService.hash_password(password):
            return {"success": False, "message": "密码错误"}
        
        # 生成token
        token = AuthService.generate_token()
        expires_at = (datetime.now() + timedelta(days=7)).isoformat()
        
        if db.save_token(token, user["id"], expires_at):
            return {
                "success": True,
                "message": "登录成功",
                "token": token,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user_email,
                    "role": user.get("role", "user"),
                    "is_first_login": bool(user.get("is_first_login", False)),
                    "profile_completed": bool(user.get("profile_completed", False)),
                    "avatar_url": f"/avatars/{user['avatar']}" if user.get("avatar") else None
                }
            }
        else:
            return {"success": False, "message": "登录失败，请稍后重试"}
    
    @staticmethod
    def logout(token: str) -> Dict:
        """
        用户退出
        
        Args:
            token: 访问令牌
            
        Returns:
            退出结果
        """
        if db.delete_token(token):
            return {"success": True, "message": "退出成功"}
        return {"success": False, "message": "无效的token"}
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """
        验证token
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息或None
        """
        user = db.get_token_user(token)
        
        if not user:
            return None
        
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "is_first_login": bool(user.get("is_first_login", False)),
            "profile_completed": bool(user.get("profile_completed", False)),
            "avatar_url": f"/avatars/{user['avatar']}" if user.get("avatar") else None
        }
    
    @staticmethod
    def send_email(to_email: str, code: str) -> bool:
        """
        发送验证码邮件
        从环境变量读取 SMTP 配置：
          EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_FROM
        """
        host = os.environ.get("EMAIL_HOST", "smtp.qq.com")
        port = int(os.environ.get("EMAIL_PORT", "465"))
        user = os.environ.get("EMAIL_USER", "")
        password = os.environ.get("EMAIL_PASSWORD", "")
        from_addr = os.environ.get("EMAIL_FROM", user)

        if not user or not password:
            print(f"[警告] 邮件配置缺失，验证码 {code} 未发送到 {to_email}")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "【运动训练助手】密码重置验证码"
        msg["From"] = from_addr
        msg["To"] = to_email

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:32px;
                    border:1px solid #e5e7eb;border-radius:8px;">
          <h2 style="color:#2563eb;margin-bottom:8px;">密码重置验证码</h2>
          <p style="color:#374151;">您正在重置运动训练助手账号密码，验证码为：</p>
          <div style="font-size:36px;font-weight:bold;letter-spacing:8px;
                      color:#111827;text-align:center;margin:24px 0;">{code}</div>
          <p style="color:#6b7280;font-size:13px;">验证码 10 分钟内有效，请勿泄露给他人。</p>
          <p style="color:#6b7280;font-size:13px;">如非本人操作，请忽略此邮件。</p>
        </div>
        """
        msg.attach(MIMEText(html, "html", "utf-8"))

        try:
            if port == 465:
                server = smtplib.SMTP_SSL(host, port, timeout=10)
            else:
                server = smtplib.SMTP(host, port, timeout=10)
                server.starttls()
            server.login(user, password)
            server.sendmail(from_addr, [to_email], msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"[邮件发送失败] {e}")
            return False

    @staticmethod
    def send_verification_code(email: str) -> Dict:
        """
        发送验证码（模拟）
        
        Args:
            email: 邮箱
            
        Returns:
            发送结果
        """
        # 验证邮箱格式
        if not AuthService.validate_email(email):
            return {"success": False, "message": "邮箱格式不正确"}
        
        # 检查邮箱是否已注册
        if not db.user_exists(email):
            return {"success": False, "message": "该邮箱未注册"}
        
        # 生成验证码
        code = AuthService.generate_verification_code()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        
        if db.save_verification_code(email, code, expires_at):
            if not AuthService.send_email(email, code):
                return {"success": False, "message": "验证码发送失败，请检查邮件配置或稍后重试"}

            return {
                "success": True,
                "message": "验证码已发送到您的邮箱，请注意查收"
            }
        else:
            return {"success": False, "message": "发送验证码失败，请稍后重试"}
    
    @staticmethod
    def verify_code(email: str, code: str) -> bool:
        """
        验证验证码
        
        Args:
            email: 邮箱
            code: 验证码
            
        Returns:
            是否验证成功
        """
        code_data = db.get_verification_code(email)
        
        if not code_data:
            return False
        
        # 检查是否过期
        if datetime.fromisoformat(code_data["expires_at"]) < datetime.now():
            db.delete_verification_code(email)
            return False
        
        # 验证码匹配
        if code_data["code"] == code:
            db.delete_verification_code(email)
            return True
        
        return False
    
    @staticmethod
    def reset_password(email: str, code: str, new_password: str) -> Dict:
        """
        重置密码
        
        Args:
            email: 邮箱
            code: 验证码
            new_password: 新密码
            
        Returns:
            重置结果
        """
        # 验证密码强度
        valid, msg = AuthService.validate_password(new_password)
        if not valid:
            return {"success": False, "message": msg}
        
        # 验证验证码
        if not AuthService.verify_code(email, code):
            return {"success": False, "message": "验证码错误或已过期"}
        
        # 检查邮箱是否存在
        if not db.user_exists(email):
            return {"success": False, "message": "该邮箱未注册"}
        
        # 更新密码
        password_hash = AuthService.hash_password(new_password)
        if db.update_user_password(email, password_hash):
            return {"success": True, "message": "密码重置成功"}
        else:
            return {"success": False, "message": "密码重置失败，请稍后重试"}
    
    @staticmethod
    def update_profile_status(email: str, completed: bool = True) -> Dict:
        """
        更新用户资料完成状态
        
        Args:
            email: 邮箱
            completed: 是否完成
            
        Returns:
            更新结果
        """
        user = db.get_user_by_email(email)
        if not user:
            return {"success": False, "message": "用户不存在"}
        
        if db.update_profile_status(email, completed):
            return {"success": True, "message": "资料状态已更新"}
        else:
            return {"success": False, "message": "更新失败，请稍后重试"}


# 初始化测试用户
def init_test_users():
    """初始化测试用户"""
    test_users = [
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456",
            "role": "user"
        },
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "role": "admin"
        }
    ]
    
    for user in test_users:
        # 只在用户不存在时才创建
        if not db.user_exists(user["email"]):
            AuthService.register(
                username=user["username"],
                email=user["email"],
                password=user["password"],
                role=user["role"]
            )
            # 标记为已完成资料
            db.update_profile_status(user["email"], completed=True)


# 启动时初始化测试用户
init_test_users()
