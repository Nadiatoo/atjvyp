#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""华丰科技(688629.SH) 投研报告"""

from fpdf import FPDF
import os

FONT_PATH = "/Users/tuqibiao/Library/Fonts/阿里巴巴普惠体 M.ttf"
OUTPUT_DIR = "/Users/tuqibiao/.hermes/knowledge_base/reports/"

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.add_font("Ali", "", FONT_PATH, uni=True)
        self.add_font("Ali", "B", FONT_PATH, uni=True)
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Ali", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "华丰科技(688629.SH) 投研报告 | 小禾出品 2026.05.19", align="L")
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
        self.cell(0, 8, f"\u25ce {title}", ln=True)
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
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        self.set_fill_color(25, 50, 120)
        self.set_text_color(255, 255, 255)
        self.set_font("Ali", "", 8)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=0, fill=True, align="C")
        self.ln()
        self.set_font("Ali", "", 8)
        for row_idx, row in enumerate(data):
            if self.get_y() > 265:
                self.add_page()
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

    # ===== 封面 =====
    pdf.add_page()
    pdf.set_fill_color(180, 40, 30)
    pdf.rect(0, 0, 210, 120, "F")
    pdf.set_y(28)
    pdf.set_font("Ali", "", 28)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "华丰科技 (688629.SH)", align="C", ln=True)
    pdf.ln(3)
    pdf.set_font("Ali", "", 16)
    pdf.cell(0, 10, "投研报告", align="C", ln=True)
    pdf.ln(10)
    pdf.set_font("Ali", "", 11)
    pdf.set_text_color(220, 200, 195)
    for l in ["报告日期：2026年5月19日", "分析师：小禾（Hermes Systems）",
              "数据来源：Tushare Pro / 腾讯证券 / 东方财富 / 券商研报"]:
        pdf.cell(0, 8, f"      {l}", align="C", ln=True)
    pdf.set_y(148)
    pdf.set_font("Ali", "", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, "免责声明：本报告基于公开数据整理分析，仅供参考，不构成投资建议。", align="C")

    # ===== 一、公司概况 =====
    pdf.add_page()
    pdf.section_title("公司概况", "一")
    pdf.key_text("华丰科技（688629.SH）是国内领先的防务及高端连接器供应商，"
                 "2023年6月登陆科创板。公司主营防务连接器、通信连接器及工业连接器，"
                 "是华为昇腾AI服务器高速背板连接器及高速线模组的核心供应商，"
                 "深度受益于国产AI算力基础设施建设。")

    info_data = [
        ["公司全称", "四川华丰科技股份有限公司"],
        ["股票代码", "688629.SH"],
        ["上市板块", "科创板（2023年6月）"],
        ["最新价(5/19)", "147.24元（+11.71%）"],
        ["总市值", "约460亿"],
        ["PE(TTM) / PB", "157.17倍 / 35.22倍"],
        ["所属行业", "电子·连接器"],
        ["资产负债率", "51.86%"],
    ]
    pdf.add_table(["项目", "内容"], info_data, [35, 155])

    pdf.sub_title("核心业务结构")
    biz_data = [
        ["高速线模组", "AI服务器高速互联", "含背板连接器/线缆模组/IO连接器", "爆发期"],
        ["防务连接器", "航天/航空/舰载/兵器", "电路连接/信号传输", "稳定期"],
        ["通信连接器", "5G基站/数据中心", "射频连接/电源连接", "成熟期"],
        ["工业连接器", "工控/轨交/汽车", "矩形/圆形连接器", "成长期"],
    ]
    pdf.add_table(["业务板块", "应用领域", "主要产品", "阶段"], biz_data, [28, 40, 60, 28])

    # ===== 二、核心投资逻辑 =====
    pdf.section_title("核心投资逻辑", "二")
    pdf.sub_title('逻辑1：国产AI算力的\u201c卖铲人\u201d')
    pdf.body_text("华丰科技是华为昇腾AI服务器高速连接器的核心供应商，提供高速背板连接器、高速线模组等关键互联产品。"
                  "随着昇腾910C/910B及新一代处理器的规模化部署，单台AI服务器对高速连接器的需求量持续提升。"
                  "高速线模组（含背板+线缆+IO）单台价值量约3000-5000元，是普通服务器的5-10倍。"
                  "公司2025年营收25.28亿（+131.5%），核心驱动力正是高速线模组的放量。")

    pdf.sub_title("逻辑2：2025年业绩爆发确认")
    pdf.body_text("2025年营收25.28亿（+131.5%），净利润3.51亿（2024年亏损0.24亿），大幅扭亏。"
                  "毛利率从2024年18.47%修复至31.44%（+13pct），ROE从-1.2%飙升至21.85%。"
                  "2026Q1营收6.33亿（+56.2%），净利润1.04亿（+240%），延续高增长态势。"
                  "国信证券预计2026年全年营收有望突破35亿。")

    pdf.sub_title("逻辑3：224Gbps高速互联技术壁垒")
    pdf.body_text("高速连接器的技术壁垒体现在信号完整性设计、精密制造和材料工艺上。"
                  "华丰科技是国内少数通过华为224Gbps高速互联方案认证的连接器厂商。"
                  "下一代112G/224G PAM4高速互联是AI服务器刚需，技术门槛高，竞争格局好。"
                  "公司目前在该领域的主要竞争对手为国外厂商（安费诺、泰科电子、莫仕），国产替代空间大。")

    pdf.sub_title("逻辑4：防务业务基本盘稳健")
    pdf.body_text("防务连接器是公司的传统优势业务，覆盖航天、航空、舰载、兵器等多个领域。"
                  "该业务收入稳定、毛利率高（40%+），为公司提供持续的现金流和利润支撑。"
                  "2025年防务业务受益于国防装备信息化升级，保持稳健增长。")

    # ===== 三、财务分析 =====
    pdf.section_title("财务分析", "三")
    fin_headers = ["年度", "营收(亿)", "增速", "净利润(亿)", "毛利率", "ROE"]
    fin_data = [
        ["2021", "8.31", "-", "0.73", "-", "-"],
        ["2022", "9.84", "+18.4%", "0.97", "29.89%", "12.26%"],
        ["2023", "9.04", "-8.1%", "0.67", "27.44%", "6.14%"],
        ["2024", "10.92", "+20.8%", "-0.24", "18.47%", "-1.20%"],
        ["2025", "25.28", "+131.5%", "3.51", "31.44%", "21.85%"],
    ]
    pdf.add_table(fin_headers, fin_data, [18, 28, 22, 30, 26, 22])

    pdf.key_text("2025年是公司盈利能力的分水岭。受AI服务器高速连接器放量驱动，"
                 "营收翻倍增长，毛利率提升近13个百分点，净利润扭亏为盈并大幅增长。"
                 "营收3年CAGR（2022-2025）约37%，成长性极为突出。")

    pdf.sub_title("季度数据")
    q_headers = ["季度", "营收(亿)", "净利润(亿)", "毛利率"]
    q_data = [
        ["2024Q1", "2.26", "0.09", "15.68%"],
        ["2024Q2", "2.59", "-0.29", "19.46%"],
        ["2024Q3", "2.65", "-0.33", "16.90%"],
        ["2024Q4", "3.43", "0.29", "20.40%"],
        ["2025Q1", "4.06", "0.30", "27.90%"],
        ["2025Q2", "6.99", "1.17", "32.86%"],
        ["2025Q3", "5.54", "0.69", "30.77%"],
        ["2025Q4", "8.69", "1.34", "31.63%"],
        ["2026Q1", "6.33", "1.04", "30.34%"],
    ]
    pdf.add_table(q_headers, q_data, [28, 28, 30, 28])

    pdf.body_text("2025Q4单季营收8.69亿创历史新高，2026Q1环比回落属正常季节性。"
                  "毛利率稳定在30%+，盈利能力已形成趋势。")

    pdf.sub_title("资产负债结构")
    bs_headers = ["指标", "2024年报", "2025年报", "2026Q1"]
    bs_data = [
        ["总资产(亿)", "27.74", "38.89", "40.04"],
        ["总负债(亿)", "12.99", "20.66", "20.77"],
        ["净资产(亿)", "14.61", "18.22", "19.27"],
        ["资产负债率", "46.84%", "53.12%", "51.86%"],
    ]
    pdf.add_table(bs_headers, bs_data, [35, 40, 40, 40])

    pdf.body_text("资产负债率从2024年46.8%升至53.1%，主要系业务扩张带来的经营负债增加。"
                  "负债率在连接器行业中处于合理水平，尚无重大偿债风险。")

    # ===== 四、券商研报 =====
    pdf.section_title("券商研报观点", "四")
    rpt_headers = ["机构", "日期", "评级", "核心观点", "2026E EPS"]
    rpt_data = [
        ["山西证券", "2026/02", "买入", "国产超节点项目储备丰富，高速线模组加速放量", "1.50"],
        ["中邮证券", "2025/11", "增持", "高速线模组持续上量", "1.21"],
        ["中邮证券", "2025/09", "增持", "连接AI，触达未来", "1.41"],
        ["山西证券", "2025/09", "买入", "高速连接器开始起量，盈利能力大幅提升", "1.49"],
        ["东吴证券", "2025/05", "买入", "乘国产AI东风，高速连接器定鼎", "-"],
        ["中邮证券", "2025/05", "买入", "高速线模组产能快速爬坡", "0.76"],
        ["中邮证券", "2025/01", "买入", "224G高速互联方案助力AI腾飞", "0.69"],
        ["开源证券", "2024/08", "买入", "AI催生高速互联需求，高速背板连接器勇立潮头", "0.58"],
    ]
    pdf.add_table(rpt_headers, rpt_data, [28, 18, 15, 95, 22])

    pdf.body_text("券商一致预期：2026年EPS均值约1.40元，净利润约4.39亿。"
                  "当前股价147.24元对应2026年PE约105倍，高于券商估值中枢。")

    # ===== 五、股价与估值 =====
    pdf.section_title("股价表现与估值", "五")
    price_data = [
        ["近1年最高价", "148.50元", "今日"],
        ["近1年最低价", "47.57元", "约6个月前"],
        ["上市以来最低", "14.70元", "2023年"],
        ["最新价", "147.24元", "2026/05/19"],
        ["今日涨幅", "+11.71%", "放量大涨"],
        ["近1年涨幅", "+209.5%", "从47.57→147.24"],
        ["换手率", "19.31%", "极高"],
        ["PE(TTM)", "157.17x", "高估值"],
        ["PB", "35.22x", "极高"],
    ]
    pdf.add_table(["指标", "数值", "备注"], price_data, [35, 35, 70])

    pdf.body_text("股价从近1年低点47.57元涨至147.24元，涨幅约210%，"
                  "今日大涨11.7%，换手率19.3%，交投极为活跃。"
                  "当前PE(TTM) 157倍，PB 35倍，估值处于极高位置。"
                  "高估值隐含了市场对AI服务器连接器持续高增长的强烈预期。")

    # ===== 六、核心结论 =====
    pdf.section_title("核心结论", "六")
    pdf.key_text("综合评级：\u2b50\u2b50\u2b50\u2b50（积极偏谨慎）\n\n"
                 "核心看点：\n"
                 "1. 华为昇腾AI服务器核心连接器供应商，国产AI算力核心受益标的\n"
                 "2. 2025年营收+132%、净利扭亏为盈，基本面反转确认\n"
                 "3. 224G高速互联技术壁垒高、竞争格局好，国产替代空间大\n"
                 "4. 防务基本盘提供安全垫，AI高速连接器打开成长天花板\n\n"
                 "核心风险：\n"
                 "1. PE 157x / PB 35x，估值极度昂贵，隐含极高增长预期\n"
                 "2. 业务高度依赖华为昇腾体系，客户集中度高\n"
                 "3. 高速连接器行业竞争加剧可能压缩毛利率\n"
                 "4. 今日大涨11.7%、换手率19.3%，短期有博弈风险\n\n"
                 "老涂的跟踪建议：\n"
                 "华丰科技的业绩爆发是真实的，不是概念炒作——营收翻倍、毛利率修复、"
                 "ROE回正，基本面扎实。但当前估值已非常高（157x PE），"
                 "市场已经把未来2-3年的增长预期充分定价。建议关注回调至100-120元区间、"
                 "对应2026年PE 70-85x时介入，安全边际更充分。"
                 "核心观察指标：高速线模组季度收入占比能否持续提升至50%以上。")

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "华丰科技688629_投研报告_20260519.pdf")
    pdf.output(path)
    print(f"PDF saved: {path}")
    return path

if __name__ == "__main__":
    generate()
