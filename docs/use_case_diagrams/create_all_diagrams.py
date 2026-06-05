import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Ellipse
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['Songti SC', 'STHeiti', 'PingFang HK', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def draw_actor(ax, x, y, label, scale=1.0):
    head_r = 0.12 * scale
    ax.add_patch(plt.Circle((x, y + 0.35 * scale), head_r, fill=False, edgecolor='black', linewidth=1.5))
    ax.plot([x, x], [y + 0.35 * scale - head_r, y + 0.05 * scale], color='black', linewidth=1.5)
    ax.plot([x - 0.15 * scale, x + 0.15 * scale], [y + 0.22 * scale, y + 0.22 * scale], color='black', linewidth=1.5)
    ax.plot([x, x - 0.12 * scale], [y + 0.05 * scale, y - 0.15 * scale], color='black', linewidth=1.5)
    ax.plot([x, x + 0.12 * scale], [y + 0.05 * scale, y - 0.15 * scale], color='black', linewidth=1.5)
    ax.text(x, y - 0.28 * scale, label, ha='center', va='top', fontsize=10, fontweight='bold')

def draw_usecase(ax, x, y, label, w=1.6, h=0.45):
    ellipse = Ellipse((x, y), w, h, fill=True, facecolor='#E8F4FD', edgecolor='#2E75B6', linewidth=1.5)
    ax.add_patch(ellipse)
    fontsize = 9 if len(label) > 10 else 10
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize, color='#1a1a1a')

