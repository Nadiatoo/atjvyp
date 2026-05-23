#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""芯朋微(688508.SH) 投研报告 V2 - 含DRMOS/服务器电源深度分析"""

from fpdf import FPDF
import os, datetime

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
        self.cell(0, 8, "芯朋微(688508.SH) 投研报告 V2 | 小禾出品 2026.05.19", align="L")
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
    pdf.set_fill_color(25, 50, 120)
    pdf.rect(0, 0, 210, 120, "F")
    pdf.set_y(28)
    pdf.set_font("Ali", "", 28)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "芯朋微 (688508.SH)", align="C", ln=True)
    pdf.ln(3)
    pdf.set_font("Ali", "", 16)
    pdf.cell(0, 10, "深度投研报告 V2", align="C", ln=True)
    pdf.ln(5)
    pdf.set_font("Ali", "", 10)
    pdf.cell(0, 8, "含 DRMOS / 服务器电源深度分析", align="C", ln=True)
    pdf.ln(12)
    pdf.set_font("Ali", "", 11)
    pdf.set_text_color(200, 215, 240)
    for l in ["报告日期：2026年5月19日", "分析师：小禾（Hermes Systems）",
              "数据来源：Tushare Pro / 腾讯证券 / 东方财富 / 中邮/西南/国信研报"]:
        pdf.cell(0, 8, f"      {l}", align="C", ln=True)
    pdf.set_y(148)
    pdf.set_font("Ali", "", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, "免责声明：本报告基于公开数据整理分析，仅供参考，不构成投资建议。", align="C")

    # ===== 一、公司概况 =====
    pdf.add_page()
    pdf.section_title("公司概况", "一")
    pdf.key_text("芯朋微（Chipown Micro-electronics，688508.SH）是国内领先的电源管理IC设计公司，"
                 "2020年登陆科创板。产品覆盖家用电器AC-DC、标准电源、工业及车规级电源管理三大市场，"
                 "已开发超过2000个型号产品。近年来向AI服务器电源领域全面布局，实现一次至三次电源全链路覆盖。")
    info_data = [
        ["公司全称", "无锡芯朋微电子股份有限公司"],
        ["股票代码", "688508.SH"],
        ["总市值/PE/PB", "~132亿 / 77.71x / 4.40x"],
        ["最新价(5/19)", "93.28元（+6.97%）"],
        ["所属行业", "半导体·电源管理IC"],
        ["总资产/负债率", "33.32亿 / 17.61%"],
        ["产品型号数", "超2000款"],
        ["知识产权", "341项有效授权"],
    ]
    pdf.add_table(["项目", "内容"], info_data, [35, 155])

    # ===== 二、DRMOS与服务器电源深度分析 =====
    pdf.section_title("DRMOS与服务器电源布局", "二")

    pdf.sub_title("2.1 服务器电源架构与DRMOS的市场定位")
    pdf.body_text("服务器电源系统分为三级架构：")
    pdf.body_text("一次电源（PSU）：将220V AC转换为48V DC，功率因数校正（PFC）+ LLC谐振变换器，"
                  "价值量约300-500元/台")
    pdf.body_text("二次电源（IBC）：将48V DC转换为12V DC，中间总线转换器，"
                  "价值量约150-250元/台")
    pdf.body_text("三次电源（POL/VRM）：将12V DC转换为CPU/GPU核心电压（<1V），"
                  "核心器件为多相控制器+DrMOS（集成驱动+MOSFET功率级），"
                  "价值量约400-800元/台（8相配置）")
    pdf.key_text("DRMOS是服务器电源中最核心、技术壁垒最高的器件之一。"
                 "一颗DrMOS集成高压侧MOSFET、低压侧MOSFET和驱动电路于单芯片，"
                 "单颗承载40-90A电流。AI服务器（8卡GPU）电源系统总成本800-1500元，"
                 "其中DrMOS+控制器占比约50-60%。")

    pdf.sub_title("2.2 芯朋微产品布局：首家完成全链路覆盖")
    pdf.key_text("2025年12月，芯朋微发布12款面向AI计算能源的核心新品，"
                 "成为国内首家完成服务器一次电源、二次电源到三次电源全链路布局的公司。"
                 "来源：中邮证券研报，2025/12/22")

    prod_headers = ["电源层级", "产品", "技术指标", "进度"]
    prod_data = [
        ["一次电源", "1700V SiC辅源/隔离驱动/SiC-GaN驱动", "面向800V HVDC系统", "发布"],
        ["一次电源", "数字PFC/LLC控制器", "高耐压AC-DC", "客户突破+量产"],
        ["二次电源", "48V输入数模混合电源芯片", "服务器/通信批量爬坡", "批量爬坡出货"],
        ["二次电源", "兆赫兹开环DCX控制器", "高频高效", "发布"],
        ["三次电源", "8/12/16多相VRM控制器", "多相控制", "发布+验证"],
        ["三次电源", "70A/90A Cu-Clip DrMOS", "集成Driver+MOSFET", "试产+量产"],
        ["三次电源", "EFuse / PoL", "大电流保护/负载点", "试产"],
    ]
    pdf.add_table(prod_headers, prod_data, [28, 62, 50, 38])

    pdf.sub_title("2.3 验证进度：已通过服务器主板厂商验证")
    pdf.body_text("根据西南证券2025年9月研报：")
    pdf.body_text("\u2022 二次电源侧：48V输入数模混合高集成电源芯片系列已在服务器和通信设备批量爬坡出货")
    pdf.body_text("\u2022 三次电源侧：EFUSE、大电流POL、多相控制器及配套DRMOS已经过服务器主板厂商验证和逐步试产")
    pdf.body_text("\u2022 工业市场营收2025H1同比增长57%，非AC-DC品类收入同比大幅提升73%")
    pdf.body_text("根据国信证券2026年3月研报：")
    pdf.body_text("\u2022 2025年新兴市场（服务器/通信/光储充/新能源车）营收同比增长50%")
    pdf.body_text("\u2022 服务器应用领域营收同比增长超4倍（从低基数起步）")
    pdf.body_text("\u2022 新品类产品（DC-DC/Driver/Digital PMIC/Power Device/Module）营收同比增长39%")

    pdf.sub_title("2.4 Cu-Clip DrMOS技术优势")
    pdf.body_text("芯朋微的DrMOS采用Cu-Clip封装技术——用铜夹取代传统金线键合，"
                  "显著降低导通电阻和寄生电感，提升电流承载能力（70-90A/相），"
                  "同时改善散热性能。这是目前DrMOS的主流先进封装方案，"
                  "MPS、英飞凌等国际龙头的同类产品同样采用Cu-Clip工艺，"
                  "证明芯朋微在该领域已对标国际水平。")

    # ===== 三、竞争格局 =====
    pdf.section_title("竞争格局分析", "三")
    comp_headers = ["公司", "DRMOS", "服务器客户", "优势", "服务器收入体量"]
    comp_data = [
        ["MPS", "量产主力", "Intel/AMD/NVIDIA", "全球标杆，全方案", ">50亿（全球）"],
        ["英飞凌", "量产主力", "全系", "功率器件王者", ">30亿（全球）"],
        ["Renesas", "量产", "全系", "方案完整", ">20亿"],
        ["杰华特", "已有", "部分验证", "国内首家突破", "~2亿（估计）"],
        ["芯朋微", "验证/试产", "验证中", "高压积累+全链路", "~1亿（估计）"],
        ["南芯科技", "消费级", "尚无", "充电芯片龙头", "0"],
    ]
    pdf.add_table(comp_headers, comp_data, [22, 20, 32, 38, 48])

    pdf.body_text('芯朋微的核心差异化：从家电AC-DC（700V高压）向服务器低压大电流DRMOS延伸，'
                  '技术路径独特。相比杰华特等直接切服务器的公司，芯朋微的底层技术积累在\u201c功率\u201d而不只是\u201c模拟\u201d，'
                  '对器件物理的理解更深。但服务器领域客户验证周期长（6-12个月），'
                  '从Design-Win到BOM大规模切换还需时间。')

    # ===== 四、财务分析 =====
    pdf.section_title("财务分析", "四")
    fin_headers = ["年度", "营收(亿)", "增速", "净利润(亿)", "毛利率", "ROE"]
    fin_data = [
        ["2020", "4.29", "-", "1.00", "37.69%", "11.34%"],
        ["2021", "7.53", "+75.5%", "2.01", "43.00%", "14.35%"],
        ["2022", "7.20", "-4.4%", "0.89", "41.15%", "6.02%"],
        ["2023", "7.80", "+8.3%", "0.56", "37.94%", "3.00%"],
        ["2024", "9.65", "+23.7%", "1.09", "36.75%", "4.47%"],
        ["2025", "11.43", "+18.5%", "1.86", "37.24%", "6.80%"],
    ]
    pdf.add_table(fin_headers, fin_data, [18, 25, 22, 30, 26, 22])

    pdf.sub_title("2025年分业务数据")
    seg_headers = ["板块", "2025收入(亿)", "占比", "增速", "毛利率"]
    seg_data = [
        ["家用电器", "7.58", "65.3%", "+22.0%", "38.7%"],
        ["标准电源", "1.71", "15.0%", "-2.0%", "22.4%"],
        ["工控功率", "2.10", "18.4%", "+27.2%", "44.6%"],
        ["伺服器/新兴市场", "大幅增长", "-", "+50%/+400%*", "-"],
    ]
    pdf.add_table(seg_headers, seg_data, [32, 35, 18, 30, 22])
    pdf.body_text("* 新兴市场（含服务器）营收同比+50%，服务器营收同比+400%（低基数）。数据来源：国信证券")

    # ===== 五、券商研报 =====
    pdf.section_title("券商研报观点", "五")
    pdf.sub_title("最新完整研报提取")
    pdf.body_text("中邮证券（2025/12/22，买入）：")
    pdf.body_text("   2025-2027E营收12.0/14.7/17.6亿，归母净利2.2/2.3/2.7亿。"
                  "核心观点：12款AI计算能源重磅新品发布，实现服务器一次到三次电源完整战略布局。"
                  "Cu-Clip DrMOS、多相VRM、EFuse、PoL系列化产品全面覆盖。")
    pdf.body_text("西南证券（2025/09/12，买入，目标价75.6元）：")
    pdf.body_text("   工业市场营收+57%，非AC-DC品类+73%。DrMOS套片已通过服务器主板厂商验证。"
                  "预测工业驱动2025-2027增速51%/40%/30%，毛利率45%/48%/49%。")
    pdf.body_text("国信证券（2026/03/18，优于大市，目标价63元）：")
    pdf.body_text("   2025年新兴市场营收+50%，其中服务器+400%。"
                  "12款AI计算能源新品覆盖全链路，首家完成服务器一二三次电源布局。"
                  "预测2026-2028归母净利1.95/2.17/2.50亿。")

    # ===== 六、增长逻辑 =====
    pdf.section_title("增长逻辑与验证指标", "六")
    pdf.sub_title("三条增长曲线")
    g_headers = ["增长曲线", "阶段", "收入占比", "增速", "确定性"]
    g_data = [
        ["家电AC-DC（基本盘）", "成熟", "~65%", "~12-15%", "高"],
        ["标准电源（补充）", "成熟", "~15%", "~20-25%", "中"],
        ["工业·服务器·车规", "成长期", "~18-20%", ">50%", "中高"],
    ]
    pdf.add_table(g_headers, g_data, [42, 18, 28, 28, 22])

    pdf.sub_title("DRMOS/服务器增长的硬数据")
    pdf.body_text("已验证的进度：")
    pdf.body_text("  a) 多相控制器（8/12/16相）+ 70A/90A Cu-Clip DrMOS 套片完成开发并通过验证 → 来源：中邮/西南")
    pdf.body_text("  b) 服务器营收2025年同比增长超4倍 → 来源：国信证券2026/03年报点评")
    pdf.body_text("  c) 新兴市场（含服务器）整体营收+50% → 来源：国信证券")
    pdf.body_text("  d) 48V输入电源芯片在服务器/通信批量爬坡出货 → 来源：西南证券")
    pdf.body_text("需验证的信号：")
    pdf.body_text("  a) 非家电收入占比能否从~35%提升至50%+")
    pdf.body_text("  b) 是否进入国内头部服务器厂商（浪潮/超聚变/新华三）BOM清单")
    pdf.body_text("  c) 季度营收能否突破3.5亿（当前单季2.4-3.0亿）")
    pdf.body_text("  d) 毛利率能否维持在37%以上（竞争加剧可能压制）")

    # ===== 七、核心结论 =====
    pdf.section_title("核心结论", "七")
    pdf.key_text("综合评级：\u2b50\u2b50\u2b50（中性偏积极）\n\n"
                 "核心看点：\n"
                 "1. 服务器电源全链路布局国内第一，12款AI新品对标MPS/英飞凌\n"
                 "2. 2025年服务器营收同比+400%，新兴市场+50%，第二曲线已在兑现\n"
                 "3. 家电基本盘稳固（65%收入），毛利率37%，现金牛业务支撑转型\n"
                 "4. 17.6%负债率，无有息负债，财务极度健康\n\n"
                 "关键风险：\n"
                 "1. PE 77.7x/TTM已充分反映服务器预期，即使2026E也达42-56x\n"
                 "2. 2026Q1净利润同比-66%，季度波动大\n"
                 "3. 服务器领域竞争激烈（MPS/杰华特），客户切换周期长\n"
                 "4. 服务器收入占比仍低（估计<10%），尚不足以影响整体估值\n\n"
                 "老涂的跟踪建议：\n"
                 "盯紧下文三个季度非家电收入占比。如果工业+服务器收入占比从当前~18%提升到25-30%，"
                 "且毛利率持续修复，则第二曲线的逻辑进一步强化。当前股价93元已反映不少预期，"
                 "建议等回调或季度数据验证后再考虑介入。")

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "芯朋微688508_深度研报V2_20260519.pdf")
    pdf.output(path)
    print(f"PDF saved: {path}")
    return path

if __name__ == "__main__":
    generate()
