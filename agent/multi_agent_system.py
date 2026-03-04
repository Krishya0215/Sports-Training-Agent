"""
多智能体协同训练支持系统
模拟真实运动指导团队的协作模式
"""
from typing import TypedDict, List, Annotated, Literal
from operator import add
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from model.factory import chat_model
from rag.vector_store import VectorStoreService
from rag.advanced_retriever import AdvancedRetriever
from memory.memory_manager import MemoryManager
from utils.logger_handler import logger
from utils.prompt_loader import load_prompt_by_key
import json


class TrainingState(TypedDict):
    """训练系统状态定义"""
    user_input: str  # 用户输入
    user_profile: dict  # 用户档案（目标、能力、历史数据）
    training_plan: str  # 训练计划
    technique_guidance: str  # 技术指导
    fitness_assessment: str  # 体能评估
    recovery_advice: str  # 康复建议
    safety_warnings: str  # 安全提示
    final_response: str  # 最终响应
    retrieved_docs: List  # 检索到的文档
    current_coach: str  # 当前激活的教练
    workflow_history: Annotated[List[str], add]  # 工作流历史


class CoachAgent:
    """教练智能体基类"""
    
    def __init__(self, name: str, role: str, prompt_template: str):
        self.name = name
        self.role = role
        self.model = chat_model
        self.prompt = PromptTemplate.from_template(prompt_template)
        self.chain = self.prompt | self.model | StrOutputParser()
        logger.info(f"初始化教练: {name} - {role}")
    
    def process(self, state: TrainingState, context: str = "") -> str:
        """处理请求"""
        try:
            result = self.chain.invoke({
                "user_input": state["user_input"],
                "user_profile": json.dumps(state.get("user_profile", {}), ensure_ascii=False),
                "context": context,
                "retrieved_docs": self._format_docs(state.get("retrieved_docs", []))
            })
            logger.info(f"{self.name} 处理完成")
            return result
        except Exception as e:
            logger.error(f"{self.name} 处理失败: {e}")
            return f"[{self.name}处理出错: {str(e)}]"
    
    def _format_docs(self, docs: List) -> str:
        """格式化文档"""
        if not docs:
            return "无相关文档"
        formatted = []
        for i, doc in enumerate(docs[:5], 1):
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            formatted.append(f"[文档{i}] {content[:200]}...")
        return "\n".join(formatted)


