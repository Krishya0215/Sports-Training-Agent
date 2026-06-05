const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = '刘冰彦';
pres.title = '系统测试';

// Sophisticated blue-white minimalist palette
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

slide1.addText("第五章", {
  x: 0.5, y: 1.5, w: 9, h: 0.5,
  fontSize: 16, fontFace: "Arial", color: colors.lightBlue, align: "center"
});

slide1.addText("系统测试", {
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

// ============ Slide 2: Test Overview ============
let slide2 = pres.addSlide();
slide2.background = { color: colors.white };

slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide2.addText("05  测试概述", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const testOverview = [
  { num: "01", title: "测试环境", desc: "硬件与软件配置" },
  { num: "02", title: "三大模块测试", desc: "RAG、记忆、多智能体功能验证" },
  { num: "03", title: "综合对比实验", desc: "消融实验与阈值对照" },
  { num: "04", title: "非功能性测试", desc: "性能、安全、兼容、易用" }
];

testOverview.forEach((item, idx) => {
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

// ============ Slide 3: Test Environment ============
let slide3 = pres.addSlide();
slide3.background = { color: colors.white };

slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide3.addText("05.1  测试环境", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

// Hardware
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.1, w: 4.3, h: 2.5, fill: { color: colors.white }, shadow: cardShadow()
});
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.1, w: 4.3, h: 0.08, fill: { color: colors.blue }
});

slide3.addText("硬件环境", {
  x: 0.8, y: 1.35, w: 3.9, h: 0.4,
  fontSize: 16, fontFace: "Arial", color: colors.navy, bold: true
});

slide3.addText([
  { text: "CPU: Apple M2 Pro", options: { bullet: true, breakLine: true } },
  { text: "内存: 16GB", options: { bullet: true, breakLine: true } },
  { text: "存储: 512GB SSD", options: { bullet: true, breakLine: true } },
  { text: "操作系统: macOS", options: { bullet: true } }
], {
  x: 0.8, y: 1.85, w: 3.9, h: 1.5,
  fontSize: 12, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 6, bullet: { color: colors.blue }
});

// Software
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.1, w: 4.3, h: 2.5, fill: { color: colors.white }, shadow: cardShadow()
});
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.1, w: 4.3, h: 0.08, fill: { color: colors.skyBlue }
});

slide3.addText("软件环境", {
  x: 5.3, y: 1.35, w: 3.9, h: 0.4,
  fontSize: 16, fontFace: "Arial", color: colors.navy, bold: true
});

slide3.addText([
  { text: "Python 3.11", options: { bullet: true, breakLine: true } },
  { text: "FastAPI + Vue3", options: { bullet: true, breakLine: true } },
  { text: "SQLite + ChromaDB", options: { bullet: true, breakLine: true } },
  { text: "Claude API", options: { bullet: true } }
], {
  x: 5.3, y: 1.85, w: 3.9, h: 1.5,
  fontSize: 12, fontFace: "Arial", color: colors.slate,
  paraSpaceAfter: 6, bullet: { color: colors.skyBlue }
});

// Test data
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 3.85, w: 8.8, h: 1.4, fill: { color: colors.iceBlue }
});

slide3.addText("测试数据", {
  x: 0.8, y: 4.0, w: 8.4, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
});

slide3.addText("运动训练领域测试样本：300条 | 用户画像：5类 | 复杂任务：50个", {
  x: 0.8, y: 4.4, w: 8.4, h: 0.7,
  fontSize: 13, fontFace: "Arial", color: colors.slate
});

// ============ Slide 4: RAG Testing ============
let slide4 = pres.addSlide();
slide4.background = { color: colors.white };

slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide4.addText("05.2.1  基于RAG的科学化训练指导功能测试", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 24, fontFace: "Arial", color: colors.navy, bold: true
});

slide4.addText("测试目标：验证ST-RAG在知识检索与生成方面的性能", {
  x: 0.6, y: 0.95, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray
});

