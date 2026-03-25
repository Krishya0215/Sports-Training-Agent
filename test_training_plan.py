"""
测试训练计划功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_training_plan():
    """测试创建训练计划"""
    print("测试创建训练计划...")
    
    plan_data = {
        "title": "测试训练计划",
        "content": "这是一个测试训练计划\n包含多个训练项目",
        "goal": "增肌",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "created_from_ai": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/training/plans", json=plan_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 创建训练计划成功")
            return response.json()["plan"]["id"]
        else:
            print("❌ 创建训练计划失败")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_get_training_plans():
    """测试获取训练计划列表"""
    print("\n测试获取训练计划列表...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/training/plans")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"总计划数: {data.get('total', 0)}")
        print(f"计划列表: {json.dumps(data.get('plans', []), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200 and data.get("plans"):
            print("✅ 获取训练计划列表成功")
            return True
        else:
            print("❌ 获取训练计划列表失败或为空")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_get_single_plan(plan_id):
    """测试获取单个训练计划"""
    print(f"\n测试获取单个训练计划 (ID: {plan_id})...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/training/plans/{plan_id}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 获取单个训练计划成功")
            return True
        else:
            print("❌ 获取单个训练计划失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_delete_plan(plan_id):
    """测试删除训练计划"""
    print(f"\n测试删除训练计划 (ID: {plan_id})...")
    
    try:
        response = requests.delete(f"{BASE_URL}/api/training/plans/{plan_id}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 删除训练计划成功")
            return True
        else:
            print("❌ 删除训练计划失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("训练计划功能测试")
    print("=" * 60)
    
    # 确保后端服务正在运行
    print("请确保后端服务正在运行 (python backend/api.py)")
    input("按Enter键开始测试...")
    
    # 测试1: 创建训练计划
    plan_id = test_create_training_plan()
    
    if plan_id:
        # 测试2: 获取训练计划列表
        test_get_training_plans()
        
        # 测试3: 获取单个训练计划
        test_get_single_plan(plan_id)
        
        # 测试4: 删除训练计划
        test_delete_plan(plan_id)
        
        # 再次获取列表确认删除
        test_get_training_plans()
    else:
        print("❌ 无法继续测试，因为创建计划失败")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()