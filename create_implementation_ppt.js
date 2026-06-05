const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = '刘冰彦';
pres.title = '系统实现';

// Color palette
const colors = {
  navy: "0F172A",
  darkBlue: "1E3A8A",
  blue: "2563EB",
  skyBlue: "3B82F6",
  lightBlue: "60A5FA",
  paleBlue: "DBEAFE",
  iceBlue: "EFF6FF",
  white: "FFFFFF",
  slate: "475569",
  darkSlate: "1E293B",
  gray: "94A3B8",
  success: "10B981",
  accent: "F59E0B"
};

const cardShadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 });

// ============ Slide 1: Title ============
let slide1 = pres.addSlide();
slide1.background = { color: colors.navy };

slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.blue }
});
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.545, w: 10, h: 0.08, fill: { color: colors.blue }
});

slide1.addText("第四章", {
  x: 0.5, y: 1.5, w: 9, h: 0.5,
  fontSize: 16, fontFace: "Arial", color: colors.lightBlue, align: "center"
});

slide1.addText("系统实现", {
  x: 0.5, y: 2.0, w: 9, h: 1.2,
  fontSize: 44, fontFace: "Arial", color: colors.white, bold: true, align: "center"
});

slide1.addText("基于多智能体与检索增强生成的智能运动训练系统", {
  x: 0.5, y: 3.3, w: 9, h: 0.5,
  fontSize: 14, fontFace: "Arial", color: colors.gray, align: "center"
});

slide1.addText("刘冰彦 | 22301126", {
  x: 0.5, y: 4.5, w: 9, h: 0.4,
  fontSize: 12, fontFace: "Arial", color: colors.gray, align: "center"
});

// ============ Slide 2: Overview ============
let slide2 = pres.addSlide();
slide2.background = { color: colors.white };

slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide2.addText("04  系统实现概述", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const implOverview = [
  { num: "01", title: "开发环境", desc: "技术栈选型与开发配置" },
  { num: "02", title: "前端实现", desc: "Vue3五大功能页面" },
  { num: "03", title: "后端实现", desc: "FastAPI + 三大核心模块" },
  { num: "04", title: "模块集成", desc: "RAG + 记忆 + 多智能体" }
];

implOverview.forEach((item, idx) => {
  const yPos = 1.2 + idx * 1.05;

  slide2.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 0.9, fill: { color: colors.paleBlue }, shadow: cardShadow()
  });

  slide2.addShape(pres.shapes.OVAL, {
    x: 0.8, y: yPos + 0.2, w: 0.5, h: 0.5, fill: { color: colors.blue }
  });
  slide2.addText(item.num, {
    x: 0.8, y: yPos + 0.2, w: 0.5, h: 0.5,
    fontSize: 14, fontFace: "Arial", color: colors.white, bold: true, align: "center", valign: "middle"
  });

  slide2.addText(item.title, {
    x: 1.5, y: yPos + 0.15, w: 3, h: 0.35,
    fontSize: 16, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide2.addText(item.desc, {
    x: 1.5, y: yPos + 0.5, w: 7.5, h: 0.3,
    fontSize: 12, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 3: Tech Stack ============
let slide3 = pres.addSlide();
slide3.background = { color: colors.white };

slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide3.addText("04.1  开发环境与技术栈", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const techStack = [
  { category: "前端", tech: "Vue3 + Vite + Axios + Pinia", color: colors.blue },
  { category: "后端", tech: "FastAPI + LangGraph + SQLAlchemy", color: colors.skyBlue },
  { category: "数据库", tech: "SQLite + ChromaDB", color: colors.navy },
  { category: "AI模型", tech: "Claude API + Embedding Model", color: colors.success }
];

techStack.forEach((tech, idx) => {
  const xPos = 0.6 + idx * 2.35;

  slide3.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.15, w: 2.2, h: 2.0, fill: { color: tech.color }, shadow: cardShadow()
  });

  slide3.addText(tech.category, {
    x: xPos, y: 1.4, w: 2.2, h: 0.45,
    fontSize: 14, fontFace: "Arial", color: colors.white, bold: true, align: "center"
  });

  slide3.addText(tech.tech, {
    x: xPos + 0.1, y: 2.0, w: 2.0, h: 1.0,
    fontSize: 11, fontFace: "Arial", color: colors.white, align: "center"
  });
});

// Development tools
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 3.5, w: 8.8, h: 1.7, fill: { color: colors.iceBlue }
});

slide3.addText("开发工具与环境", {
  x: 0.8, y: 3.7, w: 8.4, h: 0.4,
  fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
});

slide3.addText([
  { text: "Python 3.11 + Node.js 18+", options: { bullet: true, breakLine: true } },
  { text: "Git版本控制 + PyCharm/VS Code", options: { bullet: true, breakLine: true } },
  { text: "ChromaDB向量数据库 + SQLite关系数据库", options: { bullet: true } }
], {
  x: 0.8, y: 4.15, w: 8.4, h: 0.9,
  fontSize: 12, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 6, bullet: { color: colors.blue }
});

// ============ Slide 4: Frontend Pages ============
let slide4 = pres.addSlide();
slide4.background = { color: colors.white };

slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide4.addText("04.2  前端展示层实现", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide4.addText("Vue3 实现的五大功能页面", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray
});

const pages = [
  { name: "用户信息页面", desc: "个人资料查看与编辑", icon: "1" },
  { name: "AI教练问答页面", desc: "智能问答与引用展示", icon: "2" },
  { name: "训练计划页面", desc: "计划生成、查看、修改", icon: "3" },
  { name: "健康记录页面", desc: "训练、饮食、体重记录", icon: "4" },
  { name: "知识库管理页面", desc: "文档上传与维护", icon: "5" }
];

pages.forEach((page, idx) => {
  const yPos = 1.4 + idx * 0.78;

  slide4.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 0.68, fill: { color: colors.white }, shadow: cardShadow()
  });

  slide4.addShape(pres.shapes.OVAL, {
    x: 0.75, y: yPos + 0.14, w: 0.4, h: 0.4, fill: { color: colors.blue }
  });
  slide4.addText(page.icon, {
    x: 0.75, y: yPos + 0.14, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.white, bold: true, align: "center", valign: "middle"
  });

  slide4.addText(page.name, {
    x: 1.3, y: yPos + 0.1, w: 3.5, h: 0.48,
    fontSize: 13, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide4.addText(page.desc, {
    x: 4.8, y: yPos + 0.1, w: 4.3, h: 0.48,
    fontSize: 12, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 5: Frontend Features ============
let slide5 = pres.addSlide();
slide5.background = { color: colors.white };

slide5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide5.addText("04.2  前端核心功能特性", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const frontendFeatures = [
  { title: "用户信息管理", features: ["注册/登录", "资料编辑", "头像上传"] },
  { title: "AI教练问答", features: ["流式响应", "引用展示", "单/多智能体切换"] },
  { title: "训练计划", features: ["计划生成", "周期安排", "进度追踪"] },
  { title: "健康记录", features: ["训练记录", "饮食记录", "体重追踪"] }
];

frontendFeatures.forEach((feat, idx) => {
  const xPos = 0.6 + idx * 2.35;

  slide5.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.15, w: 2.2, h: 3.0, fill: { color: colors.white }, shadow: cardShadow()
  });

  slide5.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.15, w: 2.2, h: 0.06, fill: { color: colors.blue }
  });

  slide5.addText(feat.title, {
    x: xPos + 0.1, y: 1.35, w: 2.0, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.navy, bold: true, align: "center"
  });

  feat.features.forEach((f, i) => {
    slide5.addText("• " + f, {
      x: xPos + 0.1, y: 1.85 + i * 0.5, w: 2.0, h: 0.4,
      fontSize: 10, fontFace: "Arial", color: colors.slate
    });
  });
});

// ============ Slide 6: Backend Architecture ============
let slide6 = pres.addSlide();
slide6.background = { color: colors.white };

slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide6.addText("04.3  后端服务层实现", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide6.addText("FastAPI + LangGraph 技术架构", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray
});

const backendModules = [
  { title: "FastAPI框架", desc: "RESTful API\n路由管理\n中间件集成", color: colors.blue },
  { title: "RAG检索模块", desc: "HyDE + MQE\n记忆感知检索\n引用约束生成", color: colors.skyBlue },
  { title: "记忆管理模块", desc: "三层记忆体系\n记忆巩固服务\n遗忘机制", color: colors.navy },
  { title: "多智能体模块", desc: "意图识别\n角色智能体\n结果整合", color: colors.success }
];

backendModules.forEach((mod, idx) => {
  const xPos = 0.6 + idx * 2.35;

  slide6.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.2, h: 3.0, fill: { color: mod.color }, shadow: cardShadow()
  });

  slide6.addText(mod.title, {
    x: xPos + 0.1, y: 1.6, w: 2.0, h: 0.45,
    fontSize: 13, fontFace: "Arial", color: colors.white, bold: true, align: "center"
  });

  slide6.addText(mod.desc, {
    x: xPos + 0.1, y: 2.15, w: 2.0, h: 2.0,
    fontSize: 10, fontFace: "Arial", color: colors.white, align: "center"
  });
});

// ============ Slide 7: RAG Implementation ============
let slide7 = pres.addSlide();
slide7.background = { color: colors.white };

slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide7.addText("04.3.2  RAG检索模块实现", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide7.addText("ST-RAG：语义增强RAG策略实现", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray
});

const ragImpl = [
  { step: "HyDE", desc: "生成假设性专业回答，映射到专业知识空间" },
  { step: "MQE", desc: "多查询扩展，将复杂问题拆解为语义子查询" },
  { step: "记忆感知", desc: "融合用户长期状态，实现个性化检索" },
  { step: "RRF融合", desc: "Reciprocal Rank Fusion多查询结果融合" },
  { step: "引用约束", desc: "强制引用来源，后校验降低幻觉" }
];

ragImpl.forEach((item, idx) => {
  const yPos = 1.4 + idx * 0.78;

  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 0.68, fill: { color: colors.paleBlue }
  });

  slide7.addText(item.step, {
    x: 0.8, y: yPos + 0.14, w: 1.5, h: 0.4,
    fontSize: 13, fontFace: "Arial", color: colors.blue, bold: true
  });

  slide7.addText(item.desc, {
    x: 2.5, y: yPos + 0.14, w: 6.5, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.slate
  });
});

