const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.title = '研究问题与技术方案对应关系';
pres.author = '刘冰彦';

// 颜色定义
const colors = {
  problem1: "2E86AB",      // 蓝色 - 知识问题
  problem2: "28A745",      // 绿色 - 记忆问题
  problem3: "E85D04",      // 橙色 - 多智能体问题
  challenge: "6C757D",     // 灰色 - 挑战
  solution: "343A40",     // 深灰 - 解决方案
  white: "FFFFFF",
  lightBg: "F8F9FA",
  darkText: "212529"
};

let slide = pres.addSlide();
slide.background = { color: colors.lightBg };

// 标题
slide.addText("研究问题与技术方案对应关系", {
  x: 0.5, y: 0.2, w: 9, h: 0.7,
  fontSize: 32, fontFace: "Arial", bold: true, color: colors.darkText, align: "center"
});

// ========== 第一列：问题一 ==========
const col1X = 0.3;
const colWidth = 3.1;
const startY = 1.1;

// 问题一卡片
slide.addShape(pres.shapes.RECTANGLE, {
  x: col1X, y: startY, w: colWidth, h: 0.7,
  fill: { color: colors.problem1 },
  shadow: { type: "outer", color: "000000", blur: 4, offset: 2, angle: 135, opacity: 0.15 }
});
slide.addText("问题一", {
  x: col1X, y: startY, w: colWidth, h: 0.35,
  fontSize: 14, fontFace: "Arial", bold: true, color: colors.white, align: "center", valign: "middle"
});
slide.addText("训练指导缺乏科学依据\n与权威支撑", {
  x: col1X, y: startY + 0.35, w: colWidth, h: 0.35,
  fontSize: 11, fontFace: "Arial", color: colors.white, align: "center", valign: "middle"
});

// 挑战一卡片
slide.addShape(pres.shapes.RECTANGLE, {
  x: col1X, y: startY + 0.85, w: colWidth, h: 1.5,
  fill: { color: colors.white },
  line: { color: colors.challenge, width: 1 }
});
slide.addText("挑战", {
  x: col1X, y: startY + 0.9, w: colWidth, h: 0.3,
  fontSize: 10, fontFace: "Arial", bold: true, color: colors.challenge, align: "center"
});
slide.addText([
  { text: "• 用户口语化与专业文档语义鸿沟", options: { breakLine: true, fontSize: 9 } },
  { text: "• 单次检索覆盖不足", options: { breakLine: true, fontSize: 9 } },
  { text: "• 生成幻觉问题", options: { fontSize: 9 } }
], {
  x: col1X + 0.15, y: startY + 1.2, w: colWidth - 0.3, h: 1.0,
  fontFace: "Arial", color: colors.darkText, valign: "top"
});

// 箭头
slide.addText("↓", {
  x: col1X, y: startY + 2.45, w: colWidth, h: 0.3,
  fontSize: 18, color: colors.problem1, align: "center"
});

// 解决方案一卡片
slide.addShape(pres.shapes.RECTANGLE, {
  x: col1X, y: startY + 2.75, w: colWidth, h: 1.6,
  fill: { color: colors.problem1 }
});
slide.addText("解决方案", {
  x: col1X, y: startY + 2.8, w: colWidth, h: 0.3,
  fontSize: 10, fontFace: "Arial", bold: true, color: colors.white, align: "center"
});
slide.addText("ST-RAG", {
  x: col1X, y: startY + 3.1, w: colWidth, h: 0.3,
  fontSize: 12, fontFace: "Arial", bold: true, color: colors.white, align: "center"
});
slide.addText("HyDE + MQE\n约束感知检索\n引用约束与后校验", {
  x: col1X + 0.1, y: startY + 3.4, w: colWidth - 0.2, h: 0.9,
  fontSize: 9, fontFace: "Arial", color: colors.white, align: "center"
});

// ========== 第二列：问题二 ==========
const col2X = col1X + colWidth + 0.2;

// 问题二卡片
slide.addShape(pres.shapes.RECTANGLE, {
  x: col2X, y: startY, w: colWidth, h: 0.7,
  fill: { color: colors.problem2 },
  shadow: { type: "outer", color: "000000", blur: 4, offset: 2, angle: 135, opacity: 0.15 }
});
slide.addText("问题二", {
  x: col2X, y: startY, w: colWidth, h: 0.35,
  fontSize: 14, fontFace: "Arial", bold: true, color: colors.white, align: "center", valign: "middle"
});
slide.addText("缺乏长期用户信息记忆\n难以实现个性化", {
  x: col2X, y: startY + 0.35, w: colWidth, h: 0.35,
  fontSize: 11, fontFace: "Arial", color: colors.white, align: "center", valign: "middle"
});

