#!/usr/bin/env python3
"""弘信电子分析报告PDF v4 (完整版)"""
from fpdf import FPDF
import os

class ProPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        fp = os.path.expanduser("~/Library/Fonts/阿里巴巴普惠体 M.ttf")
        self.add_font("Ali", "", fp)

    def header(self):
        if self.page_no() <= 1: return
        self.set_font("Ali", "", 7); self.set_text_color(150, 150, 150)
        self.cell(0, 4, "弘信电子（300657.SZ）深度分析报告 | 2026.05.17", align="L")
        self.ln(5); self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y()); self.ln(3)

    def footer(self):
        self.set_y(-13); self.set_font("Ali", "", 7); self.set_text_color(170, 170, 170)
        if self.page_no() > 1:
            self.cell(0, 5, "- 本报告基于公开市场数据分析，不构成投资建议 -", align="C")
            self.ln(3); self.cell(0, 5, f"{self.page_no()}", align="C")

    def h1(self, t):
        self.ln(2); self.set_font("Ali", "", 14); self.set_text_color(25, 50, 120)
        self.cell(0, 8, t, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(25, 50, 120); self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.l_margin + 30, self.get_y())
        self.set_line_width(0.2); self.ln(4)

    def h2(self, t):
        self.ln(1); self.set_font("Ali", "", 10.5); self.set_text_color(50, 50, 50)
        self.cell(0, 7, t, new_x="LMARGIN", new_y="NEXT"); self.ln(2)

    def h3(self, t):
        self.set_font("Ali", "", 9.5); self.set_text_color(25, 50, 120)
        self.cell(0, 6, t, new_x="LMARGIN", new_y="NEXT"); self.ln(1)

    def p(self, t):
        self.set_font("Ali", "", 9); self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, t); self.ln(1.5)

    def bullet(self, t):
        self.set_font("Ali", "", 9); self.set_text_color(50, 50, 50)
        self.cell(4); self.cell(3, 5, "-"); self.multi_cell(0, 5, t); self.ln(0.5)

    def note(self, t):
        self.set_font("Ali", "", 8); self.set_text_color(130, 130, 130)
        self.multi_cell(0, 4.5, t); self.ln(1)

    def table(self, headers, rows, col_widths=None, fs=8):
        if col_widths is None:
            col_widths = [self.w / len(headers)] * len(headers)
        self.set_font("Ali", "", fs); self.set_fill_color(25, 50, 120)
        self.set_text_color(255, 255, 255); self.set_draw_color(25, 50, 120)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, f" {h}", border=1, fill=True, align="C")
        self.ln(); self.set_text_color(50, 50, 50); alt = (245, 247, 252)
        for ri, row in enumerate(rows):
            if self.get_y() > self.h - 30:
                self.add_page(); self.set_font("Ali", "", fs); self.set_fill_color(25, 50, 120)
                self.set_text_color(255, 255, 255)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 7, f" {h}", border=1, fill=True, align="C")
                self.ln(); self.set_text_color(50, 50, 50)
            fill = ri % 2 == 1
            self.set_fill_color(*alt) if fill else self.set_fill_color(255, 255, 255)
            for i, v in enumerate(row):
                a = "C" if i > 0 else "L"
                self.cell(col_widths[i], 6, f" {v}", border=1, fill=fill, align=a)
            self.ln()
        self.ln(3)

    def kv(self, rows, fs=8):
        w = self.w - self.l_margin - self.r_margin; cw = [w*0.28, w*0.72]; alt = (245,247,252)
        for ri,(k,v) in enumerate(rows):
            if self.get_y() > self.h - 25: self.add_page()
            fill = ri % 2 == 1
            self.set_fill_color(*alt) if fill else self.set_fill_color(255,255,255)
            self.set_font("Ali","",fs); self.set_text_color(80,80,80)
            self.cell(cw[0],6,f"  {k}",border=1,fill=fill)
            self.set_text_color(40,40,40); self.cell(cw[1],6,f" {v}",border=1,fill=fill); self.ln()
        self.ln(2)


