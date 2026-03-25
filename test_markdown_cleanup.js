// 复制改进后的removeMarkdownFormat函数
const removeMarkdownFormat = (text = '') => {
  if (!text || typeof text !== 'string') return text

  // 处理HTML实体
  let cleaned = text
    .replace(/&middot;|&bull;|&sdot;/g, '') // HTML项目符号
    .replace(/&nbsp;/g, ' ')              // 非换行空格
    .replace(/&[a-z]+;/g, '')             // 其他简单HTML实体

  // 处理Markdown表格：移除表格分隔符和表头分隔线，将表格转换为更易读的格式
  const lines = cleaned.split('\n')
  const processedLines = []
  let inTable = false
  let tableHeaders = []
  let tableRows = []

  for (let line of lines) {
    // 检测表格行：包含 | 且不是代码块
    if (line.includes('|') && !line.startsWith('    ') && !line.startsWith('\t')) {
      const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell !== '')

      // 检测表头分隔线（只包含 - 和 |）
      const isHeaderSeparator = /^[\s|]*[-:| ]+[\s|]*$/.test(line)

      if (!inTable) {
        inTable = true
        tableHeaders = cells
        tableRows = []
      } else if (isHeaderSeparator) {
        // 跳过表头分隔线
        continue
      } else {
        tableRows.push(cells)
      }

      // 如果这一行处理完了，继续下一行
      continue
    } else if (inTable) {
      // 表格结束，将表格转换为更易读的格式
      if (tableRows.length > 0) {
        // 简单格式：每行作为文本
        for (let row of tableRows) {
          let rowText = ''
          for (let i = 0; i < Math.min(tableHeaders.length, row.length); i++) {
            rowText += `${tableHeaders[i]}: ${row[i]}  `
          }
          processedLines.push(rowText.trim())
        }
      }
      inTable = false
      tableHeaders = []
      tableRows = []
    }

    // 非表格行，直接添加
    if (!inTable) {
      processedLines.push(line)
    }
  }

  // 处理最后可能剩余的表格
  if (inTable && tableRows.length > 0) {
    for (let row of tableRows) {
      let rowText = ''
      for (let i = 0; i < Math.min(tableHeaders.length, row.length); i++) {
        rowText += `${tableHeaders[i]}: ${row[i]}  `
      }
      processedLines.push(rowText.trim())
    }
  }

  cleaned = processedLines.join('\n')

  // 移除常见的Markdown格式符号
  cleaned = cleaned
    .replace(/\*\*(.*?)\*\*/g, '$1')      // 粗体 **text**
    .replace(/\*(.*?)\*/g, '$1')          // 斜体 *text*
    .replace(/__(.*?)__/g, '$1')          // 粗体 __text__
    .replace(/_(.*?)_/g, '$1')            // 斜体 _text_
    .replace(/~~(.*?)~~/g, '$1')          // 删除线 ~~text~~
    .replace(/`(.*?)`/g, '$1')            // 行内代码 `text`
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')   // 链接 [text](url)
    .replace(/^#+\s*/gm, '')              // 标题 # text
    .replace(/^-\s*/gm, '')               // 无序列表 - text
    .replace(/^\d+\.\s*/gm, '')           // 有序列表 1. text
    .replace(/^\s*[-*+]\s*/gm, '')        // 各种列表符号
    .replace(/^>\s*/gm, '')               // 引用块 > text
    .replace(/<br\s*\/?>/g, '\n')         // HTML换行 <br> 替换为换行
    .replace(/[-=*_]{3,}/g, '')           // 分隔线 --- === *** ___
    // 清理常见的Unicode符号（复选框、警告、项目符号等）
    .replace(/[✅❌⚠️🔹🗓️🌟📌💡🌿🛑📊🎯🌱💪😊📄📝🔍💬📋🎯🏥💡🚫✨🌞💦🏃‍♀️🏃‍♂️🧘‍♀️🧘‍♂️]/gu, '')
    .replace(/[▪•·∙◦●○◆◇■□▢▣▲△▶▷▼▽➤➢➔→]/g, '') // 各种项目符号
    .replace(/[·•]/g, '')                 // 中文常用的项目符号
    .replace(/[ 　]/g, ' ')               // 全角空格和中文空格
    .replace(/\|\s*/g, ' ')               // 表格分隔符 | 替换为空格（处理残留的）
    .replace(/\s*\|\s*/g, ' ')            // 表格分隔符 | 替换为空格（带空格的）
    .replace(/\n{3,}/g, '\n\n')           // 多个换行符减少为两个
    .replace(/\s{2,}/g, ' ')              // 多个空格合并为一个
    .replace(/^\s+|\s+$/g, '')            // 去除首尾空格
    .trim()

  return cleaned
}

// 测试用例
const testInput = `| 训练日 | 主题 | 建议时长 | 训练重点 | 恢复建议 |
|--------|------|----------|-----------|------------|
| 第1天 | 动态热身 + 快走-慢跑交替 | 10分钟 | - 3分钟动态热身：<br> · 原地踏步 + 自然摆臂 × 1分钟（避免高抬臂）<br> · 髋部环绕 × 30秒（前后各15秒）<br> · 臀桥 × 10次（2组）<br> · 躯干旋转 × 30秒（左右各15秒）<br>- 7分钟快走与慢跑交替：<br> · 快走2分钟 → 慢跑1分钟 → 重复3轮（共6分钟）<br> · 摆臂控制：双臂自然下垂，小幅摆动，不超肩线<br>- 1分钟静态拉伸：<br> · 股四头肌拉伸（站立扶墙）<br> · 小腿拉伸（靠墙弓步） | ✔️ 训练后补水150ml<br>✔️ 用毛巾轻揉肩部周围肌肉，促进循环 |`

console.log('原始输入:')
console.log(testInput)
console.log('\n' + '='.repeat(80) + '\n')
console.log('清理后输出:')
console.log(removeMarkdownFormat(testInput))
console.log('\n' + '='.repeat(80) + '\n')

// 额外测试
const test2 = `**粗体** *斜体* ~~删除线~~ \`代码\`
# 标题1
## 标题2
- 列表1
- 列表2
1. 有序1
2. 有序2
> 引用
---
[链接](http://example.com)
✅❌⚠️🔹 符号
· 项目符号 • 另一个
&middot; HTML实体
 全角空格`
console.log('额外测试:')
console.log(removeMarkdownFormat(test2))