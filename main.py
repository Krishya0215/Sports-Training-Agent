"""
运动训练知识问答Agent - 主程序
"""
import sys
from agent.graph_agent import SportsTrainingAgent
from utils.logger_handler import logger


def main():
    """主函数"""
    print("=" * 80)
    print("运动训练知识问答Agent")
    print("基于LangChain + LangGraph + 多层次记忆管理")
    print("=" * 80)
    
    # 初始化Agent
    print("\n正在初始化Agent...")
    agent = SportsTrainingAgent()
    print("✓ Agent初始化完成")
    
    # 显示菜单
    while True:
        print("\n" + "=" * 80)
        print("请选择操作:")
        print("1. 加载知识库（首次使用或更新知识库时）")
        print("2. 开始问答")
        print("3. 查看记忆摘要")
        print("4. 清空工作记忆")
        print("5. 退出")
        print("=" * 80)
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == "1":
            print("\n正在加载知识库...")
            try:
                agent.load_knowledge_base()
                print("✓ 知识库加载完成")
            except Exception as e:
                print(f"✗ 知识库加载失败: {e}")
                logger.error(f"知识库加载失败: {e}")
        
        elif choice == "2":
            print("\n进入问答模式（输入 'quit' 返回主菜单）")
            print("-" * 80)
            
            while True:
                question = input("\n请输入您的问题: ").strip()
                
                if question.lower() == 'quit':
                    break
                
                if not question:
                    print("问题不能为空，请重新输入")
                    continue
                
                print("\n正在思考...")
                try:
                    answer = agent.query(question)
                    print("\n" + "=" * 80)
                    print("回答:")
                    print(answer)
                    print("=" * 80)
                except Exception as e:
                    print(f"\n✗ 处理问题时出错: {e}")
                    logger.error(f"查询失败: {e}")
        
        elif choice == "3":
            print("\n记忆摘要:")
            print("-" * 80)
            summary = agent.get_memory_summary()
            for key, value in summary.items():
                print(f"{key}: {value}")
            print("-" * 80)
        
        elif choice == "4":
            agent.clear_working_memory()
            print("\n✓ 工作记忆已清空")
        
        elif choice == "5":
            print("\n感谢使用，再见！")
            sys.exit(0)
        
        else:
            print("\n✗ 无效选项，请重新选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        print(f"\n程序异常退出: {e}")
        sys.exit(1)
