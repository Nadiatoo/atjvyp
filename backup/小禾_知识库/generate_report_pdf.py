#!/usr/bin/env python3
"""蓝思科技分析报告PDF - v2 专业版"""
from fpdf import FPDF
import os

class ProPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        fp = os.path.expanduser("~/Library/Fonts/阿里巴巴普惠体 M.ttf")
        self.add_font("Ali", "", fp)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Ali", "", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 4, "蓝思科技（300433.SZ）深度分析报告 | 2026.05.17", align="L")
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-13)
        self.set_font("Ali", "", 7)
        self.set_text_color(170, 170, 170)
        self.cell(0, 5, "- 免责声明：本报告基于公开市场数据分析，不构成投资建议 -" if self.page_no() > 1 else "", align="C")
        if self.page_no() > 1:
            self.ln(3)
            self.cell(0, 5, f"{self.page_no()}", align="C")

    def h1(self, t):
        self.ln(2)
        self.set_font("Ali", "", 14)
        self.set_text_color(25, 50, 120)
        self.cell(0, 8, t, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(25, 50, 120)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.l_margin + 30, self.get_y())
        self.set_line_width(0.2)
        self.ln(4)

    def h2(self, t):
        self.ln(1)
        self.set_font("Ali", "", 10.5)
        self.set_text_color(50, 50, 50)
        self.cell(0, 7, t, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def h3(self, t):
        self.set_font("Ali", "", 9.5)
        self.set_text_color(25, 50, 120)
        self.cell(0, 6, t, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def p(self, t):
        self.set_font("Ali", "", 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, t)
        self.ln(1.5)

    def bullet(self, t):
        self.set_font("Ali", "", 9)
        self.set_text_color(50, 50, 50)
        self.cell(4)
        self.cell(3, 5, "-")
        self.multi_cell(0, 5, t)
        self.ln(0.5)

    def table(self, headers, rows, col_widths=None, font_size=8):
        if col_widths is None:
            col_widths = [self.w / len(headers)] * len(headers)
        # 表头
        self.set_font("Ali", "", font_size)
        self.set_fill_color(25, 50, 120)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(25, 50, 120)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, f" {h}", border=1, fill=True, align="C")
        self.ln()
        # 数据行
        self.set_text_color(50, 50, 50)
        alt = (245, 247, 252)
        for ri, row in enumerate(rows):
            if self.get_y() > self.h - 30:
                self.add_page()
                self.set_font("Ali", "", font_size)
                self.set_fill_color(25, 50, 120)
                self.set_text_color(255, 255, 255)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 7, f" {h}", border=1, fill=True, align="C")
                self.ln()
                self.set_text_color(50, 50, 50)
            fill = ri % 2 == 1
            if fill:
                self.set_fill_color(*alt)
            else:
                self.set_fill_color(255, 255, 255)
            for i, v in enumerate(row):
                a = "C" if i > 0 else "L"
                self.cell(col_widths[i], 6, f" {v}", border=1, fill=fill, align=a)
            self.ln()
        self.ln(3)

    def kv_table(self, rows, font_size=8):
        w = self.w - self.l_margin - self.r_margin
        cw = [w * 0.28, w * 0.72]
        alt = (245, 247, 252)
        for ri, (k, v) in enumerate(rows):
            if self.get_y() > self.h - 25:
                self.add_page()
            fill = ri % 2 == 1
            self.set_fill_color(*alt) if fill else self.set_fill_color(255, 255, 255)
            self.set_font("Ali", "", font_size)
            self.set_text_color(80, 80, 80)
            self.cell(cw[0], 6, f"  {k}", border=1, fill=fill)
            self.set_text_color(40, 40, 40)
            self.cell(cw[1], 6, f" {v}", border=1, fill=fill)
            self.ln()
        self.ln(2)

    def highlight(self, t):
        self.set_fill_color(240, 245, 255)
        self.set_draw_color(25, 50, 120)
        self.set_line_width(0.3)
        y0 = self.get_y()
        self.set_x(self.l_margin + 3)
        self.rect(self.l_margin + 1, y0, 1.2, 14, "F")
        self.set_font("Ali", "", 9)
        self.set_text_color(30, 55, 130)
        self.set_x(self.l_margin + 5)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 5, t, fill=True)
        self.ln(2)