// Results table
slide4.addTable([
  [
    { text: "评估指标", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "数值", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "目标阈值", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "达标情况", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } }
  ],
  [
    { text: "Precision@5", options: { align: "center" } },
    { text: "0.84", options: { align: "center", bold: true, color: colors.blue } },
    { text: "≥0.80", options: { align: "center" } },
    { text: "✓ 达标", options: { align: "center", color: colors.success } }
  ],
  [
    { text: "Recall@5", options: { align: "center" } },
    { text: "0.79", options: { align: "center", bold: true, color: colors.blue } },
    { text: "≥0.75", options: { align: "center" } },
    { text: "✓ 达标", options: { align: "center", color: colors.success } }
  ],
  [
    { text: "Faithfulness", options: { align: "center" } },
    { text: "0.88", options: { align: "center", bold: true, color: colors.blue } },
    { text: "≥0.85", options: { align: "center" } },
    { text: "✓ 达标", options: { align: "center", color: colors.success } }
  ],
  [
    { text: "Relevancy", options: { align: "center" } },
    { text: "0.91", options: { align: "center", bold: true, color: colors.blue } },
    { text: "≥0.85", options: { align: "center" } },
    { text: "✓ 达标", options: { align: "center", color: colors.success } }
  ]
], {
  x: 0.6, y: 1.5, w: 8.8, h: 2.2,
  fontFace: "Arial", fontSize: 12,
  border: { pt: 0.5, color: "E2E8F0" },
  colW: [2.2, 2, 2, 2.6]
});

// Key achievement
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.0, w: 8.8, h: 1.2, fill: { color: colors.paleBlue }
});

slide4.addText("核心指标", {
  x: 0.8, y: 4.15, w: 2, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: colors.navy, bold: true
});

slide4.addText("Precision@5: 0.84  |  Faithfulness: 0.88  |  Relevancy: 0.91", {
  x: 0.8, y: 4.55, w: 8.4, h: 0.5,
  fontSize: 14, fontFace: "Arial", color: colors.blue, bold: true
});

// ============ Slide 5: Memory Testing ============
let slide5 = pres.addSlide();
slide5.background = { color: colors.white };

slide5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide5.addText("05.2.2  基于长期记忆的个性化训练管理测试", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 24, fontFace: "Arial", color: colors.navy, bold: true
});

slide5.addText("测试目标：验证三层记忆体系对个性化匹配的提升效果", {
  x: 0.6, y: 0.95, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray
});

// Big metric
slide5.addShape(pres.shapes.RECTANGLE, {
  x: 2.5, y: 1.5, w: 5, h: 2.0, fill: { color: colors.iceBlue }, shadow: cardShadow()
});

slide5.addText("个性化匹配准确率", {
  x: 2.5, y: 1.75, w: 5, h: 0.5,
  fontSize: 16, fontFace: "Arial", color: colors.navy, align: "center"
});

slide5.addText("0.87", {
  x: 2.5, y: 2.25, w: 5, h: 0.9,
  fontSize: 52, fontFace: "Arial", color: colors.blue, bold: true, align: "center"
});

slide5.addText("目标: ≥0.85  ✓ 达标", {
  x: 2.5, y: 3.15, w: 5, h: 0.3,
  fontSize: 12, fontFace: "Arial", color: colors.success, align: "center"
});

// Test scenarios
slide5.addText("测试场景", {
  x: 0.6, y: 3.8, w: 8.8, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
});

const memoryTests = [
  "膝关节伤病用户 → 优先召回康复建议",
  "力量训练者 → 优先召回高负荷训练",
  "减脂用户 → 优先召回有氧+饮食建议",
  "新手用户 → 优先召回基础动作指导"
];

