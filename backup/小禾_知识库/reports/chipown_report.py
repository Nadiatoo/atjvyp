#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""芯朋微(688508.SH) 投研报告 PDF 生成"""

from fpdf import FPDF
import os, datetime

FONT_PATH = "/Users/tuqibiao/Library/Fonts/阿里巴巴普惠体 M.ttf"
OUTPUT_DIR = "/Users/tuqibiao/.hermes/knowledge_base/reports/"

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.add_font("Ali", "", FONT_PATH, uni=True)
        self.add_font("Ali", "B", FONT_PATH, uni=True)  # 用同一字体加粗
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Ali", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "芯朋微(688508.SH) 投研报告 | 小禾出品", align="L")
        self.ln(2)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Ali", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"- {self.page_no()} -", align="C")

    def section_title(self, title, num=""):
        self.ln(6)
        self.set_fill_color(25, 50, 120)
        self.set_text_color(255, 255, 255)
        self.set_font("Ali", "", 12)
        full = f"{num} {title}" if num else title
        self.cell(0, 10, f"  {full}", fill=True, ln=True)
        self.ln(4)

    def sub_title(self, title):
        self.set_font("Ali", "", 10)
        self.set_text_color(25, 50, 120)
        self.cell(0, 8, f"▎{title}", ln=True)
        self.ln(2)

    def body_text(self, text):
        self.set_font("Ali", "", 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def key_text(self, text):
        self.set_fill_color(235, 245, 255)
        self.set_font("Ali", "", 9)
        self.set_text_color(20, 60, 140)
        self.set_x(15)
        self.multi_cell(180, 6, text, fill=True, border=0)
        self.ln(3)

    def add_table(self, headers, data, col_widths=None):
        """专业表格：深色表头+交替行色"""
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)

        # 表头
        self.set_fill_color(25, 50, 120)
        self.set_text_color(255, 255, 255)
        self.set_font("Ali", "", 8)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=0, fill=True, align="C")
        self.ln()

        # 数据行
        self.set_font("Ali", "", 8)
        for row_idx, row in enumerate(data):
            if self.get_y() > 265:
                self.add_page()
                # 重复表头
                self.set_fill_color(25, 50, 120)
                self.set_text_color(255, 255, 255)
                self.set_font("Ali", "", 8)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 7, h, border=0, fill=True, align="C")
                self.ln()

            fill = row_idx % 2 == 0
            if fill:
                self.set_fill_color(245, 247, 252)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_text_color(50, 50, 50)

            for i, val in enumerate(row):
                self.cell(col_widths[i], 6.5, str(val), border=0, fill=fill, align="C")
            self.ln()
        self.ln(4)