pdf = ProPDF()
pdf.set_auto_page_break(auto=True, margin=18)

# ── 封面 ──
pdf.add_page(); pdf.ln(20)
pdf.set_font("Ali","",8); pdf.set_text_color(160,160,160)
pdf.cell(0,5,"INVESTMENT RESEARCH REPORT",align="C",new_x="LMARGIN",new_y="NEXT"); pdf.ln(10)
pdf.set_font("Ali","",26); pdf.set_text_color(25,50,120)
pdf.cell(0,12,"弘信电子（300657.SZ）",align="C",new_x="LMARGIN",new_y="NEXT"); pdf.ln(2)
pdf.set_font("Ali","",15); pdf.set_text_color(70,70,70)
pdf.cell(0,9,"深 度 分 析 报 告",align="C",new_x="LMARGIN",new_y="NEXT"); pdf.ln(4)
pdf.set_draw_color(25,50,120); pdf.set_line_width(0.4)
pdf.line(60,pdf.get_y(),pdf.w-60,pdf.get_y()); pdf.set_line_width(0.2); pdf.ln(7)
for label,val in [
    ("报告日期","2026年5月17日"),("分析师","小禾"),
    ("行业","FPC / AI算力 / 机器人"),("数据来源","同花顺iFinD / 腾讯证券 / 民生证券研报"),
]:
    pdf.set_font("Ali","",9); pdf.set_text_color(110,110,110)
    pdf.cell(35,7,"",align="R"); pdf.cell(18,7,label,align="R"); pdf.cell(4)
    pdf.set_text_color(50,50,50); pdf.cell(0,7,val,new_x="LMARGIN",new_y="NEXT")