// Key features
slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 5.1, w: 8.8, h: 0.4, fill: { color: colors.navy }
});

slide7.addText("知识库：运动训练领域专业文档 | 向量数据库：ChromaDB + HNSW索引", {
  x: 0.6, y: 5.1, w: 8.8, h: 0.4,
  fontSize: 11, fontFace: "Arial", color: colors.white, align: "center", valign: "middle"
});

// ============ Slide 8: Memory Implementation ============
let slide8 = pres.addSlide();
slide8.background = { color: colors.white };

slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide8.addText("04.3.3  长期记忆模块实现", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide8.addText("三层记忆体系实现", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray
});

const memoryImpl = [
  { title: "工作记忆", func: "当前会话上下文", update: "每次交互", storage: "memory_working_messages" },
  { title: "情景记忆", func: "历史训练事件", update: "每次交互", storage: "memory_episodic_events" },
  { title: "语义记忆", func: "长期用户特征", update: "周期更新", storage: "memory_semantic_facts" }
];

memoryImpl.forEach((mem, idx) => {
  const yPos = 1.4 + idx * 1.15;

  slide8.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 1.0, fill: { color: colors.white }, shadow: cardShadow()
  });

  slide8.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 0.1, h: 1.0, fill: { color: colors.blue }
  });

  slide8.addText(mem.title, {
    x: 0.85, y: yPos + 0.1, w: 1.8, h: 0.35,
    fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide8.addText("功能: " + mem.func, {
    x: 0.85, y: yPos + 0.45, w: 3, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: colors.slate
  });

  slide8.addText("更新: " + mem.update, {
    x: 3.5, y: yPos + 0.45, w: 2.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: colors.slate
  });

  slide8.addText("存储: " + mem.storage, {
    x: 6, y: yPos + 0.45, w: 3.2, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: colors.gray
  });
});

// Key features
slide8.addText("核心功能：记忆感知检索 | 记忆巩固服务 | 遗忘机制", {
  x: 0.6, y: 4.85, w: 8.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: colors.blue, align: "center"
});

// ============ Slide 9: Multi-agent Implementation ============
let slide9 = pres.addSlide();
slide9.background = { color: colors.white };

slide9.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide9.addText("04.3.4  多智能体模块实现", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide9.addText("基于LangGraph的多智能体协同", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray
});

const agents = [
  { title: "训练规划教练", keywords: "计划、规划、周期、目标", role: "制定科学训练计划" },
  { title: "技术指导教练", keywords: "动作、姿势、技术、要领", role: "提供动作指导与纠正" },
  { title: "运动康复教练", keywords: "恢复、康复、损伤、预防", role: "损伤风险评估与恢复建议" }
];

agents.forEach((agent, idx) => {
  const yPos = 1.4 + idx * 1.15;

  slide9.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 1.0, fill: { color: colors.white }, shadow: cardShadow()
  });

  slide9.addShape(pres.shapes.OVAL, {
    x: 0.8, y: yPos + 0.25, w: 0.5, h: 0.5, fill: { color: colors.blue }
  });
  slide9.addText(`${idx + 1}`, {
    x: 0.8, y: yPos + 0.25, w: 0.5, h: 0.5,
    fontSize: 14, fontFace: "Arial", color: colors.white, bold: true, align: "center", valign: "middle"
  });

  slide9.addText(agent.title, {
    x: 1.5, y: yPos + 0.1, w: 3, h: 0.35,
    fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide9.addText("关键词: " + agent.keywords, {
    x: 1.5, y: yPos + 0.45, w: 4, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: colors.gray
  });

  slide9.addText(agent.role, {
    x: 5.5, y: yPos + 0.25, w: 3.5, h: 0.5,
    fontSize: 11, fontFace: "Arial", color: colors.slate
  });
});

