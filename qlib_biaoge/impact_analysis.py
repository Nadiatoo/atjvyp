#!/usr/bin/env python3
"""
美伊冲突对市场影响深度分析
基于中信研报《伊朗局势后续推演》
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_impact_analysis():
    """创建影响分析图"""
    
    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor('#f8f9fa')
    
    # 标题
    fig.text(0.5, 0.97, '美伊冲突对市场影响深度分析', 
             ha='center', fontsize=24, fontweight='bold', color='#2c3e50')
    fig.text(0.5, 0.94, '基于中信研报 | 伊朗最高领袖遇害 | 美以"政权更迭"军事行动', 
             ha='center', fontsize=12, color='#c62828', fontweight='bold')
    
    # ========== 1. 短期冲击（左上）==========
    ax1 = plt.axes([0.02, 0.68, 0.30, 0.23])
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    
    ax1.text(5, 9.5, '短期冲击（1-3天）', ha='center', fontsize=14, fontweight='bold', color='#d32f2f')
    
    impacts = [
        ('A股', '低开概率大', '两会窗口有支撑', '#ffebee'),
        ('港股', '情绪冲击', '离岸市场更敏感', '#fff3e0'),
        ('美股', '已部分消化', '周五夜盘修复', '#e8f5e9'),
        ('原油', '高开', '布油或冲80+', '#e3f2fd'),
        ('黄金', '跳涨', '冲击前高', '#fff8e1'),
    ]
    
    y = 8
    for name, impact1, impact2, color in impacts:
        box = FancyBboxPatch((0.3, y-0.8), 9.4, 1.6, boxstyle="round,pad=0.1", 
                            facecolor=color, edgecolor='gray', alpha=0.5)
        ax1.add_patch(box)
        ax1.text(1.5, y, name, fontsize=12, fontweight='bold')
        ax1.text(4, y+0.3, impact1, fontsize=11, color='#c62828')
        ax1.text(4, y-0.3, impact2, fontsize=10, color='#666')
        y -= 1.8
    
    # ========== 2. 中期趋势（右上）==========
    ax2 = plt.axes([0.34, 0.68, 0.32, 0.23])
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    
    ax2.text(5, 9.5, '中期趋势（1-4周）', ha='center', fontsize=14, fontweight='bold', color='#1976d2')
    
    # 基准情形
    box1 = FancyBboxPatch((0.5, 6), 9, 3, boxstyle="round,pad=0.1", 
                          facecolor='#e8f5e9', edgecolor='#4caf50', linewidth=2)
    ax2.add_patch(box1)
    ax2.text(5, 8.5, '基准情形（概率70%）', ha='center', fontsize=12, fontweight='bold', color='#2e7d32')
    ax2.text(5, 7.5, '• 冲突一周左右→谈判解决', ha='center', fontsize=10)
    ax2.text(5, 6.8, '• 市场低开高走→情绪修复', ha='center', fontsize=10)
    
    # 悲观情形
    box2 = FancyBboxPatch((0.5, 2.5), 4.2, 3, boxstyle="round,pad=0.1", 
                          facecolor='#ffebee', edgecolor='#e53935', linewidth=2)
    ax2.add_patch(box2)
    ax2.text(2.6, 5, '悲观（20%）', ha='center', fontsize=11, fontweight='bold', color='#c62828')
    ax2.text(2.6, 4, '冲突升级', ha='center', fontsize=10)
    ax2.text(2.6, 3, '霍尔木兹关闭', ha='center', fontsize=10)
    
    # 乐观情形
    box3 = FancyBboxPatch((5.3, 2.5), 4.2, 3, boxstyle="round,pad=0.1", 
                          facecolor='#e3f2fd', edgecolor='#1976d2', linewidth=2)
    ax2.add_patch(box3)
    ax2.text(7.4, 5, '乐观（10%）', ha='center', fontsize=11, fontweight='bold', color='#1565c0')
    ax2.text(7.4, 4, '快速停火', ha='center', fontsize=10)
    ax2.text(7.4, 3, '情绪快速修复', ha='center', fontsize=10)
    
    # ========== 3. 板块影响矩阵（左中+右中）==========
    ax3 = plt.axes([0.02, 0.35, 0.64, 0.30])
    ax3.axis('off')
    
    ax3.text(0.5, 0.95, '板块影响矩阵', ha='center', fontsize=14, fontweight='bold', transform=ax3.transAxes)
    
    # 表头
    headers = ['板块', '短期影响', '中期影响', '核心逻辑', '龙头标的']
    x_pos = [0.05, 0.18, 0.35, 0.52, 0.78]
    for i, h in enumerate(headers):
        ax3.text(x_pos[i], 0.88, h, fontsize=11, fontweight='bold', transform=ax3.transAxes)
    
    # 数据
    sectors = [
        ['军工', '大涨', '持续强势', '无人机+智能化作战', '航天彩虹、中航沈飞'],
        ['黄金', '跳涨', '冲击前高', '避险需求+美元信用', '山东黄金、中金黄金'],
        ['油运', '涨停潮', '运价飙升', '霍尔木兹风险', '招商轮船、中远海能'],
        ['原油', '高开', '维持高位', '供给冲击担忧', '中石油、中石化'],
        ['化工', '分化', '涨价主线', '供给约束+成本推动', '万华化学、华鲁恒升'],
        ['有色', '冲高', '战略配置', '资源安全+新能源', '北方稀土、洛阳钼业'],
        ['航空', '大跌', '承压', '油价上涨成本增加', '回避'],
        ['航运(集运)', '下跌', '中性', '需求担忧', '暂时回避'],
    ]
    
    colors_map = {
        '大涨': '#c62828', '跳涨': '#c62828', '涨停潮': '#c62828',
        '高开': '#f57c00', '冲高': '#f57c00',
        '分化': '#ff8f00',
        '大跌': '#2e7d32', '下跌': '#2e7d32', '承压': '#2e7d32',
        '持续强势': '#c62828', '冲击前高': '#c62828', '运价飙升': '#c62828',
        '维持高位': '#f57c00', '涨价主线': '#f57c00', '战略配置': '#f57c00',
    }
    
    y = 0.80
    for row in sectors:
        for i, cell in enumerate(row):
            color = colors_map.get(cell, '#333')
            weight = 'bold' if i == 0 else 'normal'
            ax3.text(x_pos[i], y, cell, fontsize=9, color=color, fontweight=weight,
                    transform=ax3.transAxes)
        y -= 0.09
    
    # ========== 4. 资金流向（右下）==========
    ax4 = plt.axes([0.68, 0.35, 0.30, 0.30])
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 10)
    ax4.axis('off')
    
    ax4.text(5, 9.5, '资金流向预判', ha='center', fontsize=14, fontweight='bold', color='#6a1b9a')
    
    # 流入
    ax4.text(2.5, 8.5, '资金流入', ha='center', fontsize=12, fontweight='bold', color='#2e7d32')
    inflows = ['军工ETF', '黄金ETF', '原油基金', '红利低波']
    y = 7.5
    for item in inflows:
        box = FancyBboxPatch((0.5, y-0.4), 4, 0.8, boxstyle="round,pad=0.05", 
                            facecolor='#e8f5e9', edgecolor='#4caf50', alpha=0.7)
        ax4.add_patch(box)
        ax4.text(2.5, y, item, ha='center', fontsize=10)
        y -= 1
    
    # 流出
    ax4.text(7.5, 8.5, '资金流出', ha='center', fontsize=12, fontweight='bold', color='#c62828')
    outflows = ['科技成长', '航空航运', '出口制造', '港股通']
    y = 7.5
    for item in outflows:
        box = FancyBboxPatch((5.5, y-0.4), 4, 0.8, boxstyle="round,pad=0.05", 
                            facecolor='#ffebee', edgecolor='#e53935', alpha=0.7)
        ax4.add_patch(box)
        ax4.text(7.5, y, item, ha='center', fontsize=10)
        y -= 1
    
    # ========== 5. 核心矛盾（底部左）==========
    ax5 = plt.axes([0.02, 0.04, 0.47, 0.28])
    ax5.set_xlim(0, 10)
    ax5.set_ylim(0, 10)
    ax5.axis('off')
    
    ax5.text(5, 9.5, '核心矛盾：两会窗口 vs 地缘冲击', ha='center', fontsize=13, fontweight='bold', color='#d32f2f')
    
    # 两会因素
    box1 = FancyBboxPatch((0.3, 5), 4.2, 4, boxstyle="round,pad=0.1", 
                          facecolor='#e3f2fd', edgecolor='#1976d2', linewidth=2)
    ax5.add_patch(box1)
    ax5.text(2.4, 8.5, '两会维稳', ha='center', fontsize=12, fontweight='bold', color='#1565c0')
    ax5.text(2.4, 7.5, '• 政策预期', ha='center', fontsize=10)
    ax5.text(2.4, 6.8, '• 指数波动有限', ha='center', fontsize=10)
    ax5.text(2.4, 6.1, '• 结构性机会', ha='center', fontsize=10)
    
    # 地缘因素
    box2 = FancyBboxPatch((5.5, 5), 4.2, 4, boxstyle="round,pad=0.1", 
                          facecolor='#ffebee', edgecolor='#e53935', linewidth=2)
    ax5.add_patch(box2)
    ax5.text(7.6, 8.5, '地缘冲击', ha='center', fontsize=12, fontweight='bold', color='#c62828')
    ax5.text(7.6, 7.5, '• 避险情绪', ha='center', fontsize=10)
    ax5.text(7.6, 6.8, '• 外资流出压力', ha='center', fontsize=10)
    ax5.text(7.6, 6.1, '• 成长股承压', ha='center', fontsize=10)
    
    # 结论
    ax5.text(5, 3, '结果：A股大概率低开高走，两会政策对冲地缘风险', 
            ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#fff8e1', edgecolor='#ff8f00', linewidth=2))
    
    # ========== 6. 关键指标（底部右）==========
    ax6 = plt.axes([0.52, 0.04, 0.46, 0.28])
    ax6.axis('off')
    
    ax6.text(0.5, 0.95, '周一开盘关键指标', ha='center', fontsize=13, fontweight='bold', transform=ax6.transAxes)
    
    indicators = [
        ('上证指数低开幅度', '< 1.5%', '1.5-3%', '> 3%', ['绿', '黄', '红']),
        ('北向资金流向', '净流入', '小幅流出', '大幅流出', ['红', '黄', '绿']),
        ('涨停家数', '> 50家', '30-50家', '< 30家', ['红', '黄', '绿']),
        ('黄金股表现', '多股涨停', '普遍大涨', '高开低走', ['红', '黄', '绿']),
        ('原油相关', '两桶油大涨', '小幅上涨', '高开低走', ['红', '黄', '绿']),
    ]
    
    y = 0.82
    for name, good, mid, bad, colors in indicators:
        ax6.text(0.05, y, name, fontsize=10, fontweight='bold', transform=ax6.transAxes)
        
        # 好
        box1 = FancyBboxPatch((0.38, y-0.03), 0.18, 0.07, boxstyle="round,pad=0.02", 
                             facecolor='#e8f5e9', edgecolor='#4caf50', transform=ax6.transAxes)
        ax6.add_patch(box1)
        ax6.text(0.47, y, good, fontsize=9, ha='center', transform=ax6.transAxes)
        
        # 中
        box2 = FancyBboxPatch((0.58, y-0.03), 0.18, 0.07, boxstyle="round,pad=0.02", 
                             facecolor='#fff3e0', edgecolor='#ff9800', transform=ax6.transAxes)
        ax6.add_patch(box2)
        ax6.text(0.67, y, mid, fontsize=9, ha='center', transform=ax6.transAxes)
        
        # 差
        box3 = FancyBboxPatch((0.78, y-0.03), 0.18, 0.07, boxstyle="round,pad=0.02", 
                             facecolor='#ffebee', edgecolor='#e53935', transform=ax6.transAxes)
        ax6.add_patch(box3)
        ax6.text(0.87, y, bad, fontsize=9, ha='center', transform=ax6.transAxes)
        
        y -= 0.17
    
    # 底部
    fig.text(0.5, 0.01, '数据来源：中信研报 | 分析框架：彪哥战法 | 仅供参考，投资有风险', 
             ha='center', fontsize=10, style='italic', color='#9e9e9e')
    
    plt.savefig('/Users/tuqibiao/Desktop/美伊冲突_市场影响分析.png', 
                dpi=150, bbox_inches='tight', facecolor='#f8f9fa')
    print('✅ 市场影响分析图已保存到桌面')

if __name__ == '__main__':
    create_impact_analysis()
