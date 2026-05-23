#!/usr/bin/env python3
"""
持仓分析报告生成器
基于用户持仓数据生成Word格式的分析报告
"""

import os
import sys
from datetime import datetime

# 持仓数据
HOLDINGS = [
    {"code": "601698", "name": "中国卫通", "shares": 400, "cost": 36.5329, "price": 36.9800, "pnl": 165.80},
    {"code": "601888", "name": "中国中免", "shares": 200, "cost": 67.8557, "price": 77.3100, "pnl": 1877.48},
    {"code": "000815", "name": "美利云", "shares": 900, "cost": 12.3644, "price": 13.6600, "pnl": 1154.35},
    {"code": "300059", "name": "东方财富", "shares": 700, "cost": 23.1671, "price": 21.2100, "pnl": -1382.92},
]

def calculate_metrics():
    """计算持仓指标"""
    total_cost = sum(h["shares"] * h["cost"] for h in HOLDINGS)
    total_value = sum(h["shares"] * h["price"] for h in HOLDINGS)
    total_pnl = sum(h["pnl"] for h in HOLDINGS)
    pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
    
    # 计算每只股票权重
    for h in HOLDINGS:
        h["weight"] = (h["shares"] * h["price"]) / total_value * 100 if total_value > 0 else 0
        h["pnl_pct"] = (h["pnl"] / (h["shares"] * h["cost"])) * 100 if h["cost"] > 0 else 0
    
    return {
        "total_cost": total_cost,
        "total_value": total_value,
        "total_pnl": total_pnl,
        "pnl_pct": pnl_pct,
    }

def get_sector_analysis():
    """获取板块分析"""
    sectors = {
        "601698": {"sector": "卫星通信/军工", "trend": "中性", "analysis": "卫星互联网建设加速，国防信息化需求增长，但短期涨幅较大需警惕回调。"},
        "601888": {"sector": "免税零售", "trend": "偏多", "analysis": "海南自贸港政策持续催化，出境游复苏带动免税消费，龙头地位稳固。"},
        "000815": {"sector": "国资云/东数西算", "trend": "偏多", "analysis": "数据中心建设加速，国资云政策利好，东数西算核心标的。"},
        "300059": {"sector": "互联网金融", "trend": "偏空", "analysis": "券商板块整体承压，成交量萎缩影响业绩预期，短期难有起色。"},
    }
    return sectors

