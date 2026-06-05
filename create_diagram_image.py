import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm
import os

# 查找中文字体
def find_chinese_font():
    font_paths = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Helvetica.ttc',
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return fp
    return None

chinese_font = find_chinese_font()
if chinese_font:
    prop = fm.FontProperties(fname=chinese_font)
    plt.rcParams['font.family'] = ['PingFang SC', 'Heiti SC', 'sans-serif']
else:
    prop = None

# 创建画布
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis('off')

# 颜色定义
colors = {
    'problem1': '#2E86AB',  # 蓝色
    'problem2': '#28A745',  # 绿色
    'problem3': '#E85D04',  # 橙色
}

# 列位置
col_positions = [1, 5, 9]
col_width = 3.5
start_y = 6.5

# 数据
data = [
    (col_positions[0], colors['problem1'], '问题一',
     '训练指导缺乏科学依据\n与权威支撑',
     ['用户口语化与专业文档\n语义鸿沟', '单次检索覆盖不足', '生成幻觉问题'],
     ['ST-RAG', 'HyDE + MQE', '约束感知检索', '引用约束与后校验']),
    (col_positions[1], colors['problem2'], '问题二',
     '缺乏长期用户信息记忆\n难以实现个性化',
     ['无状态模型与长期\n训练过程不匹配', '检索忽略用户状态', '记忆无限膨胀'],
     ['三层记忆体系', '工作记忆 + 情景记忆\n+ 语义记忆', '记忆感知检索', '遗忘机制']),
    (col_positions[2], colors['problem3'], '问题三',
     '单一模型难以覆盖\n多角色专业指导',
     ['训练规划/技术指导/\n康复角色知识结构差异', '复杂问题建议片面化', '风险遗漏'],
     ['多智能体协同', '规划/技术/康复教练', 'LangGraph状态图', '意图识别与调度'])
]

# 绘制三列
for i, (x, color, title, problem_text, challenges, solutions) in enumerate(data):
    # 问题卡片
    problem_box = FancyBboxPatch((x, start_y), col_width, 0.9,
                                   boxstyle="round,pad=0.05,rounding_size=0.1",
                                   facecolor=color, edgecolor='none', alpha=0.9)
    ax.add_patch(problem_box)
    ax.text(x + col_width/2, start_y + 0.65, title, ha='center', va='center',
            fontsize=12, fontweight='bold', color='white', fontproperties=prop)
    ax.text(x + col_width/2, start_y + 0.25, problem_text, ha='center', va='center',
            fontsize=9, color='white', linespacing=1.3, fontproperties=prop)

    # 挑战卡片
    challenge_y = start_y - 1.1
    challenge_box = FancyBboxPatch((x, challenge_y - 1.4), col_width, 1.5,
                                    boxstyle="round,pad=0.02,rounding_size=0.1",
                                    facecolor='white', edgecolor=color, linewidth=2)
    ax.add_patch(challenge_box)
    ax.text(x + col_width/2, challenge_y - 0.1, '挑战', ha='center', va='center',
            fontsize=10, fontweight='bold', color=color, fontproperties=prop)

    for j, ch in enumerate(challenges):
        ax.text(x + 0.15, challenge_y - 0.4 - j*0.35, ch, ha='left', va='center',
                fontsize=8, color='#212529', fontproperties=prop)

    # 箭头
    ax.annotate('', xy=(x + col_width/2, challenge_y - 1.5), xytext=(x + col_width/2, challenge_y - 1.55),
                arrowprops=dict(arrowstyle='->', color=color, lw=2))

    # 解决方案卡片
    solution_y = challenge_y - 1.7
    solution_box = FancyBboxPatch((x, solution_y - 1.3), col_width, 1.4,
                                   boxstyle="round,pad=0.05,rounding_size=0.1",
                                   facecolor=color, edgecolor='none')
    ax.add_patch(solution_box)
    ax.text(x + col_width/2, solution_y - 0.1, '解决方案', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white', fontproperties=prop)

    for j, sol in enumerate(solutions):
        ax.text(x + col_width/2, solution_y - 0.45 - j*0.3, sol, ha='center', va='center',
                fontsize=8, color='white', fontproperties=prop)

# 标题
ax.text(7, 7.8, '研究问题与技术方案对应关系', ha='center', va='center',
        fontsize=20, fontweight='bold', color='#212529', fontproperties=prop)

# 底部标注
ax.text(3.5, 0.5, '知识失配', ha='center', va='center', fontsize=10, color='#6C757D', fontproperties=prop)
ax.text(7, 0.5, '状态失配', ha='center', va='center', fontsize=10, color='#6C757D', fontproperties=prop)
ax.text(10.5, 0.5, '角色失配', ha='center', va='center', fontsize=10, color='#6C757D', fontproperties=prop)

plt.tight_layout()
plt.savefig('docs/研究问题与技术方案对应关系.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("图片已生成: docs/研究问题与技术方案对应关系.png")
