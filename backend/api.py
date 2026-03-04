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
    username: str
    password: str


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
                    yield f"data: {json.dumps({'error': '多智能体系统未初始化'}, ensure_ascii=False)}\n\n"
                    return
                
                logger.info(f"收到多智能体查询: {request.question}")
                
                # 使用多智能体系统处理
                result = multi_agent_system.process_request(
                    request.question,
                    request.user_profile
                )
                
                answer = result["response"]
                workflow = result.get("workflow", [])
                
                # 记录到历史
                chat_history.append({
                    "question": request.question,
                    "answer": answer,
                    "timestamp": datetime.now(),
                    "mode": "multi_agent",
                    "workflow": workflow
                })
                
            else:
                if not agent:
                    yield f"data: {json.dumps({'error': 'Agent未初始化'}, ensure_ascii=False)}\n\n"
                    return
                
                logger.info(f"收到单智能体查询: {request.question}")
                
                # 使用单智能体处理
                answer = agent.query(request.question)
                
                # 记录到历史
                chat_history.append({
                    "question": request.question,
                    "answer": answer,
                    "timestamp": datetime.now(),
                    "mode": "single_agent"
                })
            
            # 模拟流式输出，逐字发送
            words = answer
            chunk_size = 2  # 每次发送的字符数
            
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i + chunk_size]
                data = {
                    "content": chunk,
                    "done": False
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.03)  # 控制输出速度
            
            # 发送完成信号
            yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            logger.error(f"查询失败: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    
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
        answer = agent.query(request.question)
        
        # 记录到历史
        chat_history.append({
            "question": request.question,
            "answer": answer,
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
            "workflow": result.get("workflow", []),
            "coaches_involved": result.get("coaches_involved", "unknown"),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"多智能体查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
