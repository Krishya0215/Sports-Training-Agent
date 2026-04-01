"""
运动训练知识问答系统 - FastAPI后端接口
为Vue前端提供RESTful API
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path
import json
import asyncio
import threading

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.graph_agent import SportsTrainingAgent
from agent.multi_agent_system import MultiAgentTrainingSystem
from utils.logger_handler import logger
from backend.auth import AuthService
from backend.database import db
from backend.memory_service import memory_service
from backend.memory_consolidation import consolidation_service

app = FastAPI(
    title="运动训练知识问答API",
    description="基于RAG的智能运动训练问答系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局Agent实例
agent = None
multi_agent_system = None
chat_history = []

DATA_DIR = Path(__file__).parent / "data"
users = {  # 用户数据
    "user": {"username": "user", "password": "user123", "role": "user"},
    "admin": {"username": "admin", "password": "admin123", "role": "admin"}
}


class QueryRequest(BaseModel):
    """查询请求模型"""
    question: str
    use_multi_agent: bool = False  # 是否使用多智能体系统
    user_profile: Optional[Dict] = None  # 用户档案


class TrainingPlan(BaseModel):
    """训练计划模型"""
    title: str
    content: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    goal: Optional[str] = None
    created_from_ai: bool = False  # 是否从AI回复生成


    metadata: Optional[Dict] = None
    selected_weekdays: Optional[List[str]] = None
    source_prompt: Optional[str] = None
    ai_response: Optional[str] = None


class TrainingPlanUpdate(BaseModel):
    """璁粌璁″垝鏇存柊妯″瀷"""
    title: Optional[str] = None
    content: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    goal: Optional[str] = None
    created_from_ai: Optional[bool] = None  # 鏄惁浠嶢I鍥炲鐢熸垚
    metadata: Optional[Dict] = None
    selected_weekdays: Optional[List[str]] = None
    source_prompt: Optional[str] = None
    ai_response: Optional[str] = None


class TrainingRecord(BaseModel):
    """训练记录模型"""
    date: str
    training_type: str
    plan_id: Optional[int] = None
    plan_session_key: Optional[str] = None
    duration: Optional[int] = None  # 分钟
    intensity: Optional[str] = None  # 低/中/高
    feedback: Optional[str] = None  # 用户反馈
    fatigue_level: Optional[int] = None  # 疲劳度 1-5
    pain_level: Optional[int] = None  # 疼痛度 1-5
    notes: Optional[str] = None
    completion_status: Optional[str] = "completed"


class DailyRecord(BaseModel):
    """饮食记录模型"""
    date: str
    meal_type: str  # 早餐/午餐/晚餐/加餐/零食
    food_content: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    notes: Optional[str] = None


class WeightRecord(BaseModel):
    """体重记录模型"""
    date: str
    weight: float  # kg
    body_fat: Optional[float] = None  # %
    chest_circumference: Optional[float] = None  # cm
    waist_circumference: Optional[float] = None  # cm
    hip_circumference: Optional[float] = None  # cm
    notes: Optional[str] = None


class UserProfilePayload(BaseModel):
    goal: Optional[str] = None
    preferred_method: Optional[str] = None
    weekly_days: Optional[int] = None
    daily_duration: Optional[int] = None
    intensity_level: Optional[str] = None
    injury_status: Optional[str] = None
    injury_detail: Optional[str] = None
    fitness_level: Optional[str] = None
    age_range: Optional[str] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    profile_source: Optional[str] = "manual"


class MemoryEpisodePayload(BaseModel):
    event_type: str
    event_time: Optional[str] = None
    conversation_id: Optional[str] = None
    plan_id: Optional[int] = None
    record_id: Optional[int] = None
    question: Optional[str] = None
    answer_summary: Optional[str] = None
    event_summary: Optional[str] = None
    trigger_source: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    importance_score: Optional[float] = 0
    tags: Optional[List[str]] = None


class LoginRequest(BaseModel):
    """登录请求模型"""
    account: str  # 账号（用户名或邮箱）
    password: str


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str
    email: str
    password: str
    confirm_password: str


class VerificationCodeRequest(BaseModel):
    """验证码请求模型"""
    email: str


class ResetPasswordRequest(BaseModel):
    """重置密码请求模型"""
    email: str
    code: str
    new_password: str
    confirm_password: str


class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str
    timestamp: datetime


class MemorySummary(BaseModel):
    """记忆摘要模型"""
    working_memory_size: int
    episodic_memory_size: int
    semantic_concepts: int
    perceptual_documents: int


def _extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    value = authorization.strip()
    if value.lower().startswith("bearer "):
        return value[7:].strip()
    return value or None


def _require_current_user(authorization: Optional[str]) -> Dict[str, Any]:
    token = _extract_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="未登录或缺少访问令牌")

    user = db.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="登录状态已失效，请重新登录")
    return user


def _safe_int(value: Any) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _build_profile_from_questionnaire(questionnaire: Optional[Dict[str, Any]], source: str) -> Optional[Dict[str, Any]]:
    if not questionnaire:
        return None

    injury_status = questionnaire.get("injury")
    injury_detail = questionnaire.get("injury_detail")
    if injury_status == "other":
        injury_status = "其他"

    return {
        "goal": questionnaire.get("goal"),
        "preferred_method": questionnaire.get("method") or questionnaire.get("preferred_method"),
        "weekly_days": _safe_int(questionnaire.get("weekly_days")),
        "daily_duration": _safe_int(questionnaire.get("daily_duration")),
        "intensity_level": questionnaire.get("intensity") or questionnaire.get("intensity_level"),
        "injury_status": injury_status,
        "injury_detail": injury_detail,
        "profile_source": source
    }


def _sync_profile_semantic_memory(user_id: int, profile: Dict[str, Any], source_event_id: Optional[int] = None):
    semantic_mappings = [
        ("profile", "goal", profile.get("goal")),
        ("preference", "preferred_method", profile.get("preferred_method")),
        ("profile", "weekly_days", str(profile.get("weekly_days")) if profile.get("weekly_days") is not None else None),
        ("habit", "daily_duration", str(profile.get("daily_duration")) if profile.get("daily_duration") is not None else None),
        ("profile", "intensity_level", profile.get("intensity_level")),
        ("constraint", "injury_status", profile.get("injury_status")),
        ("constraint", "injury_detail", profile.get("injury_detail"))
    ]

    for category, key, value in semantic_mappings:
        if value in (None, ""):
            continue
        db.upsert_semantic_fact(
            user_id=user_id,
            fact_category=category,
            fact_key=key,
            fact_value=str(value),
            confidence=0.9,
            source_event_id=source_event_id,
            source_type="profile"
        )


def _record_episode(user_id: int, event: Dict[str, Any]) -> Dict[str, Any]:
    return db.create_episodic_event(user_id, event)


def _update_semantic_from_training_record(user_id: int, record: Dict[str, Any], source_event_id: Optional[int] = None):
    """
    从训练记录更新语义记忆（增强版）

    提取：
    - 疼痛水平 → 风险评估
    - 疲劳度 → 适应性规则
    - 训练类型 → 偏好更新
    - 训练备注 → 关键词提取
    - 训练时段 → 时段偏好
    """
    pain_level = _safe_int(record.get("pain_level"))
    fatigue_level = _safe_int(record.get("fatigue_level"))
    training_type = record.get("training_type")
    notes = record.get("notes", "")
    record_date = record.get("date")

    # 1. 疼痛风险评估
    if pain_level is not None:
        if pain_level >= 3:
            db.upsert_semantic_fact(
                user_id=user_id,
                fact_category="risk",
                fact_key="recent_pain_level",
                fact_value=str(pain_level),
                confidence=0.8,
                source_event_id=source_event_id,
                source_type="training_record"
            )

        # 提取疼痛部位（从备注中）
        if notes and pain_level >= 2:
            pain_keywords = {
                "膝盖": ["膝盖", "膝", "knee"],
                "腰部": ["腰", "背", "lower back"],
                "肩部": ["肩", "shoulder"],
                "脚踝": ["脚踝", "踝", "ankle"],
                "手腕": ["手腕", "腕", "wrist"]
            }

            for body_part, keywords in pain_keywords.items():
                if any(kw in notes.lower() for kw in keywords):
                    db.upsert_semantic_fact(
                        user_id=user_id,
                        fact_category="constraint",
                        fact_key=f"pain_{body_part}",
                        fact_value=f"{body_part}疼痛(疼痛度{pain_level})",
                        confidence=0.7,
                        source_event_id=source_event_id,
                        source_type="training_record"
                    )
                    break

    # 2. 疲劳度分析
    if fatigue_level is not None:
        if fatigue_level >= 4:
            db.upsert_semantic_fact(
                user_id=user_id,
                fact_category="adaptation_rule",
                fact_key="recent_high_fatigue",
                fact_value="true",
                confidence=0.75,
                source_event_id=source_event_id,
                source_type="training_record"
            )

        # 疲劳度趋势
        recent_records = db.list_training_records(user_id, limit=10)
        if len(recent_records) >= 3:
            recent_fatigue = [_safe_int(r.get("fatigue_level")) for r in recent_records if _safe_int(r.get("fatigue_level")) is not None]
            if recent_fatigue:
                avg_fatigue = sum(recent_fatigue) / len(recent_fatigue)
                if avg_fatigue >= 3.5:
                    db.upsert_semantic_fact(
                        user_id=user_id,
                        fact_category="adaptation_rule",
                        fact_key="avg_fatigue_high",
                        fact_value="true",
                        confidence=0.7,
                        source_event_id=source_event_id,
                        source_type="training_record"
                    )

    # 3. 训练类型偏好更新（简单的计数逻辑）
    if training_type:
        # 获取历史训练类型统计
        all_records = db.list_training_records(user_id, limit=50)
        type_counts = {}
        for r in all_records:
            t = r.get("training_type")
            if t:
                type_counts[t] = type_counts.get(t, 0) + 1

        total = sum(type_counts.values())
        if total >= 5 and training_type in type_counts:
            type_ratio = type_counts[training_type] / total
            if type_ratio >= 0.4:  # 某类型占比超过40%
                db.upsert_semantic_fact(
                    user_id=user_id,
                    fact_category="preference",
                    fact_key="preferred_training_type",
                    fact_value=training_type,
                    confidence=min(0.9, type_ratio + 0.3),
                    source_event_id=source_event_id,
                    source_type="training_record"
                )

    # 4. 从备注中提取训练相关关键词
    if notes:
        keyword_mappings = {
            "喜欢": ["喜欢", "开心", "感觉不错", "good", "like"],
            "困难": ["困难", "累", "challenging", "hard"],
            "容易": ["轻松", "easy", "简单"],
            "受伤": ["疼", "痛", "伤", "hurt", "pain"],
            "进步": ["进步", "提高", "improve", "better"]
        }

        for sentiment, keywords in keyword_mappings.items():
            if any(kw in notes.lower() for kw in keywords):
                db.upsert_semantic_fact(
                    user_id=user_id,
                    fact_category="feedback",
                    fact_key=f"recent_{sentiment}",
                    fact_value="true",
                    confidence=0.6,
                    source_event_id=source_event_id,
                    source_type="training_record"
                )
                break

    # 5. 提炼时段偏好（基于记录的时间）
    if record_date and notes:
        # 尝试从备注中提取时段信息
        time_keywords = {
            "morning": ["早", "晨", "morning"],
            "afternoon": ["午", "下午", "afternoon"],
            "evening": ["晚", "evening", "night"]
        }

        for time_slot, keywords in time_keywords.items():
            if any(kw in notes.lower() for kw in keywords):
                db.upsert_semantic_fact(
                    user_id=user_id,
                    fact_category="habit",
                    fact_key="training_time_slot",
                    fact_value=time_slot,
                    confidence=0.65,
                    source_event_id=source_event_id,
                    source_type="training_record"
                )
                break


def _update_semantic_from_weekday_selection(user_id: int, weekdays: List[str], source_event_id: Optional[int] = None):
    """
    从训练日选择更新语义记忆

    分析：
    - 避开周末
    - 偏好特定周几
    - 训练日数量
    """
    if not weekdays:
        return

    weekday_map = {"周一": 0, "周二": 1, "周三": 2, "周四": 3, "周五": 4, "周六": 5, "周日": 6}
    weekday_numbers = [weekday_map.get(w) for w in weekdays if w in weekday_map]

    if not weekday_numbers:
        return

    # 检查是否避开周末
    has_weekend = any(w in [5, 6] for w in weekday_numbers)
    has_weekday = any(w in [0, 1, 2, 3, 4] for w in weekday_numbers)

    if has_weekday and not has_weekend:
        db.upsert_semantic_fact(
            user_id=user_id,
            fact_category="habit",
            fact_key="avoid_weekends",
            fact_value="true",
            confidence=0.85,
            source_event_id=source_event_id,
            source_type="plan_update"
        )

    # 检查训练日数量偏好
    weekly_days = len(weekday_numbers)
    if weekly_days <= 3:
        db.upsert_semantic_fact(
            user_id=user_id,
            fact_category="preference",
            fact_key="weekly_training_days",
            fact_value=str(weekly_days),
            confidence=0.8,
            source_event_id=source_event_id,
            source_type="plan_update"
        )

    # 找出最常选择的周几
    if len(weekday_numbers) >= 2:
        weekday_counts = {}
        for w in weekday_numbers:
            weekday_counts[w] = weekday_counts.get(w, 0) + 1

        max_weekday = max(weekday_counts.items(), key=lambda x: x[1])
        if max_weekday[1] >= 2:  # 至少选择过2次
            weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            db.upsert_semantic_fact(
                user_id=user_id,
                fact_category="habit",
                fact_key="preferred_weekday",
                fact_value=str(max_weekday[0]),
                confidence=0.75,
                source_event_id=source_event_id,
                source_type="plan_update"
            )


def _build_memory_dashboard(user_id: int) -> Dict[str, Any]:
    agent_summary = agent.get_memory_summary() if agent else {}
    semantic_facts = db.list_semantic_facts(user_id)[:5]
    recent_events = db.list_episodic_events(user_id, limit=5)

    return {
        "working_memory": {
            "message_count": agent_summary.get("working_memory_size", 0)
        },
        "episodic_memory": {
            "event_count": db.count_episodic_events(user_id),
            "recent_events": recent_events
        },
        "semantic_memory": {
            "fact_count": db.count_semantic_facts(user_id),
            "top_facts": semantic_facts
        },
        "perceptual_memory": {
            "asset_count": db.count_perceptual_assets(),
            "document_count": agent_summary.get("perceptual_documents", 0)
        }
    }


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化Agent"""
    global agent, multi_agent_system
    logger.info("正在初始化Agent...")
    agent = SportsTrainingAgent()
    logger.info("Agent初始化完成")
    
    logger.info("正在初始化多智能体系统...")
    multi_agent_system = MultiAgentTrainingSystem()
    logger.info("多智能体系统初始化完成")



