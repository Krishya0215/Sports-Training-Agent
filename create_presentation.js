const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = '刘冰彦';
pres.title = '基于多智能体与检索增强生成的智能运动训练系统';

// Sophisticated blue-white minimalist palette
const colors = {
  navy: "0F172A",           // Deep navy
  darkBlue: "1E3A8A",       // Primary dark blue
  blue: "2563EB",           // Primary blue
  skyBlue: "3B82F6",        // Secondary blue
  lightBlue: "60A5FA",      // Accent blue
  paleBlue: "DBEAFE",       // Light background
  iceBlue: "EFF6FF",        // Very light background
  white: "FFFFFF",
  slate: "475569",          // Body text
  darkSlate: "1E293B",      // Headings
  gray: "94A3B8",           // Muted text
  success: "10B981",        // Green for metrics
  accent: "F59E0B"          // Amber accent
};

// Helper functions
const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.12 });
const cardShadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 });

// ============ Slide 1: Title Slide ============
let slide1 = pres.addSlide();
slide1.background = { color: colors.navy };

// Gradient-like decorative elements
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.blue }
});
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.545, w: 10, h: 0.08, fill: { color: colors.blue }
});

// Geometric accent shapes
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 7.5, y: 0, w: 2.5, h: 5.625, fill: { color: colors.darkBlue, transparency: 50 }
});
slide1.addShape(pres.shapes.OVAL, {
  x: -1.5, y: 3.5, w: 3, h: 3, fill: { color: colors.blue, transparency: 85 }
});

// Main title
slide1.addText("基于多智能体与检索增强生成的\n智能运动训练系统", {
  x: 0.5, y: 1.4, w: 9, h: 1.6,
  fontSize: 38, fontFace: "Arial", color: colors.white, bold: true,
  align: "center", valign: "middle", lineSpacing: 44
});

// English subtitle
slide1.addText("Intelligent Sports Training System Based on Multi-Agent and RAG", {
  x: 0.5, y: 3.1, w: 9, h: 0.45,
  fontSize: 14, fontFace: "Arial", color: colors.lightBlue, align: "center"
});

// Divider line
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 3.5, y: 3.7, w: 3, h: 0.02, fill: { color: colors.lightBlue }
});

// Author info block
slide1.addText("本科毕业论文（设计）", {
  x: 0.5, y: 3.95, w: 9, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray, align: "center"
});

slide1.addText([
  { text: "学院：软件学院    专业：软件工程\n", options: { breakLine: true } },
  { text: "学生姓名：刘冰彦    学号：22301126\n", options: { breakLine: true } },
  { text: "指导教师：李令昆    北京交通大学" }
], {
  x: 0.5, y: 4.4, w: 9, h: 0.9,
  fontSize: 11, fontFace: "Arial", color: colors.gray, align: "center", lineSpacing: 22
});

// ============ Slide 2: Outline ============
let slide2 = pres.addSlide();
slide2.background = { color: colors.iceBlue };

slide2.addText("目录", {
  x: 0.6, y: 0.4, w: 8.8, h: 0.7,
  fontSize: 36, fontFace: "Arial", color: colors.navy, bold: true
});

slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.05, w: 1.0, h: 0.05, fill: { color: colors.blue }
});

const tocItems = [
  { num: "01", title: "研究背景与意义" },
  { num: "02", title: "核心问题与技术方案" },
  { num: "03", title: "系统总体设计" },
  { num: "04", title: "系统实现" },
  { num: "05", title: "系统测试" },
  { num: "06", title: "结论与展望" }
];

tocItems.forEach((item, idx) => {
  const yPos = 1.4 + idx * 0.65;

  // Number circle
  slide2.addShape(pres.shapes.OVAL, {
    x: 0.6, y: yPos, w: 0.5, h: 0.5, fill: { color: colors.blue }
  });
  slide2.addText(item.num, {
    x: 0.6, y: yPos, w: 0.5, h: 0.5,
    fontSize: 12, fontFace: "Arial", color: colors.white, bold: true, align: "center", valign: "middle"
  });

  // Title
  slide2.addText(item.title, {
    x: 1.3, y: yPos + 0.05, w: 7.5, h: 0.45,
    fontSize: 18, fontFace: "Arial", color: colors.darkSlate
  });
});

// Right side decorative element
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 8.2, y: 1.4, w: 0.04, h: 3.8, fill: { color: colors.paleBlue }
});

// ============ Slide 3: Background ============
let slide3 = pres.addSlide();
slide3.background = { color: colors.white };

// Header bar
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide3.addText("01  研究背景", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

// Left content area
slide3.addText("研究背景与现状", {
  x: 0.6, y: 1.1, w: 5.5, h: 0.4,
  fontSize: 16, fontFace: "Arial", color: colors.blue, bold: true
});

slide3.addText([
  { text: "全民健身战略深入推进，科学化运动训练需求持续增长", options: { bullet: true, breakLine: true } },
  { text: "传统私人教练成本较高，难以满足大众化、持续性需求", options: { bullet: true, breakLine: true } },
  { text: "大语言模型与智能体技术取得显著进展，为智能化训练提供新路径", options: { bullet: true, breakLine: true } },
  { text: "现有智能训练系统仍存在三大共性不足", options: { bullet: true } }
], {
  x: 0.6, y: 1.55, w: 5.2, h: 1.8,
  fontSize: 13, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 10, bullet: { color: colors.blue }
});

// Right highlight box
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 6.2, y: 1.1, w: 3.2, h: 3.9, fill: { color: colors.iceBlue }, shadow: cardShadow()
});

slide3.addText("核心挑战", {
  x: 6.4, y: 1.3, w: 2.8, h: 0.4,
  fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
});

slide3.addText([
  { text: "训练建议缺乏科学依据", options: { bullet: true, breakLine: true } },
  { text: "缺乏长期用户记忆", options: { bullet: true, breakLine: true } },
  { text: "单一模型难以多角色", options: { bullet: true } }
], {
  x: 6.4, y: 1.8, w: 2.8, h: 1.5,
  fontSize: 12, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 8, bullet: { color: colors.blue }
});

