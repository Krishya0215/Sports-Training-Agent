"""
多智能体协同训练支持系统
模拟真实运动指导团队的协作模式
"""
from typing import TypedDict, List, Annotated, Dict, Any
from operator import add
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from backend.model.factory import chat_model, build_chat_model
from backend.rag.vector_store import VectorStoreService
from backend.rag.advanced_retriever import AdvancedRetriever
from backend.memory.memory_manager import MemoryManager
from backend.utils.logger_handler import logger
import json


class TrainingState(TypedDict, total=False):
    """训练系统状态定义"""
    user_input: str
    user_profile: dict
    retrieved_docs: List
    routing: Dict[str, Any]
    selected_agents: List[str]
    execution_plan: List[List[str]]
    agent_results: Dict[str, str]
    final_response: str
    structured_response: Dict[str, Any]
    workflow_history: Annotated[List[str], add]
    _stream_callback: Any


class CoachAgent:
    """教练智能体基类"""
    
    def __init__(
        self,
        name: str,
        role: str,
        prompt_template: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.4,
        request_timeout: int = 45,
        max_retries: int = 1
    ):
        self.name = name
        self.role = role
        self.model = build_chat_model(
            temperature=temperature,
            max_tokens=max_tokens,
            request_timeout=request_timeout,
            max_retries=max_retries
        ) or chat_model
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
        self._init_synthesizer()
        
        # 构建协作状态图
        self.graph = self._build_graph()
        
        logger.info("多智能体训练支持系统初始化完成")
    
    def _init_coaches(self):
        """初始化各个专业教练智能体"""

        planning_coach = CoachAgent(
            name="训练规划教练",
            role="制定科学训练计划并动态优化",
            max_tokens=1400,
            temperature=0.35,
            request_timeout=40,
            max_retries=1,
            prompt_template="""你是一位专业的训练规划教练。根据用户的目标、能力和历史数据，制定科学的训练计划。

用户输入: {user_input}
用户档案: {user_profile}
参考知识: {retrieved_docs}

如果用户是在生成完整训练计划：
1. 请直接输出一份结构完整的 Markdown 训练计划草案。
2. 草案要包含标题、计划概述、按周安排、按训练日安排。
3. 每个训练日至少包含训练主题、建议时长、训练重点、恢复建议。
4. 在用户还没有明确选定每周具体训练日之前，不要擅自写“周一训练日”“周四训练日”等具体周几，只使用“训练日1”“训练日2”这类编号。
5. 训练日标题里也不要附带括号或连字符形式的星期信息，例如禁止输出“训练日1（周一）”“训练日2(周四)”或“训练日1-周一”。
6. 先保证结构完整和可执行，不必写额外解释。

如果不是生成完整训练计划：
请给出简洁清晰的训练规划建议。

训练计划:"""
        )

        technique_coach = CoachAgent(
            name="技术指导教练",
            role="提供动作指导和姿势分析",
            max_tokens=420,
            temperature=0.2,
            request_timeout=25,
            max_retries=1,
            prompt_template="""你是一位专业的技术指导教练。为用户提供规范的动作指导和详细的姿势分析。

用户输入: {user_input}
用户档案: {user_profile}
参考知识: {retrieved_docs}
上下文: {context}

请只输出精简的技术修正建议，不要重复完整训练计划。
优先给出：
1. 关键动作执行提醒
2. 最容易出错的地方
3. 需要加入最终计划的技术提示
总长度控制在 4 条以内。

技术指导:"""
        )

        recovery_coach = CoachAgent(
            name="运动康复教练",
            role="提供损伤预防与恢复建议",
            max_tokens=420,
            temperature=0.2,
            request_timeout=25,
            max_retries=1,
            prompt_template="""你是一位专业的运动康复教练。针对运动损伤风险或已出现的伤痛，提供预防措施与恢复建议。

用户输入: {user_input}
用户档案: {user_profile}
参考知识: {retrieved_docs}
上下文: {context}

请只输出精简的康复和风险规避建议，不要重复完整训练计划。
优先给出：
1. 需要规避的高风险动作
2. 可替代动作或调整方式
3. 恢复和注意事项
总长度控制在 4 条以内。

康复建议:"""
        )

        self.coaches = {
            "planning": planning_coach,
            "technique": technique_coach,
            "recovery": recovery_coach
        }

        self.coach_catalog = {
            "planning": {
                "name": "训练规划教练",
                "icon": "📋",
                "role": "planning",
                "description": "根据用户目标、能力和历史数据制定科学训练计划并动态优化",
                "depends_on": []
            },
            "technique": {
                "name": "技术指导教练",
                "icon": "🎯",
                "role": "technique",
                "description": "提供规范的动作指导和详细的姿势分析",
                "depends_on": []
            },
            "recovery": {
                "name": "运动康复教练",
                "icon": "🏥",
                "role": "recovery",
                "description": "针对运动损伤风险或已出现的伤痛提供预防措施与恢复建议",
                "depends_on": ["planning", "technique"]
            }
        }

    def _init_synthesizer(self):
        """初始化综合输出器"""
        self.synthesis_prompt = PromptTemplate.from_template(
            """你是一位资深 AI 运动教练负责人，需要把多个专项教练的建议整合成一份最终答复。

用户原始问题:
{user_input}

用户档案:
{user_profile}

专项教练建议:
{agent_outputs}

请严格遵循以下要求：
1. 最终只输出一份综合后的答案，不要分成“训练规划教练/技术指导教练/运动康复教练”多个小节。
2. 如果用户是在生成训练计划，必须输出为清晰、标准的 Markdown，并尽量遵循下面结构：
   # 计划标题
   ## 计划概述
   ## 第1周
   ### 训练日1
   - 训练主题：
   - 建议时长：
   - 训练重点：
   - 恢复建议：
   - 替代方案：如无伤病风险可不写
3. 训练计划应尽量细化到 4 周，并按周、按训练日安排内容。
4. 如用户有伤病或风险提示，必须把技术指导与康复建议融合进对应训练日，不要单独再列一个“Agent建议”区域。
5. 不要输出“以下是综合建议”“以下分别来自不同Agent”之类的说明。
6. 不要输出“计划标题：”这几个字，只保留真正的标题文本。
7. 不要使用 ---、*** 等分隔线，使用 Markdown 标题层级和自然分段。
8. 如果用户不是要生成完整训练计划，就输出一份整合后的简洁专业回答，同样不要按 Agent 分节。
9. 在用户尚未手动选择每周训练日之前，不要写具体星期几，只能写“训练日1 / 训练日2”这类编号。
10. 训练日标题禁止出现括号或连字符补充的星期信息，例如“训练日1（周一）”“训练日1-周一”都不允许。

        最终答案："""
        )
        synthesis_model = build_chat_model(
            temperature=0.3,
            max_tokens=1400,
            request_timeout=35,
            max_retries=1
        ) or chat_model
        self.synthesis_chain = self.synthesis_prompt | synthesis_model | StrOutputParser()

    def _build_graph(self) -> StateGraph:
        """构建多智能体协作状态图"""
        workflow = StateGraph(TrainingState)

        workflow.add_node("retrieve_knowledge", self._retrieve_node)
        workflow.add_node("build_execution_plan", self._build_execution_plan_node)
        workflow.add_node("execute_agents", self._execute_agents_node)
        workflow.add_node("synthesize_response", self._synthesize_node)
        workflow.add_node("update_memory", self._update_memory_node)

        workflow.set_entry_point("retrieve_knowledge")
        workflow.add_edge("retrieve_knowledge", "build_execution_plan")
        workflow.add_edge("build_execution_plan", "execute_agents")
        workflow.add_edge("execute_agents", "synthesize_response")
        workflow.add_edge("synthesize_response", "update_memory")
        workflow.add_edge("update_memory", END)

        return workflow.compile()

    def _retrieve_node(self, state: TrainingState) -> TrainingState:
        """检索相关知识"""
        user_input = state["user_input"]
        logger.info(f"检索知识: {user_input}")
        if self._should_skip_retrieval(state):
            state["retrieved_docs"] = []
            state["workflow_history"] = ["已跳过知识检索"]
            logger.info("当前请求已跳过知识检索")
            self._emit_progress(state, "已跳过知识检索，直接开始生成计划")
            return state

        self._emit_progress(state, "正在检索与你问题相关的训练知识")
        
        try:
            retrieved_docs = self.retriever.retrieve(user_input)
            state["retrieved_docs"] = retrieved_docs
            state["workflow_history"] = [f"检索到 {len(retrieved_docs)} 个相关文档"]
            logger.info(f"检索完成: {len(retrieved_docs)} 个文档")
            self._emit_progress(state, f"检索完成，找到 {len(retrieved_docs)} 条相关内容")
        except Exception as e:
            logger.error(f"检索失败: {e}")
            state["retrieved_docs"] = []
            state["workflow_history"] = ["检索失败"]
            self._emit_progress(state, "知识检索未命中，接下来将直接结合你的输入进行分析")
        
        return state

    def _build_execution_plan_node(self, state: TrainingState) -> TrainingState:
        """根据输入、画像和检索结果动态构建执行计划"""
        routing = self._analyze_request(state)
        selected_agents = self._select_agents(routing)
        execution_plan = self._build_execution_batches(selected_agents)

        state["routing"] = routing
        state["selected_agents"] = selected_agents
        state["execution_plan"] = execution_plan
        state["agent_results"] = {}
        state["workflow_history"] = state.get("workflow_history", []) + [
            f"调度信号: {', '.join(routing.get('signals', [])) or '常规问答'}",
            f"已选择教练: {', '.join(selected_agents)}",
            f"执行批次: {' -> '.join(['+'.join(batch) for batch in execution_plan])}"
        ]

        logger.info(f"调度完成: {selected_agents}")
        self._emit_progress(
            state,
            f"已安排 {len(selected_agents)} 位教练一起整理这份建议"
        )
        return state

    def _analyze_request(self, state: TrainingState) -> Dict[str, Any]:
        """提取路由信号"""
        user_input = state["user_input"].lower()
        profile = state.get("user_profile", {}) or {}
        signals = set()
        injury_text = json.dumps(profile, ensure_ascii=False)
        has_injury = any(keyword in injury_text for keyword in ["伤", "痛", "膝", "腰", "肩", "腕", "康复"])
        is_plan_request = any(keyword in user_input for keyword in [
            "训练计划", "1 个月训练计划", "计划概述", "训练日", "每周训练天数", "第1周", "第2周"
        ])

        keyword_map = {
            "planning": ["计划", "规划", "安排", "周期", "目标", "课表"],
            "technique": ["动作", "姿势", "技术", "要领", "标准", "纠正"],
            "recovery": ["恢复", "康复", "损伤", "伤痛", "拉伤", "酸痛", "不适", "风险", "危险", "注意", "防护", "禁忌"]
        }

        for signal, keywords in keyword_map.items():
            if any(keyword in user_input for keyword in keywords):
                signals.add(signal)

        if is_plan_request:
            signals.update(["planning", "technique"])
            if has_injury:
                signals.add("recovery")
        if has_injury:
            signals.add("recovery")

        if not signals:
            signals.add("planning")

        return {
            "signals": sorted(signals),
            "has_injury": has_injury,
            "is_plan_request": is_plan_request,
            "query": state["user_input"]
        }

    def _select_agents(self, routing: Dict[str, Any]) -> List[str]:
        """根据调度信号选择参与教练"""
        signals = set(routing.get("signals", []))
        selected = []

        if "planning" in signals:
            selected.append("planning")

        for agent_id in ["technique", "recovery"]:
            if agent_id in signals:
                selected.append(agent_id)

        if routing.get("has_injury"):
            for agent_id in ["recovery"]:
                if agent_id not in selected:
                    selected.append(agent_id)

        if not selected:
            selected = ["planning"]

        return selected

    def _build_execution_batches(self, selected_agents: List[str]) -> List[List[str]]:
        """构建按需执行批次"""
        if not selected_agents:
            return [["planning"]]

        batches: List[List[str]] = []
        remaining = list(selected_agents)

        if "planning" in remaining:
            batches.append(["planning"])
            remaining.remove("planning")

        if remaining:
            batches.append(remaining)

        return batches

    def _execute_agents_node(self, state: TrainingState) -> TrainingState:
        """执行调度后的教练批次"""
        agent_results = state.get("agent_results", {}) or {}

        for batch_index, batch in enumerate(state.get("execution_plan", []), start=1):
            state["workflow_history"] = state.get("workflow_history", []) + [
                f"开始执行批次 {batch_index}: {', '.join(batch)}"
            ]
            self._emit_progress(
                state,
                f"正在进行第 {batch_index} 轮分析：{self._format_batch_names(batch)}"
            )

            can_run_parallel = batch_index > 1 and len(batch) > 1

            if can_run_parallel:
                for agent_id in batch:
                    self._emit_progress(state, f"{self.coach_catalog[agent_id]['name']}正在整理建议")

                with ThreadPoolExecutor(max_workers=len(batch)) as executor:
                    future_map = {
                        executor.submit(
                            self.coaches[agent_id].process,
                            state,
                            self._build_agent_context(agent_id, agent_results)
                        ): agent_id
                        for agent_id in batch
                    }

                    for future in as_completed(future_map):
                        agent_id = future_map[future]
                        result = future.result()
                        self._store_agent_result(state, agent_results, agent_id, result)
            else:
                for agent_id in batch:
                    coach = self.coaches[agent_id]
                    self._emit_progress(state, f"{self.coach_catalog[agent_id]['name']}正在整理建议")
                    context = self._build_agent_context(agent_id, agent_results)
                    result = coach.process(state, context)
                    self._store_agent_result(state, agent_results, agent_id, result)

        state["agent_results"] = agent_results
        return state

    def _build_agent_context(self, agent_id: str, agent_results: Dict[str, str]) -> str:
        """构造 agent 上下文"""
        if agent_id == "planning":
            return ""
        if agent_id == "technique":
            return f"训练规划结果:\n{agent_results.get('planning', '')}"
        if agent_id == "recovery":
            return f"训练规划结果:\n{agent_results.get('planning', '')}"
        return ""

    def _synthesize_node(self, state: TrainingState) -> TrainingState:
        """综合各教练的建议，生成最终响应（结构化格式）"""
        logger.info("综合各教练建议")
        self._emit_progress(state, "正在整合各位教练的建议，生成最终计划")

        def summarize_agent_output(text: str) -> str:
            first_line = text.split("\n")[0].strip()
            if "。" in first_line:
                return first_line.split("。")[0] + "。"
            if len(first_line) > 80:
                return first_line[:80] + "..."
            return first_line

        coaches = []
        agent_output_parts = []
        for agent_id in state.get("selected_agents", []):
            content = state.get("agent_results", {}).get(agent_id, "")
            if not content:
                continue

            coach_info = self.coach_catalog[agent_id]
            coach_payload = {
                "name": coach_info["name"],
                "icon": coach_info["icon"],
                "role": coach_info["role"],
                "content": summarize_agent_output(content)
            }
            coaches.append(coach_payload)
            agent_output_parts.append(f"[{coach_info['name']}]\n{content}")

        synthesized_answer = self.synthesis_chain.invoke({
            "user_input": state["user_input"],
            "user_profile": json.dumps(state.get("user_profile", {}), ensure_ascii=False),
            "agent_outputs": "\n\n".join(agent_output_parts) or "无专项建议"
        }).strip()

        if not synthesized_answer:
            synthesized_answer = state.get("agent_results", {}).get("planning", "")

        structured_response = {
            "summary": synthesized_answer[:240],
            "coaches": coaches,
            "scheduler": {
                "signals": state.get("routing", {}).get("signals", []),
                "selected_agents": state.get("selected_agents", []),
                "execution_plan": state.get("execution_plan", [])
            }
        }

        state["final_response"] = synthesized_answer
        state["structured_response"] = structured_response
        state["workflow_history"] = state.get("workflow_history", []) + ["综合响应生成完成"]

        logger.info("综合响应生成完成")
        self._emit_progress(state, "综合计划已生成完成")
        return state

    def _update_memory_node(self, state: TrainingState) -> TrainingState:
        """更新记忆系统"""
        try:
            # 提取图像描述信息
            image_descriptions = []
            for doc in state.get("retrieved_docs", []):
                if doc.metadata.get("content_type") == "image_description":
                    image_descriptions.append({
                        "image_id": doc.metadata.get("image_filename", "unknown"),
                        "description": doc.page_content,
                        "metadata": doc.metadata
                    })
            
            self.memory_manager.record_interaction(
                question=state["user_input"],
                answer=state["final_response"],
                retrieved_docs=[doc.metadata.get("source", "未知") for doc in state.get("retrieved_docs", [])],
                metadata={
                    "workflow": state.get("workflow_history", []),
                    "coaches_involved": state.get("selected_agents", []),
                    "image_descriptions": image_descriptions
                }
            )
            logger.info("记忆更新完成")
            self._emit_progress(state, "已保存本次分析记录")
        except Exception as e:
            logger.error(f"记忆更新失败: {e}")
        
        return state

    def _emit_progress(self, state: TrainingState, message: str):
        """向流式接口发送过程进度"""
        if state.get("_stream_callback"):
            state["_stream_callback"]({
                "type": "progress_log",
                "message": message
            })

    def _store_agent_result(self, state: TrainingState, agent_results: Dict[str, str], agent_id: str, result: str):
        """统一记录 agent 输出，便于串行和并行流程复用"""
        agent_results[agent_id] = result

        coach_payload = {
            "name": self.coach_catalog[agent_id]["name"],
            "icon": self.coach_catalog[agent_id]["icon"],
            "role": self.coach_catalog[agent_id]["role"],
            "content": result
        }

        state["workflow_history"] = state.get("workflow_history", []) + [
            f"{self.coach_catalog[agent_id]['name']}完成"
        ]
        self._emit_progress(state, f"{self.coach_catalog[agent_id]['name']}已完成")

        if state.get("_stream_callback"):
            state["_stream_callback"]({
                "type": "coach_result",
                "coach": coach_payload
            })

    def _should_skip_retrieval(self, state: TrainingState) -> bool:
        """训练计划问卷请求直接跳过知识检索，减少等待时间"""
        profile = state.get("user_profile", {}) or {}
        if profile.get("source") == "training_questionnaire":
            return True

        user_input = state.get("user_input", "")
        return any(keyword in user_input for keyword in ["生成一个 1 个月训练计划", "生成训练计划"])

    def _format_batch_names(self, batch: List[str]) -> str:
        return "、".join(
            self.coach_catalog.get(agent_id, {}).get("name", agent_id)
            for agent_id in batch
        )
    
    def process_request(self, user_input: str, user_profile: dict = None, stream_callback=None) -> dict:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入
            user_profile: 用户档案（目标、能力、历史数据等）
            stream_callback: 流式回调函数，用于实时返回每个教练的结果
            
        Returns:
            包含最终响应和工作流历史的字典
        """
        # 初始化状态
        initial_state = {
            "user_input": user_input,
            "user_profile": user_profile or {},
            "routing": {},
            "selected_agents": [],
            "execution_plan": [],
            "agent_results": {},
            "final_response": "",
            "retrieved_docs": [],
            "workflow_history": [],
            "_stream_callback": stream_callback  # 存储回调函数
        }
        
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"多智能体处理尝试 {attempt + 1}/{max_retries}")
                
                # 执行状态图
                final_state = self.graph.invoke(initial_state)
                
                # 构建思考过程
                thinking_steps = []
                thinking_steps.append(f"📖 **接收请求**: {initial_state['user_input'][:100]}")
                if final_state.get("workflow_history"):
                    for step in final_state.get("workflow_history", [])[:3]:
                        thinking_steps.append(f"🤖 **{step}**")
                thinking_steps.append(f"💡 **综合分析**: 整合多个教练的建议")
                
                logger.info(f"多智能体处理成功 (第 {attempt + 1} 次尝试)")
                
                return {
                    "thinking": "\n".join(thinking_steps),
                    "response": final_state["final_response"],
                    "structured_response": final_state.get("structured_response", {}),
                    "workflow": final_state.get("workflow_history", []),
                    "coaches_involved": final_state.get("selected_agents", [])
                }
                
            except Exception as e:
                last_error = e
                error_str = str(e)
                logger.warning(f"多智能体处理失败 (第 {attempt + 1}/{max_retries}): {error_str[:100]}")
                
                # 检查是否是网络错误
                is_network_error = any(keyword in error_str.lower() 
                                      for keyword in ['ssl', 'timeout', 'connection', 'max retries'])
                
                if is_network_error and attempt < max_retries - 1:
                    import time
                    wait_time = 2 ** attempt
                    logger.info(f"网络错误，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                    continue
                elif attempt < max_retries - 1:
                    logger.info("正在重试...")
                    continue
        
        # 所有重试都失败
        logger.error(f"多智能体处理失败 (经过 {max_retries} 次尝试): {str(last_error)[:200]}")
        error_msg = str(last_error)
        
        if 'ssl' in error_msg.lower():
            thinking = "❌ **SSL连接错误**\n\n与AI服务的连接出现问题。"
            response = "网络连接出现问题，请检查您的网络连接并稍后重试。"
        elif 'timeout' in error_msg.lower():
            thinking = "❌ **请求超时**\n\nAI服务响应较慢。"
            response = "请求处理超时，请稍后重试。"
        else:
            thinking = f"❌ **处理出错**: {error_msg[:100]}"
            response = f"处理您的请求时出现错误，请稍后重试。\n\n详情：{error_msg[:150]}"
        
        return {
            "thinking": thinking,
            "response": response,
            "workflow": [f"处理失败: {error_msg[:50]}"],
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
