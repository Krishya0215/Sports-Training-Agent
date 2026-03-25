"""
运动训练知识问答系统 - FastAPI后端接口
为Vue前端提供RESTful API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import sys
from pathlib import Path
import json
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.graph_agent import SportsTrainingAgent
from agent.multi_agent_system import MultiAgentTrainingSystem
from utils.logger_handler import logger
from backend.auth import AuthService

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

# 数据存储（生产环境应使用数据库）
training_plans = []  # 训练计划
training_records = []  # 训练记录
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
    duration: Optional[int] = None  # 分钟
    intensity: Optional[str] = None  # 低/中/高
    feedback: Optional[str] = None  # 用户反馈
    fatigue_level: Optional[int] = None  # 疲劳度 1-5
    pain_level: Optional[int] = None  # 疼痛度 1-5
    notes: Optional[str] = None


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
async def query(request: QueryRequest):
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
            # 根据请求选择使用单智能体或多智能体系统
            if request.use_multi_agent:
                if not multi_agent_system:
                    yield f"data: {json.dumps({'type': 'answer', 'content': '多智能体系统未初始化', 'done': True}, ensure_ascii=False)}\n\n"
                    return
                
                logger.info(f"收到多智能体查询: {request.question}")
                
                # 使用多智能体系统处理
                result = multi_agent_system.process_request(
                    request.question,
                    request.user_profile
                )
                
                thinking = result.get("thinking", "")
                answer = result["response"]
                
            else:
                if not agent:
                    yield f"data: {json.dumps({'type': 'answer', 'content': 'Agent未初始化', 'done': True}, ensure_ascii=False)}\n\n"
                    return
                
                logger.info(f"收到单智能体查询: {request.question}")
                
                # 使用单智能体处理
                result = agent.query(request.question)
                thinking = result.get("thinking", "")
                answer = result.get("answer", "")
            
            # 先流式输出思考过程
            if thinking:
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
                "mode": "multi_agent" if request.use_multi_agent else "single_agent"
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
async def query_sync(request: QueryRequest):
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
async def get_memory_summary():
    """
    获取记忆系统摘要
    
    Returns:
        记忆系统各层的统计信息
    """
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent未初始化")
        
        summary = agent.get_memory_summary()
        
        return MemorySummary(
            working_memory_size=summary.get('working_memory_size', 0),
            episodic_memory_size=summary.get('episodic_memory_size', 0),
            semantic_concepts=summary.get('semantic_concepts', 0),
            perceptual_documents=summary.get('perceptual_documents', 0)
        )
    except Exception as e:
        logger.error(f"获取记忆摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/clear")
async def clear_working_memory():
    """
    清空工作记忆
    
    Returns:
        操作结果
    """
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent未初始化")
        
        agent.clear_working_memory()
        logger.info("工作记忆已清空")
        
        return {
            "status": "success",
            "message": "工作记忆已清空",
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"清空工作记忆失败: {e}")
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
                "name": "体能评估教练",
                "role": "fitness_coach",
                "description": "分析用户身体状态与疲劳程度，判断训练适宜性",
                "icon": "💪"
            },
            {
                "name": "运动康复教练",
                "role": "recovery_coach",
                "description": "针对运动损伤风险或已出现的伤痛提供预防措施与恢复建议",
                "icon": "🏥"
            },
            {
                "name": "安全督导教练",
                "role": "safety_coach",
                "description": "识别训练过程中的潜在风险因素，提高训练安全性",
                "icon": "⚠️"
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
async def create_training_plan(plan: TrainingPlan):
    """创建训练计划"""
    try:
        plan_dict = plan.dict()
        plan_dict["id"] = len(training_plans) + 1
        plan_dict["created_at"] = datetime.now().isoformat()
        training_plans.append(plan_dict)
        
        logger.info(f"创建训练计划: {plan.title}")
        return {
            "status": "success",
            "plan": plan_dict
        }
    except Exception as e:
        logger.error(f"创建训练计划失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/plans")
async def get_training_plans():
    """获取所有训练计划"""
    try:
        return {
            "plans": training_plans,
            "total": len(training_plans)
        }
    except Exception as e:
        logger.error(f"获取训练计划失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/plans/{plan_id}")
async def get_training_plan(plan_id: int):
    """获取单个训练计划"""
    try:
        plan = next((p for p in training_plans if p["id"] == plan_id), None)
        if not plan:
            raise HTTPException(status_code=404, detail="训练计划不存在")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练计划失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/training/plans/{plan_id}")
async def update_training_plan(plan_id: int, payload: TrainingPlanUpdate):
    """鏇存柊璁粌璁″垝"""
    try:
        plan = next((p for p in training_plans if p["id"] == plan_id), None)
        if not plan:
            raise HTTPException(status_code=404, detail="璁粌璁″垝涓嶅瓨鍦?")

        updates = payload.dict(exclude_unset=True)
        plan.update(updates)
        plan["updated_at"] = datetime.now().isoformat()

        logger.info(f"鏇存柊璁粌璁″垝: {plan_id}")
        return {
            "status": "success",
            "plan": plan
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"鏇存柊璁粌璁″垝澶辫触: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/training/plans/{plan_id}")
async def delete_training_plan(plan_id: int):
    """删除训练计划"""
    try:
        global training_plans
        training_plans = [p for p in training_plans if p["id"] != plan_id]
        logger.info(f"删除训练计划: {plan_id}")
        return {"status": "success", "message": "训练计划已删除"}
    except Exception as e:
        logger.error(f"删除训练计划失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 训练记录接口 ====================

@app.post("/api/training/records")
async def create_training_record(record: TrainingRecord):
    """创建训练记录"""
    try:
        record_dict = record.dict()
        record_dict["id"] = len(training_records) + 1
        record_dict["created_at"] = datetime.now().isoformat()
        training_records.append(record_dict)
        
        logger.info(f"创建训练记录: {record.training_type} - {record.date}")
        
        # 分析训练负荷并生成建议
        suggestion = _analyze_training_load()
        
        return {
            "status": "success",
            "record": record_dict,
            "suggestion": suggestion
        }
    except Exception as e:
        logger.error(f"创建训练记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/records")
async def get_training_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    training_type: Optional[str] = None
):
    """获取训练记录（支持筛选）"""
    try:
        filtered_records = training_records
        
        # 按日期筛选
        if start_date:
            filtered_records = [r for r in filtered_records if r["date"] >= start_date]
        if end_date:
            filtered_records = [r for r in filtered_records if r["date"] <= end_date]
        
        # 按训练类型筛选
        if training_type:
            filtered_records = [r for r in filtered_records if r["training_type"] == training_type]
        
        return {
            "records": filtered_records,
            "total": len(filtered_records)
        }
    except Exception as e:
        logger.error(f"获取训练记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/records/{record_id}")
async def get_training_record(record_id: int):
    """获取单个训练记录"""
    try:
        record = next((r for r in training_records if r["id"] == record_id), None)
        if not record:
            raise HTTPException(status_code=404, detail="训练记录不存在")
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取训练记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/training/records/{record_id}")
async def delete_training_record(record_id: int):
    """删除训练记录"""
    try:
        global training_records
        training_records = [r for r in training_records if r["id"] != record_id]
        logger.info(f"删除训练记录: {record_id}")
        return {"status": "success", "message": "训练记录已删除"}
    except Exception as e:
        logger.error(f"删除训练记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 数据分析接口 ====================

@app.get("/api/training/analytics/frequency")
async def get_training_frequency(days: int = 30):
    """获取训练频率趋势"""
    try:
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 统计每天的训练次数
        frequency_map = defaultdict(int)
        for record in training_records:
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
    except Exception as e:
        logger.error(f"获取训练频率失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/analytics/load")
async def get_training_load(days: int = 30):
    """获取训练负荷变化"""
    try:
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 计算每天的训练负荷（疲劳度 * 时长）
        load_map = defaultdict(float)
        for record in training_records:
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
    except Exception as e:
        logger.error(f"获取训练负荷失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/analytics/summary")
async def get_training_summary(period: str = "week"):
    """获取训练总结（周/月）"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        # 筛选时间范围内的记录
        period_records = [
            r for r in training_records
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
    except Exception as e:
        logger.error(f"获取训练总结失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _analyze_training_load() -> str:
    """分析训练负荷并生成建议"""
    try:
        from datetime import datetime, timedelta
        
        # 分析最近2周的训练负荷
        two_weeks_ago = datetime.now() - timedelta(days=14)
        recent_records = [
            r for r in training_records
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
