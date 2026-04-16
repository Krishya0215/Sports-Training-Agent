"""
记忆服务模块 - 统一的记忆读取接口
用于从语义记忆、情景记忆、工作记忆中获取用户上下文
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from backend.api.database import db
from backend.utils.logger_handler import logger


class MemoryService:
    """记忆服务 - 提供统一的记忆读取接口"""

    def __init__(self):
        self.logger = logger

    def get_user_memory_context(self, user_id: int, include_working: bool = False) -> Dict[str, Any]:
        """
        获取用户的完整记忆上下文

        Args:
            user_id: 用户ID
            include_working: 是否包含工作记忆

        Returns:
            记忆上下文字典
        """
        context = {
            "semantic_profile": self.get_semantic_profile(user_id),
            "recent_episodes": self.get_recent_episodes(user_id, limit=10),
            "training_patterns": self.get_training_patterns(user_id),
            "user_profile": db.get_user_profile(user_id) or {}
        }

        if include_working:
            context["working_context"] = self.get_working_context(user_id)

        self.logger.debug(f"获取用户记忆上下文: user_id={user_id}, "
                         f"semantic_facts={len(context['semantic_profile'])}, "
                         f"episodes={len(context['recent_episodes'])}")
        return context

    def get_semantic_profile(self, user_id: int) -> Dict[str, Dict[str, Any]]:
        """
        获取语义记忆中的用户画像

        按类别组织：
        - profile: 目标、水平等
        - preference: 训练偏好
        - habit: 训练习惯
        - constraint: 约束条件（伤病等）
        - risk: 风险因素
        - adaptation_rule: 适应性规则

        Returns:
            按类别分组的语义事实字典
        """
        facts = db.list_semantic_facts(user_id)
        profile = defaultdict(dict)

        for fact in facts:
            category = fact.get("fact_category")
            key = fact.get("fact_key")
            value = fact.get("fact_value")
            confidence = fact.get("confidence", 0.5)

            if category and key and value:
                profile[category][key] = {
                    "value": value,
                    "confidence": confidence,
                    "updated_at": fact.get("updated_at")
                }

        return dict(profile)

    def get_recent_episodes(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的情景事件

        Args:
            user_id: 用户ID
            limit: 获取数量

        Returns:
            最近情景事件列表
        """
        episodes = db.list_episodic_events(user_id, limit=limit)
        return episodes

    def get_episodes_by_type(self, user_id: int, event_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        按类型获取情景事件

        Args:
            user_id: 用户ID
            event_type: 事件类型 (training_completed, plan_generated, coach_chat等)
            limit: 获取数量

        Returns:
            指定类型的情景事件列表
        """
        episodes = db.list_episodic_events(user_id, event_type=event_type, limit=limit)
        return episodes

    def get_training_patterns(self, user_id: int) -> Dict[str, Any]:
        """
        获取训练相关规律

        分析：
        - 训练频率趋势
        - 偏好训练类型
        - 疲劳/疼痛模式
        - 时段偏好
        - 完成率统计

        Returns:
            训练规律字典
        """
        patterns = {
            "frequency": self._analyze_training_frequency(user_id),
            "type_preference": self._analyze_training_type_preference(user_id),
            "fatigue_pattern": self._analyze_fatigue_pattern(user_id),
            "completion_rate": self._analyze_completion_rate(user_id),
            "risk_factors": self._identify_risk_factors(user_id)
        }

        return patterns

    def _analyze_training_frequency(self, user_id: int) -> Dict[str, Any]:
        """分析训练频率"""
        now = datetime.now()
        recent_records = [
            r for r in db.list_training_records(user_id)
            if datetime.fromisoformat(r["date"]) >= now - timedelta(days=30)
        ]

        if not recent_records:
            return {"status": "no_data"}

        # 按周统计
        weekly_counts = defaultdict(int)
        for record in recent_records:
            week_start = (datetime.fromisoformat(record["date"]) - timedelta(days=datetime.fromisoformat(record["date"]).weekday())).date()
            weekly_counts[week_start] += 1

        avg_weekly = sum(weekly_counts.values()) / len(weekly_counts) if weekly_counts else 0

        return {
            "avg_weekly_sessions": round(avg_weekly, 1),
            "total_last_30_days": len(recent_records),
            "recent_trend": "stable"  # 可以进一步计算趋势
        }

    def _analyze_training_type_preference(self, user_id: int) -> Dict[str, Any]:
        """分析训练类型偏好"""
        records = db.list_training_records(user_id)

        if not records:
            return {"status": "no_data"}

        type_counts = defaultdict(int)
        for record in records:
            training_type = record.get("training_type", "unknown")
            type_counts[training_type] += 1

        total = sum(type_counts.values())
        preferences = [
            {"type": t, "count": c, "percentage": round(c / total * 100, 1)}
            for t, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "most_common": preferences[0]["type"] if preferences else None,
            "distribution": preferences[:5]  # 最多返回前5种
        }

    def _analyze_fatigue_pattern(self, user_id: int) -> Dict[str, Any]:
        """分析疲劳模式"""
        recent_records = [
            r for r in db.list_training_records(user_id)[:20]
            if r.get("fatigue_level") is not None
        ]

        if not recent_records:
            return {"status": "no_data"}

        fatigue_levels = [r.get("fatigue_level") for r in recent_records]
        avg_fatigue = sum(fatigue_levels) / len(fatigue_levels)

        # 统计高疲劳次数
        high_fatigue_count = sum(1 for f in fatigue_levels if f >= 4)

        return {
            "avg_fatigue": round(avg_fatigue, 1),
            "high_fatigue_count": high_fatigue_count,
            "recent_trend": "high" if avg_fatigue >= 4 else "moderate" if avg_fatigue >= 2 else "low"
        }

    def _analyze_completion_rate(self, user_id: int) -> Dict[str, Any]:
        """分析完成率"""
        records = db.list_training_records(user_id)[:50]

        if not records:
            return {"status": "no_data"}

        completed = sum(1 for r in records if r.get("completion_status") == "completed")
        skipped = sum(1 for r in records if r.get("completion_status") == "skipped")

        total = completed + skipped
        completion_rate = (completed / total * 100) if total > 0 else 0

        return {
            "completion_rate": round(completion_rate, 1),
            "completed_count": completed,
            "skipped_count": skipped
        }

    def _identify_risk_factors(self, user_id: int) -> List[str]:
        """识别风险因素"""
        risks = []

        # 从语义记忆中获取
        semantic = self.get_semantic_profile(user_id)
        if "risk" in semantic:
            risks.extend(semantic["risk"].keys())

        # 从训练记录分析
        recent_records = db.list_training_records(user_id)[:30]
        recent_pain = [r.get("pain_level") for r in recent_records if r.get("pain_level") is not None]

        if recent_pain and sum(recent_pain) / len(recent_pain) >= 3:
            risks.append("high_avg_pain")

        return list(set(risks))  # 去重

    def get_working_context(self, user_id: int, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取工作记忆上下文

        Args:
            user_id: 用户ID
            conversation_id: 对话ID（可选）

        Returns:
            工作记忆上下文
        """
        if not conversation_id:
            return {
                "session_id": None,
                "messages": []
            }

        # 从数据库获取工作记忆
        return db.get_working_context(user_id, conversation_id)

    def create_working_session(
        self,
        user_id: int,
        conversation_id: str,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建新的工作记忆会话

        Args:
            user_id: 用户ID
            conversation_id: 对话ID
            source: 来源（chat/plan等）

        Returns:
            会话信息
        """
        return db.create_working_session(user_id, conversation_id, source)

    def add_message_to_working_memory(
        self,
        user_id: int,
        conversation_id: str,
        role: str,
        content: str,
        message_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        向工作记忆添加消息

        Args:
            user_id: 用户ID
            conversation_id: 对话ID
            role: 角色（human/ai）
            content: 消息内容
            message_type: 消息类型

        Returns:
            消息信息
        """
        # 确保会话存在
        session = db.get_working_session(user_id, conversation_id)
        if not session:
            session = db.create_working_session(user_id, conversation_id, source="chat")

        return db.add_working_message(session["id"], role, content, message_type)

    def end_working_session(
        self,
        user_id: int,
        conversation_id: str
    ) -> bool:
        """
        结束工作记忆会话

        Args:
            user_id: 用户ID
            conversation_id: 对话ID

        Returns:
            是否成功
        """
        return db.end_working_session(user_id, conversation_id)

    def build_memory_prompt(self, user_id: int, context: Optional[Dict[str, Any]] = None) -> str:
        """
        构建注入LLM的记忆提示词

        Args:
            user_id: 用户ID
            context: 预先获取的上下文（可选，如不传则重新获取）

        Returns:
            格式化的记忆提示词字符串
        """
        if context is None:
            context = self.get_user_memory_context(user_id)

        prompt_parts = ["【用户画像与偏好】"]

        # 语义记忆部分
        semantic = context.get("semantic_profile", {})

        # 目标与水平
        if "profile" in semantic:
            profile_facts = []
            for key, info in semantic["profile"].items():
                profile_facts.append(f"{key}: {info['value']}")
            if profile_facts:
                prompt_parts.append(f"- 基本信息: {', '.join(profile_facts)}")

        # 训练偏好
        if "preference" in semantic or "habit" in semantic:
            pref_facts = []
            for category in ["preference", "habit"]:
                if category in semantic:
                    for key, info in semantic[category].items():
                        pref_facts.append(f"{key}: {info['value']}")
            if pref_facts:
                prompt_parts.append(f"- 偏好与习惯: {', '.join(pref_facts)}")

        # 约束条件
        if "constraint" in semantic:
            constraints = []
            for key, info in semantic["constraint"].items():
                constraints.append(f"{key}: {info['value']}")
            if constraints:
                prompt_parts.append(f"- 约束条件: {', '.join(constraints)}")

        # 训练规律
        patterns = context.get("training_patterns", {})
        if patterns:
            prompt_parts.append("\n【训练规律】")
            if patterns.get("frequency"):
                freq = patterns["frequency"]
                if freq.get("status") != "no_data":
                    prompt_parts.append(f"- 训练频率: 平均每周{freq.get('avg_weekly_sessions')}次")
            if patterns.get("type_preference"):
                pref = patterns["type_preference"]
                if pref.get("status") != "no_data" and pref.get("most_common"):
                    prompt_parts.append(f"- 常用类型: {pref.get('most_common')}")
            if patterns.get("fatigue_pattern"):
                fatigue = patterns["fatigue_pattern"]
                if fatigue.get("status") != "no_data":
                    prompt_parts.append(f"- 疲劳趋势: {fatigue.get('recent_trend')}")
            if patterns.get("risk_factors"):
                risks = patterns["risk_factors"]
                if risks:
                    prompt_parts.append(f"- 风险因素: {', '.join(risks)}")

        # 最近动态
        recent_episodes = context.get("recent_episodes", [])
        if recent_episodes:
            prompt_parts.append("\n【最近动态】")
            for ep in recent_episodes[:5]:  # 最多显示5条
                event_time = ep.get("event_time", "")[:10]  # 只取日期
                summary = ep.get("event_summary", ep.get("event_type", ""))
                prompt_parts.append(f"- {event_time}: {summary}")

        return "\n".join(prompt_parts) if len(prompt_parts) > 1 else "暂无用户记忆数据"


# 全局实例
memory_service = MemoryService()