// Bottom stats
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 3.7, w: 5.2, h: 1.5, fill: { color: colors.paleBlue }, shadow: cardShadow()
});
slide3.addText("三大共性不足", {
  x: 0.8, y: 3.85, w: 4.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.navy, bold: true
});
slide3.addText("知识支撑不足  |  状态记忆缺失  |  多角色协同困难", {
  x: 0.8, y: 4.3, w: 4.8, h: 0.7,
  fontSize: 11, fontFace: "Arial", color: colors.slate
});

// ============ Slide 4: Research Significance ============
let slide4 = pres.addSlide();
slide4.background = { color: colors.white };

slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide4.addText("01  研究意义", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

// Two large cards
// Left card - Theory
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.15, w: 4.3, h: 4.0, fill: { color: colors.white }, shadow: cardShadow()
});
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.15, w: 4.3, h: 0.08, fill: { color: colors.blue }
});

slide4.addText("理论意义", {
  x: 0.8, y: 1.4, w: 3.9, h: 0.45,
  fontSize: 18, fontFace: "Arial", color: colors.navy, bold: true
});

slide4.addText([
  { text: "探索多智能体系统在运动训练领域的应用模式", options: { bullet: true, breakLine: true } },
  { text: "结合MQE与HyDE提升RAG准确性和召回率", options: { bullet: true, breakLine: true } },
  { text: "构建三层记忆管理系统，模拟人类记忆机制", options: { bullet: true } }
], {
  x: 0.8, y: 2.0, w: 3.9, h: 2.8,
  fontSize: 13, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 14, bullet: { color: colors.blue }
});

// Right card - Application
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.15, w: 4.3, h: 4.0, fill: { color: colors.white }, shadow: cardShadow()
});
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.15, w: 4.3, h: 0.08, fill: { color: colors.success }
});

slide4.addText("实际应用价值", {
  x: 5.3, y: 1.4, w: 3.9, h: 0.45,
  fontSize: 18, fontFace: "Arial", color: colors.navy, bold: true
});

slide4.addText([
  { text: "为普通健身爱好者提供便捷、专业的训练指导", options: { bullet: true, breakLine: true } },
  { text: "作为体育院校和训练机构的辅助教学工具", options: { bullet: true, breakLine: true } },
  { text: "为运动康复领域提供损伤预防和恢复建议", options: { bullet: true } }
], {
  x: 5.3, y: 2.0, w: 3.9, h: 2.8,
  fontSize: 13, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 14, bullet: { color: colors.success }
});

// ============ Slide 5: Core Problems ============
let slide5 = pres.addSlide();
slide5.background = { color: colors.white };

slide5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide5.addText("02  核心问题分析", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const problems = [
  { num: "01", title: "知识失配", desc: "用户口语化提问与专业文献表述错位，单次检索覆盖不足", color: colors.blue },
  { num: "02", title: "状态失配", desc: "无状态模型无法跨会话保留用户状态，难以实现个性化", color: colors.skyBlue },
  { num: "03", title: "角色失配", desc: "单一模型难以同时胜任训练规划、技术指导与运动康复", color: colors.navy }
];

problems.forEach((prob, idx) => {
  const yPos = 1.15 + idx * 1.4;

  slide5.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 1.2, fill: { color: colors.white }, shadow: cardShadow()
  });

  // Left accent bar
  slide5.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 0.1, h: 1.2, fill: { color: prob.color }
  });

  // Number
  slide5.addText(prob.num, {
    x: 0.85, y: yPos + 0.15, w: 0.7, h: 0.9,
    fontSize: 32, fontFace: "Arial", color: prob.color, bold: true, valign: "middle"
  });

  // Title
  slide5.addText(prob.title, {
    x: 1.7, y: yPos + 0.2, w: 2.0, h: 0.5,
    fontSize: 20, fontFace: "Arial", color: colors.navy, bold: true
  });

  // Description
  slide5.addText(prob.desc, {
    x: 1.7, y: yPos + 0.65, w: 7.5, h: 0.4,
    fontSize: 13, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 6: Technical Solutions ============
let slide6 = pres.addSlide();
slide6.background = { color: colors.white };

slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide6.addText("02  技术方案", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide6.addText("针对三大核心问题的技术应对", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.gray
});

const solutions = [
  {
    title: "ST-RAG",
    subtitle: "语义增强RAG",
    desc: "结合MQE与HyDE\n解决知识失配",
    color: colors.blue,
    metric: "Precision@5: 0.84"
  },
  {
    title: "三层记忆",
    subtitle: "长期记忆体系",
    desc: "工作/情景/语义\n解决状态失配",
    color: colors.skyBlue,
    metric: "匹配准确率: 0.87"
  },
  {
    title: "多智能体",
    subtitle: "协同决策",
    desc: "规划/技术/康复\n解决角色失配",
    color: colors.navy,
    metric: "完成率: 0.93"
  }
];

solutions.forEach((sol, idx) => {
  const xPos = 0.6 + idx * 3.05;

  slide6.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.9, h: 3.7, fill: { color: sol.color }, shadow: cardShadow()
  });

  // Top accent
  slide6.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.9, h: 0.1, fill: { color: colors.white, transparency: 30 }
  });

  slide6.addText(sol.title, {
    x: xPos, y: 1.7, w: 2.9, h: 0.7,
    fontSize: 26, fontFace: "Arial", color: colors.white, bold: true, align: "center"
  });

  slide6.addText(sol.subtitle, {
    x: xPos, y: 2.35, w: 2.9, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.lightBlue, align: "center"
  });

  slide6.addText(sol.desc, {
    x: xPos + 0.15, y: 2.9, w: 2.6, h: 1.2,
    fontSize: 13, fontFace: "Arial", color: colors.white, align: "center"
  });

  // Metric box
  slide6.addShape(pres.shapes.RECTANGLE, {
    x: xPos + 0.3, y: 4.2, w: 2.3, h: 0.6, fill: { color: colors.white, transparency: 20 }
  });
  slide6.addText(sol.metric, {
    x: xPos + 0.3, y: 4.2, w: 2.3, h: 0.6,
    fontSize: 11, fontFace: "Arial", color: colors.white, align: "center", valign: "middle"
  });
});

// ============ Slide 7: System Architecture ============
let slide7 = pres.addSlide();
slide7.background = { color: colors.white };

slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide7.addText("03  系统总体架构", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

// Architecture layers - vertical stack
const layers = [
  { name: "前端展示层", tech: "Vue3 + Vite", color: colors.paleBlue },
  { name: "后端服务层", tech: "FastAPI + LangGraph", color: colors.lightBlue },
  { name: "数据存储层", tech: "SQLite + ChromaDB", color: colors.skyBlue },
  { name: "模型服务层", tech: "LLM + Embedding", color: colors.blue }
];

layers.forEach((layer, idx) => {
  const yPos = 1.15 + idx * 1.05;

  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 0.9, fill: { color: layer.color }, shadow: cardShadow()
  });

  slide7.addText(layer.name, {
    x: 0.8, y: yPos + 0.2, w: 2.2, h: 0.5,
    fontSize: 15, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide7.addText(layer.tech, {
    x: 3.2, y: yPos + 0.2, w: 5, h: 0.5,
    fontSize: 13, fontFace: "Arial", color: colors.slate
  });

  // Arrow
  if (idx < 3) {
    slide7.addText("↓", {
      x: 9.2, y: yPos + 0.25, w: 0.4, h: 0.4,
      fontSize: 16, fontFace: "Arial", color: colors.gray, align: "center"
    });
  }
});

// Bottom note
slide7.addText("前后端分离架构 · 分层解耦 · 模块化设计", {
  x: 0.6, y: 5.1, w: 8.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: colors.gray, align: "center"
});

// ============ Slide 8: ST-RAG Overview ============
let slide8 = pres.addSlide();
slide8.background = { color: colors.white };

slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide8.addText("03  ST-RAG：语义增强RAG策略", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide8.addText("解决「知识失配」问题", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.3,
  fontSize: 13, fontFace: "Arial", color: colors.blue
});

// Process flow - horizontal
const ragSteps = [
  { title: "查询增强", desc: "HyDE + MQE\n语义空间映射" },
  { title: "记忆感知", desc: "用户状态融合\n个性化检索" },
  { title: "结果融合", desc: "RRF排序\nCross-Encoder精排" },
  { title: "引用生成", desc: "约束引用\n后校验降幻觉" }
];

ragSteps.forEach((step, idx) => {
  const xPos = 0.5 + idx * 2.38;

  slide8.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.2, h: 2.8, fill: { color: colors.white }, shadow: cardShadow()
  });

  // Top accent
  slide8.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.2, h: 0.08, fill: { color: colors.blue }
  });

  // Step number
  slide8.addText(`0${idx + 1}`, {
    x: xPos, y: 1.55, w: 2.2, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: colors.blue, bold: true, align: "center"
  });

  slide8.addText(step.title, {
    x: xPos + 0.1, y: 2.0, w: 2.0, h: 0.45,
    fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true, align: "center"
  });

  slide8.addText(step.desc, {
    x: xPos + 0.1, y: 2.55, w: 2.0, h: 1.4,
    fontSize: 11, fontFace: "Arial", color: colors.slate, align: "center"
  });

  // Arrow between steps
  if (idx < 3) {
    slide8.addText("→", {
      x: xPos + 2.1, y: 2.5, w: 0.3, h: 0.4,
      fontSize: 18, fontFace: "Arial", color: colors.lightBlue, align: "center"
    });
  }
});

// Bottom metrics
slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.5, w: 8.8, h: 0.85, fill: { color: colors.paleBlue }
});

const ragMetrics = [
  { label: "Precision@5", value: "0.84" },
  { label: "Recall@5", value: "0.79" },
  { label: "Faithfulness", value: "0.88" },
  { label: "Relevancy", value: "0.91" }
];

ragMetrics.forEach((m, idx) => {
  const xPos = 1.0 + idx * 2.1;
  slide8.addText(m.value, {
    x: xPos, y: 4.6, w: 1.8, h: 0.45,
    fontSize: 18, fontFace: "Arial", color: colors.blue, bold: true, align: "center"
  });
  slide8.addText(m.label, {
    x: xPos, y: 5.0, w: 1.8, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: colors.slate, align: "center"
  });
});

// ============ Slide 9: Three-tier Memory ============
let slide9 = pres.addSlide();
slide9.background = { color: colors.white };

slide9.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide9.addText("03  三层记忆体系", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide9.addText("解决「状态失配」问题", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.3,
  fontSize: 13, fontFace: "Arial", color: colors.skyBlue
});

const memories = [
  {
    title: "工作记忆",
    content: "最近10轮对话\n当前任务状态\n检索上下文",
    color: colors.paleBlue,
    icon: "短"
  },
  {
    title: "情景记忆",
    content: "历史训练记录\n疲劳与恢复状态\n阶段性目标",
    color: colors.lightBlue,
    icon: "中"
  },
  {
    title: "语义记忆",
    content: "训练目标与偏好\n运动能力等级\n伤病历史",
    color: colors.blue,
    icon: "长"
  }
];

memories.forEach((mem, idx) => {
  const xPos = 0.6 + idx * 3.1;

  slide9.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.35, w: 2.9, h: 3.6, fill: { color: mem.color }, shadow: cardShadow()
  });

  // Icon circle
  slide9.addShape(pres.shapes.OVAL, {
    x: xPos + 1.1, y: 1.6, w: 0.7, h: 0.7, fill: { color: colors.white, transparency: 50 }
  });
  slide9.addText(mem.icon, {
    x: xPos + 1.1, y: 1.6, w: 0.7, h: 0.7,
    fontSize: 14, fontFace: "Arial", color: colors.white, bold: true, align: "center", valign: "middle"
  });

  slide9.addText(mem.title, {
    x: xPos, y: 2.5, w: 2.9, h: 0.5,
    fontSize: 18, fontFace: "Arial", color: colors.white, bold: true, align: "center"
  });

  slide9.addText(mem.content, {
    x: xPos + 0.15, y: 3.1, w: 2.6, h: 1.6,
    fontSize: 12, fontFace: "Arial", color: colors.white, align: "center"
  });
});

// Bottom note
slide9.addText("记忆感知检索：Query + User State 联合检索模式", {
  x: 0.6, y: 5.1, w: 8.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: colors.slate, align: "center"
});