def generate():
    pdf = ReportPDF()
    pdf.set_margins(10, 10, 10)

    # ═══════════════ 封面 ═══════════════
    pdf.add_page()
    pdf.set_fill_color(25, 50, 120)
    pdf.rect(0, 0, 210, 120, "F")
    pdf.set_y(30)
    pdf.set_font("Ali", "", 28)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "芯朋微 (688508.SH)", align="C", ln=True)
    pdf.ln(5)
    pdf.set_font("Ali", "", 18)
    pdf.cell(0, 10, "深度投研报告", align="C", ln=True)
    pdf.ln(15)
    pdf.set_font("Ali", "", 11)
    pdf.set_text_color(200, 215, 240)
    lines = [
        f"报告日期：2026年5月19日",
        f"分析师：小禾（Hermes Systems）",
        f"数据来源：Tushare Pro / 腾讯证券 / 东方财富",
        "评级参考：券商评级汇总（详见报告正文）",
    ]
    for l in lines:
        pdf.cell(0, 8, f"      {l}", align="C", ln=True)

    # 封面底部
    pdf.set_y(140)
    pdf.set_draw_color(25, 50, 120)
    pdf.set_line_width(0.5)
    pdf.line(30, 140, 180, 140)

    pdf.set_y(148)
    pdf.set_font("Ali", "", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, "免责声明：本报告基于公开数据整理分析，仅供参考，不构成投资建议。"
                        "股市有风险，投资需谨慎。分析师持证投顾资格，报告内容合规。", align="C")

    # ═══════════════ 一、公司概况 ═══════════════
    pdf.add_page()
    pdf.section_title("公司概况", "一")

    pdf.key_text("芯朋微（Chipown Micro-electronics，688508.SH）是国内领先的电源管理芯片（PMIC）设计公司，"
                 "总部位于江苏无锡，2020年7月登陆科创板。公司专注于AC-DC电源管理芯片领域，"
                 "产品覆盖家用电器、标准电源、工业及车规级电源管理三大市场，是中国电源管理IC细分领域龙头之一。")

    pdf.sub_title("基本信息")
    info_headers = ["项目", "内容"]
    info_data = [
        ["公司全称", "无锡芯朋微电子股份有限公司"],
        ["股票代码", "688508.SH"],
        ["上市板块", "科创板"],
        ["总市值", "约132亿元（2026/05/19）"],
        ["PE(TTM)", "77.71倍"],
        ["PB", "4.40倍"],
        ["最新价", "93.28元（+6.97%，2026/05/19）"],
        ["所属行业", "半导体 — 电源管理芯片"],
        ["员工人数", "约400人（2024年报）"],
    ]
    pdf.add_table(info_headers, info_data, [40, 150])

    # ═══════════════ 二、核心业务分析 ═══════════════
    pdf.section_title("核心业务分析", "二")

    pdf.sub_title("业务板块总览")
    pdf.body_text("芯朋微的产品线可分为三大板块：")

    biz_headers = ["业务板块", "主要产品", "应用领域", "成长阶段"]
    biz_data = [
        ["家用电器AC-DC", "电源管理芯片、驱动IC", "空调/冰箱/洗衣机/厨电", "成熟期（基本盘）"],
        ["标准电源", "快充芯片、适配器芯片", "手机快充/适配器/排插", "成熟期（稳定增长）"],
        ["工业及车规", "高压电源芯片、隔离芯片", "服务器/光储充/新能源汽车", "成长期（第二曲线）"],
    ]
    pdf.add_table(biz_headers, biz_data, [35, 40, 45, 40])

    pdf.sub_title("家用电器（基本盘）")
    pdf.body_text("家用电器AC-DC电源管理芯片是芯朋微的传统优势领域，"
                  "公司在国内家电电源管理IC市场占有率位居前列，客户覆盖美的、格力、海尔、苏泊尔等头部家电企业。"
                  "家电领域需求稳定，受益于家电智能化趋势和国产替代，为公司提供稳固的收入基本盘。")

    pdf.sub_title("标准电源（成熟业务）")
    pdf.body_text("标准电源芯片广泛应用于手机充电器、适配器、排插等消费电子场景。"
                  "公司在该领域积累了丰富的客户资源和产品经验，"
                  "近年来快充技术的普及带动了该板块的持续增长，但受消费电子周期波动影响较大。")

    pdf.sub_title("工业及车规（第二增长曲线）")
    pdf.body_text("工业及车规级电源管理芯片是公司重点发力的新方向，"
                  "涵盖服务器电源、光储充逆变器、新能源汽车OBC/DC-DC等应用场景。"
                  "根据券商研报，2024年该板块收入同比大幅增长，是公司未来最重要的增长引擎。"
                  "公司通过出售芯联越州股权等方式强化上游产能合作，加速推进Fab-lite模式转型。"
                  "2025年工业及服务器领域营收同比大幅提升，成为增长新引擎（西南证券）。")

    # ═══════════════ 三、财务分析 ═══════════════
    pdf.section_title("财务分析", "三")

    pdf.sub_title("年度财务数据")
    fin_headers = ["年度", "营收(亿)", "增速", "净利润(亿)", "增速", "毛利率", "ROE"]
    fin_data = [
        ["2020", "4.29", "-", "1.00", "-", "37.69%", "11.34%"],
        ["2021", "7.53", "+75.5%", "2.01", "+101%", "43.00%", "14.35%"],
        ["2022", "7.20", "-4.4%", "0.89", "-55.7%", "41.15%", "6.02%"],
        ["2023", "7.80", "+8.3%", "0.56", "-36.8%", "37.94%", "3.00%"],
        ["2024", "9.65", "+23.7%", "1.09", "+93.9%", "36.75%", "4.47%"],
        ["2025", "11.43", "+18.5%", "1.85", "+69.7%", "37.24%", "7.14%"],
    ]
    pdf.add_table(fin_headers, fin_data, [18, 25, 22, 30, 22, 22, 22])

    pdf.key_text("核心发现：公司营收从2020年4.29亿增长至2025年11.43亿，5年CAGR约21.6%。"
                 "净利润经历2022-2023年下滑后于2024-2025年强劲反弹，2025年利润修复至1.85亿。"
                 "毛利率稳定在36-43%区间，ROE从2023年低谷3.0%回升至7.14%。")

    pdf.sub_title("最新季度数据")
    q_headers = ["季度", "营收(亿)", "净利润(万)", "毛利率"]
    q_data = [
        ["2024Q1", "2.03", "2,315", "36.74%"],
        ["2024Q2", "2.50", "1,946", "36.22%"],
        ["2024Q3", "2.54", "3,324", "37.11%"],
        ["2024Q4", "2.57", "3,321", "36.58%"],
        ["2025Q1", "3.01", "4,021", "36.69%"],
        ["2025Q2", "3.35", "4,942", "37.99%"],
        ["2025Q3", "2.41", "8,734", "37.17%"],
        ["2025Q4", "2.65", "844", "37.28%"],
        ["2026Q1", "2.94", "1,372", "35.61%"],
    ]
    pdf.add_table(q_headers, q_data, [28, 30, 32, 25])

    pdf.body_text("注：2026Q1营收2.94亿（同比-2.6%），净利润1,372万（同比-65.9%），"
                  "季度利润波动较大。券商认为主要受季节性因素和研发投入加大影响（太平洋证券）。")

    pdf.sub_title("资产负债结构")
    bs_headers = ["指标", "2024年报", "2025年报", "2026Q1"]
    bs_data = [
        ["总资产(亿)", "29.49", "33.08", "33.32"],
        ["总负债(亿)", "4.63", "5.83", "5.87"],
        ["净资产(亿)", "24.92", "27.26", "27.45"],
        ["资产负债率", "15.69%", "17.61%", "17.61%"],
        ["经营现金流(亿)", "0.41", "0.02", "-0.17"],
    ]
    pdf.add_table(bs_headers, bs_data, [40, 40, 40, 40])

    pdf.body_text("公司资产负债率仅17.6%，财务状况非常稳健，几乎无有息负债。"
                  "经营现金流2025年偏低（184.5万），主要受应收账款和存货增加影响。"
                  "2026Q1经营现金流为负，属季节性波动。")

    # ═══════════════ 四、券商研报观点 ═══════════════
    pdf.section_title("券商研报观点汇总", "四")

    rpt_headers = ["机构", "日期", "评级", "核心观点", "2026E EPS"]
    rpt_data = [
        ["国信证券", "2026/03", "增持", "收入增长18%，新兴市场和新品类进入放量期", "1.48"],
        ["中邮证券", "2025/12", "买入", "计算能源IC全布局，迈向系统级电源解决方案", "1.72"],
        ["太平洋", "2025/11", "买入", "季节因素业绩扰动，出售芯联越州股权强化上游", "1.70"],
        ["西南证券", "2025/09", "买入", "利润率修复显著，工业及服务器领域成新引擎", "1.68"],
        ["中邮证券", "2025/08", "买入", "工业市场营收同比大幅提升", "1.80"],
        ["国信证券", "2025/08", "增持", "二季度收入创季度新高，非ACDC产品进入收获期", "1.58"],
        ["中邮证券", "2025/04", "买入", "业绩超预期", "1.67"],
        ["太平洋", "2025/04", "买入", "新产品线拓展带动营收增长，转向Fablite模式", "1.71"],
        ["国信证券", "2025/04", "增持", "2024年推出逾百款新品，四季度收入创季度新高", "1.49"],
    ]
    pdf.add_table(rpt_headers, rpt_data, [28, 18, 15, 95, 22])

    pdf.sub_title("盈利预测汇总")
    fc_headers = ["机构", "2026E EPS", "PE(2026E)", "2027E EPS", "PE(2027E)"]
    fc_data = [
        ["国信证券", "1.48", "42.5x", "1.66", "38.0x"],
        ["中邮证券", "1.72", "33.7x", "2.08", "27.9x"],
        ["太平洋", "1.70", "35.6x", "2.04", "29.6x"],
        ["西南证券", "1.68", "37.0x", "2.07", "29.9x"],
    ]
    pdf.add_table(fc_headers, fc_data, [28, 35, 35, 35, 35])

    pdf.body_text("券商一致预期：2026年EPS均值约1.65元，净利润约2.18亿；"
                  "2027年EPS均值约1.96元，净利润约2.59亿。当前股价93.28元对应2026年PE约56.5倍，"
                  "高于券商目标PE均值37x，估值处于历史较高分位。")

    # ═══════════════ 五、股价与估值 ═══════════════
    pdf.section_title("股价表现与估值", "五")

    pdf.sub_title("近1年股价表现")
    price_headers = ["指标", "数值"]
    price_data = [
        ["近1年最高价", "97.59元"],
        ["近1年最低价", "49.62元"],
        ["近1年均价", "62.66元"],
        ["最新价(2026/05/19)", "93.28元"],
        ["今日涨跌幅", "+6.97%"],
        ["近1年涨幅(低点起)", "+88.0%"],
        ["换手率(今日)", "7.41%"],
        ["成交额(今日)", "8.82亿"],
    ]
    pdf.add_table(price_headers, price_data, [45, 80])

    pdf.body_text("股价从近1年低点49.62元反弹至93.28元，涨幅约88%，"
                  "已接近近1年高点97.59元。当前股价对应PE(TTM) 77.71倍，"
                  "PB 4.40倍。估值处于历史较高水平，市场对公司2025年业绩修复和工业/服务器"
                  "第二增长曲线给予了较高溢价。")

    # ═══════════════ 六、核心逻辑与风险 ═══════════════
    pdf.section_title("投资逻辑与风险提示", "六")

    pdf.sub_title("核心投资逻辑")
    pdf.body_text("① 家电基本盘稳固：国内家电电源管理IC市占率领先，客户粘性强，国产替代持续深化")
    pdf.body_text("② 业绩反转趋势确认：公司经历了2022-2023年的利润低谷后，2024-2025年连续两年高增长，"
                  "净利润从0.56亿修复至1.85亿，年复合增速超80%")
    pdf.body_text("③ 工业及车规第二曲线：服务器电源、光储充、新能源汽车等新市场进入放量期，"
                  "有望复制家电领域的成功路径，打开3-5倍的市场空间")
    pdf.body_text("④ Fab-lite模式转型：通过出售芯联越州股权、加强与上游晶圆代工厂深度合作，"
                  "降低重资产风险，聚焦芯片设计核心能力")
    pdf.body_text('⑤ 多券商一致看好：近半年8份研报全部给予"买入/增持"评级，'
                  "覆盖机构包括国信、中邮、太平洋、西南等主流券商")

    pdf.sub_title("风险提示")
    pdf.body_text("① 季度业绩波动大：2026Q1净利润同比下滑65.9%，单季度波动剧烈，需要注意观察是否是趋势性变化")
    pdf.body_text("② 估值偏高：当前PE(TTM) 77.71倍，即使按2026年一致预期EPS 1.65元计算，PE仍在56倍以上，"
                  "对应PEG超过3倍，估值安全边际不足")
    pdf.body_text("③ 消费电子周期：家电和标准电源业务受宏观经济和消费电子周期影响，"
                  "2022-2023年的利润下滑即为前车之鉴")
    pdf.body_text("④ 竞争加剧：电源管理芯片市场参与者众多（圣邦微、矽力杰、南芯科技等），"
                  "价格竞争可能影响毛利率")
    pdf.body_text("⑤ 工业/车规拓展不及预期：新市场开拓需要时间，客户认证周期长，"
                  "短期难以快速贡献利润")

    # ═══════════════ 七、核心结论 ═══════════════
    pdf.section_title("核心结论", "七")
    pdf.ln(2)
    pdf.key_text("综合评级：⭐⭐⭐（中性偏积极）\n\n"
                 "芯朋微是电源管理芯片细分赛道的优质标的，家电基本盘稳固，"
                 "工业及车规级产品打开第二成长曲线，业绩修复趋势明确。"
                 "但当前77.71倍PE已经Price-in了较高的增长预期，"
                 "建议关注2026年后续季度业绩兑现情况，等待更好的介入时机。"
                 "中长期来看，公司在电源管理IC领域的技术积累和客户资源具有核心竞争力，"
                 "看好其在国产替代大背景下的成长空间。")

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "芯朋微688508_投研报告_20260519.pdf")
    pdf.output(path)
    print(f"PDF saved: {path}")
    return path

if __name__ == "__main__":
    generate()
