"""
测试重启后数据持久化
验证应用重启后用户数据是否仍然存在
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.auth import AuthService
from backend.database import db

def test_restart_persistence():
    """测试重启后数据是否仍然存在"""
    print("=" * 50)
    print("测试: 重启后数据持久化验证")
    print("=" * 50)
    print()
    
    test_email = "persistent_test@example.com"
    test_username = "persistent_tester"
    
    # 尝试从数据库查询用户
    user = db.get_user_by_email(test_email)
    
    if user:
        print(f"✓ 在数据库中找到了用户信息（说明数据已持久化）")
        print(f"  用户ID: {user['id']}")
        print(f"  用户名: {user['username']}")
        print(f"  邮箱: {user['email']}")
        print(f"  创建时间: {user['created_at']}")
        print(f"  更新时间: {user['updated_at']}")
        
        # 验证用户名
        if user['username'] == test_username:
            print(f"✓ 用户名匹配")
        
        # 尝试登录验证密码确实被保存了
        print()
        print("尝试登录以验证密码...")
        
        login_result = AuthService.login(test_email, "TestPassword123")
        if login_result['success']:
            print(f"✓ 登录成功（密码已正确保存）")
            print(f"  Token: {login_result['token'][:15]}...")
            return True
        else:
            print(f"✗ 登录失败: {login_result['message']}")
            return False
    else:
        print(f"✗ 数据库中未找到用户")
        print(f"  邮箱: {test_email}")
        return False


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║       应用重启后数据持久化验证测试          ║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    try:
        if test_restart_persistence():
            print()
            print("╔" + "=" * 48 + "╗")
            print("║      测试通过! 数据已成功持久化! ✓         ║")
            print("║    即使应用重启后，用户数据也保持!        ║")
            print("╚" + "=" * 48 + "╝")
        else:
            print()
            print("╔" + "=" * 48 + "╗")
            print("║            测试失败，请检查!              ║")
            print("╚" + "=" * 48 + "╝")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ 测试期间发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