// ============ Slide 10: Multi-agent System ============
let slide10 = pres.addSlide();
slide10.background = { color: colors.white };

slide10.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide10.addText("03  多智能体协同", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide10.addText("解决「角色失配」问题", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.3,
  fontSize: 13, fontFace: "Arial", color: colors.navy
});

const agents = [
  {
    title: "训练规划教练",
    keywords: "计划 · 规划 · 周期 · 目标",
    color: colors.blue,
    desc: "制定科学训练计划"
  },
  {
    title: "技术指导教练",
    keywords: "动作 · 姿势 · 技术 · 要领",
    color: colors.skyBlue,
    desc: "提供动作指导与纠正"
  },
  {
    title: "运动康复教练",
    keywords: "恢复 · 康复 · 损伤 · 预防",
    color: colors.navy,
    desc: "损伤风险评估与恢复建议"
  }
];

agents.forEach((agent, idx) => {
  const yPos = 1.35 + idx * 1.35;

  slide10.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 1.15, fill: { color: colors.white }, shadow: cardShadow()
  });

  // Left accent
  slide10.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 0.1, h: 1.15, fill: { color: agent.color }
  });

  // Agent icon
  slide10.addShape(pres.shapes.OVAL, {
    x: 0.9, y: yPos + 0.25, w: 0.65, h: 0.65, fill: { color: agent.color }
  });
  slide10.addText(`${idx + 1}`, {
    x: 0.9, y: yPos + 0.25, w: 0.65, h: 0.65,
    fontSize: 14, fontFace: "Arial", color: colors.white, bold: true, align: "center", valign: "middle"
  });

  slide10.addText(agent.title, {
    x: 1.75, y: yPos + 0.15, w: 3, h: 0.45,
    fontSize: 16, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide10.addText(agent.keywords, {
    x: 1.75, y: yPos + 0.55, w: 3, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: colors.gray
  });

  slide10.addText(agent.desc, {
    x: 5.2, y: yPos + 0.35, w: 4, h: 0.45,
    fontSize: 13, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 11: System Features ============
let slide11 = pres.addSlide();
slide11.background = { color: colors.white };

slide11.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide11.addText("03  系统功能模块", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const features = [
  { title: "用户信息管理", desc: "注册、登录、个人资料管理", icon: "👤" },
  { title: "AI教练问答", desc: "自然语言问答，支持单/多智能体模式", icon: "💬" },
  { title: "训练计划", desc: "个性化训练计划生成与管理", icon: "📋" },
  { title: "健康记录", desc: "训练表现、饮食、体重追踪", icon: "📊" },
  { title: "知识库管理", desc: "运动科学知识库维护", icon: "📚" },
  { title: "记忆管理", desc: "跨会话用户状态追踪", icon: "🧠" }
];

features.forEach((feat, idx) => {
  const col = idx % 3;
  const row = Math.floor(idx / 3);
  const xPos = 0.6 + col * 3.05;
  const yPos = 1.15 + row * 2.1;

  slide11.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: yPos, w: 2.9, h: 1.9, fill: { color: colors.white }, shadow: cardShadow()
  });

  // Top accent
  slide11.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: yPos, w: 2.9, h: 0.06, fill: { color: colors.blue }
  });

  slide11.addText(feat.title, {
    x: xPos + 0.15, y: yPos + 0.25, w: 2.6, h: 0.45,
    fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide11.addText(feat.desc, {
    x: xPos + 0.15, y: yPos + 0.8, w: 2.6, h: 0.8,
    fontSize: 11, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 12: Frontend Implementation ============
let slide12 = pres.addSlide();
slide12.background = { color: colors.white };

slide12.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide12.addText("04  前端实现", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide12.addText("Vue3 + Vite 技术栈", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.gray
});

const pages = [
  { name: "用户信息页面", desc: "个人资料查看与编辑" },
  { name: "AI教练问答页面", desc: "智能问答与引用展示" },
  { name: "训练计划页面", desc: "计划生成、查看、修改" },
  { name: "健康记录页面", desc: "训练、饮食、体重记录" },
  { name: "知识库管理页面", desc: "文档上传与维护" }
];

pages.forEach((page, idx) => {
  const yPos = 1.4 + idx * 0.78;

  slide12.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 0.68, fill: { color: colors.paleBlue }
  });

  slide12.addText(`${idx + 1}`, {
    x: 0.75, y: yPos + 0.14, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.white, bold: true, align: "center", valign: "middle"
  });

  slide12.addText(page.name, {
    x: 1.3, y: yPos + 0.14, w: 3.5, h: 0.4,
    fontSize: 13, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide12.addText(page.desc, {
    x: 4.8, y: yPos + 0.14, w: 4.3, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 13: Backend Implementation ============
let slide13 = pres.addSlide();
slide13.background = { color: colors.white };

slide13.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide13.addText("04  后端实现", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide13.addText("FastAPI + LangGraph 技术栈", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.gray
});

const backendMods = [
  {
    title: "RAG检索模块",
    items: ["HyDE假设文档", "MQE多查询扩展", "记忆感知检索", "引用约束生成"],
    color: colors.blue
  },
  {
    title: "记忆管理模块",
    items: ["工作记忆管理", "情景记忆存储", "语义记忆抽象", "遗忘机制"],
    color: colors.skyBlue
  },
  {
    title: "多智能体模块",
    items: ["意图识别路由", "角色智能体池", "LangGraph状态图", "结果整合"],
    color: colors.navy
  }
];

backendMods.forEach((mod, idx) => {
  const xPos = 0.6 + idx * 3.1;

  slide13.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.9, h: 3.7, fill: { color: mod.color }, shadow: cardShadow()
  });

  slide13.addText(mod.title, {
    x: xPos + 0.1, y: 1.6, w: 2.7, h: 0.5,
    fontSize: 14, fontFace: "Arial", color: colors.white, bold: true, align: "center"
  });

  mod.items.forEach((item, i) => {
    slide13.addText("• " + item, {
      x: xPos + 0.2, y: 2.3 + i * 0.6, w: 2.5, h: 0.45,
      fontSize: 11, fontFace: "Arial", color: colors.white
    });
  });
});

// ============ Slide 14: Data Storage ============
let slide14 = pres.addSlide();
slide14.background = { color: colors.white };

slide14.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide14.addText("04  数据存储层设计", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

// SQLite card
slide14.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.1, w: 4.3, h: 4.1, fill: { color: colors.white }, shadow: cardShadow()
});
slide14.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.1, w: 4.3, h: 0.08, fill: { color: colors.blue }
});

slide14.addText("SQLite", {
  x: 0.8, y: 1.35, w: 3.9, h: 0.5,
  fontSize: 20, fontFace: "Arial", color: colors.navy, bold: true
});
slide14.addText("关系数据库", {
  x: 0.8, y: 1.8, w: 3.9, h: 0.3,
  fontSize: 11, fontFace: "Arial", color: colors.gray
});

slide14.addText([
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

// ChromaDB card
slide14.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.1, w: 4.3, h: 4.1, fill: { color: colors.white }, shadow: cardShadow()
});
slide14.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.1, w: 4.3, h: 0.08, fill: { color: colors.skyBlue }
});

slide14.addText("ChromaDB", {
  x: 5.3, y: 1.35, w: 3.9, h: 0.5,
  fontSize: 20, fontFace: "Arial", color: colors.navy, bold: true
});
slide14.addText("向量数据库", {
  x: 5.3, y: 1.8, w: 3.9, h: 0.3,
  fontSize: 11, fontFace: "Arial", color: colors.gray
});

slide14.addText([
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

// ============ Slide 15: Testing - RAG Module ============
let slide15 = pres.addSlide();
slide15.background = { color: colors.white };

slide15.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide15.addText("05  系统测试：RAG模块", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide15.addText("基于RAG的科学化训练指导功能测试（300条测试样本）", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: colors.gray
});

// Results table
slide15.addTable([
  [
    { text: "指标", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "数值", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "说明", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } }
  ],
  [
    { text: "Precision@5", options: { align: "center" } },
    { text: "0.84", options: { align: "center", bold: true, color: colors.blue } },
    { text: "Top-5检索准确率" }
  ],
  [
    { text: "Recall@5", options: { align: "center" } },
    { text: "0.79", options: { align: "center", bold: true, color: colors.blue } },
    { text: "Top-5召回率" }
  ],
  [
    { text: "Faithfulness", options: { align: "center" } },
    { text: "0.88", options: { align: "center", bold: true, color: colors.blue } },
    { text: "答案可信度" }
  ],
  [
    { text: "Relevancy", options: { align: "center" } },
    { text: "0.91", options: { align: "center", bold: true, color: colors.blue } },
    { text: "答案相关性" }
  ]
], {
  x: 0.6, y: 1.4, w: 8.8, h: 2.2,
  fontFace: "Arial", fontSize: 12,
  border: { pt: 0.5, color: "E2E8F0" },
  colW: [2.8, 2, 4]
});

// ============ Slide 16: Testing - Memory Module ============
let slide16 = pres.addSlide();
slide16.background = { color: colors.white };

slide16.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide16.addText("05  系统测试：记忆模块", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide16.addText("基于长期记忆的个性化训练管理测试", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: colors.gray
});

// Big metric card
slide16.addShape(pres.shapes.RECTANGLE, {
  x: 2.5, y: 1.5, w: 5, h: 2.2, fill: { color: colors.paleBlue }, shadow: cardShadow()
});

slide16.addText("个性化匹配准确率", {
  x: 2.5, y: 1.75, w: 5, h: 0.5,
  fontSize: 16, fontFace: "Arial", color: colors.navy, align: "center"
});

slide16.addText("0.87", {
  x: 2.5, y: 2.3, w: 5, h: 1.0,
  fontSize: 56, fontFace: "Arial", color: colors.blue, bold: true, align: "center"
});

slide16.addText("87%", {
  x: 6.8, y: 2.5, w: 1.2, h: 0.6,
  fontSize: 24, fontFace: "Arial", color: colors.success, bold: true
});

slide16.addText("测试结论：三层记忆体系有效提升了用户状态追踪能力，\n实现跨会话的个性化训练管理", {
  x: 0.6, y: 4.0, w: 8.8, h: 0.7,
  fontSize: 13, fontFace: "Arial", color: colors.slate, align: "center"
});

// ============ Slide 17: Testing - Multi-agent ============
let slide17 = pres.addSlide();
slide17.background = { color: colors.white };

slide17.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide17.addText("05  系统测试：多智能体模块", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide17.addText("基于多智能体协同的完整训练支持测试", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: colors.gray
});

// Big metric card
slide17.addShape(pres.shapes.RECTANGLE, {
  x: 2.5, y: 1.5, w: 5, h: 2.2, fill: { color: colors.iceBlue }, shadow: cardShadow()
});

slide17.addText("任务完成率", {
  x: 2.5, y: 1.75, w: 5, h: 0.5,
  fontSize: 16, fontFace: "Arial", color: colors.navy, align: "center"
});

slide17.addText("0.93", {
  x: 2.5, y: 2.3, w: 5, h: 1.0,
  fontSize: 56, fontFace: "Arial", color: colors.navy, bold: true, align: "center"
});

slide17.addText("93%", {
  x: 6.8, y: 2.5, w: 1.2, h: 0.6,
  fontSize: 24, fontFace: "Arial", color: colors.success, bold: true
});

slide17.addText("测试结论：多智能体协同机制有效提升复杂训练支持任务完成率，\n实现多角色专业分工与协同决策", {
  x: 0.6, y: 4.0, w: 8.8, h: 0.7,
  fontSize: 13, fontFace: "Arial", color: colors.slate, align: "center"
});

// ============ Slide 18: Comparison Experiment ============
let slide18 = pres.addSlide();
slide18.background = { color: colors.white };

slide18.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide18.addText("05  对比实验", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide18.addText("消融实验：逐级对照方案", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: colors.gray
});

// Comparison table
slide18.addTable([
  [
    { text: "方案", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "Precision@5", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "个性化准确率", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "任务完成率", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } }
  ],
  [
    { text: "裸LLM", options: { align: "center" } },
    { text: "0.52", options: { align: "center" } },
    { text: "0.45", options: { align: "center" } },
    { text: "0.61", options: { align: "center" } }
  ],
  [
    { text: "基础RAG", options: { align: "center" } },
    { text: "0.71", options: { align: "center" } },
    { text: "0.48", options: { align: "center" } },
    { text: "0.68", options: { align: "center" } }
  ],
  [
    { text: "RAG+记忆", options: { align: "center" } },
    { text: "0.78", options: { align: "center" } },
    { text: "0.75", options: { align: "center" } },
    { text: "0.79", options: { align: "center" } }
  ],
  [
    { text: "RAG+记忆+多智能体", options: { align: "center", bold: true, color: colors.blue } },
    { text: "0.84", options: { align: "center", bold: true, color: colors.blue } },
    { text: "0.87", options: { align: "center", bold: true, color: colors.blue } },
    { text: "0.93", options: { align: "center", bold: true, color: colors.blue } }
  ]
], {
  x: 0.6, y: 1.4, w: 8.8, h: 2.4,
  fontFace: "Arial", fontSize: 11,
  border: { pt: 0.5, color: "E2E8F0" },
  colW: [2.8, 1.9, 2.05, 2.05]
});

// ============ Slide 19: Non-functional Testing ============
let slide19 = pres.addSlide();
slide19.background = { color: colors.white };

slide19.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide19.addText("05  非功能性测试", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const nfTests = [
  { title: "性能", items: ["平均响应时间<8秒", "复杂查询<15秒", "首屏加载流畅"], color: colors.blue },
  { title: "安全", items: ["Token身份鉴权", "密码加密存储", "接口权限控制"], color: colors.success },
  { title: "兼容", items: ["Chrome 120+", "Safari 17+", "主流浏览器适配"], color: colors.skyBlue },
  { title: "易用", items: ["界面简洁直观", "操作逻辑清晰", "错误提示友好"], color: colors.navy }
];

nfTests.forEach((test, idx) => {
  const xPos = 0.6 + idx * 2.35;

  slide19.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.15, w: 2.2, h: 4.1, fill: { color: colors.white }, shadow: cardShadow()
  });

  // Top accent
  slide19.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.15, w: 2.2, h: 0.08, fill: { color: test.color }
  });

  slide19.addText(test.title, {
    x: xPos + 0.1, y: 1.4, w: 2.0, h: 0.5,
    fontSize: 16, fontFace: "Arial", color: colors.navy, bold: true, align: "center"
  });

  test.items.forEach((item, i) => {
    slide19.addText("✓ " + item, {
      x: xPos + 0.15, y: 2.1 + i * 0.75, w: 1.9, h: 0.55,
      fontSize: 11, fontFace: "Arial", color: colors.slate
    });
  });
});

// ============ Slide 20: Technical Summary ============
let slide20 = pres.addSlide();
slide20.background = { color: colors.white };

slide20.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide20.addText("05  技术总结", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const techSummary = [
  { title: "知识可靠", desc: "ST-RAG提升到\n0.84 Precision@5", value: "84%", color: colors.blue },
  { title: "个性适配", desc: "三层记忆达到\n0.87匹配准确率", value: "87%", color: colors.skyBlue },
  { title: "协同决策", desc: "多智能体实现\n0.93任务完成率", value: "93%", color: colors.navy }
];

techSummary.forEach((item, idx) => {
  const xPos = 0.6 + idx * 3.1;

  slide20.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.15, w: 2.9, h: 4.1, fill: { color: item.color }, shadow: cardShadow()
  });

  slide20.addText(item.value, {
    x: xPos, y: 1.5, w: 2.9, h: 1.0,
    fontSize: 42, fontFace: "Arial", color: colors.white, bold: true, align: "center"
  });

  slide20.addText(item.title, {
    x: xPos, y: 2.6, w: 2.9, h: 0.5,
    fontSize: 18, fontFace: "Arial", color: colors.white, bold: true, align: "center"
  });

  slide20.addText(item.desc, {
    x: xPos + 0.15, y: 3.2, w: 2.6, h: 1.6,
    fontSize: 12, fontFace: "Arial", color: colors.white, align: "center"
  });
});

