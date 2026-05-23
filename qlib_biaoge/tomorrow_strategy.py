#!/usr/bin/env python3
"""
彪哥战法 - 明日策略（基于中信研报）
2026年3月2日周一盘前
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_tomorrow_strategy():
    """创建明日策略图"""
    
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('#f8f9fa')
    
    # 标题
    fig.text(0.5, 0.96, '【彪哥战法】明日策略（3月2日周一）', 
             ha='center', fontsize=22, fontweight='bold', color='#2c3e50')
    fig.text(0.5, 0.93, '基于中信研报《伊朗局势后续推演》| 美伊冲突+两会窗口', 
             ha='center', fontsize=12, color='#7f8c8d')
    
    # ========== 1. 局势判断（左上）==========
    ax1 = plt.axes([0.03, 0.65, 0.45, 0.25])
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    
    ax1.text(5, 9, '地缘政治局势', ha='center', fontsize=14, fontweight='bold')
    
    # 事件框
    box1 = FancyBboxPatch((0.5, 5.5), 9, 3, boxstyle="round,pad=0.1", 
                          facecolor='#ffebee', edgecolor='#e53935', linewidth=2)
    ax1.add_patch(box1)
    ax1.text(5, 7.5, '伊朗最高领袖遇害', ha='center', fontsize=12, fontweight='bold', color='#c62828')
    ax1.text(5, 6.5, '美以发动"政权更迭"军事行动', ha='center', fontsize=11)
    
    # 基准判断
    box2 = FancyBboxPatch((0.5, 1), 9, 4, boxstyle="round,pad=0.1", 
                          facecolor='#e8f5e9', edgecolor='#43a047', linewidth=2)
    ax1.add_patch(box2)
    ax1.text(5, 4.2, '基准判断：有限冲突（约一周）', ha='center', fontsize=11, fontweight='bold', color='#2e7d32')
    ax1.text(5, 3.2, '• 无地面部队，仅空袭', ha='center', fontsize=10)
    ax1.text(5, 2.4, '• 最终谈判解决', ha='center', fontsize=10)
    ax1.text(5, 1.6, '• 完全失控为小概率', ha='center', fontsize=10)
    
    # ========== 2. 明日剧本（右上）==========
    ax2 = plt.axes([0.52, 0.65, 0.45, 0.25])
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    
    ax2.text(5, 9, '明日A股剧本推演', ha='center', fontsize=14, fontweight='bold')
    
    # 剧本1：低开高走（基准）
    box3 = FancyBboxPatch((0.5, 5.5), 4.2, 3, boxstyle="round,pad=0.1", 
                          facecolor='#e3f2fd', edgecolor='#1976d2', linewidth=2)
    ax2.add_patch(box3)
    ax2.text(2.6, 8, '剧本1：基准', ha='center', fontsize=11, fontweight='bold', color='#1565c0')
    ax2.text(2.6, 7, '低开高走', ha='center', fontsize=10)
    ax2.text(2.6, 6, '概率：60%', ha='center', fontsize=9, color='#1976d2')
    ax2.text(2.6, 5, '操作：春播信号', ha='center', fontsize=9)
    
    # 剧本2：持续弱势
    box4 = FancyBboxPatch((5.3, 5.5), 4.2, 3, boxstyle="round,pad=0.1", 
                          facecolor='#fff3e0', edgecolor='#f57c00', linewidth=2)
    ax2.add_patch(box4)
    ax2.text(7.4, 8, '剧本2：悲观', ha='center', fontsize=11, fontweight='bold', color='#e65100')
    ax2.text(7.4, 7, '低开低走', ha='center', fontsize=10)
    ax2.text(7.4, 6, '概率：25%', ha='center', fontsize=9, color='#f57c00')
    ax2.text(7.4, 5, '操作：继续冬藏', ha='center', fontsize=9)
    
    # 剧本3：高开高走（乐观）
    box5 = FancyBboxPatch((0.5, 1), 9, 4, boxstyle="round,pad=0.1", 
                          facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=2)
    ax2.add_patch(box5)
    ax2.text(5, 4.2, '剧本3：乐观（小概率）', ha='center', fontsize=11, fontweight='bold', color='#6a1b9a')
    ax2.text(5, 3.2, '周末情绪已消化，直接高开', ha='center', fontsize=10)
    ax2.text(5, 2.4, '概率：15%', ha='center', fontsize=9, color='#7b1fa2')
    ax2.text(5, 1.6, '操作：谨慎追高，确认量能', ha='center', fontsize=9)
    
    # ========== 3. 关注题材（左下）==========
    ax3 = plt.axes([0.03, 0.08, 0.45, 0.50])
    ax3.axis('off')
    
    ax3.text(0.5, 0.95, '重点关注题材', ha='center', fontsize=14, fontweight='bold', transform=ax3.transAxes)
    
    themes = [
        {'name': '军工', 'logic': '低成本无人机+智能化', 'leader': '航天彩虹', 'army': '中航沈飞', 'color': '#c62828'},
        {'name': '黄金', 'logic': '避险+冲击前高', 'leader': '山东黄金', 'army': '中金黄金', 'color': '#f9a825'},
        {'name': '油运', 'logic': '霍尔木兹风险', 'leader': '招商轮船', 'army': '中远海能', 'color': '#1565c0'},
        {'name': '化工', 'logic': '涨价+供给约束', 'leader': '万华化学', 'army': '华鲁恒升', 'color': '#2e7d32'},
        {'name': '有色', 'logic': '稀土/战略小金属', 'leader': '北方稀土', 'army': '洛阳钼业', 'color': '#6a1b9a'},
    ]
    
    y_pos = 0.82
    for theme in themes:
        box = FancyBboxPatch((0.02, y_pos-0.12), 0.96, 0.16, boxstyle="round,pad=0.02", 
                            facecolor='white', edgecolor=theme['color'], linewidth=2, alpha=0.3,
                            transform=ax3.transAxes)
        ax3.add_patch(box)
        
        ax3.text(0.05, y_pos, theme['name'], fontsize=13, fontweight='bold', 
                color=theme['color'], transform=ax3.transAxes)
        ax3.text(0.25, y_pos, theme['logic'], fontsize=10, transform=ax3.transAxes)
        ax3.text(0.55, y_pos, f"龙头:{theme['leader']}", fontsize=9, color='#c62828', transform=ax3.transAxes)
        ax3.text(0.55, y_pos-0.05, f"中军:{theme['army']}", fontsize=9, color='#1565c0', transform=ax3.transAxes)
        
        y_pos -= 0.17
    
    # ========== 4. 仓位策略（右下）==========
    ax4 = plt.axes([0.52, 0.08, 0.45, 0.50])
    ax4.axis('off')
    
    ax4.text(0.5, 0.95, '仓位管理策略', ha='center', fontsize=14, fontweight='bold', transform=ax4.transAxes)
    
    # 当前建议
    box6 = FancyBboxPatch((0.1, 0.72), 0.8, 0.18, boxstyle="round,pad=0.05", 
                          facecolor='#ffebee', edgecolor='#e53935', linewidth=3,
                          transform=ax4.transAxes)
    ax4.add_patch(box6)
    ax4.text(0.5, 0.85, '当前建议仓位', ha='center', fontsize=12, transform=ax4.transAxes, color='#666')
    ax4.text(0.5, 0.76, '20-30%', ha='center', fontsize=28, fontweight='bold', 
            color='#c62828', transform=ax4.transAxes)
    
    # 动态调整
    strategies = [
        ('若低开高走（剧本1）', '加仓至40-50%', '#4caf50'),
        ('若低开低走（剧本2）', '保持20%或减仓', '#ff9800'),
        ('若直接高开（剧本3）', '不追高等回踩', '#9c27b0'),
    ]
    
    y_pos = 0.62
    for cond, action, color in strategies:
        ax4.text(0.1, y_pos, cond, fontsize=11, fontweight='bold', transform=ax4.transAxes)
        ax4.text(0.1, y_pos-0.06, action, fontsize=11, color=color, transform=ax4.transAxes)
        y_pos -= 0.15
    
    # 风险提示
    box7 = FancyBboxPatch((0.05, 0.05), 0.9, 0.18, boxstyle="round,pad=0.05", 
                          facecolor='#fff8e1', edgecolor='#ff8f00', linewidth=2,
                          transform=ax4.transAxes)
    ax4.add_patch(box7)
    ax4.text(0.5, 0.18, '关键跟踪信号', ha='center', fontsize=11, fontweight='bold', 
            color='#e65100', transform=ax4.transAxes)
    ax4.text(0.5, 0.12, '1.伊朗报复手段 2.美军调动 3.霍尔木兹海峡', ha='center', 
            fontsize=9, transform=ax4.transAxes)
    ax4.text(0.5, 0.07, '4.两会政策 5.北向资金流向', ha='center', 
            fontsize=9, transform=ax4.transAxes)
    
    # 底部
    fig.text(0.5, 0.02, '基于中信研报，仅供参考，投资有风险', 
             ha='center', fontsize=10, style='italic', color='#9e9e9e')
    
    plt.savefig('/Users/tuqibiao/Desktop/彪哥战法_明日策略_0302.png', 
                dpi=150, bbox_inches='tight', facecolor='#f8f9fa')
    print('✅ 明日策略图已保存到桌面')

if __name__ == '__main__':
    create_tomorrow_strategy()
