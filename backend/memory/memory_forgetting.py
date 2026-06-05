"""
记忆遗忘机制 - 基于时间衰减与访问频率的强度计算

对每条已经入库的长期记忆维护一个动态强度 strength，并周期性扫描归档低强度记录：

    strength(t) = importance · exp(-λ · Δt) + γ · log(1 + access_count)

其中：
    importance      初始重要性（写入时由 ImportanceScorer 给出；语义事实复用 confidence）
    Δt              距上次访问的天数（若从未访问，则取距 created_at 的天数）
    access_count    该记录被检索调用的累计次数
    λ               时间衰减系数（默认 0.01/天，约 100 天衰减到 e^-1 ≈ 0.37 基线）
    γ               访问加成系数（默认 0.05）

当 strength 首次低于 ARCHIVE_THRESHOLD（默认 0.1）时，将该记录的 is_active 置 0，
list_semantic_facts 会自动过滤掉 is_active=0 的记录，不再参与在线检索；归档区仍可被人工审计追溯。
"""
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.api.database import db
from backend.utils.logger_handler import logger


# 时间衰减系数（/天）
LAMBDA = 0.01
# 访问加成系数
GAMMA = 0.05
# 归档阈值（strength 低于此值即软删除）
ARCHIVE_THRESHOLD = 0.1


class ForgettingService:
    """记忆遗忘服务"""

    def __init__(
        self,
        lambda_: float = LAMBDA,
        gamma: float = GAMMA,
        archive_threshold: float = ARCHIVE_THRESHOLD,
    ):
        self.lambda_ = lambda_
        self.gamma = gamma
        self.archive_threshold = archive_threshold
        self.logger = logger

    # ---------- 强度计算 ----------

    def compute_strength(
        self,
        importance: float,
        last_accessed_at: Optional[str],
        access_count: int,
        fallback_time: Optional[str] = None,
    ) -> float:
        """
        计算一条记忆的当前强度。
        importance ∈ [0, 1]，未访问时以 fallback_time（一般为 created_at）作为时间基线。
        """
        ref_time_str = last_accessed_at or fallback_time
        if not ref_time_str:
            # 无任何时间信息，按"刚创建"处理，不衰减
            delta_days = 0.0
        else:
            try:
                ref_time = datetime.fromisoformat(ref_time_str)
                delta_days = max(0.0, (datetime.now() - ref_time).total_seconds() / 86400.0)
            except Exception:
                delta_days = 0.0

        decay = math.exp(-self.lambda_ * delta_days)
        bonus = self.gamma * math.log(1 + max(0, access_count or 0))
        strength = importance * decay + bonus
        return max(0.0, min(1.0, strength))

    # ---------- 扫描 + 归档 ----------

    def decay_and_archive_facts(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        扫描语义事实，计算 strength，归档低强度记录。

        Args:
            user_id: 指定用户；None 表示对所有用户全表扫描（适合后台任务）

        Returns:
            {"total": N, "archived": [(fact_id, strength), ...], "lambda": ..., "gamma": ...}
        """
        facts = db.list_active_facts_for_decay(user_id=user_id)
        archived: List[Dict[str, Any]] = []

        for fact in facts:
            # 语义事实把 confidence 作为 importance 的初始基线
            importance = fact.get("confidence") or 0.5
            strength = self.compute_strength(
                importance=importance,
                last_accessed_at=fact.get("last_accessed_at"),
                access_count=fact.get("access_count") or 0,
                fallback_time=fact.get("updated_at") or fact.get("created_at"),
            )
            if strength < self.archive_threshold:
                db.archive_semantic_fact(fact["id"])
                archived.append({
                    "fact_id": fact["id"],
                    "user_id": fact["user_id"],
                    "fact_category": fact.get("fact_category"),
                    "fact_key": fact.get("fact_key"),
                    "strength": round(strength, 4),
                })

        result = {
            "total_scanned": len(facts),
            "archived_count": len(archived),
            "archived": archived,
            "lambda": self.lambda_,
            "gamma": self.gamma,
            "threshold": self.archive_threshold,
        }
        if archived:
            self.logger.info(
                f"遗忘扫描完成: 共扫描 {len(facts)} 条语义事实，归档 {len(archived)} 条"
            )
        else:
            self.logger.debug(f"遗忘扫描完成: 共扫描 {len(facts)} 条，无需归档")
        return result

    # ---------- 调试 / 监控 ----------

    def snapshot_strength(self, user_id: int) -> List[Dict[str, Any]]:
        """
        返回该用户所有活跃语义事实的当前 strength 快照（不修改任何记录），
        用于调试或答辩展示"哪些记忆正在衰减"。
        """
        facts = db.list_active_facts_for_decay(user_id=user_id)
        snapshot = []
        for fact in facts:
            importance = fact.get("confidence") or 0.5
            strength = self.compute_strength(
                importance=importance,
                last_accessed_at=fact.get("last_accessed_at"),
                access_count=fact.get("access_count") or 0,
                fallback_time=fact.get("updated_at") or fact.get("created_at"),
            )
            snapshot.append({
                "fact_id": fact["id"],
                "fact_category": fact.get("fact_category"),
                "fact_key": fact.get("fact_key"),
                "confidence": importance,
                "access_count": fact.get("access_count") or 0,
                "last_accessed_at": fact.get("last_accessed_at"),
                "strength": round(strength, 4),
                "will_archive": strength < self.archive_threshold,
            })
        # 按 strength 升序排列，便于一眼看到"濒危"记忆
        snapshot.sort(key=lambda x: x["strength"])
        return snapshot


# 全局单例
forgetting_service = ForgettingService()
