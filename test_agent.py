"""
Agent测试脚本
"""
from agent.graph_agent import SportsTrainingAgent
from utils.logger_handler import logger


def test_basic_query():
    """测试基础查询功能"""
    print("\n" + "=" * 80)
    print("测试1: 基础查询功能")
    print("=" * 80)
    
    agent = SportsTrainingAgent()
    
    questions = [
        "什么是有氧运动？",
        "如何进行深蹲训练？",
        "运动后应该如何拉伸？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题{i}: {question}")
        print("-" * 80)
        try:
            answer = agent.query(question)
            print(f"答案: {answer}")
        except Exception as e:
            print(f"错误: {e}")
            logger.error(f"查询失败: {e}")
        print("-" * 80)


def test_context_awareness():
    """测试上下文感知能力"""
    print("\n" + "=" * 80)
    print("测试2: 上下文感知能力")
    print("=" * 80)
    
    agent = SportsTrainingAgent()
    
    # 连续对话
    conversation = [
        "什么是力量训练？",
        "它有什么好处？",  # 测试代词理解
        "给我推荐一些动作"  # 测试上下文延续
    ]
    
    for i, question in enumerate(conversation, 1):
        print(f"\n轮次{i}: {question}")
        print("-" * 80)
        try:
            answer = agent.query(question)
            print(f"答案: {answer}")
        except Exception as e:
            print(f"错误: {e}")
        print("-" * 80)


def test_memory_system():
    """测试记忆系统"""
    print("\n" + "=" * 80)
    print("测试3: 记忆系统")
    print("=" * 80)
    
    agent = SportsTrainingAgent()
    
    # 进行几次查询
    questions = [
        "什么是有氧运动？",
        "如何进行力量训练？"
    ]
    
    for question in questions:
        agent.query(question)
    
    # 查看记忆摘要
    print("\n记忆摘要:")
    print("-" * 80)
    summary = agent.get_memory_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("-" * 80)
    
    # 测试工作记忆
    print("\n工作记忆内容:")
    print("-" * 80)
    context = agent.memory_manager.get_context_for_query()
    print(context if context else "工作记忆为空")
    print("-" * 80)
    
    # 清空工作记忆
    print("\n清空工作记忆...")
    agent.clear_working_memory()
    
    # 再次查看
    print("\n清空后的工作记忆:")
    print("-" * 80)
    context = agent.memory_manager.get_context_for_query()
    print(context if context else "工作记忆为空")
    print("-" * 80)


def test_advanced_retrieval():
    """测试高级检索功能"""
    print("\n" + "=" * 80)
    print("测试4: 高级检索功能 (MQE + HyDE)")
    print("=" * 80)
    
    agent = SportsTrainingAgent()
    
    # 测试复杂查询
    complex_questions = [
        "我想减肥，应该做什么运动？",
        "如何避免运动损伤？",
        "运动后吃什么比较好？"
    ]
    
    for i, question in enumerate(complex_questions, 1):
        print(f"\n复杂问题{i}: {question}")
        print("-" * 80)
        try:
            answer = agent.query(question)
            print(f"答案: {answer}")
        except Exception as e:
            print(f"错误: {e}")
        print("-" * 80)


def test_knowledge_loading():
    """测试知识库加载"""
    print("\n" + "=" * 80)
    print("测试5: 知识库加载")
    print("=" * 80)
    
    agent = SportsTrainingAgent()
    
    print("\n开始加载知识库...")
    try:
        agent.load_knowledge_base()
        print("✓ 知识库加载成功")
    except Exception as e:
        print(f"✗ 知识库加载失败: {e}")
        logger.error(f"知识库加载失败: {e}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("运动训练知识问答Agent - 测试套件")
    print("=" * 80)
    
    tests = [
        ("知识库加载", test_knowledge_loading),
        ("基础查询", test_basic_query),
        ("上下文感知", test_context_awareness),
        ("记忆系统", test_memory_system),
        ("高级检索", test_advanced_retrieval)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n\n{'=' * 80}")
            print(f"开始测试: {test_name}")
            print(f"{'=' * 80}")
            test_func()
            print(f"\n✓ {test_name} 测试完成")
        except Exception as e:
            print(f"\n✗ {test_name} 测试失败: {e}")
            logger.error(f"{test_name} 测试失败: {e}")
    
    print("\n\n" + "=" * 80)
    print("所有测试完成")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        test_map = {
            "basic": test_basic_query,
            "context": test_context_awareness,
            "memory": test_memory_system,
            "retrieval": test_advanced_retrieval,
            "loading": test_knowledge_loading,
            "all": run_all_tests
        }
        
        if test_name in test_map:
            test_map[test_name]()
        else:
            print(f"未知测试: {test_name}")
            print(f"可用测试: {', '.join(test_map.keys())}")
    else:
        # 默认运行所有测试
        run_all_tests()