// ============ Slide 21: Related Work - RAG ============
let slide21 = pres.addSlide();
slide21.background = { color: colors.white };

slide21.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide21.addText("02  相关技术综述：RAG", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide21.addText("检索增强生成（RAG）", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.blue, bold: true
});

const ragTechs = [
  { title: "基础架构", desc: "文档解析→切分→\n向量化→检索→生成" },
  { title: "向量检索", desc: "双塔编码架构，\n余弦相似度匹配" },
  { title: "高级策略", desc: "MQE多查询扩展、\nHyDE假设文档嵌入" },
  { title: "Agentic RAG", desc: "Self-RAG、CRAG\n自主决策检索" }
];

ragTechs.forEach((tech, idx) => {
  const xPos = 0.6 + idx * 2.35;
  slide21.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.2, h: 2.6, fill: { color: colors.white }, shadow: cardShadow()
  });
  slide21.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.2, h: 0.06, fill: { color: colors.blue }
  });
  slide21.addText(tech.title, {
    x: xPos + 0.1, y: 1.6, w: 2.0, h: 0.45,
    fontSize: 13, fontFace: "Arial", color: colors.navy, bold: true, align: "center"
  });
  slide21.addText(tech.desc, {
    x: xPos + 0.1, y: 2.15, w: 2.0, h: 1.6,
    fontSize: 11, fontFace: "Arial", color: colors.slate, align: "center"
  });
});