@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "运动训练知识问答API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/query")
async def query(request: QueryRequest, authorization: Optional[str] = Header(None)):
    """
    处理用户问题查询（流式响应）
    支持单智能体和多智能体模式
    流式输出思考过程和答案

    Args:
        request: 包含问题的请求对象

    Returns:
        流式响应
    """
    async def generate():
        try:
            current_user = None
            memory_context = None
            token = _extract_token_from_header(authorization)
            if token:
                current_user = db.get_user_by_token(token)

            # 获取用户记忆上下文
            if current_user:
                memory_context = memory_service.get_user_memory_context(current_user["id"])
                memory_context["user_id"] = current_user["id"]  # 添加用户ID以便构建提示词
                memory_prompt = memory_service.build_memory_prompt(current_user["id"], memory_context)
                logger.debug(f"获取用户记忆上下文: user_id={current_user['id']}, "
                            f"semantic_facts={len(memory_context.get('semantic_profile', {}))}")

            if current_user and request.user_profile:
                profile = _build_profile_from_questionnaire(request.user_profile, request.user_profile.get("source", "chat"))
                if profile:
                    saved_profile = db.upsert_user_profile(current_user["id"], profile)
                    _sync_profile_semantic_memory(current_user["id"], saved_profile)

            # 根据请求选择使用单智能体或多智能体系统
            if request.use_multi_agent:
                if not multi_agent_system:
                    yield f"data: {json.dumps({'type': 'answer', 'content': '多智能体系统未初始化', 'done': True}, ensure_ascii=False)}\n\n"
                    return
                
                logger.info(f"收到多智能体查询: {request.question}")

                loop = asyncio.get_running_loop()
                event_queue: asyncio.Queue = asyncio.Queue()
                result_holder = {"result": None, "error": None}
                processing_done = threading.Event()

                def stream_callback(data):
                    loop.call_soon_threadsafe(event_queue.put_nowait, data)

                def run_multi_agent():
                    try:
                        # 将记忆上下文注入到 user_profile
                        enhanced_profile = request.user_profile or {}
                        if memory_context:
                            enhanced_profile = {
                                **enhanced_profile,
                                "_memory_context": memory_context,
                                "_memory_prompt": memory_prompt
                            }
                        result_holder["result"] = multi_agent_system.process_request(
                            request.question,
                            enhanced_profile,
                            stream_callback=stream_callback
                        )
                    except Exception as exc:
                        result_holder["error"] = exc
                    finally:
                        processing_done.set()
                        loop.call_soon_threadsafe(event_queue.put_nowait, {"type": "_processing_done"})

                threading.Thread(target=run_multi_agent, daemon=True).start()

                yield f"data: {json.dumps({'type': 'thinking', 'content': '', 'done': False}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.05)
                yield f"data: {json.dumps({'type': 'progress_log', 'message': '正在开始分析你的需求'}, ensure_ascii=False)}\n\n"

                while True:
                    event = await event_queue.get()
                    event_type = event.get("type")

                    if event_type == "_processing_done":
                        break

                    if event_type == "progress_log":
                        yield f"data: {json.dumps({'type': 'progress_log', 'message': event.get('message', '')}, ensure_ascii=False)}\n\n"
                        continue

                    if event_type == "coach_result":
                        yield f"data: {json.dumps({'type': 'coach_result', 'coach': event.get('coach', {})}, ensure_ascii=False)}\n\n"
                        continue

                if result_holder["error"]:
                    raise result_holder["error"]

                result = result_holder["result"] or {}
                thinking = result.get("thinking", "")
                answer = result.get("response", "")
                structured_response = result.get("structured_response", {}) or {}
                scheduler = structured_response.get("scheduler", {}) or {}
                coach_catalog = structured_response.get("coaches", []) or []
                
            else:
                if not agent:
                    yield f"data: {json.dumps({'type': 'answer', 'content': 'Agent未初始化', 'done': True}, ensure_ascii=False)}\n\n"
                    return

                logger.info(f"收到单智能体查询: {request.question}")

                # 使用单智能体处理，注入记忆上下文
                result = agent.query(request.question, memory_context=memory_context)
                thinking = result.get("thinking", "")
                answer = result.get("answer", "")
                structured_response = {}
                scheduler = {}
                coach_catalog = []

            # 单智能体仍保留原有思考过程流式输出
            if thinking and not request.use_multi_agent:
                yield f"data: {json.dumps({'type': 'thinking', 'content': '', 'done': False}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
                
                thinking_lines = thinking.split('\n')
                for line in thinking_lines:
                    if line.strip():
                        # 每行思考过程逐字输出
                        chunk_size = 2
                        for i in range(0, len(line), chunk_size):
                            chunk = line[i:i + chunk_size]
                            data = {
                                "type": "thinking",
                                "content": chunk,
                                "done": False
                            }
                            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                            await asyncio.sleep(0.02)
                        
                        # 每行末尾加换行
                        data = {
                            "type": "thinking",
                            "content": "\n",
                            "done": False
                        }
                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.05)
                
                # 思考过程完成
                yield f"data: {json.dumps({'type': 'thinking', 'content': '', 'done': True}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.3)  # 思考和答案之间的延迟

            if request.use_multi_agent:
                yield f"data: {json.dumps({'type': 'thinking', 'content': '', 'done': True}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)

            if request.use_multi_agent and (scheduler or coach_catalog):
                scheduler_event = {
                    "type": "scheduler",
                    "content": "",
                    "done": False,
                    "scheduler": scheduler,
                    "coaches": coach_catalog
                }
                yield f"data: {json.dumps(scheduler_event, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
            
            # 再流式输出最终答案
            yield f"data: {json.dumps({'type': 'answer', 'content': '', 'done': False}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.05)
            
            chunk_size = 2  # 每次发送的字符数
            for i in range(0, len(answer), chunk_size):
                chunk = answer[i:i + chunk_size]
                data = {
                    "type": "answer",
                    "content": chunk,
                    "done": False
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.03)  # 控制输出速度
            
            # 记录到历史
            chat_history.append({
                "question": request.question,
                "answer": answer,
                "thinking": thinking,
                "timestamp": datetime.now(),
                "mode": "multi_agent" if request.use_multi_agent else "single_agent",
                "structured_response": structured_response
            })

            if current_user:
                _record_episode(current_user["id"], {
                    "event_type": "coach_chat",
                    "question": request.question,
                    "answer_summary": answer[:240],
                    "event_summary": f"用户发起了一次{'多智能体' if request.use_multi_agent else '单智能体'}咨询",
                    "trigger_source": "chat_query",
                    "payload": {
                        "use_multi_agent": request.use_multi_agent,
                        "user_profile": request.user_profile or {},
                        "mode": "multi_agent" if request.use_multi_agent else "single_agent"
                    },
                    "importance_score": 0.5,
                    "tags": ["chat", "qa"]
                })
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'answer', 'content': '', 'done': True}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            # 发送错误信息
            error_thinking = f"❌ **系统错误**\n\n{str(e)[:100]}"
            error_answer = f"抱歉，处理您的请求时出现错误。请稍后重试。\n\n技术信息：{str(e)[:150]}"
            
            # 流式发送思考过程\
            yield f"data: {json.dumps({'type': 'thinking', 'content': error_thinking, 'done': True}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.2)
            
            # 流式发送错误答案
            yield f"data: {json.dumps({'type': 'answer', 'content': error_answer, 'done': True}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/query/sync", response_model=QueryResponse)
