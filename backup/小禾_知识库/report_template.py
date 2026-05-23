#!/usr/bin/env python3
"""
个股深度分析报告 PDF 生成引擎
用法: python3 report_template.py <data_json> <markdown_content>
输入: 数据 JSON 文件路径 + Markdown 分析内容文件路径
输出: ~/.hermes/knowledge_base/reports/{name}_分析报告_{date}.pdf
"""
import json, os, sys
from datetime import datetime
from fpdf import FPDF

FONT_PATH = os.path.expanduser("~/Library/Fonts/阿里巴巴普惠体 M.ttf")
OUTPUT_DIR = os.path.expanduser("~/.hermes/knowledge_base/reports")

# 颜色定义
DARK = (44, 62, 80)
LIGHT_ROW = (236, 240, 241)
WHITE = (255, 255, 255)
HIGHLIGHT_BLUE = (41, 128, 185)
BORDER_GRAY = (189, 195, 199)
TEXT_SUB = (52, 73, 94)


class StockReport(FPDF):

    def __init__(self, stock_name: str, report_date: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.stock_name = stock_name
        self.report_date = report_date
        self.add_font("AliPuHui", "", FONT_PATH)
        # bold 用同字体（避免同一 20MB 文件加载两次），fpdf 不支持假粗体，用同字体
        self.add_font("AliPuHui", "B", FONT_PATH)
        self.set_auto_page_break(True, 20)

    def header(self):
        if self.page_no() == 1:
            return  # 封面不显示页眉
        self.set_font("AliPuHui", "", 7)
        self.set_text_color(*BORDER_GRAY)
        self.cell(0, 5, f"{self.stock_name}  深度分析报告", align="L")
        self.cell(0, 5, self.report_date, align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("AliPuHui", "", 7)
        self.set_text_color(*BORDER_GRAY)
        self.cell(0, 10, str(self.page_no()), align="C")

    def cover_page(self):
        self.add_page()
        self.ln(50)
        self.set_font("AliPuHui", "B", 28)
        self.set_text_color(*TEXT_SUB)
        self.multi_cell(0, 14, f"{self.stock_name}\n深度分析报告", align="C")
        self.ln(10)
        self.set_draw_color(*HIGHLIGHT_BLUE)
        self.set_line_width(0.5)
        mid = self.w / 2
        self.line(mid - 25, self.get_y(), mid + 25, self.get_y())
        self.ln(10)
        self.set_font("AliPuHui", "", 14)
        self.set_text_color(*BORDER_GRAY)
        self.cell(0, 10, self.report_date, align="C")
        self.ln(6)
        self.set_font("AliPuHui", "", 10)
        self.cell(0, 8, "彪哥战法投研体系", align="C")

    def section_title(self, title: str):
        self.ln(4)
        self.set_font("AliPuHui", "B", 14)
        self.set_text_color(*DARK)
        self.set_fill_color(*DARK)
        self.set_draw_color(*DARK)
        self.cell(0, 9, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK)
        self.ln(2)

    def body_text(self, text: str):
        self.set_x(self.l_margin)
        self.set_font("AliPuHui", "", 10)
        self.set_text_color(*DARK)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 6, text, align="L")

    def highlight_box(self, title: str, content: str):
        self.ln(2)
        x0 = self.l_margin
        self.set_x(x0)
        y0 = self.get_y()
        # 蓝色左侧竖线
        self.set_fill_color(*HIGHLIGHT_BLUE)
        self.set_draw_color(*HIGHLIGHT_BLUE)
        self.rect(x0, y0, 2, 14, style="DF")
        # 标题
        self.set_xy(x0 + 5, y0 + 1)
        self.set_font("AliPuHui", "B", 10)
        self.set_text_color(*HIGHLIGHT_BLUE)
        self.cell(0, 6, title)
        # 内容
        self.set_xy(x0 + 5, y0 + 8)
        self.set_font("AliPuHui", "", 9)
        self.set_text_color(*DARK)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 5, 5.5, content)
        self.set_x(self.l_margin)
        self.ln(4)

    def data_table(self, headers: list, rows: list, col_widths: list = None):
        if not headers:
            return
        if not col_widths:
            col_widths = [self.w / len(headers)] * len(headers)
        total_w = sum(col_widths)
        if total_w > self.w - self.l_margin - self.r_margin:
            scale = (self.w - self.l_margin - self.r_margin) / total_w
            col_widths = [w * scale for w in col_widths]

        # 表头
        self.set_font("AliPuHui", "B", 8)
        self.set_fill_color(*DARK)
        self.set_text_color(*WHITE)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=0, fill=True, align="C")
        self.ln()

        # 数据行
        self.set_text_color(*DARK)
        for ri, row in enumerate(rows):
            if ri % 2 == 0:
                self.set_fill_color(*LIGHT_ROW)
            else:
                self.set_fill_color(*WHITE)
            self.set_font("AliPuHui", "", 8)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6.5, str(cell)[:20], border=0, fill=True, align="C")
            self.ln()
        self.ln(2)

    def parse_markdown_sections(self, md_file: str) -> list:
        """简易 Markdown 解析，返回 [(title, content), ...]"""
        if not md_file or not os.path.exists(md_file):
            return [("待分析", "分析内容尚未编写")]
        with open(md_file, encoding="utf-8") as f:
            text = f.read()

        sections = []
        current_title = ""
        current_lines = []

        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                if current_title or current_lines:
                    sections.append((current_title, "\n".join(current_lines)))
                current_title = line[3:]
                current_lines = []
            elif line.startswith("# "):
                if current_title or current_lines:
                    sections.append((current_title, "\n".join(current_lines)))
                current_title = ""
                current_lines = []
            else:
                current_lines.append(line)

        if current_title or current_lines:
            sections.append((current_title, "\n".join(current_lines)))

        return sections

    def build_report(self, data_file: str, md_file: str = None):
        with open(data_file, encoding="utf-8") as f:
            stock_data = json.load(f)

        ts_code = stock_data.get("stock_code", "")
        basic = stock_data["data"].get("basic_info", {}).get("data", {})
        fin = stock_data["data"].get("financial_data", {}).get("data", [])
        quote = stock_data["data"].get("realtime_quote", {}).get("data", {})
        reports = stock_data["data"].get("research_reports", {}).get("data", [])
        kline = stock_data["data"].get("daily_kline", {}).get("data", [])

        name = basic.get("name") or quote.get("name", ts_code)
        self.stock_name = name

        # ── 封面 ──
        self.cover_page()

        # ── 公司概况 ──
        self.add_page()
        self.section_title("一、公司概况")
        info_lines = []
        if basic.get("name"):
            info_lines.append(f"公司名称：{basic['name']}")
        if basic.get("industry"):
            info_lines.append(f"所属行业：{basic['industry']}")
        if basic.get("area"):
            info_lines.append(f"所属地区：{basic['area']}")
        if basic.get("list_date"):
            info_lines.append(f"上市日期：{basic['list_date']}")
        if basic.get("chairman"):
            info_lines.append(f"董事长：{basic['chairman']}")
        if basic.get("reg_capital"):
            info_lines.append(f"注册资本：{float(basic['reg_capital'])/1e4:.0f}万元")
        if basic.get("main_business"):
            info_lines.append(f"主营业务：{basic['main_business'][:200]}")
        self.body_text("\n".join(info_lines))

        # ── 实时行情 ──
        if quote:
            self.ln(2)
            self.highlight_box("实时行情",
                f"股价：{quote.get('price','N/A')}  涨跌幅：{quote.get('change_pct','N/A')}%  "
                f"PE：{quote.get('pe','N/A')}  总市值：{quote.get('market_cap','N/A')}")

        # ── 财务分析 ──
        self.add_page()
        self.section_title("二、财务分析")
        if fin:
            headers = ["报告期", "ROE(%)", "ROA(%)", "毛利率(%)", "净利率(%)", "EPS", "资产负债率(%)"]
            rows = []
            for f in fin:
                rows.append([
                    f.get("period", ""),
                    f"{f.get('roe',0) or 0:.2f}",
                    f"{f.get('roa',0) or 0:.2f}",
                    f"{f.get('grossprofit_margin',0) or 0:.2f}",
                    f"{f.get('netprofit_margin',0) or 0:.2f}",
                    f"{f.get('eps',0) or 0:.4f}",
                    f"{f.get('debt_to_assets',0) or 0:.2f}",
                ])
            self.data_table(headers, rows)
            self.body_text("数据来源：Tushare Pro 财务指标接口")
        else:
            self.body_text("（财务数据暂缺）")

        # ── K线趋势简述 ──
        if kline:
            recent = kline[-5:]
            if recent:
                closes = [d.get("close", 0) for d in recent]
                trend = "上涨" if closes[-1] > closes[0] else "下跌"
                self.body_text(f"近5日趋势：{trend}（{closes[0]:.2f} → {closes[-1]:.2f}）")

        # ── 券商观点 ──
        self.add_page()
        self.section_title("三、券商观点")
        if reports:
            rating_count = {}
            for rp in reports:
                r = rp.get("rating", "未评级")
                rating_count[r] = rating_count.get(r, 0) + 1
            self.body_text(f"近6个月共有 {len(reports)} 篇研报。评级分布：{rating_count}")
            self.ln(2)
            headers = ["日期", "机构", "标题", "评级"]
            rows = []
            for rp in reports[:10]:
                rows.append([
                    rp.get("date", ""),
                    rp.get("org", ""),
                    rp.get("title", "")[:30],
                    rp.get("rating", ""),
                ])
            cols = [22, 30, 70, 20]
            self.data_table(headers, rows, cols)
        else:
            self.body_text("（暂无券商研报数据）")

        # ── Markdown 分析章节 ──
        sections = self.parse_markdown_sections(md_file)
        chapter_map = {
            "公司概况": None,
            "财务分析": None,
            "券商观点": None,
        }
        for title, content in sections:
            if not title:
                continue
            self.add_page()
            self.section_title(title)
            # Markdown 表格无法在 PDF 中完美渲染，跳过表格行
            if "|" in content and "---" in content:
                text_lines = [l for l in content.split("\n") if not l.strip().startswith("|")]
                self.body_text("\n".join(text_lines))
                self.body_text("（表格数据请参考上方数据章节）")
            else:
                self.body_text(content)

        # ── 风险提示 ──
        self.add_page()
        self.section_title("风险提示")
        self.highlight_box("免责声明",
            "本报告由彪哥战法投研体系自动生成，数据来源包括 Tushare Pro、"
            "东方财富、腾讯证券等公开渠道。报告内容仅供参考，不构成投资建议。"
            "投资者应当根据自身情况独立判断，市场有风险，投资需谨慎。")

    def save_report(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        fname = f"{self.stock_name}_分析报告_{self.report_date}.pdf"
        out_path = os.path.join(OUTPUT_DIR, fname)
        self.output(out_path)
        return out_path


def main():
    if len(sys.argv) < 2:
        print("用法: python3 report_template.py <data_json> [markdown_file]")
        print("示例: python3 report_template.py data/000001_SZ_data.json analysis.md")
        sys.exit(1)

    data_file = sys.argv[1]
    md_file = sys.argv[2] if len(sys.argv) > 2 else None
    date_str = datetime.now().strftime("%Y%m%d")

    report = StockReport("", date_str)
    report.build_report(data_file, md_file)
    out = report.save_report()
    print(f"报告已生成: {out}")


if __name__ == "__main__":
    main()