memoryTests.forEach((test, idx) => {
  const yPos = 4.2 + idx * 0.32;
  slide5.addText("✓ " + test, {
    x: 0.6, y: yPos, w: 8.8, h: 0.3,
    fontSize: 11, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 6: Multi-agent Testing ============
let slide6 = pres.addSlide();
slide6.background = { color: colors.white };

slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide6.addText("05.2.3  基于多智能体协同的完整训练支持测试", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 24, fontFace: "Arial", color: colors.navy, bold: true
});

slide6.addText("测试目标：验证多智能体在复杂任务中的协同决策能力", {
  x: 0.6, y: 0.95, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray
});

// Big metric
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 2.5, y: 1.5, w: 5, h: 2.0, fill: { color: colors.paleBlue }, shadow: cardShadow()
});

slide6.addText("任务完成率", {
  x: 2.5, y: 1.75, w: 5, h: 0.5,
  fontSize: 16, fontFace: "Arial", color: colors.navy, align: "center"
});

slide6.addText("0.93", {
  x: 2.5, y: 2.25, w: 5, h: 0.9,
  fontSize: 52, fontFace: "Arial", color: colors.navy, bold: true, align: "center"
});

slide6.addText("目标: ≥0.90  ✓ 达标", {
  x: 2.5, y: 3.15, w: 5, h: 0.3,
  fontSize: 12, fontFace: "Arial", color: colors.success, align: "center"
});

// Test cases
slide6.addText("复杂任务测试用例", {
  x: 0.6, y: 3.8, w: 8.8, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
});

const agentTests = [
  "减脂期间跑步膝盖疼怎么办 → 训练规划 + 康复协同",
  "增肌期深蹲动作不标准 → 技术指导 + 训练规划",
  "运动损伤后如何恢复训练 → 康复 + 训练规划协同"
];

agentTests.forEach((test, idx) => {
  const yPos = 4.2 + idx * 0.4;
  slide6.addText("✓ " + test, {
    x: 0.6, y: yPos, w: 8.8, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: colors.slate
  });
});

// ============ Slide 7: Comparison Experiment ============
let slide7 = pres.addSlide();
slide7.background = { color: colors.white };

slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide7.addText("05.2.4  系统级综合对比与讨论", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

slide7.addText("消融实验：逐级对照方案", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 13, fontFace: "Arial", color: colors.gray
});

// Comparison table
slide7.addTable([
  [
    { text: "方案", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "Precision@5", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "个性化准确率", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "任务完成率", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } }
  ],
  [
    { text: "裸LLM", options: { align: "center" } },
    { text: "0.52", options: { align: "center", color: colors.gray } },
    { text: "0.45", options: { align: "center", color: colors.gray } },
    { text: "0.61", options: { align: "center", color: colors.gray } }
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

// Key insight
slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.0, w: 8.8, h: 1.2, fill: { color: colors.iceBlue }
});

slide7.addText("关键发现", {
  x: 0.8, y: 4.15, w: 8.4, h: 0.35,
  fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true
});

slide7.addText("三者协同效果显著：Precision提升61.5%，个性化准确率提升93.3%，任务完成率提升52.5%", {
  x: 0.8, y: 4.55, w: 8.4, h: 0.5,
  fontSize: 12, fontFace: "Arial", color: colors.slate
});

// ============ Slide 8: Non-functional Testing Overview ============
let slide8 = pres.addSlide();
slide8.background = { color: colors.white };

slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide8.addText("05.3  非功能性测试", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const nfCategories = [
  { title: "性能测试", items: ["平均响应时间<8秒", "复杂查询<15秒", "首屏加载<2秒"], color: colors.blue },
  { title: "安全性测试", items: ["Token身份鉴权", "密码加密存储", "接口权限控制"], color: colors.success },
  { title: "兼容性测试", items: ["Chrome 120+", "Safari 17+", "响应式布局"], color: colors.skyBlue },
  { title: "易用性测试", items: ["界面简洁直观", "操作逻辑清晰", "错误提示友好"], color: colors.navy }
];

nfCategories.forEach((cat, idx) => {
  const xPos = 0.6 + idx * 2.35;

  slide8.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.15, w: 2.2, h: 3.8, fill: { color: colors.white }, shadow: cardShadow()
  });

  slide8.addShape(pres.shapes.RECTANGLE, {
    x: xPos, y: 1.15, w: 2.2, h: 0.08, fill: { color: cat.color }
  });

  slide8.addText(cat.title, {
    x: xPos + 0.1, y: 1.4, w: 2.0, h: 0.45,
    fontSize: 14, fontFace: "Arial", color: colors.navy, bold: true, align: "center"
  });

  cat.items.forEach((item, i) => {
    slide8.addText("✓ " + item, {
      x: xPos + 0.15, y: 2.0 + i * 0.7, w: 1.9, h: 0.5,
      fontSize: 10, fontFace: "Arial", color: colors.slate
    });
  });
});