pdf.ln(6)
pdf.set_font("Ali","",8); pdf.set_text_color(170,170,170)
pdf.cell(0,5,"股价：36.17元（2026.05.15）| 总市值：174.38亿元",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.ln(15)
pdf.set_font("Ali","",7.5); pdf.set_text_color(180,180,180)
pdf.cell(0,5,"本报告基于公开市场数据与券商研报整理分析，不构成投资建议",align="C")

# ═══ 一、公司概况 ═══
pdf.add_page(); pdf.h1("一、公司概况")
pdf.p("弘信电子是国内柔性电路板（FPC）头部企业。2024年起通过子公司燧弘等切入AI算力赛道，形成「FPC + AI算力」双轮驱动格局，当年实现扭亏为盈。")
pdf.table(
    ["业务板块","2024年收入","毛利率","业务形态"],
    [["印制电路板（FPC）","30.97亿","—","手机/可穿戴/新能源车FPC软板"],
     ["AI算力","19.88亿","19.72%","AI服务器组装销售+算力资源服务"]],
    [40,28,22,80], fs=8
)
pdf.note("数据来源：民生证券2024年报点评")

# ═══ 二、核心业务 ═══
pdf.h1("二、核心业务分析")
pdf.h2("2.1 FPC主业（基本盘修复）")
pdf.table(
    ["年度","营收","归母净利","毛利率","ROE","EPS"],
    [["2021","32.03亿","-2.68亿","3.95%","-17.72%","-0.64"],
     ["2022","27.92亿","-3.08亿","4.80%","-18.00%","-0.66"],
     ["2023","34.78亿","-4.36亿","2.39%","-28.91%","-0.89"],
     ["2024","58.75亿","0.57亿","10.04%","4.60%","0.12"],
     ["2025","73.13亿","1.47亿","12.45%","11.92%","0.31"]],
    [18,28,28,24,24,28]
)
pdf.p("营收从2022年低谷27.92亿反弹至2025年73.13亿（3年CAGR约38%）。毛利率从2.39%修复至12.45%。FPC主业2024年营收30.97亿（+6.95%），修复来自产线整合优化及大客户回归。")
pdf.p("2026Q1：营收16.16亿，净利3,792万（+457.6%），毛利率12.70%，修复延续。民生证券指出AI手机/AIPC/AI眼镜等终端创新将提升FPC价值量。")

pdf.h2("2.2 AI算力业务")
pdf.p("弘信电子通过子公司燧弘等开展算力业务，是2024年扭亏的核心驱动力。")
pdf.kv([
    ("2024年算力收入","19.88亿元"),("毛利率","19.72%"),
    ("业务模式","AI服务器组装及销售 + 算力资源服务"),
    ("运营主体","燧弘等两个子公司"),
    ("产能","燧弘一期工厂年产2万台高性能AI服务器"),
    ("核心优势","GPU拿卡渠道 + 组网能力"),
    ("算力来源","英伟达 + 燧原科技（双重保障）"),
])
pdf.p("业务逻辑：弘信电子利用拿卡渠道采购GPU，结合组网能力集成AI服务器后销售或提供算力租赁服务。算力毛利率19.72%显著高于FPC，带动整体毛利率从2.39%跃升至10.04%。")
pdf.h3("营收结构拆分（2024年）")
pdf.table(
    ["业务","收入","占比"],
    [["FPC/印制电路板","30.97亿","60.9%"],
     ["AI算力","19.88亿","39.1%"]],
    [48,40,42]
)
pdf.note("合计50.85亿，与58.75亿总营收的差异可能来自CCS新能源产线等其他业务。")

pdf.h2("2.3 小米机器人供应链")
pdf.p("据公开资料，弘信电子是小米铁蛋（CyberDog）机器人的独家FPC软板供应商，用于柔性电路连接和传感器信号传输。")
pdf.note("注：小米机器人当前仍处于研发/小批量阶段，对营收贡献有限，属于远期期权逻辑。")

# ═══ 三、估值 ═══
pdf.add_page(); pdf.h1("三、估值与市场指标")
pdf.kv([("股价","36.17元"),("PE（TTM）","97.78倍"),("PB","12.27倍"),("总市值","174.38亿")])
pdf.p("民生证券盈利预测与对应PE：")
pdf.table(
    ["年度","预测EPS","对应PE"],
    [["2025E","0.68元","53倍"],["2026E","1.34元","26倍"],["2027E","1.97元","18倍"]],
    [40,40,40]
)
pdf.p("TTM PE 98倍处于较高水平。2026E PE 26倍、2027E PE 18倍，高增长预期下估值有望逐步消化。")

# ═══ 四、逻辑与风险 ═══
pdf.h1("四、核心逻辑与风险提示")
pdf.h2("核心逻辑")
pdf.bullet("FPC盈利拐点确认：毛利率从2.39%修复至12.45%，2026Q1净利+457.6%")
pdf.bullet("AI算力高增长：2024年算力收入19.88亿（占39%），毛利率19.72%，是扭亏核心驱动力")
pdf.bullet("双轮驱动格局：FPC提供修复弹性，算力提供增长弹性")
pdf.bullet("小米机器人期权价值：独家FPC软板供应商身份提供远期弹性")
pdf.bullet("混改优化治理：厦门国贸入股，融资成本有望下降")

pdf.h2("风险提示")
for r in [
    "估值偏高：TTM PE 98倍，即使2026E PE亦有26倍，安全边际不足",
    "算力可预测性低：依赖GPU拿卡渠道，供应链波动+竞争加剧风险",
    "小米机器人尚未放量：铁蛋未规模量产",
    "FPC竞争压力：毛利率修复能否持续存疑",
    "流动性有限：总市值仅174亿",
]:
    pdf.bullet(r)

out = os.path.expanduser("~/.hermes/knowledge_base/弘信电子分析报告_20260517.pdf")
pdf.output(out)
print(f"Done: {out}")
print(f"Pages: {pdf.page_no()}")
