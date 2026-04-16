#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

# 读取文件
with open(r'd:\Graduation Project\运动训练问答Agent\frontend\src\views\Chat.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复1: suggestions 数组
old_suggestions = """const suggestions = [
  '鎴戞兂鐢熸垚涓€浠借缁冭鍒?,
  '甯垜瀹夋帓浠婂ぉ鐨勮缁冨唴瀹?,
  '鎴戞渶杩戞仮澶嶄笉澶ソ锛屾€庝箞鍔烇紵',
  '甯垜鍒嗘瀽涓€涓嬭缁冭妭濂?
]"""

new_suggestions = """const suggestions = [
  '我想生成一份运动训练计划',
  '帮我安排今天的训练内容',
  '我最近恢复不太好，怎么办？',
  '帮我分析一下训练节奏'
]"""

content = content.replace(old_suggestions, new_suggestions)

# 修复2: extractAnswer 函数
old_extract = "const extractAnswer = (response) => response?.answer || response?.content || response?.response || '鎴戝凡缁忔敹鍒颁綘鐨勯棶棰橈紝浣嗘殏鏃舵病鏈夌敓鎴愭湁鏁堝洖澶嶃€?"
new_extract = "const extractAnswer = (response) => response?.answer || response?.content || response?.response || '我已经收到你的问题，但暂时没有生成有效回复。'"

content = content.replace(old_extract, new_extract)

# 修复3: buildBriefAdvice 的第一个返回
old_brief1 = "if (!normalized) return '鎴戝凡缁忔牴鎹綘鐨勬儏鍐垫暣鐞嗗嚭涓€浠借缁冨缓璁紝骞剁敓鎴愪簡瀵瑰簲璁粌璁″垝銆?"
new_brief1 = "if (!normalized) return '我已经根据你的情况整理出一份运动建议，并生成了对应训练计划。'"

content = content.replace(old_brief1, new_brief1)

# 修复4: sendMessage 的 catch 块 alert
old_alert1 = "window.alert('娑堟伅鍙戦€佸け璐ワ紝璇风◢鍚庨噸璇曘€?"
new_alert1 = "window.alert('消息发送失败，请稍后重试。'"

content = content.replace(old_alert1, new_alert1)

# 修复5: generatePlan 的 alert
old_alert2 = "window.alert('璁粌璁″垝鐢熸垚澶辫触锛岃绋嶅悗閲嶈瘯銆?"
new_alert2 = "window.alert('训练计划生成失败，请稍后重试。'"

content = content.replace(old_alert2, new_alert2)

# 修复6: viewPlanDetails 的 alert
old_alert3 = "window.alert('璁粌璁″垝璇︽儏鍔犺浇澶辫触锛岃绋嶅悗閲嶈瘯銆?"
new_alert3 = "window.alert('训练计划详情加载失败，请稍后重试。'"

content = content.replace(old_alert3, new_alert3)

# 修复7: savePreviewWeekdays 的 alert
old_alert4 = "window.alert('淇濆瓨璁粌鏃ュけ璐ワ紝璇风◢鍚庨噸璇曘€?"
new_alert4 = "window.alert('保存训练日失败，请稍后重试。'"

content = content.replace(old_alert4, new_alert4)

# 修复8: quickAction 中的 if 条件
old_condition = "if (action === '鎴戞兂鐢熸垚涓€浠借缁冭鍒?')"
new_condition = "if (action === '我想生成一份运动训练计划')"

content = content.replace(old_condition, new_condition)

# 写入文件
with open(r'd:\Graduation Project\运动训练问答Agent\frontend\src\views\Chat.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Chat.vue 已成功修复所有错误！')