class MultiAgentTrainingSystem:
    """多智能体协同训练支持系统"""
    
    def __init__(self):
        # 初始化RAG组件
        self.vector_store_service = VectorStoreService()
        base_retriever = self.vector_store_service.get_retriever()
        self.retriever = AdvancedRetriever(base_retriever)
        
        # 初始化记忆管理器
        self.memory_manager = MemoryManager()
        
        # 初始化各个专业教练
        self._init_coaches()
        
        # 构建协作状态图
        self.graph = self._build_graph()
        
        logger.info("多智能体训练支持系统初始化完成")
    
    def _init_coaches(self):
        """初始化各个专业教练智能体"""
        
        # 1. 训练规划教练
        self.planning_coach = CoachAgent(
            name="训练规划教练",
            role="制定科学训练计划并动态优化",
            prompt_template="""你是一位专业的训练规划教练。根据用户的目标、能力和历史数据，制定科学的训练计划。

用户输入: {user_input}
用户档案: {user_profile}
参考知识: {retrieved_docs}

请提供:
1. 训练目标分析
2. 阶段性训练计划（周期、强度、频率）
3. 动态优化建议
4. 预期效果

训练计划:"""
        )
        
        # 2. 技术指导教练
        self.technique_coach = CoachAgent(
            name="技术指导教练",
            role="提供动作指导和姿势分析",
            prompt_template="""你是一位专业的技术指导教练。为用户提供规范的动作指导和详细的姿势分析。

用户输入: {user_input}
用户档案: {user_profile}
参考知识: {retrieved_docs}
上下文: {context}

请提供:
1. 动作要领和标准姿势
2. 常见错误及纠正方法
3. 分步骤详细指导
4. 技术要点提示

技术指导:"""
        )
        
        # 3. 体能评估教练
        self.fitness_coach = CoachAgent(
            name="体能评估教练",
            role="分析身体状态与疲劳程度",
            prompt_template="""你是一位专业的体能评估教练。分析用户的身体状态与疲劳程度，判断训练适宜性。

用户输入: {user_input}
用户档案: {user_profile}
训练计划: {context}

请提供:
1. 当前体能状态评估
2. 疲劳程度分析
3. 是否适合继续训练的建议
4. 训练强度调整建议

体能评估:"""
        )
        
        # 4. 运动康复教练
        self.recovery_coach = CoachAgent(
            name="运动康复教练",
            role="提供损伤预防与恢复建议",
            prompt_template="""你是一位专业的运动康复教练。针对运动损伤风险或已出现的伤痛，提供预防措施与恢复建议。

用户输入: {user_input}
用户档案: {user_profile}
参考知识: {retrieved_docs}
上下文: {context}

请提供:
1. 损伤风险评估
2. 预防措施
3. 恢复训练建议
4. 注意事项

康复建议:"""
        )
        
        # 5. 安全督导教练
        self.safety_coach = CoachAgent(
            name="安全督导教练",
            role="识别风险因素并提供安全提示",
            prompt_template="""你是一位专业的安全督导教练。识别训练过程中的潜在风险因素，提高训练安全性。

用户输入: {user_input}
训练计划: {context}
参考知识: {retrieved_docs}

请提供:
1. 潜在风险识别（危险姿势、动作）
2. 安全注意事项
3. 紧急情况处理建议
4. 环境与装备检查要点

安全提示:"""
        )
    
    def _build_graph(self) -> StateGraph:
        """构建多智能体协作状态图"""
        workflow = StateGraph(TrainingState)
        
        # 添加节点
        workflow.add_node("retrieve_knowledge", self._retrieve_node)
        workflow.add_node("analyze_intent", self._analyze_intent_node)
        workflow.add_node("planning_coach", self._planning_coach_node)
        workflow.add_node("technique_coach", self._technique_coach_node)
        workflow.add_node("fitness_coach", self._fitness_coach_node)
        workflow.add_node("recovery_coach", self._recovery_coach_node)
        workflow.add_node("safety_coach", self._safety_coach_node)
        workflow.add_node("synthesize_response", self._synthesize_node)
        workflow.add_node("update_memory", self._update_memory_node)
        
        # 定义工作流
        workflow.set_entry_point("retrieve_knowledge")
        workflow.add_edge("retrieve_knowledge", "analyze_intent")
        
        # 根据意图路由到不同教练
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_to_coaches,
            {
                "planning": "planning_coach",
                "technique": "technique_coach",
                "fitness": "fitness_coach",
                "recovery": "recovery_coach",
                "safety": "safety_coach",
                "comprehensive": "planning_coach"  # 综合咨询从规划开始
            }
        )
        
        # 综合咨询流程：规划 -> 技术 -> 体能 -> 康复 -> 安全 -> 综合
        workflow.add_edge("planning_coach", "technique_coach")
        workflow.add_edge("technique_coach", "fitness_coach")
        workflow.add_edge("fitness_coach", "recovery_coach")
        workflow.add_edge("recovery_coach", "safety_coach")
        workflow.add_edge("safety_coach", "synthesize_response")
        
        # 最终节点
        workflow.add_edge("synthesize_response", "update_memory")
        workflow.add_edge("update_memory", END)
        
        return workflow.compile()

    
    def _retrieve_node(self, state: TrainingState) -> TrainingState:
        """检索相关知识"""
        user_input = state["user_input"]
        logger.info(f"检索知识: {user_input}")
        
        try:
            retrieved_docs = self.retriever.retrieve(user_input)
            state["retrieved_docs"] = retrieved_docs
            state["workflow_history"] = [f"检索到 {len(retrieved_docs)} 个相关文档"]
            logger.info(f"检索完成: {len(retrieved_docs)} 个文档")
        except Exception as e:
            logger.error(f"检索失败: {e}")
            state["retrieved_docs"] = []
            state["workflow_history"] = ["检索失败"]
        
        return state
    
    def _analyze_intent_node(self, state: TrainingState) -> TrainingState:
        """分析用户意图，决定激活哪些教练"""
        user_input = state["user_input"].lower()
        
        # 简单的意图识别（可以用更复杂的NLP模型）
        intent_keywords = {
            "planning": ["计划", "规划", "安排", "周期", "目标"],
            "technique": ["动作", "姿势", "技术", "要领", "标准"],
            "fitness": ["体能", "疲劳", "状态", "评估", "能力"],
            "recovery": ["恢复", "康复", "损伤", "伤痛", "拉伤"],
            "safety": ["安全", "风险", "危险", "注意", "防护"]
        }
        
        detected_intents = []
        for intent, keywords in intent_keywords.items():
            if any(kw in user_input for kw in keywords):
                detected_intents.append(intent)
        
        # 如果检测到多个意图或没有明确意图，使用综合模式
        if len(detected_intents) != 1:
            state["current_coach"] = "comprehensive"
        else:
            state["current_coach"] = detected_intents[0]
        
        state["workflow_history"] = state.get("workflow_history", []) + [
            f"意图分析: {state['current_coach']}"
        ]
        logger.info(f"意图识别: {state['current_coach']}")
        
        return state
    
    def _route_to_coaches(self, state: TrainingState) -> str:
        """路由到相应的教练"""
        return state["current_coach"]
    
    def _planning_coach_node(self, state: TrainingState) -> TrainingState:
        """训练规划教练节点"""
        state["training_plan"] = self.planning_coach.process(state)
        state["workflow_history"] = state.get("workflow_history", []) + ["训练规划教练完成"]
        return state
    
    def _technique_coach_node(self, state: TrainingState) -> TrainingState:
        """技术指导教练节点"""
        context = state.get("training_plan", "")
        state["technique_guidance"] = self.technique_coach.process(state, context)
        state["workflow_history"] = state.get("workflow_history", []) + ["技术指导教练完成"]
        return state
    
    def _fitness_coach_node(self, state: TrainingState) -> TrainingState:
        """体能评估教练节点"""
        context = state.get("training_plan", "")
        state["fitness_assessment"] = self.fitness_coach.process(state, context)
        state["workflow_history"] = state.get("workflow_history", []) + ["体能评估教练完成"]
        return state
    
    def _recovery_coach_node(self, state: TrainingState) -> TrainingState:
        """运动康复教练节点"""
        context = f"训练计划: {state.get('training_plan', '')}\n技术指导: {state.get('technique_guidance', '')}"
        state["recovery_advice"] = self.recovery_coach.process(state, context)
        state["workflow_history"] = state.get("workflow_history", []) + ["运动康复教练完成"]
        return state
    
    def _safety_coach_node(self, state: TrainingState) -> TrainingState:
        """安全督导教练节点"""
        context = f"训练计划: {state.get('training_plan', '')}"
        state["safety_warnings"] = self.safety_coach.process(state, context)
        state["workflow_history"] = state.get("workflow_history", []) + ["安全督导教练完成"]
        return state
    
    def _synthesize_node(self, state: TrainingState) -> TrainingState:
        """综合各教练的建议，生成最终响应"""
        logger.info("综合各教练建议")
        
        # 构建综合响应
        response_parts = []
        
        if state.get("training_plan"):
            response_parts.append(f"## 📋 训练规划\n{state['training_plan']}\n")
        
        if state.get("technique_guidance"):
            response_parts.append(f"## 🎯 技术指导\n{state['technique_guidance']}\n")
        
        if state.get("fitness_assessment"):
            response_parts.append(f"## 💪 体能评估\n{state['fitness_assessment']}\n")
        
        if state.get("recovery_advice"):
            response_parts.append(f"## 🏥 康复建议\n{state['recovery_advice']}\n")
        
        if state.get("safety_warnings"):
            response_parts.append(f"## ⚠️ 安全提示\n{state['safety_warnings']}\n")
        
        state["final_response"] = "\n".join(response_parts)
        state["workflow_history"] = state.get("workflow_history", []) + ["综合响应生成完成"]
        
        logger.info("综合响应生成完成")
        return state
    
    def _update_memory_node(self, state: TrainingState) -> TrainingState:
        """更新记忆系统"""
        try:
            self.memory_manager.record_interaction(
                question=state["user_input"],
                answer=state["final_response"],
                retrieved_docs=[doc.metadata.get("source", "未知") for doc in state.get("retrieved_docs", [])],
                metadata={
                    "workflow": state.get("workflow_history", []),
                    "coaches_involved": state.get("current_coach", "unknown")
                }
            )
            logger.info("记忆更新完成")
        except Exception as e:
            logger.error(f"记忆更新失败: {e}")
        
        return state
    
    def process_request(self, user_input: str, user_profile: dict = None) -> dict:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入
            user_profile: 用户档案（目标、能力、历史数据等）
            
        Returns:
            包含最终响应和工作流历史的字典
        """
        # 初始化状态
        initial_state = {
            "user_input": user_input,
            "user_profile": user_profile or {},
            "training_plan": "",
            "technique_guidance": "",
            "fitness_assessment": "",
            "recovery_advice": "",
            "safety_warnings": "",
            "final_response": "",
            "retrieved_docs": [],
            "current_coach": "",
            "workflow_history": []
        }
        
        try:
            # 执行状态图
            final_state = self.graph.invoke(initial_state)
            
            return {
                "response": final_state["final_response"],
                "workflow": final_state.get("workflow_history", []),
                "coaches_involved": final_state.get("current_coach", "unknown")
            }
        except Exception as e:
            logger.error(f"请求处理失败: {e}")
            return {
                "response": f"抱歉，处理您的请求时出现错误: {str(e)}",
                "workflow": ["处理失败"],
                "coaches_involved": "error"
            }
    
    def load_knowledge_base(self):
        """加载知识库"""
        logger.info("开始加载知识库...")
        self.vector_store_service.load_documents()
        logger.info("知识库加载完成")
    
    def get_memory_summary(self):
        """获取记忆摘要"""
        return self.memory_manager.summarize_memory()
    
    def clear_working_memory(self):
        """清空工作记忆"""
        self.memory_manager.working_memory.clear()
        logger.info("工作记忆已清空")


if __name__ == "__main__":
    # 测试多智能体系统
    system = MultiAgentTrainingSystem()
    
    # 测试用户档案
    user_profile = {
        "name": "张三",
        "age": 28,
        "fitness_level": "中级",
        "goals": ["增肌", "提高耐力"],
        "training_history": "已训练6个月",
        "health_status": "健康，无运动损伤"
    }
    
    # 测试不同类型的请求
    test_requests = [
        "我想制定一个增肌训练计划",
        "深蹲的标准动作是什么？",
        "我感觉很疲劳，还能继续训练吗？",
        "如何预防跑步时的膝盖损伤？",
        "高强度训练有哪些安全注意事项？"
    ]
    
    for request in test_requests:
        print(f"\n{'='*80}")
        print(f"用户请求: {request}")
        print(f"{'='*80}")
        
        result = system.process_request(request, user_profile)
        
        print(f"\n工作流: {' -> '.join(result['workflow'])}")
        print(f"\n{result['response']}")
    
    # 查看记忆摘要
    print(f"\n{'='*80}")
    print("记忆摘要:")
    print(system.get_memory_summary())