slide21.addText("向量数据库：ChromaDB（HNSW索引，毫秒级检索）", {
  x: 0.6, y: 4.2, w: 8.8, h: 0.35,
  fontSize: 11, fontFace: "Arial", color: colors.gray
});

// ============ Slide 22: Related Work - Memory ============
let slide22 = pres.addSlide();
slide22.background = { color: colors.white };

slide22.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide22.addText("02  相关技术综述：长期记忆", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide22.addText("大语言模型的记忆机制", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.skyBlue, bold: true
});

const memoryConcepts = [
  { title: "认知科学基础", items: ["Atkinson-Shiffrin模型", "工作记忆模型", "情景与语义记忆"] },
  { title: "模型局限", items: ["参数化知识固化", "会话级无状态", "上下文迷失中间"] },
  { title: "外部记忆方案", items: ["向量存储历史", "MemoryBank动态强化", "分层记忆架构"] },
  { title: "记忆机制", items: ["重要性评分写入", "Ebbinghaus遗忘曲线", "记忆巩固与检索"] }
];

memoryConcepts.forEach((concept, idx) => {
  const xPos = 0.6 + idx * 2.35;
  slide22.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.2, h: 3.3, fill: { color: colors.paleBlue }, shadow: cardShadow()
  });
  slide22.addText(concept.title, {
    x: xPos + 0.1, y: 1.55, w: 2.0, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.navy, bold: true, align: "center"
  });
  concept.items.forEach((item, i) => {
    slide22.addText("• " + item, {
      x: xPos + 0.1, y: 2.1 + i * 0.55, w: 2.0, h: 0.45,
      fontSize: 10, fontFace: "Arial", color: colors.slate
    });
  });
});

