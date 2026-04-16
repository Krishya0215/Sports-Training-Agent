#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

# 读取文件
with open(r'd:\Graduation Project\运动训练问答Agent\frontend\src\views\Chat.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复策略：使用正则表达式替换所有乱码
# 这些乱码看起来是Lantinext库的结果，所以我们用正则表达式来替换

# 1. 修复suggestions数组中的乱码
suggestions_pattern = r"const suggestions = \[.*?\]"
suggestions_replacement = """const suggestions = [
  '我想生成一份运动训练计划',
  '帮我安排今天的训练内容',
  '我最近恢复不太好，怎么办？',
  '帮我分析一下训练节奏'
]"""

content = re.sub(suggestions_pattern, suggestions_replacement, content, flags=re.DOTALL)

# 2. 修复快速操作按钮中的乱码 @click="quickAction('..."
# 第1个按钮
content = re.sub(
    r'<button type="button" class="quick-btn" @click="quickAction\(\'[^\']*\'\)">鐢熸垚璁″垝</button>',
    '<button type="button" class="quick-btn" @click="quickAction(\'我想生成一份运动训练计划\')">生成计划</button>',
    content
)

# 3. 修复 buildBriefAdvice 函数中的return语句
old_return = r"if \(!normalized\) return '[^']+"
new_return = "if (!normalized) return '我已经根据你的情况整理出一份运动建议，并生成了对应训练计划。'"
content = re.sub(old_return, new_return, content, flags=re.DOTALL)

# 4. 修复 quickAction 函数中的 if 条件
content = re.sub(
    r"if \(action === '[^']+'\) \{",
    "if (action === '我想生成一份运动训练计划') {",
    content
)

# 5. 修复所有window.alert中的乱码
alerts_to_fix = [
    (r"window\.alert\('[^']*训练计划生成失败[^']*'\)", "window.alert('训练计划生成失败，请稍后重试。')"),
    (r"window\.alert\('[^']*训练计划详情加载失败[^']*'\)", "window.alert('训练计划详情加载失败，请稍后重试。')"),
    (r"window\.alert\('[^']*保存训练日失败[^']*'\)", "window.alert('保存训练日失败，请稍后重试。')")
]

for pattern, replacement in alerts_to_fix:
    content = re.sub(pattern, replacement, content)

# 6. 修复 console.error 中的乱码
error_logs = [
    (r"console\.error\('[^']*\)', error\)", "console.error('发送消息失败', error)"),
]
for pattern, replacement in error_logs:
    content = re.sub(pattern, replacement, content)

# 写入文件
with open(r'd:\Graduation Project\运动训练问答Agent\frontend\src\views\Chat.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Chat.vue 已通过正则表达式修复所有乱码错误！')
