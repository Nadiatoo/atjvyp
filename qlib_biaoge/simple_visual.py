#!/usr/bin/env python3
"""
彪哥战法 - 简化版可视化（超直观）
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 数据
seasons = ['春播', '夏长', '秋收', '冬藏']
days = [56, 419, 390, 684]
colors = ['#2ecc71', '#f1c40f', '#e67e22', '#3498db']
desc = ['逐步建仓', '重仓持股', '逢高减仓', '空仓观望']
positions = ['30-50%', '70-90%', '30-50%', '0-10%']

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('【彪哥战法】AI四季判断系统', fontsize=18, fontweight='bold')

# 图1: 饼图
ax1 = axes[0, 0]
total = sum(days)
sizes = [d/total*100 for d in days]
wedges, texts, autotexts = ax1.pie(sizes, labels=seasons, colors=colors, autopct='%1.1f%%', startangle=90)
ax1.set_title('四季分布', fontsize=14, fontweight='bold')

# 图2: 柱状图
ax2 = axes[0, 1]
bars = ax2.bar(seasons, days, color=colors, edgecolor='black', linewidth=2)
ax2.set_title('各季节天数', fontsize=14, fontweight='bold')
ax2.set_ylabel('天数')
for bar, day in zip(bars, days):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
             f'{day}天', ha='center', fontsize=11, fontweight='bold')

# 图3: 策略表
ax3 = axes[1, 0]
ax3.axis('off')
table_data = [['季节', '特征', '策略', '仓位']]
for i, s in enumerate(seasons):
    table_data.append([s, desc[i], '...', positions[i]])

table = ax3.table(cellText=table_data, cellLoc='center', loc='center', colWidths=[0.2, 0.3, 0.3, 0.2])
table.scale(1, 2)
table.set_fontsize(11)
for i in range(4):
    table[(0, i)].set_facecolor('#34495e')
    table[(0, i)].set_text_props(color='white', weight='bold')
for i in range(1, 5):
    for j in range(4):
        table[(i, j)].set_facecolor(colors[i-1])
        table[(i, j)].set_alpha(0.3)
ax3.set_title('四季策略表', fontsize=14, fontweight='bold', pad=20)

# 图4: 当前状态
ax4 = axes[1, 1]
ax4.axis('off')
ax4.text(0.5, 0.7, '当前市场季节', fontsize=16, ha='center', transform=ax4.transAxes)
ax4.text(0.5, 0.5, '冬藏', fontsize=40, ha='center', fontweight='bold', color='#3498db', transform=ax4.transAxes)
ax4.text(0.5, 0.3, '空仓观望', fontsize=14, ha='center', color='gray', transform=ax4.transAxes)
ax4.text(0.5, 0.15, '建议仓位: 0-10%', fontsize=12, ha='center', 
         bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.3), transform=ax4.transAxes)
ax4.set_title('当前状态', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/tuqibiao/Desktop/彪哥战法_四季分析.png', dpi=150, bbox_inches='tight')
print('✅ 图片已保存到桌面: 彪哥战法_四季分析.png')