// Workflow
slide9.addText("工作流程：意图识别 → 任务分发 → 协同执行 → 结果整合 → 异常兜底", {
  x: 0.6, y: 4.85, w: 8.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: colors.blue, align: "center"
});

// ============ Slide 10: Data Storage ============
let slide10 = pres.addSlide();
slide10.background = { color: colors.white };

slide10.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide10.addText("04.3  数据存储层设计", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

// SQLite
slide10.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.1, w: 4.3, h: 4.1, fill: { color: colors.white }, shadow: cardShadow()
});
slide10.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.1, w: 4.3, h: 0.08, fill: { color: colors.blue }
});

slide10.addText("SQLite", {
  x: 0.8, y: 1.35, w: 3.9, h: 0.5,
  fontSize: 20, fontFace: "Arial", color: colors.navy, bold: true
});
slide10.addText("关系数据库", {
  x: 0.8, y: 1.8, w: 3.9, h: 0.3,
  fontSize: 11, fontFace: "Arial", color: colors.gray
});

slide10.addText([
  { text: "用户信息", options: { bullet: true, breakLine: true } },
  { text: "训练计划", options: { bullet: true, breakLine: true } },
  { text: "健康记录", options: { bullet: true, breakLine: true } },
  { text: "对话历史", options: { bullet: true, breakLine: true } },
  { text: "记忆数据", options: { bullet: true } }
], {
  x: 0.8, y: 2.3, w: 3.9, h: 2.5,
  fontSize: 12, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 8, bullet: { color: colors.blue }
});

// ChromaDB
slide10.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.1, w: 4.3, h: 4.1, fill: { color: colors.white }, shadow: cardShadow()
});
slide10.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.1, w: 4.3, h: 0.08, fill: { color: colors.skyBlue }
});

slide10.addText("ChromaDB", {
  x: 5.3, y: 1.35, w: 3.9, h: 0.5,
  fontSize: 20, fontFace: "Arial", color: colors.navy, bold: true
});
slide10.addText("向量数据库", {
  x: 5.3, y: 1.8, w: 3.9, h: 0.3,
  fontSize: 11, fontFace: "Arial", color: colors.gray
});

slide10.addText([
  { text: "运动训练知识库", options: { bullet: true, breakLine: true } },
  { text: "文档向量存储", options: { bullet: true, breakLine: true } },
  { text: "语义相似度检索", options: { bullet: true, breakLine: true } },
  { text: "HNSW索引优化", options: { bullet: true, breakLine: true } },
  { text: "元数据过滤", options: { bullet: true } }
], {
  x: 5.3, y: 2.3, w: 3.9, h: 2.5,
  fontSize: 12, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 8, bullet: { color: colors.skyBlue }
});

// ============ Slide 11: Summary ============
let slide11 = pres.addSlide();
slide11.background = { color: colors.white };

slide11.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide11.addText("04.4  本章小结", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const summaryItems = [
  { title: "前端实现", result: "Vue3五大功能页面", detail: "用户信息/AI问答/训练计划/健康记录/知识库管理" },
  { title: "后端实现", result: "三大核心模块", detail: "RAG检索/三层记忆/多智能体协同" },
  { title: "数据存储", result: "双库架构", detail: "SQLite + ChromaDB双库协同" }
];

summaryItems.forEach((item, idx) => {
  const yPos = 1.2 + idx * 1.35;

  slide11.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 1.15, fill: { color: colors.white }, shadow: cardShadow()
  });

  slide11.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 0.1, h: 1.15, fill: { color: colors.success }
  });

  slide11.addText(item.title, {
    x: 0.9, y: yPos + 0.15, w: 2, h: 0.4,
    fontSize: 16, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide11.addText(item.result, {
    x: 2.9, y: yPos + 0.15, w: 3, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: colors.success, bold: true
  });

  slide11.addText(item.detail, {
    x: 0.9, y: yPos + 0.6, w: 8.2, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.slate
  });
});

// Key achievement
slide11.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.4, w: 8.8, h: 0.9, fill: { color: colors.navy }
});

slide11.addText("完成系统全流程工程实现，为第五章测试验证奠定基础", {
  x: 0.6, y: 4.6, w: 8.8, h: 0.5,
  fontSize: 14, fontFace: "Arial", color: colors.white, align: "center", bold: true
});

// Save
pres.writeFile({ fileName: "/Users/liubingyan/Sports-Training-Agent/docs/系统实现PPT.pptx" })
  .then(() => console.log("Implementation PPT created successfully!"))
  .catch(err => console.error("Error:", err));