def draw_association(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-', color='#555555', linewidth=1.2))

def draw_include(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#555555', linewidth=1.0, linestyle='dashed'))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx, my + 0.08, '<<include>>', ha='center', va='bottom', fontsize=7, style='italic', color='#555555')

def draw_extend(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#888888', linewidth=1.0, linestyle='dashed'))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx, my + 0.08, '<<extend>>', ha='center', va='bottom', fontsize=7, style='italic', color='#888888')

def draw_system_boundary(ax, x, y, w, h, title):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                          fill=False, edgecolor='#2E75B6', linewidth=1.5, linestyle='-')
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h - 0.08, title, ha='center', va='top', fontsize=11, fontweight='bold', color='#2E75B6')


# ============================
# 1. User Information Management
# ============================
def create_diagram_1():
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))
    ax.set_xlim(-1.5, 7)
    ax.set_ylim(-0.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('用户信息管理用例图', fontsize=14, fontweight='bold', pad=15)

    draw_system_boundary(ax, 1.5, 0.2, 4.5, 5.0, '用户信息管理子系统')

    draw_actor(ax, 0.3, 3.0, '用户')

    usecases = [
        (3.75, 4.5, '用户注册'),
        (3.75, 3.7, '用户登录'),
        (3.75, 2.9, '找回密码'),
        (3.75, 2.1, '查看个人资料'),
        (3.75, 1.3, '编辑个人资料'),
    ]

    for ux, uy, ulabel in usecases:
        draw_usecase(ax, ux, uy, ulabel)

    for ux, uy, _ in usecases:
        draw_association(ax, 0.55, 3.2, ux - 0.8, uy)

    draw_include(ax, 3.75, 1.3, 3.75, 2.1)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'usecase_1_user_info.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Diagram 1 saved.")


# ============================
# 2. AI Coach Q&A
# ============================
def create_diagram_2():
    fig, ax = plt.subplots(1, 1, figsize=(9, 7))
    ax.set_xlim(-1.5, 8.5)
    ax.set_ylim(-0.5, 7.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('AI教练问答用例图', fontsize=14, fontweight='bold', pad=15)

    draw_system_boundary(ax, 1.5, 0.2, 5.5, 7.0, 'AI教练问答子系统')

    draw_actor(ax, 0.2, 4.0, '用户')

    usecases = [
        (4.25, 6.5, '提出训练问题'),
        (4.25, 5.5, '选择问答模式'),
        (4.25, 4.5, '单智能体问答'),
        (4.25, 3.5, '多智能体协同问答'),
        (4.25, 2.5, '查看引用来源'),
        (4.25, 1.5, '查看对话历史'),
        (4.25, 0.7, '意图识别与路由'),
    ]

    for ux, uy, ulabel in usecases:
        draw_usecase(ax, ux, uy, ulabel)

    user_connected = [0, 1, 4, 5]
    for idx in user_connected:
        ux, uy, _ = usecases[idx]
        draw_association(ax, 0.5, 4.2, ux - 0.8, uy)

    draw_include(ax, 4.25, 5.5, 4.25, 4.5)
    draw_extend(ax, 4.25, 5.5, 4.25, 3.5)
    draw_include(ax, 4.25, 3.5, 4.25, 0.7)
    draw_include(ax, 4.25, 6.5, 4.25, 5.5)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'usecase_2_ai_coach.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Diagram 2 saved.")


# ============================
# 3. Training Plan
# ============================
def create_diagram_3():
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))
    ax.set_xlim(-1.5, 7)
    ax.set_ylim(-0.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('训练计划管理用例图', fontsize=14, fontweight='bold', pad=15)

    draw_system_boundary(ax, 1.5, 0.2, 4.5, 5.0, '训练计划管理子系统')

    draw_actor(ax, 0.3, 3.0, '用户')

    usecases = [
        (3.75, 4.5, '生成训练计划'),
        (3.75, 3.7, '查看训练计划'),
        (3.75, 2.9, '修改训练计划'),
        (3.75, 2.1, '归档训练计划'),
        (3.75, 1.3, '读取用户画像'),
    ]

    for ux, uy, ulabel in usecases:
        draw_usecase(ax, ux, uy, ulabel)

    user_connected = [0, 1, 2, 3]
    for idx in user_connected:
        ux, uy, _ = usecases[idx]
        draw_association(ax, 0.55, 3.2, ux - 0.8, uy)

    draw_include(ax, 3.75, 4.5, 3.75, 1.3)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'usecase_3_training_plan.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Diagram 3 saved.")


# ============================
# 4. Health Record
# ============================
def create_diagram_4():
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))
    ax.set_xlim(-1.5, 7)
    ax.set_ylim(-0.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('健康记录管理用例图', fontsize=14, fontweight='bold', pad=15)

    draw_system_boundary(ax, 1.5, 0.2, 4.5, 5.0, '健康记录管理子系统')

    draw_actor(ax, 0.3, 3.0, '用户')

    usecases = [
        (3.75, 4.5, '记录训练表现'),
        (3.75, 3.7, '记录每日饮食'),
        (3.75, 2.9, '记录体重数据'),
        (3.75, 2.1, '查看健康趋势'),
        (3.75, 1.3, '写入情景记忆'),
    ]

    for ux, uy, ulabel in usecases:
        draw_usecase(ax, ux, uy, ulabel)

    user_connected = [0, 1, 2, 3]
    for idx in user_connected:
        ux, uy, _ = usecases[idx]
        draw_association(ax, 0.55, 3.2, ux - 0.8, uy)

    draw_include(ax, 3.75, 4.5, 3.75, 1.3)
    draw_include(ax, 3.75, 3.7, 3.75, 1.3)
    draw_include(ax, 3.75, 2.9, 3.75, 1.3)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'usecase_4_health_record.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Diagram 4 saved.")


# ============================
# 5. Knowledge Base Management
# ============================
def create_diagram_5():
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))
    ax.set_xlim(-1.5, 7)
    ax.set_ylim(-0.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('知识库管理用例图', fontsize=14, fontweight='bold', pad=15)

    draw_system_boundary(ax, 1.5, 0.2, 4.5, 5.0, '知识库管理子系统')

    draw_actor(ax, 0.3, 3.0, '管理员')

    usecases = [
        (3.75, 4.5, '上传训练文档'),
        (3.75, 3.7, '预览文档内容'),
        (3.75, 2.9, '删除知识文档'),
        (3.75, 2.1, '文档解析与切分'),
        (3.75, 1.3, '向量化与入库'),
    ]

    for ux, uy, ulabel in usecases:
        draw_usecase(ax, ux, uy, ulabel)

    user_connected = [0, 1, 2]
    for idx in user_connected:
        ux, uy, _ = usecases[idx]
        draw_association(ax, 0.55, 3.2, ux - 0.8, uy)

    draw_include(ax, 3.75, 4.5, 3.75, 2.1)
    draw_include(ax, 3.75, 2.1, 3.75, 1.3)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'usecase_5_knowledge_base.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Diagram 5 saved.")


# ============================
# 6. Memory Management
# ============================
def create_diagram_6():
    fig, ax = plt.subplots(1, 1, figsize=(9, 7))
    ax.set_xlim(-1.5, 8)
    ax.set_ylim(-0.5, 7.0)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('记忆管理用例图', fontsize=14, fontweight='bold', pad=15)

    draw_system_boundary(ax, 1.5, 0.2, 5.5, 6.5, '记忆管理子系统')

    draw_actor(ax, 0.2, 3.8, '系统')

    usecases = [
        (4.25, 6.0, '维护工作记忆'),
        (4.25, 5.1, '记录情景记忆'),
        (4.25, 4.2, '提取语义记忆'),
        (4.25, 3.3, '重要性评分'),
        (4.25, 2.4, '记忆遗忘与衰减'),
        (4.25, 1.5, '记忆感知检索'),
        (4.25, 0.7, '跨会话状态追踪'),
    ]

    for ux, uy, ulabel in usecases:
        draw_usecase(ax, ux, uy, ulabel)

    for idx in range(len(usecases)):
        ux, uy, _ = usecases[idx]
        draw_association(ax, 0.5, 4.0, ux - 0.8, uy)

    draw_include(ax, 4.25, 5.1, 4.25, 3.3)
    draw_include(ax, 4.25, 4.2, 4.25, 3.3)
    draw_include(ax, 4.25, 1.5, 4.25, 0.7)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'usecase_6_memory_mgmt.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Diagram 6 saved.")


if __name__ == '__main__':
    create_diagram_1()
    create_diagram_2()
    create_diagram_3()
    create_diagram_4()
    create_diagram_5()
    create_diagram_6()
    print("All diagrams created successfully!")