// ============ Slide 23: Related Work - Multi-agent ============
let slide23 = pres.addSlide();
slide23.background = { color: colors.white };

slide23.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide23.addText("02  相关技术综述：多智能体", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide23.addText("多智能体系统", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
});

const agentConcepts = [
  { title: "LLM智能体架构", items: ["ReAct：推理与行动交织", "Plan-and-Solve：先规划后执行", "Reflexion：自我反思机制"] },
  { title: "协作框架", items: ["AutoGen：可定制多方会话", "MetaGPT：标准作业流程", "LangGraph：状态图编排"] },
  { title: "协同调度", items: ["多标签意图识别", "主从/并行协作模式", "条件激活与层次调度"] }
];

agentConcepts.forEach((concept, idx) => {
  const xPos = 0.6 + idx * 3.1;
  slide23.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.9, h: 3.3, fill: { color: colors.white }, shadow: cardShadow()
  });
  slide23.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.4, w: 2.9, h: 0.06, fill: { color: colors.blue }
  });
  slide23.addText(concept.title, {
    x: xPos + 0.1, y: 1.6, w: 2.7, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.navy, bold: true, align: "center"
  });
  concept.items.forEach((item, i) => {
    slide23.addText("• " + item, {
      x: xPos + 0.15, y: 2.15 + i * 0.6, w: 2.6, h: 0.5,
      fontSize: 10, fontFace: "Arial", color: colors.slate
    });
  });
});

// ============ Slide 24: ST-RAG Detailed Design ============
let slide24 = pres.addSlide();
slide24.background = { color: colors.white };

slide24.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide24.addText("03  ST-RAG详细设计", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide24.addText("语义增强RAG策略（ST-RAG）", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.3,
  fontSize: 12, fontFace: "Arial", color: colors.gray
});

const ragDetails = [
  { step: "1. HyDE", desc: "生成假设性专业回答，映射到专业知识空间" },
  { step: "2. MQE", desc: "将复杂训练问题拆解为多个语义子查询" },
  { step: "3. 记忆感知", desc: "从语义/情景记忆中提取用户状态摘要" },
  { step: "4. RRF融合", desc: "Reciprocal Rank Fusion综合多查询排名结果" },
  { step: "5. 引用约束", desc: "提示词约束强制引用，后处理校验降幻觉" }
];