// ============ Slide 9: Performance Details ============
let slide9 = pres.addSlide();
slide9.background = { color: colors.white };

slide9.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide9.addText("05.3.1  性能测试详情", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const perfMetrics = [
  { metric: "AI问答平均响应时间", target: "<8秒", actual: "5.2秒", status: "✓" },
  { metric: "复杂查询最大响应时间", target: "<15秒", actual: "12.8秒", status: "✓" },
  { metric: "首页首屏加载时间", target: "<2秒", actual: "1.3秒", status: "✓" },
  { metric: "知识库加载时间", target: "<5秒", actual: "3.2秒", status: "✓" },
  { metric: "非AI接口响应时间", target: "<500ms", actual: "120ms", status: "✓" }
];

slide9.addTable([
  [
    { text: "测试指标", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "目标值", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "实际值", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } },
    { text: "结果", options: { fill: { color: colors.navy }, color: "FFFFFF", bold: true, align: "center" } }
  ],
  ...perfMetrics.map(m => [
    { text: m.metric, options: { align: "left" } },
    { text: m.target, options: { align: "center" } },
    { text: m.actual, options: { align: "center", bold: true, color: colors.blue } },
    { text: m.status, options: { align: "center", color: colors.success, bold: true } }
  ])
], {
  x: 0.6, y: 1.2, w: 8.8, h: 2.8,
  fontFace: "Arial", fontSize: 11,
  border: { pt: 0.5, color: "E2E8F0" },
  colW: [3.5, 1.8, 1.8, 1.7]
});

// Conclusion
slide9.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.3, w: 8.8, h: 0.9, fill: { color: colors.paleBlue }
});

slide9.addText("结论：所有性能指标均达标，系统响应流畅，用户体验良好", {
  x: 0.8, y: 4.55, w: 8.4, h: 0.4,
  fontSize: 13, fontFace: "Arial", color: colors.navy, align: "center"
});

// ============ Slide 10: Summary ============
let slide10 = pres.addSlide();
slide10.background = { color: colors.white };

slide10.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08, fill: { color: colors.navy }
});

slide10.addText("05.4  测试总结", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Arial", color: colors.navy, bold: true
});

const summaryItems = [
  { title: "功能测试", result: "全部通过", detail: "RAG/记忆/多智能体三大模块均达目标阈值" },
  { title: "对比实验", result: "效果显著", detail: "三者协同带来显著性能提升" },
  { title: "非功能性", result: "符合要求", detail: "性能/安全/兼容/易用性均达标" }
];

summaryItems.forEach((item, idx) => {
  const yPos = 1.2 + idx * 1.35;

  slide10.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 8.8, h: 1.15, fill: { color: colors.white }, shadow: cardShadow()
  });

  slide10.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: yPos, w: 0.1, h: 1.15, fill: { color: colors.success }
  });

  slide10.addText(item.title, {
    x: 0.9, y: yPos + 0.15, w: 2, h: 0.4,
    fontSize: 16, fontFace: "Arial", color: colors.navy, bold: true
  });

  slide10.addText(item.result, {
    x: 2.9, y: yPos + 0.15, w: 2, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: colors.success, bold: true
  });

  slide10.addText(item.detail, {
    x: 0.9, y: yPos + 0.6, w: 8.2, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: colors.slate
  });
});

// Final metrics
slide10.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.4, w: 8.8, h: 0.9, fill: { color: colors.navy }
});

slide10.addText("核心指标: Precision@5=0.84  |  个性化准确率=0.87  |  任务完成率=0.93", {
  x: 0.6, y: 4.6, w: 8.8, h: 0.5,
  fontSize: 14, fontFace: "Arial", color: colors.white, align: "center", bold: true
});

// Save
pres.writeFile({ fileName: "/Users/liubingyan/Sports-Training-Agent/docs/系统测试PPT.pptx" })
  .then(() => console.log("Testing PPT created successfully!"))
  .catch(err => console.error("Error:", err));