def generate_report():
    """生成Word报告"""
    try:
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
    except ImportError:
        print("正在安装依赖...")
        os.system("pip3 install python-docx -q")
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
    
    # 计算指标
    metrics = calculate_metrics()
    sectors = get_sector_analysis()
    
    # 创建文档
    doc = Document()
    
    # 设置中文字体
    def set_chinese_font(run, font_name='Microsoft YaHei'):
        run.font.name = font_name
        run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    
    # 标题
    title = doc.add_heading('', 0)
    title_run = title.add_run('持仓分析报告')
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0, 51, 102)
    set_chinese_font(title_run)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 日期
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_run = date_para.add_run(f'生成日期：{datetime.now().strftime("%Y年%m月%d日")}')
    date_run.font.size = Pt(10)
    date_run.font.color.rgb = RGBColor(128, 128, 128)
    set_chinese_font(date_run)
    
    doc.add_paragraph()
    
    # 一、持仓概览
    heading1 = doc.add_heading('', level=1)
    h1_run = heading1.add_run('一、持仓概览')
    h1_run.font.size = Pt(16)
    h1_run.font.color.rgb = RGBColor(0, 51, 102)
    set_chinese_font(h1_run)
    
    # 总体指标表格
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Light Grid Accent 1'
    
    summary_data = [
        ("持仓总市值", f"¥{metrics['total_value']:,.2f}"),
        ("持仓总成本", f"¥{metrics['total_cost']:,.2f}"),
        ("总盈亏", f"¥{metrics['total_pnl']:,.2f}"),
        ("盈亏比例", f"{metrics['pnl_pct']:+.2f}%"),
    ]
    
    for i, (label, value) in enumerate(summary_data):
        row = table.rows[i]
        row.cells[0].text = label
        row.cells[1].text = value
        # 设置字体
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    set_chinese_font(run)
                    run.font.size = Pt(11)
    
    doc.add_paragraph()
    
    # 二、个股明细
    heading2 = doc.add_heading('', level=1)
    h2_run = heading2.add_run('二、个股明细')
    h2_run.font.size = Pt(16)
    h2_run.font.color.rgb = RGBColor(0, 51, 102)
    set_chinese_font(h2_run)
    
    # 个股表格
    stock_table = doc.add_table(rows=len(HOLDINGS)+1, cols=7)
    stock_table.style = 'Light List Accent 1'
    
    # 表头
    headers = ["代码", "名称", "持股", "成本价", "现价", "盈亏额", "盈亏%"]
    for i, header in enumerate(headers):
        cell = stock_table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                set_chinese_font(run)
                run.font.bold = True
                run.font.size = Pt(10)
    
    # 数据行
    for i, h in enumerate(HOLDINGS, 1):
        row = stock_table.rows[i]
        row.cells[0].text = h["code"]
        row.cells[1].text = h["name"]
        row.cells[2].text = str(h["shares"])
        row.cells[3].text = f"{h['cost']:.2f}"
        row.cells[4].text = f"{h['price']:.2f}"
        row.cells[5].text = f"{h['pnl']:+.2f}"
        row.cells[6].text = f"{h['pnl_pct']:+.2f}%"
        
        # 设置字体和颜色
        for j, cell in enumerate(row.cells):
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    set_chinese_font(run)
                    run.font.size = Pt(10)
                    # 盈亏列根据正负设置颜色
                    if j in [5, 6]:
                        if h['pnl'] >= 0:
                            run.font.color.rgb = RGBColor(200, 0, 0)  # 红色表示盈利
                        else:
                            run.font.color.rgb = RGBColor(0, 150, 0)  # 绿色表示亏损
    
    doc.add_paragraph()
    
    # 三、板块分析
    heading3 = doc.add_heading('', level=1)
    h3_run = heading3.add_run('三、板块分析')
    h3_run.font.size = Pt(16)
    h3_run.font.color.rgb = RGBColor(0, 51, 102)
    set_chinese_font(h3_run)
    
    for h in HOLDINGS:
        sector_info = sectors.get(h["code"], {})
        
        # 股票名称作为小标题
        p = doc.add_paragraph()
        p_run = p.add_run(f"▸ {h['name']} ({h['code']}) - {sector_info.get('sector', '未知')}")
        p_run.font.bold = True
        p_run.font.size = Pt(12)
        set_chinese_font(p_run)
        
        # 趋势判断
        trend = sector_info.get('trend', '中性')
        trend_color = RGBColor(200, 0, 0) if trend == '偏多' else (RGBColor(0, 150, 0) if trend == '偏空' else RGBColor(128, 128, 128))
        trend_p = doc.add_paragraph()
        trend_p.paragraph_format.left_indent = Inches(0.2)
        trend_run = trend_p.add_run(f"趋势判断：{trend}")
        trend_run.font.color.rgb = trend_color
        trend_run.font.size = Pt(11)
        set_chinese_font(trend_run)
        
        # 分析
        analysis_p = doc.add_paragraph()
        analysis_p.paragraph_format.left_indent = Inches(0.2)
        analysis_run = analysis_p.add_run(f"分析：{sector_info.get('analysis', '暂无分析')}")
        analysis_run.font.size = Pt(10)
        set_chinese_font(analysis_run)
        
        doc.add_paragraph()
    
    # 四、风险评估
    heading4 = doc.add_heading('', level=1)
    h4_run = heading4.add_run('四、风险评估')
    h4_run.font.size = Pt(16)
    h4_run.font.color.rgb = RGBColor(0, 51, 102)
    set_chinese_font(h4_run)
    
    risks = [
        ("集中度风险", "持仓共4只股票，分散度较好，但东方财富亏损较大需关注。"),
        ("板块风险", "涉及卫星通信、免税、国资云、券商四个不同板块，相关性较低。"),
        ("流动性风险", "均为大盘或中盘股，流动性良好。"),
    ]
    
    for risk_name, risk_desc in risks:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        p_run = p.add_run(f"• {risk_name}：")
        p_run.font.bold = True
        p_run.font.size = Pt(11)
        set_chinese_font(p_run)
        
        d_run = p.add_run(risk_desc)
        d_run.font.size = Pt(10)
        set_chinese_font(d_run)
    
    doc.add_paragraph()
    
    # 五、操作建议
    heading5 = doc.add_heading('', level=1)
    h5_run = heading5.add_run('五、操作建议（基于彪哥战法）')
    h5_run.font.size = Pt(16)
    h5_run.font.color.rgb = RGBColor(0, 51, 102)
    set_chinese_font(h5_run)
    
    # 盈利股票建议
    profit_stocks = [h for h in HOLDINGS if h['pnl'] > 0]
    loss_stocks = [h for h in HOLDINGS if h['pnl'] < 0]
    
    if profit_stocks:
        p = doc.add_paragraph()
        p_run = p.add_run("【盈利持仓】")
        p_run.font.bold = True
        p_run.font.size = Pt(11)
        set_chinese_font(p_run)
        
        for h in profit_stocks:
            suggest_p = doc.add_paragraph()
            suggest_p.paragraph_format.left_indent = Inches(0.3)
            suggest_run = suggest_p.add_run(f"• {h['name']}：当前盈利{h['pnl_pct']:.1f}%，建议设置移动止损保护利润。若出现放量滞涨或跌破5日线，考虑部分止盈。")
            suggest_run.font.size = Pt(10)
            set_chinese_font(suggest_run)
    
    if loss_stocks:
        p = doc.add_paragraph()
        p_run = p.add_run("【亏损持仓】")
        p_run.font.bold = True
        p_run.font.size = Pt(11)
        set_chinese_font(p_run)
        
        for h in loss_stocks:
            suggest_p = doc.add_paragraph()
            suggest_p.paragraph_format.left_indent = Inches(0.3)
            loss_pct = abs(h['pnl_pct'])
            if loss_pct > 10:
                suggest_run = suggest_p.add_run(f"• {h['name']}：已亏损{loss_pct:.1f}%，超过7%止损线，建议严格执行止损纪律，避免深套。")
            else:
                suggest_run = suggest_p.add_run(f"• {h['name']}：亏损{loss_pct:.1f}%，关注板块能否企稳，若继续走弱考虑止损。")
            suggest_run.font.size = Pt(10)
            set_chinese_font(suggest_run)
    
    doc.add_paragraph()
    
    # 六、总体策略
    heading6 = doc.add_heading('', level=1)
    h6_run = heading6.add_run('六、总体策略建议')
    h6_run.font.size = Pt(16)
    h6_run.font.color.rgb = RGBColor(0, 51, 102)
    set_chinese_font(h6_run)
    
    strategies = [
        "1. 仓位管理：当前持仓盈亏基本平衡，建议维持现有仓位或略减仓，保留机动资金应对市场变化。",
        "2. 止盈止损：中国中免、美利云已有较好盈利，设置保本线或移动止损；东方财富严格执行7%止损纪律。",
        "3. 调仓方向：若东方财富止损，资金可转向AI算力、半导体设备等当前风口板块。",
        "4. 季节判断：关注大盘四季变化，若进入冬藏期，整体仓位应降至30%以下。",
    ]
    
    for strategy in strategies:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        s_run = p.add_run(strategy)
        s_run.font.size = Pt(10)
        set_chinese_font(s_run)
    
    doc.add_paragraph()
    
    # 免责声明
    disclaimer = doc.add_paragraph()
    disclaimer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    dis_run = disclaimer.add_run("— 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。 —")
    dis_run.font.size = Pt(9)
    dis_run.font.color.rgb = RGBColor(128, 128, 128)
    dis_run.font.italic = True
    set_chinese_font(dis_run)
    
    # 保存
    desktop = os.path.expanduser("~/Desktop")
    filename = f"持仓分析报告_{datetime.now().strftime('%Y%m%d')}.docx"
    filepath = os.path.join(desktop, filename)
    doc.save(filepath)
    
    print(f"报告已生成: {filepath}")
    return filepath

if __name__ == "__main__":
    try:
        result = generate_report()
        if result:
            print(f"SUCCESS:{result}")
        else:
            print("FAILED")
    except Exception as e:
        print(f"ERROR:{e}")
        import traceback
        traceback.print_exc()
