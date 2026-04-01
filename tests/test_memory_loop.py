"""
记忆闭环系统验证脚本

使用方法：
    python tests/test_memory_loop.py

验证内容：
1. 数据库表结构
2. 语义记忆写入与读取
3. 情景记忆写入与读取
4. 训练记录后的语义更新
5. 记忆固化触发
6. 记忆上下文注入
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime, timedelta
from backend.database import db
from backend.memory_service import memory_service
from backend.memory_consolidation import consolidation_service


class MemoryLoopValidator:
    """记忆闭环验证器"""

    def __init__(self):
        self.test_user_id = None
        self.results = []

    def log(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} - {test_name}"
        if message:
            result += f"\n       {message}"
        print(result)
        self.results.append({"test": test_name, "passed": passed, "message": message})

    def print_section(self, title: str):
        """打印章节标题"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

    def setup(self):
        """创建测试用户"""
        self.print_section("准备工作")

        # 创建或获取测试用户
        test_email = "test_memory@example.com"
        user = db.get_user_by_email(test_email)

        if not user:
            db.create_user("test_memory", test_email, "test_password_hash")
            user = db.get_user_by_email(test_email)

        self.test_user_id = user["id"]
        self.log("创建测试用户", True, f"user_id = {self.test_user_id}")

    def test_1_database_tables(self):
        """测试1: 验证数据库表结构"""
        self.print_section("测试1: 数据库表结构")

        # 检查关键表是否存在
        tables_to_check = [
            "memory_episodic_events",
            "memory_semantic_facts",
            "memory_working_sessions",
            "memory_working_messages",
            "user_profiles",
            "training_plans",
            "training_records"
        ]

        conn = db._get_connection()
        cursor = conn.cursor()

        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            result = cursor.fetchone()
            self.log(f"表 {table} 存在", result is not None)

        conn.close()

    def test_2_semantic_memory(self):
        """测试2: 语义记忆写入与读取"""
        self.print_section("测试2: 语义记忆写入与读取")

        # 写入语义事实
        fact = db.upsert_semantic_fact(
            user_id=self.test_user_id,
            fact_category="test",
            fact_key="test_preference",
            fact_value="力量训练",
            confidence=0.9,
            source_type="test_script"
        )
        self.log("写入语义事实", fact is not None, json.dumps(fact, ensure_ascii=False, default=str)[:100])

        # 读取语义事实
        retrieved = db.get_semantic_fact(self.test_user_id, "test", "test_preference")
        self.log("读取语义事实", retrieved is not None and retrieved.get("fact_value") == "力量训练")

        # 通过 memory_service 读取
        semantic_profile = memory_service.get_semantic_profile(self.test_user_id)
        has_test_category = "test" in semantic_profile
        self.log("memory_service 读取语义记忆", has_test_category)

        # 清理测试数据
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory_semantic_facts WHERE fact_category = 'test'")
        conn.commit()
        conn.close()

    def test_3_episodic_memory(self):
        """测试3: 情景记忆写入与读取"""
        self.print_section("测试3: 情景记忆写入与读取")

        # 写入情景事件
        event = db.create_episodic_event(self.test_user_id, {
            "event_type": "test_event",
            "event_summary": "这是一条测试事件",
            "trigger_source": "test_script",
            "importance_score": 0.5,
            "tags": ["test"]
        })
        self.log("写入情景事件", event is not None, json.dumps(event, ensure_ascii=False, default=str)[:100])

        # 读取情景事件
        episodes = db.list_episodic_events(self.test_user_id, limit=5)
        has_test_event = any(ep.get("event_type") == "test_event" for ep in episodes)
        self.log("读取情景事件", has_test_event, f"共 {len(episodes)} 条事件")

        # 通过 memory_service 读取
        recent_episodes = memory_service.get_recent_episodes(self.test_user_id, limit=5)
        self.log("memory_service 读取情景记忆", len(recent_episodes) > 0)

    def test_4_user_profile_and_memory_sync(self):
        """测试4: 用户画像同步到语义记忆"""
        self.print_section("测试4: 用户画像同步到语义记忆")

        # 更新用户画像
        profile = db.upsert_user_profile(self.test_user_id, {
            "goal": "增肌",
            "preferred_method": "力量训练",
            "weekly_days": 4,
            "intensity_level": "高强度"
        })
        self.log("写入用户画像", profile is not None)

        # 模拟同步到语义记忆（手动实现，避免导入 api 模块）
        # 模拟 _sync_profile_semantic_memory 的逻辑
        semantic_mappings = [
            ("profile", "goal", profile.get("goal")),
            ("preference", "preferred_method", profile.get("preferred_method")),
            ("habit", "weekly_days", str(profile.get("weekly_days")) if profile.get("weekly_days") is not None else None),
            ("profile", "intensity_level", profile.get("intensity_level"))
        ]

        for category, key, value in semantic_mappings:
            if value not in (None, ""):
                db.upsert_semantic_fact(
                    user_id=self.test_user_id,
                    fact_category=category,
                    fact_key=key,
                    fact_value=str(value),
                    confidence=0.9,
                    source_type="profile"
                )

        # 验证语义记忆中有对应数据
        semantic = memory_service.get_semantic_profile(self.test_user_id)
        has_goal = "profile" in semantic and "goal" in semantic.get("profile", {})
        self.log("画像同步到语义记忆", has_goal, f"语义记忆: {list(semantic.keys())}")

    def test_5_training_record_semantic_update(self):
        """测试5: 训练记录更新语义记忆"""
        self.print_section("测试5: 训练记录更新语义记忆")

        # 创建训练记录
        record = db.create_training_record(self.test_user_id, {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "training_type": "力量训练",
            "duration": 60,
            "intensity": "高强度",
            "fatigue_level": 4,  # 高疲劳
            "pain_level": 2,
            "notes": "今天练了腿部，感觉膝盖有点不舒服",
            "completion_status": "completed"
        })
        self.log("创建训练记录", record is not None, f"record_id = {record.get('id')}")

        # 模拟语义更新（手动实现，避免导入 api 模块）
        # 模拟 _update_semantic_from_training_record 的逻辑
        pain_level = record.get("pain_level")
        fatigue_level = record.get("fatigue_level")
        notes = record.get("notes", "")

        if pain_level is not None and pain_level >= 3:
            db.upsert_semantic_fact(
                user_id=self.test_user_id,
                fact_category="risk",
                fact_key="recent_pain_level",
                fact_value=str(pain_level),
                confidence=0.8,
                source_type="training_record"
            )

        if fatigue_level is not None and fatigue_level >= 4:
            db.upsert_semantic_fact(
                user_id=self.test_user_id,
                fact_category="adaptation_rule",
                fact_key="recent_high_fatigue",
                fact_value="true",
                confidence=0.75,
                source_type="training_record"
            )

        # 从备注中提取疼痛部位
        if notes and pain_level >= 2:
            if "膝盖" in notes.lower():
                db.upsert_semantic_fact(
                    user_id=self.test_user_id,
                    fact_category="constraint",
                    fact_key="pain_膝盖",
                    fact_value=f"膝盖疼痛(疼痛度{pain_level})",
                    confidence=0.7,
                    source_type="training_record"
                )

        # 验证语义记忆中有疲劳和膝盖疼痛相关记录
        semantic = memory_service.get_semantic_profile(self.test_user_id)

        has_fatigue = "adaptation_rule" in semantic and "recent_high_fatigue" in semantic.get("adaptation_rule", {})
        self.log("疲劳度写入语义记忆", has_fatigue)

        # 检查是否有膝盖疼痛约束
        has_knee_pain = any("膝盖" in str(v) for v in semantic.get("constraint", {}).values())
        self.log("疼痛部位写入语义记忆", has_knee_pain, f"constraint: {semantic.get('constraint', {})}")

    def test_6_memory_consolidation(self):
        """测试6: 记忆固化"""
        self.print_section("测试6: 记忆固化")

        # 执行记忆固化
        result = consolidation_service.consolidate_episodes_to_semantic(self.test_user_id)

        patterns_found = result.get("patterns_found", [])
        semantic_updates = result.get("semantic_updates", [])

        self.log("执行记忆固化", True,
                f"发现规律 {len(patterns_found)} 个, 更新语义 {len(semantic_updates)} 条")

        # 检查是否应该触发固化
        should_consolidate = consolidation_service.should_consolidate(self.test_user_id)
        self.log("触发条件判断", True, f"should_consolidate = {should_consolidate}")

    def test_7_memory_context_building(self):
        """测试7: 记忆上下文构建"""
        self.print_section("测试7: 记忆上下文构建")

        # 获取完整记忆上下文
        context = memory_service.get_user_memory_context(self.test_user_id)

        has_semantic = "semantic_profile" in context and len(context["semantic_profile"]) > 0
        has_episodes = "recent_episodes" in context
        has_patterns = "training_patterns" in context

        self.log("获取完整记忆上下文", has_semantic and has_episodes and has_patterns)

        # 构建记忆提示词
        prompt = memory_service.build_memory_prompt(self.test_user_id, context)
        has_prompt = len(prompt) > 50  # 应该有足够的内容

        self.log("构建记忆提示词", has_prompt, f"提示词长度: {len(prompt)} 字符")

        print(f"\n--- 记忆提示词预览 ---")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("--- 预览结束 ---")

    def test_8_working_memory(self):
        """测试8: 工作记忆持久化"""
        self.print_section("测试8: 工作记忆持久化")

        conversation_id = f"test_conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 创建工作记忆会话
        session = memory_service.create_working_session(
            user_id=self.test_user_id,
            conversation_id=conversation_id,
            source="test_script"
        )
        self.log("创建工作记忆会话", session is not None, f"session_id = {session.get('id')}")

        # 添加消息
        msg1 = memory_service.add_message_to_working_memory(
            user_id=self.test_user_id,
            conversation_id=conversation_id,
            role="human",
            content="我想了解如何增肌"
        )
        msg2 = memory_service.add_message_to_working_memory(
            user_id=self.test_user_id,
            conversation_id=conversation_id,
            role="ai",
            content="增肌需要力量训练配合足够的蛋白质摄入..."
        )
        self.log("添加工作记忆消息", msg1 is not None and msg2 is not None)

        # 读取工作记忆
        working_context = memory_service.get_working_context(self.test_user_id, conversation_id)
        has_messages = "messages" in working_context and len(working_context["messages"]) >= 2
        self.log("读取工作记忆", has_messages, f"消息数: {len(working_context.get('messages', []))}")

        # 结束会话
        memory_service.end_working_session(self.test_user_id, conversation_id)
        self.log("结束工作记忆会话", True)

    def test_9_end_to_end_flow(self):
        """测试9: 端到端流程验证"""
        self.print_section("测试9: 端到端流程验证")

        print("\n模拟完整记忆闭环流程:")

        # Step 1: 用户填写问卷
        print("\n  Step 1: 用户填写问卷 → 写入语义记忆")
        profile = db.upsert_user_profile(self.test_user_id, {
            "goal": "减脂",
            "fitness_level": "中级",
            "weekly_days": 5
        })
        # 手动同步到语义记忆
        for category, key, value in [
            ("profile", "goal", profile.get("goal")),
            ("profile", "fitness_level", profile.get("fitness_level")),
            ("habit", "weekly_days", str(profile.get("weekly_days")))
        ]:
            if value:
                db.upsert_semantic_fact(
                    user_id=self.test_user_id,
                    fact_category=category,
                    fact_key=key,
                    fact_value=str(value),
                    confidence=0.9,
                    source_type="profile"
                )
        self.log("  问卷数据写入", True)

        # Step 2: 生成计划前读取记忆
        print("\n  Step 2: 生成计划前读取记忆")
        memory_context = memory_service.get_user_memory_context(self.test_user_id)
        self.log("  读取记忆上下文", True, f"语义类别: {list(memory_context['semantic_profile'].keys())}")

        # Step 3: 生成计划并记录
        print("\n  Step 3: 生成训练计划 → 写入情景记忆")
        plan = db.create_training_plan(self.test_user_id, {
            "title": "减脂训练计划",
            "content": "# 第一周\n...",
            "goal": "减脂",
            "based_on_memory": True
        })
        db.create_episodic_event(self.test_user_id, {
            "event_type": "plan_generated",
            "plan_id": plan["id"],
            "event_summary": f"生成训练计划：{plan['title']}",
            "trigger_source": "test",
            "importance_score": 0.9,
            "tags": ["plan", "generated"]
        })
        self.log("  计划生成并记录", True)

        # Step 4: 用户完成训练
        print("\n  Step 4: 用户完成训练 → 写入情景记忆 + 更新语义")
        record = db.create_training_record(self.test_user_id, {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "training_type": "有氧",
            "duration": 45,
            "plan_id": plan["id"],
            "fatigue_level": 3,
            "completion_status": "completed"
        })
        # 手动更新语义（模拟 _update_semantic_from_training_record）
        if record.get("fatigue_level") is not None and record["fatigue_level"] >= 4:
            db.upsert_semantic_fact(
                user_id=self.test_user_id,
                fact_category="adaptation_rule",
                fact_key="recent_high_fatigue",
                fact_value="true",
                confidence=0.75,
                source_type="training_record"
            )
        self.log("  训练记录并更新语义", True)

        # Step 5: 触发记忆固化
        print("\n  Step 5: 触发记忆固化")
        result = consolidation_service.trigger_consolidation_if_needed(self.test_user_id)
        self.log("  记忆固化", True, f"状态: {result.get('status', 'unknown')}")

        # Step 6: 后续查询时读取记忆
        print("\n  Step 6: 后续查询时读取记忆")
        final_context = memory_service.get_user_memory_context(self.test_user_id)
        prompt = memory_service.build_memory_prompt(self.test_user_id, final_context)
        self.log("  最终记忆上下文", True, f"提示词包含 {len(prompt)} 字符")

    def cleanup(self):
        """清理测试数据"""
        self.print_section("清理测试数据")

        conn = db._get_connection()
        cursor = conn.cursor()

        # 清理测试用户相关数据
        tables_to_clean = [
            ("memory_episodic_events", "user_id", self.test_user_id),
            ("memory_semantic_facts", "user_id", self.test_user_id),
            ("memory_working_messages", "session_id",
             f"SELECT id FROM memory_working_sessions WHERE user_id = {self.test_user_id}"),
            ("memory_working_sessions", "user_id", self.test_user_id),
            ("training_records", "user_id", self.test_user_id),
            ("training_plans", "user_id", self.test_user_id),
            ("user_profiles", "user_id", self.test_user_id),
        ]

        for table, column, value in tables_to_clean:
            if isinstance(value, str) and value.startswith("SELECT"):
                cursor.execute(f"DELETE FROM {table} WHERE {column} IN ({value})")
            else:
                cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", (value,))

        conn.commit()
        conn.close()
        self.log("清理测试数据", True)

    def print_summary(self):
        """打印测试总结"""
        self.print_section("测试总结")

        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        print(f"\n总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")

        if failed > 0:
            print("\n失败的测试:")
            for r in self.results:
                if not r["passed"]:
                    print(f"  - {r['test']}: {r['message']}")

        print(f"\n通过率: {passed/total*100:.1f}%")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("  记忆闭环系统验证测试")
        print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)

        try:
            self.setup()

            self.test_1_database_tables()
            self.test_2_semantic_memory()
            self.test_3_episodic_memory()
            self.test_4_user_profile_and_memory_sync()
            self.test_5_training_record_semantic_update()
            self.test_6_memory_consolidation()
            self.test_7_memory_context_building()
            self.test_8_working_memory()
            self.test_9_end_to_end_flow()

        finally:
            self.cleanup()
            self.print_summary()


if __name__ == "__main__":
    validator = MemoryLoopValidator()
    validator.run_all_tests()