# ════════════════════ 生成报告 ════════════════════

pdf = ProPDF()
pdf.set_auto_page_break(auto=True, margin=18)

# ── 封面 ──
pdf.add_page()
pdf.ln(20)
pdf.set_font("Ali", "", 8)
pdf.set_text_color(160, 160, 160)
pdf.cell(0, 5, "INVESTMENT RESEARCH REPORT", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font("Ali", "", 26)
pdf.set_text_color(25, 50, 120)
pdf.cell(0, 12, "蓝思科技（300433.SZ）", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.set_font("Ali", "", 15)
pdf.set_text_color(70, 70, 70)
pdf.cell(0, 9, "深 度 分 析 报 告", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_draw_color(25, 50, 120)
pdf.set_line_width(0.4)
pdf.line(60, pdf.get_y(), pdf.w - 60, pdf.get_y())
pdf.set_line_width(0.2)
pdf.ln(7)
for label, val in [
    ("报告日期", "2026年5月17日"),
    ("分析师", "小禾"),
    ("行业", "消费电子 / 人形机器人"),
    ("数据来源", "同花顺iFinD / 腾讯证券 / 东方财富Choice / 券商研报"),
]:
    pdf.set_font("Ali", "", 9)
    pdf.set_text_color(110, 110, 110)
    pdf.cell(35, 7, "", align="R")
    pdf.cell(18, 7, label, align="R")
    pdf.cell(4)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 7, val, new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)
pdf.set_font("Ali", "", 8)
pdf.set_text_color(170, 170, 170)
pdf.cell(0, 5, "股价：34.21元（2026.05.15收盘）", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 5, "总市值：1,805.86亿元", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(15)
pdf.set_font("Ali", "", 7.5)
pdf.set_text_color(180, 180, 180)
pdf.cell(0, 5, "本报告基于公开市场数据与券商研报整理分析，不构成投资建议", align="C")

# ═══════ 一、公司概况 ═══════
pdf.add_page()
pdf.h1("一、公司概况")
pdf.p("蓝思科技是全球消费电子玻璃盖板龙头企业，业务覆盖消费电子、新能源汽车、人形机器人三大赛道。2025年全年营收744.10亿元，归母净利润40.18亿元。")
pdf.table(
    ["业务板块", "产品形态", "终端应用", "核心客户"],
    [
        ["消费电子", "防护玻璃/蓝宝石/陶瓷/金属中框", "手机/平板/穿戴/笔电", "苹果、华为、小米"],
        ["汽车电子", "中控屏盖板/仪表盘盖板", "新能源汽车", "特斯拉、宝马、奔驰"],
        ["人形机器人", "关节模组/夹爪/头部总成", "人形机器人", "智元、特斯拉"],
    ],
    [28, 52, 38, 52]
)

# ═══════ 二、核心业务 ═══════
pdf.h1("二、核心业务分析")

pdf.h2("2.1 消费电子（基本盘）")
pdf.p("全球玻璃盖板龙头，核心客户覆盖苹果（长期核心供应商）、华为（P70/Mate系列）、小米（14/14Pro代工）。")
pdf.kv_table([
    ("精密加工", "公差+-0.02mm，行业领先"),
    ("生产良率", "99.5%，远高于行业平均"),
    ("全制程覆盖", "开料、热弯、精雕、抛光、强化、镀膜、丝印、贴合"),
    ("产能布局", "湖南长沙、广东东莞、江苏泰州、越南"),
])
pdf.p("近期催化：折叠屏iPhone预期、AI终端换机周期。华鑫证券5月研报明确提及「折叠屏大年叠加新兴产业共振」。")

pdf.h2("2.2 人形机器人（核心增量）")

pdf.h3("（一）智元机器人（灵犀X1）")
pdf.kv_table([
    ("角色定位", "整机组装商 + 关节模组/OmniPicker夹爪独家供应商"),
    ("当前月产能", "500台，扩产至5,000台（宁波普智二期）"),
    ("良品率/精度", "99.5%/公差+-0.02mm"),
    ("商业化", "已获中国移动订单，代工费约8万元/台"),
])

pdf.h3("（二）特斯拉 Optimus V3")
pdf.table(
    ["交付层级", "产品", "市占率", "单台价值", "产能规划"],
    [
        ["一级-零部件", "夹爪模组", ">70%", "~600美元", "长沙60万台/年"],
        ["二级-总成", "头部总成", "80%专供", "~900美元", "长沙80万台/年"],
        ["三级-整机", "整机组装", "上海40%", "~800美元/台", "长沙10万台/年(26Q2)"],
    ],
    [24, 28, 20, 28, 50]
)
pdf.p("单台综合价值量1,500-2,300美元。2027年机器人业务营收预估约60亿元。在上海临港设配套工厂，与拓普集团、三花智控等15家厂商形成供应链闭环。")

pdf.h3("（三）战略收购与前瞻布局")
pdf.p("据华鑫证券2025年12月研报，蓝思科技战略收购元拾科技，切入英伟达生态，完善AI硬件全域布局。信达证券4月研报评价「机器人及新赛道战略布局显成效」，国信证券提及机器人、AR眼镜、服务器构筑新成长曲线。")

pdf.h2("2.3 新能源汽车")
pdf.p("产品包括中控显示屏盖板、仪表盘盖板、车载触控玻璃，特斯拉为核心客户之一。")

# ═══════ 三、财务分析 ═══════
pdf.add_page()
pdf.h1("三、财务分析")

pdf.h2("3.1 年度财务数据（2021-2025）")
pdf.table(
    ["年度", "营收", "归母净利", "毛利率", "ROE", "EPS", "净利同比"],
    [
        ["2021", "452.68亿", "20.70亿", "20.92%", "4.87%", "0.42", "—"],
        ["2022", "466.99亿", "24.48亿", "19.21%", "5.66%", "0.50", "+18.3%"],
        ["2023", "544.91亿", "30.21亿", "16.63%", "6.69%", "0.61", "+23.4%"],
        ["2024", "698.97亿", "36.24亿", "15.89%", "7.64%", "0.73", "+19.9%"],
        ["2025", "744.10亿", "40.18亿", "15.99%", "7.82%", "0.79", "+10.9%"],
    ],
    [18, 28, 28, 22, 22, 22, 30]
)
pdf.p("营收近5年CAGR约13.3%。毛利率从20.92%逐步降至15.99%，反映消费电子竞争加剧。ROE从4.87%稳步提升至7.82%。")

pdf.h2("3.2 最新季度（2026Q1）")
pdf.table(
    ["指标", "2026Q1", "同比变化"],
    [
        ["营业总收入", "141.40亿", "-17.1%"],
        ["归母净利润", "-1.50亿", "-134.9%"],
        ["销售毛利率", "14.55%", "-1.5pct"],
        ["基本EPS", "-0.0284元", "—"],
    ],
    [50, 60, 50]
)
pdf.p("一季度亏损，主因为消费电子淡季叠加新业务前期投入。华鑫证券预计2026全年EPS 0.92元，隐含后三季度显著恢复。")

pdf.h2("3.3 估值指标（2026.05.15）")
pdf.kv_table([
    ("股价", "34.21元"),
    ("PE（TTM）", "52.51倍"),
    ("PB", "3.31倍"),
    ("总市值 / 流通市值", "1,805.86亿 / 1,700.13亿"),
    ("5日涨幅", "+5.88%"),
])

# ═══════ 四、券商研报 ═══════
pdf.add_page()
pdf.h1("四、券商研报观点")
pdf.p("近6个月共10家券商覆盖，全部给予买入/增持评级：")
pdf.table(
    ["日期", "机构", "评级", "26E EPS", "27E EPS"],
    [
        ["2026.05.13", "华鑫证券", "买入", "0.92", "1.30"],
        ["2026.04.12", "爱建证券", "买入", "1.15", "1.41"],
        ["2026.04.06", "中银证券", "买入", "1.00", "1.40"],
        ["2026.04.03", "信达证券", "买入", "1.15", "1.38"],
        ["2026.01.12", "爱建证券", "买入", "1.35", "1.59"],
        ["2025.12.31", "爱建证券", "买入", "1.35", "1.59"],
        ["2025.12.23", "中邮证券", "买入", "1.29", "1.59"],
        ["2025.12.18", "华鑫证券", "买入", "1.29", "1.58"],
        ["2025.11.23", "华金证券", "买入", "1.31", "1.62"],
        ["2025.11.05", "国信证券", "增持", "1.32", "1.63"],
    ],
    [28, 28, 18, 28, 28]
)
pdf.p("2026年一致预期EPS约1.18元，对应PE约29倍。2027年一致预期EPS约1.51元，对应PE约22.7倍。")
pdf.highlight("核心主题词云：折叠屏大年、机器人量产、AR眼镜、服务器、元拾科技/英伟达生态、CES 2026前沿进展、AI终端创新")

# ═══════ 五、行业地位 ═══════
pdf.h1("五、行业地位与竞争壁垒")
pdf.kv_table([
    ("制造精度", "公差+-0.02mm，消费电子与机器人模组的底层共性技术"),
    ("产能规模", "长沙基地机器人模组规划产能60-80万台/年"),
    ("良率水平", "99.5%，远超行业平均"),
    ("客户认证", "苹果、华为、特斯拉等顶级客户，切换成本极高"),
    ("技术复用", "精密玻璃加工直接迁移至机器人结构件"),
    ("双线卡位", "同时锁定智元（国产）和特斯拉（海外）"),
])
pdf.p("竞争格局：消费电子与伯恩光学双寡头；机器人精密结构件切入壁垒高，跨界良率优势暂难复制。")

# ═══════ 六、盈利预测 ═══════
pdf.h1("六、盈利预测与估值区间")
pdf.p("基于券商一致预期（2026E EPS均值1.18元），不同情境下的合理估值区间：")
pdf.table(
    ["情景", "假设条件", "合理PE", "目标价", "较现价空间"],
    [
        ["保守", "消费电子复苏不及预期", "25x", "29.50元", "-13.8%"],
        ["中性", "机器人量产有序推进", "30x", "35.40元", "+3.5%"],
        ["乐观", "机器人超预期+折叠屏催化", "35x", "41.30元", "+20.7%"],
    ],
    [24, 56, 24, 28, 28]
)
pdf.p("以当前股价34.21元为基准，中性情景下基本合理，上行需等待盈利拐点确认。")

# ═══════ 七、风险 ═══════
pdf.h1("七、风险提示")
for r in [
    "经营风险：2026Q1已出现亏损，下半年能否盈利修复存不确定性",
    "量产风险：智元/特斯拉出货目标能否兑现存不确定性",
    "周期波动：苹果/华为订单节奏影响基本盘业绩",
    "竞争风险：伯恩光学等同业在玻璃盖板领域持续竞争",
    "产能消化：60-80万台/年机器人产能基于远期预期",
    "估值压力：TTM PE 52.5倍处于较高水平",
]:
    pdf.bullet(r)

# 保存
out = os.path.expanduser("~/.hermes/knowledge_base/蓝思科技分析报告_20260517.pdf")
pdf.output(out)
print(f"Done: {out}")
print(f"Pages: {pdf.page_no()}")