// 挑战二卡片
slide.addShape(pres.shapes.RECTANGLE, {
  x: col2X, y: startY + 0.85, w: colWidth, h: 1.5,
  fill: { color: colors.white },
  line: { color: colors.challenge, width: 1 }
});
slide.addText("挑战", {
  x: col2X, y: startY + 0.9, w: colWidth, h: 0.3,
  fontSize: 10, fontFace: "Arial", bold: true, color: colors.challenge, align: "center"
});
slide.addText([
  { text: "• 无状态模型与长期训练过程不匹配", options: { breakLine: true, fontSize: 9 } },
  { text: "• 检索忽略用户状态", options: { breakLine: true, fontSize: 9 } },
  { text: "• 记忆无限膨胀", options: { fontSize: 9 } }
], {
  x: col2X + 0.15, y: startY + 1.2, w: colWidth - 0.3, h: 1.0,
  fontFace: "Arial", color: colors.darkText, valign: "top"
});

// 箭头
slide.addText("↓", {
  x: col2X, y: startY + 2.45, w: colWidth, h: 0.3,
  fontSize: 18, color: colors.problem2, align: "center"
});

// 解决方案二卡片
slide.addShape(pres.shapes.RECTANGLE, {
  x: col2X, y: startY + 2.75, w: colWidth, h: 1.6,
  fill: { color: colors.problem2 }
});
slide.addText("解决方案", {
  x: col2X, y: startY + 2.8, w: colWidth, h: 0.3,
  fontSize: 10, fontFace: "Arial", bold: true, color: colors.white, align: "center"
});
slide.addText("三层记忆体系", {
  x: col2X, y: startY + 3.1, w: colWidth, h: 0.3,
  fontSize: 12, fontFace: "Arial", bold: true, color: colors.white, align: "center"
});
slide.addText("工作记忆 + 情景记忆\n+ 语义记忆\n记忆感知检索 + 遗忘机制", {
  x: col2X + 0.1, y: startY + 3.4, w: colWidth - 0.2, h: 0.9,
  fontSize: 9, fontFace: "Arial", color: colors.white, align: "center"
});

// ========== 第三列：问题三 ==========
const col3X = col2X + colWidth + 0.2;

// 问题三卡片
slide.addShape(pres.shapes.RECTANGLE, {
  x: col3X, y: startY, w: colWidth, h: 0.7,
  fill: { color: colors.problem3 },
  shadow: { type: "outer", color: "000000", blur: 4, offset: 2, angle: 135, opacity: 0.15 }
});
slide.addText("问题三", {
  x: col3X, y: startY, w: colWidth, h: 0.35,
  fontSize: 14, fontFace: "Arial", bold: true, color: colors.white, align: "center", valign: "middle"
});
slide.addText("单一模型难以覆盖\n多角色专业指导", {
  x: col3X, y: startY + 0.35, w: colWidth, h: 0.35,
  fontSize: 11, fontFace: "Arial", color: colors.white, align: "center", valign: "middle"
});

// 挑战三卡片
slide.addShape(pres.shapes.RECTANGLE, {
  x: col3X, y: startY + 0.85, w: colWidth, h: 1.5,
  fill: { color: colors.white },
  line: { color: colors.challenge, width: 1 }
});
slide.addText("挑战", {
  x: col3X, y: startY + 0.9, w: colWidth, h: 0.3,
  fontSize: 10, fontFace: "Arial", bold: true, color: colors.challenge, align: "center"
});
slide.addText([
  { text: "• 训练规划/技术指导/康复角色知识结构差异", options: { breakLine: true, fontSize: 9 } },
  { text: "• 复杂问题建议片面化", options: { breakLine: true, fontSize: 9 } },
  { text: "• 风险遗漏", options: { fontSize: 9 } }
], {
  x: col3X + 0.15, y: startY + 1.2, w: colWidth - 0.3, h: 1.0,
  fontFace: "Arial", color: colors.darkText, valign: "top"
});

// 箭头
slide.addText("↓", {
  x: col3X, y: startY + 2.45, w: colWidth, h: 0.3,
  fontSize: 18, color: colors.problem3, align: "center"
});

// 解决方案三卡片
slide.addShape(pres.shapes.RECTANGLE, {
  x: col3X, y: startY + 2.75, w: colWidth, h: 1.6,
  fill: { color: colors.problem3 }
});
slide.addText("解决方案", {
  x: col3X, y: startY + 2.8, w: colWidth, h: 0.3,
  fontSize: 10, fontFace: "Arial", bold: true, color: colors.white, align: "center"
});
slide.addText("多智能体协同", {
  x: col3X, y: startY + 3.1, w: colWidth, h: 0.3,
  fontSize: 12, fontFace: "Arial", bold: true, color: colors.white, align: "center"
});
slide.addText("规划/技术/康复教练\nLangGraph状态图\n意图识别与调度", {
  x: col3X + 0.1, y: startY + 3.4, w: colWidth - 0.2, h: 0.9,
  fontSize: 9, fontFace: "Arial", color: colors.white, align: "center"
});

// 底部说明
slide.addText("知识失配                    状态失配                    角色失配", {
  x: 0.5, y: 5.1, w: 9, h: 0.3,
  fontSize: 10, fontFace: "Arial", color: colors.challenge, align: "center"
});

pres.writeFile({ fileName: "docs/研究问题与技术方案对应关系.pptx" })
  .then(() => console.log("PPT created successfully!"))
  .catch(err => console.error(err));