async def query_sync(request: QueryRequest, authorization: Optional[str] = Header(None)):
    """
    处理用户问题查询（非流式，兼容旧版本）
    
    Args:
        request: 包含问题的请求对象
        
    Returns:
        包含答案和时间戳的响应对象
    """
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent未初始化")

        current_user = None
        token = _extract_token_from_header(authorization)
        if token:
            current_user = db.get_user_by_token(token)
        
        logger.info(f"收到查询: {request.question}")
        result = agent.query(request.question)
        
        # 提取answer和thinking
        answer = result.get("answer", "") if isinstance(result, dict) else result
        thinking = result.get("thinking", "") if isinstance(result, dict) else ""
        
        # 记录到历史
        chat_history.append({
            "question": request.question,
            "answer": answer,
            "thinking": thinking,
            "timestamp": datetime.now()
        })

        if current_user:
            _record_episode(current_user["id"], {
                "event_type": "coach_chat",
                "question": request.question,
                "answer_summary": answer[:240],
                "event_summary": "用户发起了一次同步问答",
                "trigger_source": "chat_query_sync",
                "payload": {
                    "user_profile": request.user_profile or {}
                },
                "importance_score": 0.4,
                "tags": ["chat", "sync"]
            })
        
        return QueryResponse(
            answer=answer,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge/load")
async def load_knowledge(force_reload: bool = False):
    """
    加载知识库
    
    Args:
        force_reload: 是否强制重新加载（清除缓存和向量数据库）
    
    Returns:
        加载结果信息
    """
    global agent
    
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent未初始化")
        
        logger.info(f"开始加载知识库... (强制重载: {force_reload})")
        
        if force_reload:
            import shutil
            import gc
            # 获取项目根目录
            project_root = Path(__file__).parent.parent
            
            # 清除md5记录
            md5_file = project_root / "md5.txt"
            if md5_file.exists():
                md5_file.unlink()
                logger.info(f"已清除md5缓存: {md5_file}")
            
            # 关闭当前的向量数据库连接
            try:
                if hasattr(agent, 'vector_store_service') and agent.vector_store_service:
                    # 尝试关闭Chroma客户端
                    if hasattr(agent.vector_store_service.vector_store, '_client'):
                        agent.vector_store_service.vector_store._client = None
                    agent.vector_store_service = None
                    logger.info("已关闭向量数据库连接")
            except Exception as e:
                logger.warning(f"关闭向量数据库连接时出错: {e}")
            
            # 强制垃圾回收
            gc.collect()
            
            # 等待一下确保文件句柄释放
            import time
            time.sleep(0.5)
            
            # 清除向量数据库
            chroma_db_path = project_root / "rag" / "chroma_db"
            if chroma_db_path.exists():
                try:
                    shutil.rmtree(chroma_db_path)
                    logger.info(f"已清除向量数据库: {chroma_db_path}")
                except PermissionError as e:
                    logger.error(f"无法删除向量数据库（文件被占用），尝试重新初始化Agent: {e}")
                    # 如果无法删除，重新初始化整个Agent
                    agent = SportsTrainingAgent()
                    logger.info("Agent已重新初始化")
            
            # 重新初始化向量存储服务
            from rag.vector_store import VectorStoreService
            agent.vector_store_service = VectorStoreService()
            base_retriever = agent.vector_store_service.get_retriever()
            
            # 重新初始化高级检索器
            from rag.advanced_retriever import AdvancedRetriever
            agent.retriever = AdvancedRetriever(base_retriever)
            
            logger.info("已重新初始化向量存储和检索器")
        
        agent.load_knowledge_base()
        
        # 获取加载后的文档数量
        collection = agent.vector_store_service.vector_store._collection
        doc_count = collection.count()
        
        logger.info(f"知识库加载完成，共 {doc_count} 个文档块")
        
        return {
            "status": "success",
            "message": f"知识库加载成功，共 {doc_count} 个文档块",
            "document_count": doc_count,
            "force_reload": force_reload,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"知识库加载失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge/stats")
async def get_knowledge_stats():
    """
    获取知识库统计信息
    
    Returns:
        知识库统计数据
    """
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent未初始化")
        
        # 获取向量数据库统计
        collection = agent.vector_store_service.vector_store._collection
        doc_count = collection.count()
        
        # 统计文档数量（通过data目录）
        from utils.config_handler import chroma_conf
        from utils.path_tool import get_abs_path
        from utils.file_handler import listdir_with_allowed_type
        
        knowledge_files = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allowed_knowledge_file_types"])
        )
        
        return {
            "total_documents": len(knowledge_files),
            "total_chunks": doc_count,
            "collection_name": collection.name,
            "last_update": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取知识库统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/summary", response_model=MemorySummary)
async def get_memory_summary(authorization: Optional[str] = Header(None)):
    """
    获取记忆系统摘要
    
    Returns:
        记忆系统各层的统计信息
    """
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent未初始化")
        user = _require_current_user(authorization)
        summary = agent.get_memory_summary()
        
        return MemorySummary(
            working_memory_size=summary.get('working_memory_size', 0),
            episodic_memory_size=db.count_episodic_events(user["id"]),
            semantic_concepts=db.count_semantic_facts(user["id"]),
            perceptual_documents=summary.get('perceptual_documents', 0)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取记忆摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/clear")
async def clear_working_memory(authorization: Optional[str] = Header(None)):
    """
    清空工作记忆
    
    Returns:
        操作结果
    """
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent未初始化")
        _require_current_user(authorization)
        agent.clear_working_memory()
        logger.info("工作记忆已清空")
        
        return {
            "status": "success",
            "message": "工作记忆已清空",
            "timestamp": datetime.now()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清空工作记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/dashboard")
async def get_memory_dashboard(authorization: Optional[str] = Header(None)):
    try:
        user = _require_current_user(authorization)
        return _build_memory_dashboard(user["id"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取记忆看板失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/episodes")
async def create_memory_episode(
    payload: MemoryEpisodePayload,
    authorization: Optional[str] = Header(None)
):
    try:
        user = _require_current_user(authorization)
        episode = _record_episode(user["id"], payload.dict())
        return {"status": "success", "episode": episode}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建情景记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/episodes")
async def get_memory_episodes(
    event_type: Optional[str] = None,
    plan_id: Optional[int] = None,
    limit: int = 20,
    authorization: Optional[str] = Header(None)
):
    try:
        user = _require_current_user(authorization)
        episodes = db.list_episodic_events(user["id"], event_type=event_type, plan_id=plan_id, limit=limit)
        return {"episodes": episodes, "total": len(episodes)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取情景记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/semantic")
async def get_memory_semantic(
    category: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    try:
        user = _require_current_user(authorization)
        facts = db.list_semantic_facts(user["id"], fact_category=category)
        return {"facts": facts, "total": len(facts)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取语义记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/profile/init")
async def initialize_profile(
    payload: UserProfilePayload,
    authorization: Optional[str] = Header(None)
):
    try:
        user = _require_current_user(authorization)
        profile = db.upsert_user_profile(user["id"], payload.dict())
        episode = _record_episode(user["id"], {
            "event_type": "questionnaire_submitted",
            "event_summary": "用户提交了训练问卷并初始化画像",
            "trigger_source": "profile_init",
            "payload": payload.dict(),
            "importance_score": 0.9,
            "tags": ["profile", "questionnaire"]
        })
        _sync_profile_semantic_memory(user["id"], profile, source_event_id=episode["id"])
        return {"status": "success", "profile": profile}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"初始化用户画像失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile/me")
async def get_my_profile(authorization: Optional[str] = Header(None)):
    try:
        user = _require_current_user(authorization)
        profile = db.get_user_profile(user["id"])
        return profile or {}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户画像失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/profile/me")
async def update_my_profile(
    payload: UserProfilePayload,
    authorization: Optional[str] = Header(None)
):
    try:
        user = _require_current_user(authorization)
        profile = db.upsert_user_profile(user["id"], payload.dict())
        _sync_profile_semantic_memory(user["id"], profile)
        return {"status": "success", "profile": profile}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户画像失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history")
async def get_chat_history():
    """
    获取对话历史
    
    Returns:
        对话历史列表
    """
    try:
        # 返回最近20条记录
        recent_history = chat_history[-20:] if len(chat_history) > 20 else chat_history
        
        return {
            "history": [
                {
                    "question": item["question"],
                    "answer": item["answer"],
                    "timestamp": item["timestamp"].isoformat()
                }
                for item in recent_history
            ],
            "total": len(chat_history)
        }
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """
    健康检查接口
    
    Returns:
        系统健康状态
    """
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "multi_agent_initialized": multi_agent_system is not None,
        "chat_history_count": len(chat_history),
        "timestamp": datetime.now()
    }


@app.post("/api/multi-agent/query")
async def multi_agent_query(request: QueryRequest):
    """
    多智能体系统专用查询接口（非流式）
    
    Args:
        request: 包含问题和用户档案的请求对象
        
    Returns:
        包含答案、工作流和参与教练的响应
    """
    try:
        if not multi_agent_system:
            raise HTTPException(status_code=500, detail="多智能体系统未初始化")
        
        logger.info(f"收到多智能体查询: {request.question}")
        
        result = multi_agent_system.process_request(
            request.question,
            request.user_profile
        )
        
        # 记录到历史
        chat_history.append({
            "question": request.question,
            "answer": result["response"],
            "timestamp": datetime.now(),
            "mode": "multi_agent",
            "workflow": result.get("workflow", []),
            "coaches": result.get("coaches_involved", "unknown")
        })
        
        return {
            "answer": result["response"],
            "structured_response": result.get("structured_response", {}),
            "workflow": result.get("workflow", []),
            "coaches_involved": result.get("coaches_involved", "unknown"),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"多智能体查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/multi-agent/query/stream")
async def multi_agent_query_stream(request: QueryRequest):
    """
    多智能体系统流式查询接口
    实时返回每个教练的处理进度和结果
    """
    async def generate():
        try:
            if not multi_agent_system:
                yield f"data: {json.dumps({'error': '多智能体系统未初始化'}, ensure_ascii=False)}\n\n"
                return
            
            logger.info(f"收到多智能体流式查询: {request.question}")
            
            # 发送开始信号
            yield f"data: {json.dumps({'type': 'start', 'message': '开始处理您的问题...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)
            
            # 发送检索信号
            yield f"data: {json.dumps({'type': 'progress', 'step': 'retrieve', 'message': '🔍 正在检索相关知识...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)
            
            # 用于收集教练结果的列表
            coach_results = []
            coach_count = 0
            
            # 定义流式回调函数
            def stream_callback(data):
                nonlocal coach_count
                if data.get("type") == "coach_result":
                    coach_count += 1
                    coach_results.append(data["coach"])
                    # 注意：这里不能直接yield，需要存储结果后在主流程中yield
            
            # 调用多智能体系统（带回调）
            result = multi_agent_system.process_request(
                request.question,
                request.user_profile,
                stream_callback=stream_callback
            )
            
            # 发送意图分析
            yield f"data: {json.dumps({'type': 'progress', 'step': 'intent', 'message': '🧠 分析问题意图...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)
            
            # 获取结构化响应
            structured_response = result.get("structured_response", {})
            coaches = structured_response.get("coaches", [])
            
            # 逐个发送教练的处理进度和结果
            for i, coach in enumerate(coaches, 1):
                # 发送处理中
                yield f"data: {json.dumps({'type': 'coach_start', 'coach': coach['name'], 'icon': coach['icon'], 'progress': f'{i}/{len(coaches)}'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.3)
                
                # 发送教练结果
                yield f"data: {json.dumps({'type': 'coach_result', 'coach': coach, 'progress': f'{i}/{len(coaches)}'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.2)
            
            # 发送综合建议
            yield f"data: {json.dumps({'type': 'progress', 'step': 'synthesize', 'message': '💡 生成综合建议...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)
            
            # 发送最终结果
            final_data = {
                "type": "complete",
                "answer": result["response"],
                "structured_response": structured_response,
                "workflow": result.get("workflow", []),
                "coaches_involved": result.get("coaches_involved", "unknown")
            }
            yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
            
            # 记录到历史
            chat_history.append({
                "question": request.question,
                "answer": result["response"],
                "timestamp": datetime.now(),
                "mode": "multi_agent_stream",
                "workflow": result.get("workflow", []),
                "coaches": result.get("coaches_involved", "unknown")
            })
            
            logger.info("多智能体流式查询完成")
            
        except Exception as e:
            logger.error(f"多智能体流式查询失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/multi-agent/coaches")
async def get_coaches_info():
    """
    获取所有教练的信息
    
    Returns:
        教练列表及其职责
    """
    try:
        coaches = [
            {
                "name": "训练规划教练",
                "role": "planning_coach",
                "description": "根据用户目标、能力和历史数据制定科学训练计划并动态优化",
                "icon": "📋"
            },
            {
                "name": "技术指导教练",
                "role": "technique_coach",
                "description": "提供规范的动作指导和详细的姿势分析",
                "icon": "🎯"
            },
            {
                "name": "运动康复教练",
                "role": "recovery_coach",
                "description": "针对运动损伤风险或已出现的伤痛提供预防措施与恢复建议",
                "icon": "🏥"
            }
        ]
        
        return {
            "coaches": coaches,
            "total": len(coaches)
        }
    except Exception as e:
        logger.error(f"获取教练信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 用户认证接口 ====================

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        # 验证两次密码是否一致
        if request.password != request.confirm_password:
            raise HTTPException(status_code=400, detail="两次输入的密码不一致")
        
        result = AuthService.register(
            username=request.username,
            email=request.email,
            password=request.password
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        logger.info(f"用户注册成功: {request.email}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """用户登录"""
    try:
        result = AuthService.login(
            account=request.account,
            password=request.password
        )
        
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["message"])
        
        logger.info(f"用户登录成功: {request.account}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/logout")
async def logout(token: str):
    """用户退出"""
    try:
        result = AuthService.logout(token)
        logger.info(f"用户退出: {token[:10]}...")
        return result
    except Exception as e:
        logger.error(f"退出失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/verify")
async def verify_token(token: str):
    """验证token"""
    try:
        user = AuthService.verify_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="token无效或已过期")
        return {"success": True, "user": user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证token失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/send-code")
async def send_verification_code(request: VerificationCodeRequest):
    """发送验证码"""
    try:
        result = AuthService.send_verification_code(request.email)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        logger.info(f"验证码已发送: {request.email}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送验证码失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """重置密码"""
    try:
        # 验证两次密码是否一致
        if request.new_password != request.confirm_password:
            raise HTTPException(status_code=400, detail="两次输入的密码不一致")
        
        result = AuthService.reset_password(
            email=request.email,
            code=request.code,
            new_password=request.new_password
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        logger.info(f"密码重置成功: {request.email}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置密码失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/complete-profile")
async def complete_profile(email: str):
    """标记用户资料已完成"""
    try:
        result = AuthService.update_profile_status(email, completed=True)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        logger.info(f"用户资料已完成: {email}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新资料状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 训练计划接口 ====================

@app.post("/api/training/plans")
async def create_training_plan(plan: TrainingPlan, authorization: Optional[str] = Header(None)):
    """创建训练计划"""
    try:
        user = _require_current_user(authorization)
        plan_dict = plan.dict()

        # 获取记忆上下文
        memory_context = memory_service.get_user_memory_context(user["id"])

        # 处理问卷画像
        questionnaire_profile = _build_profile_from_questionnaire(plan_dict.get("metadata"), "training_plan")
        if questionnaire_profile:
            profile = db.upsert_user_profile(user["id"], questionnaire_profile)
            _sync_profile_semantic_memory(user["id"], profile)

        # 将记忆上下文快照添加到 metadata
        existing_metadata = plan_dict.get("metadata") or {}
        metadata = {
            **existing_metadata,
            "_memory_snapshot": {
                "semantic_facts_count": len(memory_context.get("semantic_profile", {})),
                "recent_episodes_count": len(memory_context.get("recent_episodes", [])),
                "generated_at": datetime.now().isoformat()
            }
        }
        plan_dict["metadata"] = metadata

        # 标记计划基于记忆生成
        plan_dict["based_on_memory"] = True
        saved_plan = db.create_training_plan(user["id"], plan_dict)
        episode = _record_episode(user["id"], {
            "event_type": "plan_generated",
            "plan_id": saved_plan["id"],
            "event_summary": f"生成训练计划：{saved_plan['title']}",
            "trigger_source": "training_plan_create",
            "payload": {
                "goal": saved_plan.get("goal"),
                "selected_weekdays": saved_plan.get("selected_weekdays", []),
                "metadata": saved_plan.get("metadata", {})
            },
            "importance_score": 0.9,
            "tags": ["plan", "generated"]
        })

        if saved_plan.get("goal"):
            db.upsert_semantic_fact(
                user_id=user["id"],
                fact_category="profile",
                fact_key="latest_plan_goal",
                fact_value=str(saved_plan["goal"]),
                confidence=0.85,
                source_event_id=episode["id"],
                source_type="training_plan"
            )

        logger.info(f"创建训练计划: {plan.title}")

        # 触发记忆固化（如果需要）
        consolidation_result = consolidation_service.trigger_consolidation_if_needed(user["id"])
        if consolidation_result.get("status") != "skipped":
            logger.info(f"记忆固化已触发: user_id={user['id']}, patterns={len(consolidation_result.get('patterns_found', []))}")

        return {
            "status": "success",
            "plan": saved_plan,
            "consolidation": consolidation_result if consolidation_result.get("status") != "skipped" else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建训练计划失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/plans")
async def get_training_plans(authorization: Optional[str] = Header(None)):
    """获取所有训练计划"""
    try:
        user = _require_current_user(authorization)
        plans = db.list_training_plans(user["id"])
        return {
            "plans": plans,
            "total": len(plans)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练计划失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/plans/{plan_id}")
async def get_training_plan(plan_id: int, authorization: Optional[str] = Header(None)):
    """获取单个训练计划"""
    try:
        user = _require_current_user(authorization)
        plan = db.get_training_plan_by_id(user["id"], plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="训练计划不存在")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练计划失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/training/plans/{plan_id}")
async def update_training_plan(
    plan_id: int,
    payload: TrainingPlanUpdate,
    authorization: Optional[str] = Header(None)
):
    """鏇存柊璁粌璁″垝"""
    try:
        user = _require_current_user(authorization)
        plan = db.get_training_plan_by_id(user["id"], plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="璁粌璁″垝涓嶅瓨鍦?")

        updates = payload.dict(exclude_unset=True)
        updated_plan = db.update_training_plan(user["id"], plan_id, updates)
        if updated_plan is None:
            raise HTTPException(status_code=404, detail="训练计划不存在")

        tags = ["plan", "updated"]
        event_summary = f"更新训练计划：{updated_plan['title']}"

        # 处理训练日选择
        if "selected_weekdays" in updates:
            tags.append("weekday_selected")
            selected_weekdays = updated_plan.get('selected_weekdays', [])
            event_summary = f"更新训练计划训练日：{','.join(selected_weekdays)}"

            # 记录情景事件并更新语义记忆
            episode = _record_episode(user["id"], {
                "event_type": "plan_updated",
                "plan_id": plan_id,
                "event_summary": event_summary,
                "trigger_source": "training_plan_update",
                "payload": updates,
                "importance_score": 0.7,
                "tags": tags
            })

            # 从训练日选择提炼语义记忆
            _update_semantic_from_weekday_selection(user["id"], selected_weekdays, episode.get("id"))
        else:
            _record_episode(user["id"], {
                "event_type": "plan_updated",
                "plan_id": plan_id,
                "event_summary": event_summary,
                "trigger_source": "training_plan_update",
                "payload": updates,
                "importance_score": 0.7,
                "tags": tags
            })

        logger.info(f"鏇存柊璁粌璁″垝: {plan_id}")
        return {
            "status": "success",
            "plan": updated_plan
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"鏇存柊璁粌璁″垝澶辫触: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/training/plans/{plan_id}")
async def delete_training_plan(plan_id: int, authorization: Optional[str] = Header(None)):
    """删除训练计划"""
    try:
        user = _require_current_user(authorization)
        deleted = db.delete_training_plan(user["id"], plan_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="训练计划不存在")
        logger.info(f"删除训练计划: {plan_id}")
        return {"status": "success", "message": "训练计划已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除训练计划失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 训练记录接口 ====================

@app.post("/api/training/records")
async def create_training_record(record: TrainingRecord, authorization: Optional[str] = Header(None)):
    """创建训练记录"""
    try:
        user = _require_current_user(authorization)
        record_dict = record.dict()
        saved_record = db.create_training_record(user["id"], record_dict)

        event_type = "training_completed"
        if saved_record.get("completion_status") == "skipped":
            event_type = "training_skipped"

        episode = _record_episode(user["id"], {
            "event_type": event_type,
            "plan_id": saved_record.get("plan_id"),
            "record_id": saved_record["id"],
            "event_summary": f"{saved_record['date']} {saved_record['training_type']} 训练记录已保存",
            "trigger_source": "training_record_create",
            "payload": saved_record,
            "importance_score": 0.8,
            "tags": ["training", saved_record.get("completion_status", "completed")]
        })
        _update_semantic_from_training_record(user["id"], saved_record, source_event_id=episode["id"])
        
        logger.info(f"创建训练记录: {record.training_type} - {record.date}")

        # 分析训练负荷并生成建议
        suggestion = _analyze_training_load(user["id"])

        # 触发记忆固化（如果需要）
        consolidation_result = consolidation_service.trigger_consolidation_if_needed(user["id"])
        if consolidation_result.get("status") != "skipped":
            logger.info(f"记忆固化已触发: user_id={user['id']}, patterns={len(consolidation_result.get('patterns_found', []))}")

        return {
            "status": "success",
            "record": saved_record,
            "suggestion": suggestion,
            "consolidation": consolidation_result if consolidation_result.get("status") != "skipped" else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建训练记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/records")
async def get_training_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    training_type: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """获取训练记录（支持筛选）"""
    try:
        user = _require_current_user(authorization)
        filtered_records = db.list_training_records(user["id"], start_date, end_date, training_type)
        return {
            "records": filtered_records,
            "total": len(filtered_records)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/records/{record_id}")
async def get_training_record(record_id: int, authorization: Optional[str] = Header(None)):
    """获取单个训练记录"""
    try:
        user = _require_current_user(authorization)
        record = db.get_training_record_by_id(user["id"], record_id)
        if not record:
            raise HTTPException(status_code=404, detail="训练记录不存在")
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/training/records/{record_id}")
async def delete_training_record(record_id: int, authorization: Optional[str] = Header(None)):
    """删除训练记录"""
    try:
        user = _require_current_user(authorization)
        deleted = db.delete_training_record(user["id"], record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="训练记录不存在")
        logger.info(f"删除训练记录: {record_id}")
        return {"status": "success", "message": "训练记录已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除训练记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 饮食记录接口 ====================

@app.post("/api/daily/records")
async def create_daily_record(record: DailyRecord, authorization: Optional[str] = Header(None)):
    """创建饮食记录"""
    try:
        user = _require_current_user(authorization)
        record_dict = record.dict()
        saved_record = db.create_daily_record(user["id"], record_dict)

        # 记录到情景记忆
        episode = _record_episode(user["id"], {
            "event_type": "diet_recorded",
            "record_id": saved_record["id"],
            "event_summary": f"{saved_record['date']} {saved_record['meal_type']} 饮食记录已保存",
            "trigger_source": "daily_record_create",
            "payload": saved_record,
            "importance_score": 0.6,
            "tags": ["diet", saved_record["meal_type"]]
        })

        logger.info(f"创建饮食记录: {record.meal_type} - {record.date}")
        return {"status": "success", "record": saved_record}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建饮食记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/daily/records")
async def get_daily_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """获取饮食记录（支持筛选）"""
    try:
        user = _require_current_user(authorization)
        filtered_records = db.list_daily_records(user["id"], start_date, end_date)
        return {
            "records": filtered_records,
            "total": len(filtered_records)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取饮食记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/daily/records/{record_id}")
async def get_daily_record(record_id: int, authorization: Optional[str] = Header(None)):
    """获取单个饮食记录"""
    try:
        user = _require_current_user(authorization)
        record = db.get_daily_record_by_id(user["id"], record_id)
        if not record:
            raise HTTPException(status_code=404, detail="饮食记录不存在")
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取饮食记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/daily/records/{record_id}")
async def delete_daily_record(record_id: int, authorization: Optional[str] = Header(None)):
    """删除饮食记录"""
    try:
        user = _require_current_user(authorization)
        deleted = db.delete_daily_record(user["id"], record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="饮食记录不存在")
        logger.info(f"删除饮食记录: {record_id}")
        return {"status": "success", "message": "饮食记录已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除饮食记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 体重记录接口 ====================

@app.post("/api/weight/records")
async def create_weight_record(record: WeightRecord, authorization: Optional[str] = Header(None)):
    """创建体重记录"""
    try:
        user = _require_current_user(authorization)
        record_dict = record.dict()
        saved_record = db.create_weight_record(user["id"], record_dict)

        # 记录到情景记忆
        episode = _record_episode(user["id"], {
            "event_type": "weight_measured",
            "record_id": saved_record["id"],
            "event_summary": f"{saved_record['date']} 体重记录已保存: {saved_record['weight']}kg",
            "trigger_source": "weight_record_create",
            "payload": saved_record,
            "importance_score": 0.7,
            "tags": ["weight", "health_metric"]
        })

        logger.info(f"创建体重记录: {record.weight}kg - {record.date}")
        return {"status": "success", "record": saved_record}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建体重记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weight/records")
async def get_weight_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """获取体重记录（支持筛选）"""
    try:
        user = _require_current_user(authorization)
        filtered_records = db.list_weight_records(user["id"], start_date, end_date)
        return {
            "records": filtered_records,
            "total": len(filtered_records)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取体重记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weight/records/{record_id}")
async def get_weight_record(record_id: int, authorization: Optional[str] = Header(None)):
    """获取个体重记录"""
    try:
        user = _require_current_user(authorization)
        record = db.get_weight_record_by_id(user["id"], record_id)
        if not record:
            raise HTTPException(status_code=404, detail="体重记录不存在")
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取体重记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/weight/records/{record_id}")
async def delete_weight_record(record_id: int, authorization: Optional[str] = Header(None)):
    """删除体重记录"""
    try:
        user = _require_current_user(authorization)
        deleted = db.delete_weight_record(user["id"], record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="体重记录不存在")
        logger.info(f"删除体重记录: {record_id}")
        return {"status": "success", "message": "体重记录已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除体重记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 数据分析接口 ====================

@app.get("/api/training/analytics/frequency")
async def get_training_frequency(days: int = 30, authorization: Optional[str] = Header(None)):
    """获取训练频率趋势"""
    try:
        from datetime import datetime, timedelta
        from collections import defaultdict
        user = _require_current_user(authorization)
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 统计每天的训练次数
        frequency_map = defaultdict(int)
        for record in db.list_training_records(user["id"]):
            record_date = datetime.fromisoformat(record["date"])
            if start_date <= record_date <= end_date:
                date_str = record_date.strftime("%Y-%m-%d")
                frequency_map[date_str] += 1
        
        # 生成完整的日期序列
        dates = []
        counts = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            dates.append(date_str)
            counts.append(frequency_map.get(date_str, 0))
            current_date += timedelta(days=1)
        
        return {
            "dates": dates,
            "counts": counts,
            "total_trainings": sum(counts),
            "average_per_week": sum(counts) / (days / 7) if days > 0 else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练频率失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/analytics/load")
async def get_training_load(days: int = 30, authorization: Optional[str] = Header(None)):
    """获取训练负荷变化"""
    try:
        from datetime import datetime, timedelta
        from collections import defaultdict
        user = _require_current_user(authorization)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 计算每天的训练负荷（疲劳度 * 时长）
        load_map = defaultdict(float)
        for record in db.list_training_records(user["id"]):
            record_date = datetime.fromisoformat(record["date"])
            if start_date <= record_date <= end_date:
                date_str = record_date.strftime("%Y-%m-%d")
                fatigue = record.get("fatigue_level", 3)
                duration = record.get("duration", 60)
                load = fatigue * duration / 60  # 标准化为小时
                load_map[date_str] += load
        
        # 生成完整的日期序列
        dates = []
        loads = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            dates.append(date_str)
            loads.append(round(load_map.get(date_str, 0), 2))
            current_date += timedelta(days=1)
        
        return {
            "dates": dates,
            "loads": loads,
            "average_load": round(sum(loads) / len(loads), 2) if loads else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练负荷失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/analytics/summary")
async def get_training_summary(period: str = "week", authorization: Optional[str] = Header(None)):
    """获取训练总结（周/月）"""
    try:
        from datetime import datetime, timedelta
        user = _require_current_user(authorization)
        
        end_date = datetime.now()
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        # 筛选时间范围内的记录
        period_records = [
            r for r in db.list_training_records(user["id"])
            if start_date <= datetime.fromisoformat(r["date"]) <= end_date
        ]
        
        # 统计
        total_trainings = len(period_records)
        total_duration = sum(r.get("duration", 0) for r in period_records)
        avg_fatigue = sum(r.get("fatigue_level", 0) for r in period_records) / total_trainings if total_trainings > 0 else 0
        
        # 按训练类型统计
        type_counts = {}
        for record in period_records:
            t_type = record["training_type"]
            type_counts[t_type] = type_counts.get(t_type, 0) + 1
        
        return {
            "period": period,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_trainings": total_trainings,
            "total_duration": total_duration,
            "average_fatigue": round(avg_fatigue, 2),
            "training_types": type_counts
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练总结失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _analyze_training_load(user_id: int) -> str:
    """分析训练负荷并生成建议"""
    try:
        from datetime import datetime, timedelta
        
        # 分析最近2周的训练负荷
        two_weeks_ago = datetime.now() - timedelta(days=14)
        recent_records = [
            r for r in db.list_training_records(user_id)
            if datetime.fromisoformat(r["date"]) >= two_weeks_ago
        ]
        
        if len(recent_records) < 3:
            return "训练数据较少，建议保持规律训练"
        
        # 计算平均疲劳度
        avg_fatigue = sum(r.get("fatigue_level", 3) for r in recent_records) / len(recent_records)
        
        # 计算训练频率
        training_frequency = len(recent_records) / 14  # 每天平均训练次数
        
        # 生成建议
        if avg_fatigue >= 4 and training_frequency > 0.7:
            return "⚠️ 你最近2周训练负荷偏高，建议降低强度或增加休息日"
        elif avg_fatigue >= 4:
            return "💡 疲劳度较高，建议适当降低训练强度"
        elif training_frequency > 0.8:
            return "💡 训练频率较高，注意合理安排休息"
        elif avg_fatigue <= 2 and training_frequency < 0.4:
            return "✅ 训练负荷适中，可以适当增加训练强度或频率"
        else:
            return "✅ 训练状态良好，继续保持"
    except Exception as e:
        logger.error(f"分析训练负荷失败: {e}")
        return "训练状态分析中..."


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
