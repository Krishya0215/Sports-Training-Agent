"""
记忆写入机制 - 重要性评分

为每条情景事件计算 importance ∈ [0, 1] 的加权得分，仅当超过阈值时才允许进入长期记忆。
评分维度（与论文 3.3.2 节描述一致）：
    - core_goal     : 是否涉及用户核心训练目标
    - injury_risk   : 是否涉及伤病与安全风险
    - repeat_freq   : 是否被用户反复提及
    - decision_impact : 是否影响后续训练决策

四个维度均归一化到 [0, 1]，加权聚合产生最终 importance：
    importance = 0.30 * core_goal + 0.30 * injury_risk + 0.20 * repeat_freq + 0.20 * decision_impact
默认权重把"目标"和"安全"放在最高优先级。
"""
from typing import Dict, Any, Optional
from backend.api.database import db
from backend.utils.logger_handler import logger


# 评分维度的权重（论文公式 4-1）
WEIGHTS = {
    "core_goal": 0.30,
    "injury_risk": 0.30,
    "repeat_freq": 0.20,
    "decision_impact": 0.20,
}

# 写入语义记忆的阈值；情景记忆不做硬筛，只为后续遗忘服务的衰减计算提供 importance 基线
SEMANTIC_WRITE_THRESHOLD = 0.5

# 不同事件类型的"决策影响"先验值
EVENT_DECISION_IMPACT = {
    "plan_created": 0.95,        # 训练计划生成 → 直接影响后续训练
    "plan_updated": 0.85,
    "training_completed": 0.75,  # 训练记录 → 影响下次负荷调整
    "training_skipped": 0.60,
    "health_recorded": 0.55,
    "diet_recorded": 0.40,
    "qa_interaction": 0.50,      # 普通问答
    "feedback_submitted": 0.70,
}

# 与核心训练目标相关的关键词
GOAL_KEYWORDS = (
    "目标", "增肌", "减脂", "塑形", "力量", "体能", "耐力",
    "马拉松", "比赛", "训练计划", "周期", "进步"
)

# 与伤病/安全风险相关的关键词
INJURY_KEYWORDS = (
    "伤", "疼", "痛", "酸", "拉伤", "扭伤", "骨折", "炎",
    "DOMS", "拉伤", "肌腱", "韧带", "膝盖", "腰", "肩", "禁忌",
    "风险", "危险", "不适", "晕", "心率过高"
)


class ImportanceScorer:
    """对单条事件做 4 维评分，给出 importance ∈ [0, 1]"""

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        threshold: float = SEMANTIC_WRITE_THRESHOLD,
    ):
        self.weights = weights or WEIGHTS
        self.threshold = threshold
        # 简单校验权重和约为 1
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-3:
            logger.warning(f"ImportanceScorer 权重和不等于 1.0（={total:.4f}），评分将以权重原样加权")

    # ---------- 4 个维度的子打分 ----------

    def _score_core_goal(self, event: Dict[str, Any]) -> float:
        """是否涉及核心训练目标"""
        text = self._extract_text(event)
        if any(kw in text for kw in GOAL_KEYWORDS):
            return 0.9
        # 训练计划相关事件天然涉及目标
        if event.get("event_type", "").startswith("plan_"):
            return 0.8
        return 0.2

    def _score_injury_risk(self, event: Dict[str, Any]) -> float:
        """是否涉及伤病与安全风险"""
        text = self._extract_text(event)
        if any(kw in text for kw in INJURY_KEYWORDS):
            return 0.95
        # 从 payload 中查看疼痛/疲劳等级
        payload = event.get("payload") or {}
        pain = payload.get("pain_level", 0) or 0
        fatigue = payload.get("fatigue_level", 0) or 0
        if pain >= 6 or fatigue >= 8:
            return 0.85
        if pain >= 3 or fatigue >= 5:
            return 0.55
        return 0.1

    def _score_repeat_freq(self, event: Dict[str, Any]) -> float:
        """
        是否被用户反复提及：查询该用户近 30 天同 event_type 出现次数。
        次数越多得分越高，最高 0.9。
        """
        user_id = event.get("user_id")
        event_type = event.get("event_type")
        if user_id is None or event_type is None:
            return 0.3
        try:
            same_type_count = sum(
                1 for ev in db.list_episodic_events(user_id, event_type=event_type, limit=20)
            )
        except Exception:
            return 0.3
        # 0 次 → 0.2，5 次 → 0.7，10 次以上 → 0.9
        return min(0.9, 0.2 + 0.1 * same_type_count)

    def _score_decision_impact(self, event: Dict[str, Any]) -> float:
        """是否影响后续训练决策：以 event_type 先验为主"""
        et = event.get("event_type", "")
        return EVENT_DECISION_IMPACT.get(et, 0.35)

    # ---------- 总评分 + 接口 ----------

    def score(self, event: Dict[str, Any]) -> Dict[str, float]:
        """
        返回各维度评分 + 总分。
        总分 importance = Σ w_i · d_i ∈ [0, 1]
        """
        dims = {
            "core_goal": self._score_core_goal(event),
            "injury_risk": self._score_injury_risk(event),
            "repeat_freq": self._score_repeat_freq(event),
            "decision_impact": self._score_decision_impact(event),
        }
        importance = sum(self.weights[k] * dims[k] for k in dims)
        # 数值稳定性夹紧
        importance = max(0.0, min(1.0, importance))
        result = {**dims, "importance": importance}
        logger.debug(
            f"importance 评分: type={event.get('event_type')} "
            f"core_goal={dims['core_goal']:.2f} injury={dims['injury_risk']:.2f} "
            f"freq={dims['repeat_freq']:.2f} impact={dims['decision_impact']:.2f} "
            f"→ {importance:.3f}"
        )
        return result

    def passes_threshold(self, importance: float) -> bool:
        """判断该 importance 是否超过写入长期记忆的阈值"""
        return importance >= self.threshold

    # ---------- 内部工具 ----------

    @staticmethod
    def _extract_text(event: Dict[str, Any]) -> str:
        """把事件里可能含语义的字段拼成一个字符串供关键词匹配"""
        parts = [
            event.get("question") or "",
            event.get("answer_summary") or "",
            event.get("event_summary") or "",
        ]
        payload = event.get("payload") or {}
        # 把 payload 里的字符串字段也加进来
        for v in payload.values():
            if isinstance(v, str):
                parts.append(v)
        return " ".join(parts)


# 全局单例
importance_scorer = ImportanceScorer()