ragDetails.forEach((detail, idx) => {
  const yPos = 1.35 + idx * 0.8;
  slide24.addShape(pres.shapes.OVAL, {
    x: 0.6, y: yPos + 0.1, w: 0.4, h: 0.4, fill: { color: colors.blue }
  });
  slide24.addText(detail.step, {
    x: 1.1, y: yPos, w: 1.3, h: 0.55,
    fontSize: 12, fontFace: "Arial", color: colors.navy, bold: true
  });
  slide24.addText(detail.desc, {
    x: 2.5, y: yPos, w: 7, h: 0.55,
    fontSize: 12, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 25: Three-tier Memory Detailed ============
let slide25 = pres.addSlide();
slide25.background = { color: colors.white };

slide25.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide25.addText("03  三层记忆详细设计", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide25.addText("记忆与RAG联动机制", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.3,
  fontSize: 12, fontFace: "Arial", color: colors.gray
});

// Table
slide25.addTable([
  [
    { text: "记忆类型", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "功能", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "更新频率", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "容量", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } }
  ],
  [
    { text: "工作记忆", options: { align: "center", bold: true } },
    { text: "维护当前会话上下文", options: { align: "center" } },
    { text: "每次交互更新", options: { align: "center" } },
    { text: "10轮对话", options: { align: "center" } }
  ],
  [
    { text: "情景记忆", options: { align: "center", bold: true } },
    { text: "保存历史训练事件", options: { align: "center" } },
    { text: "每次交互更新", options: { align: "center" } },
    { text: "无限制", options: { align: "center" } }
  ],
  [
    { text: "语义记忆", options: { align: "center", bold: true } },
    { text: "抽象存储长期特征", options: { align: "center" } },
    { text: "偶尔更新", options: { align: "center" } },
    { text: "无限制", options: { align: "center" } }
  ]
], {
  x: 0.6, y: 1.35, w: 8.8, h: 1.7,
  fontFace: "Arial", fontSize: 10,
  border: { pt: 0.5, color: "E2E8F0" },
  colW: [1.8, 2.6, 2.2, 2.2]
});

slide25.addText("记忆感知检索流程", {
  x: 0.6, y: 3.25, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.navy, bold: true
});

slide25.addText([
  { text: "1. 从语义记忆提取用户长期状态（训练目标、伤病历史、能力等级）", options: { bullet: true, breakLine: true } },
  { text: "2. 从情景记忆提取近期训练背景（近期负荷、恢复状态）", options: { bullet: true, breakLine: true } },
  { text: "3. 与当前问题拼接为增强查询：Query + User State", options: { bullet: true, breakLine: true } },
  { text: "4. 检索结果优先匹配用户个体状态，实现真正的个性化训练指导", options: { bullet: true } }
], {
  x: 0.6, y: 3.65, w: 8.8, h: 1.6,
  fontSize: 11, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 6
});

// ============ Slide 26: Multi-agent Workflow ============
let slide26 = pres.addSlide();
slide26.background = { color: colors.white };

slide26.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide26.addText("03  多智能体协同流程", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const workflowSteps = [
  { step: "1. 请求路由", desc: "多标签意图识别，判断问题涉及的专业领域" },
  { step: "2. 任务分发", desc: "单智能体模式 vs 多智能体模式动态切换" },
  { step: "3. 协同执行", desc: "各角色智能体独立调用RAG子系统完成专业推理" },
  { step: "4. 结果整合", desc: "综合智能体统一整合多角色输出，冲突消解" },
  { step: "5. 异常兜底", desc: "单点故障时自动降级，保证系统可用性" }
];

workflowSteps.forEach((wf, idx) => {
  const yPos = 1.15 + idx * 0.85;
  slide26.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 0.75, fill: { color: colors.white }, shadow: cardShadow()
  });
  slide26.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 0.08, h: 0.75, fill: { color: colors.blue }
  });
  slide26.addText(wf.step, {
    x: 0.85, y: yPos + 0.15, w: 1.8, h: 0.45,
    fontSize: 13, fontFace: "Arial", color: colors.navy, bold: true
  });
  slide26.addText(wf.desc, {
    x: 2.8, y: yPos + 0.15, w: 6.3, h: 0.45,
    fontSize: 12, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 27: Conclusion ============
let slide27 = pres.addSlide();
slide27.background = { color: colors.white };

slide27.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide27.addText("06  结论", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide27.addText("本文工作总结", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.blue, bold: true
});

slide27.addText([
  { text: "1. 提出ST-RAG语义增强RAG策略，结合MQE与HyDE解决知识失配问题", options: { bullet: true, breakLine: true } },
  { text: "2. 设计三层记忆体系，实现跨会话用户状态追踪与个性化检索", options: { bullet: true, breakLine: true } },
  { text: "3. 构建基于LangGraph的多智能体协同架构，实现专业分工与协同决策", options: { bullet: true, breakLine: true } },
  { text: "4. 完成系统全流程工程实现与多维度测试验证", options: { bullet: true } }
], {
  x: 0.6, y: 1.4, w: 8.8, h: 2.5,
  fontSize: 13, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 12, bullet: { color: colors.blue }
});

// ============ Slide 28: Future Work ============
let slide28 = pres.addSlide();
slide28.background = { color: colors.white };

slide28.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide28.addText("06  未来工作展望", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const futureWorks = [
  "知识库动态更新机制",
  "多模态感知能力扩展",
  "个性化自适应训练",
  "系统可扩展性优化",
  "可解释性与安全性提升"
];

futureWorks.forEach((work, idx) => {
  const yPos = 1.2 + idx * 0.8;

  slide28.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 0.65, fill: { color: colors.paleBlue }
  });

  slide28.addShape(pres.shapes.OVAL, {
    x: 0.75, y: yPos + 0.12, w: 0.4, h: 0.4, fill: { color: colors.blue }
  });
  slide28.addText(`${idx + 1}`, {
    x: 0.75, y: yPos + 0.12, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.white, bold: true, align: "center", valign: "middle"
  });

  slide28.addText(work, {
    x: 1.3, y: yPos + 0.12, w: 7.8, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: colors.navy
  });
});

// ============ Slide 29: Technology Stack ============
let slide29 = pres.addSlide();
slide29.background = { color: colors.white };

slide29.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide29.addText("技术栈总结", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const techStack = [
  { category: "前端", tech: "Vue3 + Vite + Axios" },
  { category: "后端", tech: "FastAPI + LangGraph + SQLAlchemy" },
  { category: "数据库", tech: "SQLite + ChromaDB" },
  { category: "AI模型", tech: "LLM + Embedding Model" }
];

techStack.forEach((tech, idx) => {
  const yPos = 1.15 + idx * 1.05;
  slide29.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 0.85, fill: { color: colors.paleBlue }, shadow: cardShadow()
  });
  slide29.addText(tech.category, {
    x: 0.8, y: yPos + 0.2, w: 1.8, h: 0.45,
    fontSize: 14, fontFace: "Arial", color: colors.blue, bold: true
  });
  slide29.addText(tech.tech, {
    x: 2.8, y: yPos + 0.2, w: 6.3, h: 0.45,
    fontSize: 14, fontFace: "Arial", color: colors.navy
  });
});

// ============ Slide 30: Thank You ============
let slide30 = pres.addSlide();
slide30.background = { color: colors.navy };

slide30.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.blue }
});
slide30.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.545, w: 10, h: 0.08, fill: { color: colors.blue }
});

// Geometric accents
slide30.addShape(pres.shapes.OVAL, {
  x: -2, y: -1, w: 4, h: 4, fill: { color: colors.blue, transparency: 85 }
});
slide30.addShape(pres.shapes.OVAL, {
  x: 8, y: 3, w: 3, h: 3, fill: { color: colors.blue, transparency: 85 }
});

slide30.addText("感谢聆听", {
  x: 0.5, y: 1.6, w: 9, h: 1.0,
  fontSize: 48, fontFace: "Arial", color: colors.white, bold: true, align: "center"
});

slide30.addText("请批评指正", {
  x: 0.5, y: 2.7, w: 9, h: 0.6,
  fontSize: 22, fontFace: "Arial", color: colors.lightBlue, align: "center"
});

slide30.addShape(pres.shapes.RECTANGLE, {
  x: 3.5, y: 3.5, w: 3, h: 0.02, fill: { color: colors.lightBlue }
});

slide30.addText("刘冰彦 | 22301126 | 软件学院", {
  x: 0.5, y: 3.8, w: 9, h: 0.5,
  fontSize: 14, fontFace: "Arial", color: colors.gray, align: "center"
});

slide30.addText("北京交通大学", {
  x: 0.5, y: 4.3, w: 9, h: 0.4,
  fontSize: 12, fontFace: "Arial", color: colors.gray, align: "center"
});

// Save the presentation
pres.writeFile({ fileName: "/Users/liubingyan/Sports-Training-Agent/docs/论文汇报PPT.pptx" })
  .then(() => console.log("Presentation created successfully!"))
  .catch(err => console.error("Error:", err));
