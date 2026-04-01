"""
记忆固化模块 - 从情景记忆提炼规律更新语义记忆
定期或按需从情景事件中分析出稳定的用户行为模式，并写入语义记忆
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from backend.database import db
from utils.logger_handler import logger


class MemoryConsolidationService:
    """记忆固化服务 - 情景记忆提炼规律"""

    # 提炼规则配置
    MIN_EPISODES_FOR_PATTERN = 5  # 形成规律需要的最小事件数
    MIN_TRAINING_RECORDS = 10      # 分析训练规律需要的最小记录数
    PREFERENCE_CONFIDENCE = 0.75   # 偏好置信度阈值
    PATTERN_WINDOW_DAYS = 30       # 分析时间窗口（天）

    def __init__(self):
        self.logger = logger

    def consolidate_episodes_to_semantic(self, user_id: int) -> Dict[str, Any]:
        """
        执行完整的记忆固化流程
        从情景记忆中分析规律并更新语义记忆

        Args:
            user_id: 用户ID

        Returns:
            固化结果报告
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "patterns_found": [],
            "semantic_updates": [],
            "errors": []
        }

        try:
            # 1. 分析训练频率偏好
            freq_pattern = self.analyze_training_frequency_pattern(user_id)
            if freq_pattern:
                results["patterns_found"].append(freq_pattern)
                self._update_semantic_from_pattern(user_id, freq_pattern, results)

            # 2. 分析训练时段偏好
            time_pattern = self.analyze_time_preference(user_id)
            if time_pattern:
                results["patterns_found"].append(time_pattern)
                self._update_semantic_from_pattern(user_id, time_pattern, results)

            # 3. 分析训练类型偏好
            type_pattern = self.extract_stable_preferences(user_id)
            if type_pattern:
                results["patterns_found"].append(type_pattern)
                self._update_semantic_from_pattern(user_id, type_pattern, results)

            # 4. 分析疲劳风险
            fatigue_pattern = self.analyze_fatigue_risk(user_id)
            if fatigue_pattern:
                results["patterns_found"].append(fatigue_pattern)
                self._update_semantic_from_pattern(user_id, fatigue_pattern, results)

            # 5. 分析伤病风险
            injury_pattern = self.analyze_injury_risk(user_id)
            if injury_pattern:
                results["patterns_found"].append(injury_pattern)
                self._update_semantic_from_pattern(user_id, injury_pattern, results)

            # 6. 分析训练完成率
            completion_pattern = self.analyze_completion_pattern(user_id)
            if completion_pattern:
                results["patterns_found"].append(completion_pattern)
                self._update_semantic_from_pattern(user_id, completion_pattern, results)

            self.logger.info(f"记忆固化完成: user_id={user_id}, patterns={len(results['patterns_found'])}")

        except Exception as e:
            self.logger.error(f"记忆固化失败: user_id={user_id}, error={e}")
            results["errors"].append(str(e))

        return results

    def analyze_training_frequency_pattern(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        分析训练频率偏好
        识别：周几训练多、周末是否训练、连续训练习惯等
        """
        records = self._get_recent_training_records(user_id, limit=50)

        if len(records) < self.MIN_TRAINING_RECORDS:
            return None

        # 统计每个星期几的训练次数
        weekday_counts = defaultdict(int)
        for record in records:
            try:
                date = datetime.fromisoformat(record["date"])
                weekday = date.weekday()  # 0=周一, 6=周日
                weekday_counts[weekday] += 1
            except (ValueError, KeyError):
                continue

        if not weekday_counts:
            return None

        total = sum(weekday_counts.values())
        patterns = []

        # 分析：周末是否训练
        weekend_training = weekday_counts[5] + weekday_counts[6]  # 周六+周日
        if weekend_training == 0 and total >= 10:
            patterns.append({
                "type": "avoid_weekends",
                "value": "true",
                "description": "用户周末不进行训练",
                "confidence": min(0.9, total / 20)
            })

        # 分析：偏好工作日训练
        weekday_training = total - weekend_training
        if weekday_training > 0 and (weekday_training / total) >= 0.8:
            patterns.append({
                "type": "prefer_weekdays",
                "value": "true",
                "description": "用户主要在工作日训练",
                "confidence": weekday_training / total
            })

        # 分析：最常训练的星期几
        max_weekday = max(weekday_counts.items(), key=lambda x: x[1])
        max_count, total_days = max_weekday[1], len(weekday_counts)
        if max_count >= self.MIN_EPISODES_FOR_PATTERN:
            weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            patterns.append({
                "type": "preferred_weekday",
                "value": str(max_weekday[0]),
                "description": f"最常在{weekday_names[max_weekday[0]]}训练",
                "confidence": min(0.9, max_count / 20)
            })

        return {
            "category": "habit",
            "patterns": patterns
        } if patterns else None

    def analyze_time_preference(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        分析训练时段偏好
        识别：晨练（6-12点）、午练（12-18点）、晚练（18-24点）
        注意：当前数据库可能不记录具体时间，这个功能基于假设的字段
        """
        records = self._get_recent_training_records(user_id, limit=30)

        # 检查是否有时间信息
        # 由于当前训练记录只保存日期，这里从情景记忆中查询训练创建时间
        episodes = db.list_episodic_events(user_id, event_type="training_completed", limit=50)

        if len(episodes) < self.MIN_EPISODES_FOR_PATTERN:
            return None

        time_slots = defaultdict(int)
        for ep in episodes:
            try:
                event_time = datetime.fromisoformat(ep.get("event_time", ""))
                hour = event_time.hour
                if 6 <= hour < 12:
                    time_slots["morning"] += 1
                elif 12 <= hour < 18:
                    time_slots["afternoon"] += 1
                elif 18 <= hour < 24:
                    time_slots["evening"] += 1
                elif 0 <= hour < 6:
                    time_slots["night"] += 1
            except (ValueError, TypeError):
                continue

        if not time_slots:
            return None

        total = sum(time_slots.values())
        patterns = []

        # 找出最常使用的时段
        max_slot = max(time_slots.items(), key=lambda x: x[1])
        slot_names = {
            "morning": "晨间",
            "afternoon": "午间",
            "evening": "晚间",
            "night": "深夜"
        }

        if max_slot[1] / total >= 0.6:  # 某时段占比超过60%
            patterns.append({
                "type": "preferred_time",
                "value": max_slot[0],
                "description": f"偏好{slot_names.get(max_slot[0], '')}训练",
                "confidence": min(0.95, max_slot[1] / total + 0.2)
            })

        return {
            "category": "preference",
            "patterns": patterns
        } if patterns else None

    def extract_stable_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        提炼稳定的训练类型偏好
        分析：用户最常选择的训练类型、组合偏好等
        """
        records = self._get_recent_training_records(user_id, limit=50)

        if len(records) < self.MIN_TRAINING_RECORDS:
            return None

        # 统计训练类型
        type_counts = defaultdict(int)
        for record in records:
            training_type = record.get("training_type", "unknown")
            if training_type and training_type != "unknown":
                type_counts[training_type] += 1

        if not type_counts:
            return None

        total = sum(type_counts.values())
        patterns = []

        # 找出最主要的训练类型
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

        # 最常用类型占比
        if sorted_types[0][1] / total >= 0.5:  # 超过50%
            patterns.append({
                "type": "preferred_training_type",
                "value": sorted_types[0][0],
                "description": f"偏好{sorted_types[0][0]}训练",
                "confidence": min(0.95, sorted_types[0][1] / total + 0.1)
            })

        # 检查是否有类型组合偏好（如经常力量+有氧）
        if len(sorted_types) >= 2:
            top_two = sorted_types[0][1] + sorted_types[1][1]
            if top_two / total >= 0.8:
                patterns.append({
                    "type": "training_style",
                    "value": "mixed_strength_cardio",
                    "description": "训练风格偏向力量与有氧结合",
                    "confidence": top_two / total
                })

        return {
            "category": "preference",
            "patterns": patterns
        } if patterns else None

    def analyze_fatigue_risk(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        分析疲劳风险
        识别：持续高疲劳、疲劳上升趋势等
        """
        records = self._get_recent_training_records(user_id, limit=30)

        # 过滤有疲劳记录的训练
        fatigue_records = [
            r for r in records
            if r.get("fatigue_level") is not None
        ]

        if len(fatigue_records) < self.MIN_EPISODES_FOR_PATTERN:
            return None

        patterns = []
        fatigue_levels = [r["fatigue_level"] for r in fatigue_records]

        # 分析：最近10次训练平均疲劳度
        recent_fatigue = fatigue_levels[:10]
        avg_recent = sum(recent_fatigue) / len(recent_fatigue)

        if avg_recent >= 4:
            patterns.append({
                "type": "high_fatigue_risk",
                "value": "true",
                "description": "近期训练疲劳度偏高",
                "confidence": min(0.95, avg_recent / 5)
            })

        # 分析：持续高疲劳（连续3次≥4）
        consecutive_high = 0
        for level in fatigue_levels:
            if level >= 4:
                consecutive_high += 1
                if consecutive_high >= 3:
                    patterns.append({
                        "type": "overtraining_risk",
                        "value": "true",
                        "description": "存在过度训练风险",
                        "confidence": 0.85
                    })
                    break
            else:
                consecutive_high = 0

        # 分析：疲劳上升趋势
        if len(fatigue_levels) >= 5:
            first_half = fatigue_levels[len(fatigue_levels)//2:]
            second_half = fatigue_levels[:len(fatigue_levels)//2]
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)

            if avg_second > avg_first + 0.5:
                patterns.append({
                    "type": "fatigue_increasing",
                    "value": "true",
                    "description": "疲劳度呈上升趋势",
                    "confidence": 0.75
                })

        return {
            "category": "risk",
            "patterns": patterns
        } if patterns else None

    def analyze_injury_risk(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        分析伤病风险
        识别：某部位反复疼痛、疼痛频率增加等
        """
        records = self._get_recent_training_records(user_id, limit=50)

        # 过滤有疼痛记录的训练
        pain_records = [
            r for r in records
            if r.get("pain_level") is not None and r["pain_level"] > 0
        ]

        if len(pain_records) < self.MIN_EPISODES_FOR_PATTERN:
            return None

        patterns = []
        pain_levels = [r["pain_level"] for r in pain_records]
        avg_pain = sum(pain_levels) / len(pain_levels)

        # 分析：平均疼痛度偏高
        if avg_pain >= 3:
            patterns.append({
                "type": "high_avg_pain",
                "value": str(avg_pain),
                "description": f"平均疼痛度偏高 ({avg_pain:.1f}/5)",
                "confidence": min(0.9, avg_pain / 4)
            })

        # 分析：疼痛频率上升
        recent_pain = sum(1 for r in pain_records[:10] if r["pain_level"] >= 2)
        older_pain = sum(1 for r in pain_records[10:] if r["pain_level"] >= 2)

        if len(pain_records) >= 20 and recent_pain > older_pain * 1.5:
            patterns.append({
                "type": "pain_increasing",
                "value": "true",
                "description": "疼痛频率呈上升趋势",
                "confidence": 0.8
            })

        # 分析：训练备注中的伤病关键词
        notes_with_injury = [
            r.get("notes", "") for r in records
            if r.get("notes") and any(
                keyword in r["notes"].lower()
                for keyword in ["疼", "痛", "伤", "膝盖", "腰", "肩", "脚踝"]
            )
        ]

        if len(notes_with_injury) >= 3:
            patterns.append({
                "type": "reported_injury",
                "value": "true",
                "description": "训练记录中反复提到身体不适",
                "confidence": 0.85
            })

        return {
            "category": "risk",
            "patterns": patterns
        } if patterns else None

    def analyze_completion_pattern(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        分析训练完成率模式
        识别：跳过训练的频率、完成率趋势等
        """
        records = self._get_recent_training_records(user_id, limit=50)

        if len(records) < self.MIN_EPISODES_FOR_PATTERN:
            return None

        patterns = []

        completed = sum(1 for r in records if r.get("completion_status") == "completed")
        skipped = sum(1 for r in records if r.get("completion_status") == "skipped")
        total = completed + skipped

        if total == 0:
            return None

        completion_rate = completed / total

        # 分析：完成率低
        if completion_rate < 0.6:
            patterns.append({
                "type": "low_completion_rate",
                "value": str(completion_rate),
                "description": f"训练完成率偏低 ({completion_rate*100:.0f}%)",
                "confidence": 0.8
            })
        elif completion_rate < 0.8:
            patterns.append({
                "type": "moderate_completion_rate",
                "value": str(completion_rate),
                "description": f"训练完成率一般 ({completion_rate*100:.0f}%)",
                "confidence": 0.75
            })

        # 分析：跳过训练的模式（周几跳过多）
        skipped_records = [r for r in records if r.get("completion_status") == "skipped"]
        if len(skipped_records) >= 5:
            weekday_skips = defaultdict(int)
            for record in skipped_records:
                try:
                    date = datetime.fromisoformat(record["date"])
                    weekday_skips[date.weekday()] += 1
                except (ValueError, KeyError):
                    continue

            max_skip_weekday = max(weekday_skips.items(), key=lambda x: x[1])
            if max_skip_weekday[1] >= 3:
                weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                patterns.append({
                    "type": "frequently_skipped_weekday",
                    "value": str(max_skip_weekday[0]),
                    "description": f"{weekday_names[max_skip_weekday[0]]}经常跳过训练",
                    "confidence": 0.7
                })

        return {
            "category": "adaptation_rule",
            "patterns": patterns
        } if patterns else None

    def _update_semantic_from_pattern(
        self,
        user_id: int,
        pattern_result: Dict[str, Any],
        results: Dict[str, Any]
    ):
        """将提炼的规律写入语义记忆"""
        category = pattern_result.get("category")
        patterns = pattern_result.get("patterns", [])

        for pattern in patterns:
            pattern_type = pattern.get("type")
            value = pattern.get("value")
            confidence = pattern.get("confidence", 0.7)

            if not pattern_type or not value:
                continue

            try:
                db.upsert_semantic_fact(
                    user_id=user_id,
                    fact_category=category,
                    fact_key=pattern_type,
                    fact_value=str(value),
                    confidence=confidence,
                    source_type="consolidation"
                )
                results["semantic_updates"].append({
                    "category": category,
                    "key": pattern_type,
                    "value": value,
                    "confidence": confidence
                })
                self.logger.debug(f"更新语义记忆: user_id={user_id}, {category}.{pattern_type}={value}")
            except Exception as e:
                self.logger.error(f"更新语义记忆失败: {e}")
                results["errors"].append(str(e))

    def _get_recent_training_records(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近的训练记录"""
        return db.list_training_records(user_id)[:limit]

    def should_consolidate(self, user_id: int, min_records_since_last: int = 5, min_days_since_last: int = 7) -> bool:
        """
        判断是否需要执行记忆固化

        条件：
        - 距离上次固化超过X天
        - 或者新增训练记录超过N条

        Args:
            user_id: 用户ID
            min_records_since_last: 自上次固化后最少记录数
            min_days_since_last: 距上次固化最少天数

        Returns:
            是否需要执行记忆固化
        """
        # 检查训练记录数量
        recent_records = db.list_training_records(user_id)[:min_records_since_last]
        if len(recent_records) >= min_records_since_last:
            self.logger.debug(f"触发记忆固化: 用户{user_id}新增了{len(recent_records)}条训练记录")
            return True

        # 检查情景事件数量
        episode_count = db.count_episodic_events(user_id)
        if episode_count >= 20:  # 如果有足够多的情景事件
            # 检查最近的事件
            recent_episodes = db.list_episodic_events(user_id, limit=5)
            if recent_episodes:
                try:
                    last_episode_time = datetime.fromisoformat(recent_episodes[0]["event_time"])
                    days_since_last = (datetime.now() - last_episode_time).days
                    if days_since_last <= 1:  # 最近有新活动
                        self.logger.debug(f"触发记忆固化: 用户{user_id}最近有新活动")
                        return True
                except (ValueError, KeyError):
                    pass

        return False

    def trigger_consolidation_if_needed(self, user_id: int) -> Dict[str, Any]:
        """
        如果需要则触发记忆固化

        Args:
            user_id: 用户ID

        Returns:
            固化结果（如果执行了固化）或空字典（未执行）
        """
        if self.should_consolidate(user_id):
            return self.consolidate_episodes_to_semantic(user_id)
        return {"status": "skipped", "reason": "trigger_conditions_not_met"}


# 全局实例
consolidation_service = MemoryConsolidationService()
