#!/usr/bin/env python3
"""
彪哥战法 - 实战决策仪表盘
聚焦当下判断 + 未来趋势 + 操作建议
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_dashboard():
    """创建实战决策仪表盘"""
    
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#f8f9fa')
    
    # ========== 标题区 ==========
    fig.text(0.5, 0.96, '【彪哥战法】实战决策仪表盘', 
             ha='center', fontsize=24, fontweight='bold', color='#2c3e50')
    fig.text(0.5, 0.93, f'分析日期：2026年3月1日 周日 | 下个交易日：3月2日周一', 
             ha='center', fontsize=12, color='#7f8c8d')
    
    # ========== 1. 当前季节判断（左上大区域）==========
    ax1 = plt.axes([0.03, 0.58, 0.35, 0.32])
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    
    # 季节圆环
    season_colors = {'春播': '#27ae60', '夏长': '#f39c12', '秋收': '#e67e22', '冬藏': '#3498db'}
    current_season = '冬藏'
    
    # 大圆
    circle = Circle((5, 5), 3.5, facecolor=season_colors[current_season], 
                    edgecolor='black', linewidth=3, alpha=0.3)
    ax1.add_patch(circle)
    
    # 季节文字
    ax1.text(5, 6, '当前季节', ha='center', fontsize=14, color='#7f8c8d')
    ax1.text(5, 4.5, current_season, ha='center', fontsize=48, 
             fontweight='bold', color=season_colors[current_season])
    ax1.text(5, 2.5, '空仓观望', ha='center', fontsize=16, color='#e74c3c')
    
    # ========== 2. 趋势判断（季节右侧）==========
    ax2 = plt.axes([0.40, 0.58, 0.28, 0.32])
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    
    ax2.text(5, 9, '趋势判断', ha='center', fontsize=16, fontweight='bold')
    
    # 四季时间轴
    seasons = ['春播', '夏长', '秋收', '冬藏']
    positions = [2, 4, 6, 8]
    colors_list = ['#27ae60', '#f39c12', '#e67e22', '#3498db']
    
    for i, (season, pos, color) in enumerate(zip(seasons, positions, colors_list)):
        circle = Circle((pos, 6), 0.6, facecolor=color, edgecolor='black', linewidth=2)
        ax2.add_patch(circle)
        ax2.text(pos, 6, season[0], ha='center', va='center', 
                fontsize=12, fontweight='bold', color='white')
        ax2.text(pos, 4.5, season, ha='center', fontsize=10)
    
    # 当前位置标记
    current_pos = positions[3]  # 冬藏
    ax2.plot(current_pos, 6, 'o', markersize=20, markerfacecolor='red', 
             markeredgecolor='white', markeredgewidth=3)
    
    # 趋势箭头（冬→春？）
    ax2.annotate('', xy=(2.5, 6), xytext=(7.5, 6),
                arrowprops=dict(arrowstyle='->', color='gray', lw=2, ls='--'))
    ax2.text(5, 7.5, '观望中，等待春播信号', ha='center', fontsize=11, 
             style='italic', color='#e74c3c')
    
    # ========== 3. 仓位管理建议（右上）==========
    ax3 = plt.axes([0.71, 0.58, 0.26, 0.32])
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    ax3.axis('off')
    
    ax3.text(5, 9, '仓位管理', ha='center', fontsize=16, fontweight='bold')
    
    # 仓位仪表盘
    position_pct = 0  # 当前建议仓位0%
    
    # 画半圆仪表盘
    theta = np.linspace(0, np.pi, 100)
    r = 3
    for i, angle in enumerate(theta):
        color = '#e74c3c' if i < 33 else '#f39c12' if i < 66 else '#27ae60'
        ax3.plot([5, 5 + r*np.cos(angle)], [3, 3 + r*np.sin(angle)], 
                color=color, linewidth=8, alpha=0.3)
    
    # 指针
    needle_angle = np.pi * (1 - position_pct)
    ax3.plot([5, 5 + 2.5*np.cos(needle_angle)], [3, 3 + 2.5*np.sin(needle_angle)], 
            'k-', linewidth=4)
    ax3.plot(5, 3, 'ko', markersize=15)
    
    ax3.text(5, 1, f'建议仓位：{position_pct:.0%}', ha='center', fontsize=20, 
             fontweight='bold', color='#e74c3c')
    ax3.text(5, 0.3, '理由：冬藏期，市场冰点', ha='center', fontsize=10, color='#7f8c8d')
    
    # ========== 4. 热点题材（左下）==========
    ax4 = plt.axes([0.03, 0.08, 0.45, 0.42])
    ax4.axis('off')
    
    ax4.text(0.5, 0.95, '潜在热点题材', ha='center', fontsize=16, 
             fontweight='bold', transform=ax4.transAxes)
    
    # 题材列表（模拟数据）
    themes = [
        {'name': 'AI算力', 'status': '持续活跃', 'strength': 85, 
         'leader': '高新发展', 'army': '中科曙光'},
        {'name': '机器人', 'status': '政策催化', 'strength': 75, 
         'leader': '鸣志电器', 'army': '三花智控'},
        {'name': '油服', 'status': '业绩改善', 'strength': 65, 
         'leader': '海油工程', 'army': '中海油服'},
    ]
    
    y_pos = 0.78
    for theme in themes:
        # 题材框
        box = FancyBboxPatch((0.02, y_pos-0.08), 0.96, 0.22,
                            boxstyle="round,pad=0.01", 
                            facecolor='#ecf0f1', edgecolor='#bdc3c7', linewidth=1,
                            transform=ax4.transAxes)
        ax4.add_patch(box)
        
        # 题材名
        ax4.text(0.05, y_pos, theme['name'], fontsize=14, fontweight='bold',
                transform=ax4.transAxes)
        
        # 状态标签
        status_color = '#27ae60' if '活跃' in theme['status'] else '#f39c12'
        ax4.text(0.25, y_pos, theme['status'], fontsize=10, color=status_color,
                transform=ax4.transAxes)
        
        # 强度条
        ax4.barh(y_pos-0.03, theme['strength']/100*0.25, height=0.02, 
                left=0.05, color=status_color, alpha=0.7, transform=ax4.transAxes)
        ax4.text(0.31, y_pos-0.03, f"强度:{theme['strength']}", fontsize=9, 
                transform=ax4.transAxes, va='center')
        
        # 龙头+中军
        ax4.text(0.45, y_pos, f"龙头: {theme['leader']}", fontsize=11, 
                color='#e74c3c', transform=ax4.transAxes)
        ax4.text(0.45, y_pos-0.05, f"中军: {theme['army']}", fontsize=10, 
                color='#3498db', transform=ax4.transAxes)
        
        y_pos -= 0.24
    
    # ========== 5. 风险因素（右下）==========
    ax5 = plt.axes([0.52, 0.08, 0.45, 0.42])
    ax5.axis('off')
    
    ax5.text(0.5, 0.95, '风险因素与应对', ha='center', fontsize=16, 
             fontweight='bold', transform=ax5.transAxes)
    
    risks = [
        {'level': '高', 'desc': '外部市场波动', 'impact': '美股大跌可能拖累A股'},
        {'level': '中', 'desc': '量能持续萎缩', 'impact': '缺乏增量资金'},
        {'level': '中', 'desc': '年报披露期', 'impact': '警惕业绩暴雷'},
        {'level': '低', 'desc': '政策不确定性', 'impact': '关注两会政策'},
    ]
    
    y_pos = 0.78
    for risk in risks:
        # 风险等级颜色
        level_color = {'高': '#e74c3c', '中': '#f39c12', '低': '#27ae60'}[risk['level']]
        
        # 风险框
        box = FancyBboxPatch((0.02, y_pos-0.08), 0.96, 0.18,
                            boxstyle="round,pad=0.01", 
                            facecolor='#fff5f5' if risk['level']=='高' else '#fffbf0',
                            edgecolor=level_color, linewidth=2, alpha=0.5,
                            transform=ax5.transAxes)
        ax5.add_patch(box)
        
        # 风险等级标签
        ax5.text(0.05, y_pos, risk['level'], fontsize=12, fontweight='bold',
                color='white', bbox=dict(boxstyle='round', facecolor=level_color),
                transform=ax5.transAxes)
        
        # 风险描述
        ax5.text(0.15, y_pos, risk['desc'], fontsize=12, fontweight='bold',
                transform=ax5.transAxes)
        ax5.text(0.15, y_pos-0.05, risk['impact'], fontsize=10, 
                color='#7f8c8d', transform=ax5.transAxes)
        
        y_pos -= 0.20
    
    # 底部提示
    fig.text(0.5, 0.02, '本仪表盘基于AI模型生成，仅供参考，投资有风险，决策需谨慎', 
             ha='center', fontsize=10, style='italic', color='#7f8c8d')
    
    plt.savefig('/Users/tuqibiao/Desktop/彪哥战法_实战仪表盘.png', 
                dpi=150, bbox_inches='tight', facecolor='#f8f9fa')
    print('✅ 实战仪表盘已保存到桌面')

if __name__ == '__main__':
    create_dashboard()
