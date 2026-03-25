"""
测试数据库持久化功能
验证用户注册和登录信息是否正确保存
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.auth import AuthService
from backend.database import db

def test_registration():
    """测试用户注册和持久化"""
    print("=" * 50)
    print("测试1: 用户注册")
    print("=" * 50)
    
    # 创建一个测试用户
    test_email = "persistent_test@example.com"
    test_username = "persistent_tester"
    test_password = "TestPassword123"
    
    # 尝试删除旧用户（如果存在）
    old_user = db.get_user_by_email(test_email)
    if old_user:
        print(f"✓ 找到旧的测试用户，邮箱: {test_email}")
    
    # 注册用户
    result = AuthService.register(test_username, test_email, test_password)
    print(f"注册结果: {result}")
    
    # 从数据库查询用户
    user = db.get_user_by_email(test_email)
    if user:
        print(f"✓ 用户成功保存到数据库")
        print(f"  用户名: {user['username']}")
        print(f"  邮箱: {user['email']}")
        print(f"  创建时间: {user['created_at']}")
        print(f"  首次登录: {user['is_first_login']}")
        print(f"  资料完成: {user['profile_completed']}")
    else:
        print("✗ 用户未能保存到数据库")
        return False
    
    print()
    return True


def test_login():
    """测试登录功能"""
    print("=" * 50)
    print("测试2: 用户登录")
    print("=" * 50)
    
    test_email = "persistent_test@example.com"
    test_password = "TestPassword123"
    
    # 使用邮箱登录
    result = AuthService.login(test_email, test_password)
    print(f"邮箱登录结果: {result['success']}")
    
    if result['success']:
        print(f"✓ 登录成功")
        print(f"  Token: {result['token'][:15]}...")
        print(f"  用户名: {result['user']['username']}")
        
        # 验证token
        user_info = AuthService.verify_token(result['token'])
        if user_info:
            print(f"✓ Token验证成功")
            print(f"  用户信息: {user_info}")
        else:
            print(f"✗ Token验证失败")
            return False
    else:
        print(f"✗ 登录失败: {result['message']}")
        return False
    
    print()
    return True


def test_persistence():
    """测试数据持久化"""
    print("=" * 50)
    print("测试3: 数据库持久化验证")
    print("=" * 50)
    
    test_email = "persistent_test@example.com"
    
    # 从数据库直接查询（最直接的持久化测试）
    user = db.get_user_by_email(test_email)
    
    if user:
        print(f"✓ 用户信息从数据库成功检索")
        print(f"  用户ID: {user['id']}")
        print(f"  用户名: {user['username']}")
        print(f"  邮箱: {user['email']}")
        print(f"  注册时间: {user['created_at']}")
        
        # 验证密码哈希确实被保存了
        if user['password'] and len(user['password']) == 64:  # SHA256哈希长度为64
            print(f"✓ 密码已正确哈希并保存")
        else:
            print(f"✗ 密码哈希异常")
            return False
            
    else:
        print(f"✗ 无法从数据库检索用户")
        return False
    
    print()
    return True


def test_duplicate_registration():
    """测试重复注册防护"""
    print("=" * 50)
    print("测试4: 重复注册防护")
    print("=" * 50)
    
    test_email = "persistent_test@example.com"
    test_username = "another_name"
    test_password = "AnotherPassword456"
    
    # 尝试使用相同邮箱注册
    result = AuthService.register(test_username, test_email, test_password)
    print(f"重复邮箱注册结果: {result}")
    
    if not result['success'] and "已被注册" in result['message']:
        print(f"✓ 正确阻止了重复注册")
    else:
        print(f"✗ 未能正确防止重复注册")
        return False
    
    print()
    return True


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║         用户数据库持久化功能测试程序          ║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    results = []
    
    try:
        results.append(("用户注册", test_registration()))
        results.append(("用户登录", test_login()))
        results.append(("数据持久化", test_persistence()))
        results.append(("重复注册防护", test_duplicate_registration()))
        
        print("=" * 50)
        print("测试汇总")
        print("=" * 50)
        
        for name, passed in results:
            status = "✓ 通过" if passed else "✗ 失败"
            print(f"{status}: {name}")
        
        all_passed = all(r[1] for r in results)
        print()
        
        if all_passed:
            print("╔" + "=" * 48 + "╗")
            print("║               所有测试均已通过! ✓              ║")
            print("║          用户信息已成功持久化保存!            ║")
            print("╚" + "=" * 48 + "╝")
        else:
            print("╔" + "=" * 48 + "╗")
            print("║             某些测试失败，请检查!              ║")
            print("╚" + "=" * 48 + "╝")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ 测试期间发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
