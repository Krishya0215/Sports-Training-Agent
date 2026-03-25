#!/usr/bin/env python3
"""
简化认证服务器
只包含用户注册/登录/退出等认证功能，用于测试前端认证流程
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Dict
import hashlib
import secrets
import re
import uvicorn

# ==================== 认证服务类 ====================

# 模拟数据库存储（生产环境应使用真实数据库）
users_db = {}  # {email: user_data}
verification_codes = {}  # {email: {code, expires_at}}
tokens = {}  # {token: {email, expires_at}}

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
    def register(username: str, email: str, password: str) -> Dict:
        """
        用户注册

        Args:
            username: 用户名
            email: 邮箱
            password: 密码

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
        if email in users_db:
            return {"success": False, "message": "该邮箱已被注册"}

        # 检查用户名是否已存在
        for user in users_db.values():
            if user["username"] == username:
                return {"success": False, "message": "用户名已存在"}

        # 创建用户
        user_data = {
            "username": username,
            "email": email,
            "password": AuthService.hash_password(password),
            "created_at": datetime.now().isoformat(),
            "is_first_login": True,  # 首次登录标记
            "profile_completed": False  # 基础信息是否完善
        }

        users_db[email] = user_data

        return {
            "success": True,
            "message": "注册成功",
            "user": {
                "username": username,
                "email": email
            }
        }

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
        # 查找用户（支持用户名或邮箱登录）
        user = None
        user_email = None

        # 先尝试作为邮箱查找
        if account in users_db:
            user = users_db[account]
            user_email = account
        else:
            # 再尝试作为用户名查找
            for email, user_data in users_db.items():
                if user_data["username"] == account:
                    user = user_data
                    user_email = email
                    break

        if not user:
            return {"success": False, "message": "账号不存在"}

        # 验证密码
        if user["password"] != AuthService.hash_password(password):
            return {"success": False, "message": "密码错误"}

        # 生成token
        token = AuthService.generate_token()
        tokens[token] = {
            "email": user_email,
            "expires_at": datetime.now() + timedelta(days=7)
        }

        return {
            "success": True,
            "message": "登录成功",
            "token": token,
            "user": {
                "username": user["username"],
                "email": user_email,
                "is_first_login": user.get("is_first_login", False),
                "profile_completed": user.get("profile_completed", False)
            }
        }

    @staticmethod
    def logout(token: str) -> Dict:
        """
        用户退出

        Args:
            token: 访问令牌

        Returns:
            退出结果
        """
        if token in tokens:
            del tokens[token]
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
        if token not in tokens:
            return None

        token_data = tokens[token]

        # 检查是否过期
        if datetime.now() > token_data["expires_at"]:
            del tokens[token]
            return None

        email = token_data["email"]
        user = users_db.get(email)

        if not user:
            return None

        return {
            "username": user["username"],
            "email": email,
            "profile_completed": user.get("profile_completed", False)
        }

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
        if email not in users_db:
            return {"success": False, "message": "该邮箱未注册"}

        # 生成验证码
        code = AuthService.generate_verification_code()
        verification_codes[email] = {
            "code": code,
            "expires_at": datetime.now() + timedelta(minutes=10)
        }

        # 实际应用中这里应该发送邮件
        # 这里仅模拟，将验证码打印到控制台
        print(f"[验证码] {email}: {code}")

        return {
            "success": True,
            "message": "验证码已发送到您的邮箱",
            "code": code  # 仅用于测试，生产环境不应返回
        }

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
        if email not in verification_codes:
            return False

        code_data = verification_codes[email]

        # 检查是否过期
        if datetime.now() > code_data["expires_at"]:
            del verification_codes[email]
            return False

        # 验证码匹配
        if code_data["code"] == code:
            del verification_codes[email]
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
        if email not in users_db:
            return {"success": False, "message": "该邮箱未注册"}

        # 更新密码
        users_db[email]["password"] = AuthService.hash_password(new_password)

        return {"success": True, "message": "密码重置成功"}

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
        if email not in users_db:
            return {"success": False, "message": "用户不存在"}

        users_db[email]["profile_completed"] = completed
        users_db[email]["is_first_login"] = False

        return {"success": True, "message": "资料状态已更新"}


# ==================== 初始化测试用户 ====================

def init_test_users():
    """初始化测试用户"""
    test_users = [
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456"
        }
    ]

    for user in test_users:
        AuthService.register(
            username=user["username"],
            email=user["email"],
            password=user["password"]
        )
        # 标记为已完成资料
        users_db[user["email"]]["profile_completed"] = True
        users_db[user["email"]]["is_first_login"] = False


# ==================== FastAPI应用 ====================

app = FastAPI(
    title="认证测试服务器",
    description="简化版认证API测试服务器",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化测试用户
init_test_users()

# ==================== 数据模型 ====================

class LoginRequest(BaseModel):
    """登录请求模型"""
    account: str  # 账号（用户名或邮箱）
    password: str

class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str
    email: str
    password: str
    confirm_password: str

class VerificationCodeRequest(BaseModel):
    """验证码请求模型"""
    email: str

class ResetPasswordRequest(BaseModel):
    """重置密码请求模型"""
    email: str
    code: str
    new_password: str
    confirm_password: str

# ==================== API接口 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "认证测试服务器",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        # 验证两次密码是否一致
        if request.password != request.confirm_password:
            raise HTTPException(status_code=400, detail="两次输入的密码不一致")

        result = AuthService.register(
            username=request.username,
            email=request.email,
            password=request.password
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        print(f"用户注册成功: {request.email}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"注册失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """用户登录"""
    try:
        result = AuthService.login(
            account=request.account,
            password=request.password
        )

        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["message"])

        print(f"用户登录成功: {request.account}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"登录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/logout")
async def logout(token: str):
    """用户退出"""
    try:
        result = AuthService.logout(token)
        print(f"用户退出: {token[:10]}...")
        return result
    except Exception as e:
        print(f"退出失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/verify")
async def verify_token(token: str):
    """验证token"""
    try:
        user = AuthService.verify_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="token无效或已过期")
        return {"success": True, "user": user}
    except HTTPException:
        raise
    except Exception as e:
        print(f"验证token失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/send-code")
async def send_verification_code(request: VerificationCodeRequest):
    """发送验证码"""
    try:
        result = AuthService.send_verification_code(request.email)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        print(f"验证码已发送: {request.email}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"发送验证码失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """重置密码"""
    try:
        # 验证两次密码是否一致
        if request.new_password != request.confirm_password:
            raise HTTPException(status_code=400, detail="两次输入的密码不一致")

        result = AuthService.reset_password(
            email=request.email,
            code=request.code,
            new_password=request.new_password
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        print(f"密码重置成功: {request.email}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"重置密码失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/complete-profile")
async def complete_profile(email: str):
    """标记用户资料已完成"""
    try:
        result = AuthService.update_profile_status(email, completed=True)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        print(f"用户资料已完成: {email}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"更新资料状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "users_count": len(users_db),
        "timestamp": datetime.now()
    }

if __name__ == "__main__":
    print("=" * 50)
    print("启动简化认证测试服务器")
    print("访问地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("测试用户: test@example.com / 123456")
    print("=" * 50)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )