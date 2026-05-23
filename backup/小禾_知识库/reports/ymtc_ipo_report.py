#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""长江存储IPO - A股股权与供应链深度分析"""

from fpdf import FPDF
import os

FONT_PATH = "/Users/tuqibiao/Library/Fonts/阿里巴巴普惠体 M.ttf"
OUTPUT_DIR = "/Users/tuqibiao/.hermes/knowledge_base/reports/"

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.add_font("Ali", "", FONT_PATH, uni=True)
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1: return
        self.set_font("Ali", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "长江存储IPO | A股股权与供应链深度分析 | 小禾 2026.05.19", align="L")
        self.ln(2); self.set_draw_color(200,200,200); self.line(10,self.get_y(),200,self.get_y()); self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Ali", "", 8)
        self.set_text_color(150,150,150)
        self.cell(0, 10, f"- {self.page_no()} -", align="C")

    def section_title(self, title, num=""):
        self.ln(6)
        self.set_fill_color(25, 50, 120)
        self.set_text_color(255,255,255)
        self.set_font("Ali", "", 12)
        self.cell(0, 10, f"  {num + ' ' if num else ''}{title}", fill=True, ln=True)
        self.ln(4)

    def sub_title(self, title):
        self.set_font("Ali", "", 10)
        self.set_text_color(25, 50, 120)
        self.cell(0, 8, f"\u25ce {title}", ln=True)
        self.ln(2)

    def body_text(self, text):
        self.set_font("Ali", "", 9)
        self.set_text_color(50,50,50)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def key_text(self, text):
        self.set_fill_color(235,245,255)
        self.set_font("Ali", "", 9)
        self.set_text_color(20,60,140)
        self.set_x(15)
        self.multi_cell(180, 6, text, fill=True, border=0)
        self.ln(3)

    def add_table(self, headers, data, col_widths=None):
        if col_widths is None:
            col_widths = [190/len(headers)]*len(headers)
        self.set_fill_color(25,50,120); self.set_text_color(255,255,255); self.set_font("Ali","",8)
        for i,h in enumerate(headers): self.cell(col_widths[i],7,h,border=0,fill=True,align="C")
        self.ln()
        self.set_font("Ali","",8)
        for ri,row in enumerate(data):
            if self.get_y()>265:
                self.add_page()
                self.set_fill_color(25,50,120); self.set_text_color(255,255,255); self.set_font("Ali","",8)
                for i,h in enumerate(headers): self.cell(col_widths[i],7,h,border=0,fill=True,align="C")
                self.ln()
            fill=ri%2==0
            self.set_fill_color(245,247,252) if fill else self.set_fill_color(255,255,255)
            self.set_text_color(50,50,50)
            for i,v in enumerate(row): self.cell(col_widths[i],6.5,str(v),border=0,fill=fill,align="C")
            self.ln()
        self.ln(4)


def generate():
    pdf = ReportPDF()
    pdf.set_margins(10,10,10)

    # 封面
    pdf.add_page()
    pdf.set_fill_color(0,80,60)
    pdf.rect(0,0,210,120,"F")
    pdf.set_y(25)
    pdf.set_font("Ali","",26)
    pdf.set_text_color(255,255,255)
    pdf.cell(0,15,"长江存储 IPO",align="C",ln=True)
    pdf.ln(3)
    pdf.set_font("Ali","",14)
    pdf.cell(0,10,"A股股权与供应链标的深度分析",align="C",ln=True)
    pdf.ln(15)
    pdf.set_font("Ali","",11)
    pdf.set_text_color(200,220,210)
    for l in ["报告日期：2026年5月19日","分析师：小禾（Hermes Systems）",
              "覆盖范围：股权相关+设备+材料+封测+配套","数据来源：公开信息整理"]:
        pdf.cell(0,8,f"      {l}",align="C",ln=True)
    pdf.set_y(148)
    pdf.set_font("Ali","",8)
    pdf.set_text_color(120,120,120)
    pdf.multi_cell(0,5,"免责声明：本报告基于公开数据整理分析，仅供参考，不构成投资建议。",align="C")

    # 一、长江存储IPO全景
    pdf.add_page()
    pdf.section_title("长江存储IPO全景","一")
    pdf.key_text("长江存储（YMTC - Yangtze Memory Technologies Co., Ltd.）是中国最大的NAND Flash存储器制造商，"
                 "也是全球NAND Flash市场第六大参与者（仅次于三星/SK海力士/美光/铠侠/WD）。"
                 "公司总部位于武汉，专注于3D NAND闪存芯片的研发、生产和销售。"
                 "2025-2026年，公司正式启动科创板IPO进程。")

    info_data = [
        ["公司全称","长江存储科技有限责任公司"],
        ["总部","武汉（国家存储器基地）"],
        ["核心产品","3D NAND Flash（232层/300+层）"],
        ["全球地位","NAND市场第6位，国产NAND唯一规模量产"],
        ["上市板块","科创板"],
        ["估值参考","市场预期估值2000-3000亿元"],
        ["保荐机构/承销","（以官方公告为准）"],
        ["募资用途","产能扩张/技术研发/补充流动资金"],
    ]
    pdf.add_table(["项目","内容"], info_data,[40,150])

    pdf.sub_title("IPO驱动逻辑")
    pdf.body_text("1. 资本开支需求：3D NAND产线（武汉基地一二三期）总投资超2400亿元，后续扩产仍需大量资金")
    pdf.body_text("2. 国家战略支持：存储芯片国产化是国家集成电路战略的核心环节，IPO获得政策支持")
    pdf.body_text("3. 业绩改善预期：随着NAND价格周期回暖+232层以上产品量产，盈利能力有望改善")
    pdf.body_text("4. 股东退出需求：大基金一期二期、湖北国资等前期投资方有退出需求")

    # 二、股权链A股标的
    pdf.section_title("股权链A股标的","二")
    pdf.sub_title("直接/间接持股关系")
    pdf.body_text("长江存储的股权结构较为复杂，经历紫光集团重整后，主要股东包括：")
    pdf.body_text("  1) 紫光集团（北京智广芯控股）- 通过紫光存储/紫光展锐间接持股")
    pdf.body_text("  2) 国家集成电路产业投资基金（大基金一期+二期）- 合计持股约20%+")
    pdf.body_text("  3) 湖北科技投资集团（湖北科投）- 湖北国资代表")
    pdf.body_text("  4) 国开金融等政策性金融机构")

    own_headers = ["A股标的", "代码", "股权关联方式", "关联强度"]
    own_data = [
        ["中芯国际","688981","中芯聚源间接投资；工艺协同", "\u2605\u2605\u2605"],
        ["兆易创新","603986","NOR Flash龙头，NAND产业链协同；传闻参股", "\u2605\u2605\u2605"],
        ["深科技","000021","沛顿存储封测，与长江存储业务协同", "\u2605\u2605"],
        ["太极实业","600667","十一科技提供洁净室工程服务", "\u2605\u2605"],
        ["北京君正","300223","ISSI（DRAM）产业链协同", "\u2605"],
        ["通富微电","002156","存储封测，间接供应链关系", "\u2605"],
    ]
    pdf.add_table(own_headers, own_data,[26,18,96,24])

    pdf.body_text("注：长江存储IPO的直接股权关系较为封闭（非上市公司直接持股），"
                  "A股公司的关联更多体现在产业链协同和间接投资。大基金概念的传导效应值得关注。")

    # 三、设备供应链
    pdf.section_title("设备供应链A股标的","三")
    pdf.sub_title("核心国产设备供应商")
    pdf.body_text("3D NAND Flash制造是半导体制造中工艺步骤最多、设备需求量最大的品类之一。"
                  "一片3D NAND晶圆需要经过800-1000道工艺步骤，是逻辑芯片（200-400步）的2-3倍。"
                  "长江存储的扩产将显著拉动国产半导体设备需求。")

    eq_headers = ["A股标的", "代码", "核心产品", "在长江存储的验证状态", "受益弹性"]
    eq_data = [
        ["北方华创","002371","刻蚀/薄膜/氧化/清洗", "核心供应商，多产品线验证通过", "\u2605\u2605\u2605\u2605\u2605"],
        ["中微公司","688012","CCP/ICP刻蚀设备", "3D NAND高深宽比刻蚀关键设备", "\u2605\u2605\u2605\u2605\u2605"],
        ["拓荆科技","688072","CVD/PVD薄膜沉积", "多层堆叠ONON沉积必需", "\u2605\u2605\u2605\u2605"],
        ["华海清科","688120","CMP抛光设备", "存储平坦化工艺核心设备", "\u2605\u2605\u2605\u2605"],
        ["盛美上海","688082","单片/槽式清洗设备", "已获批量订单", "\u2605\u2605\u2605\u2605"],
        ["芯源微","688037","涂胶显影设备", "可与光刻机配套", "\u2605\u2605\u2605"],
        ["万业企业","600641","离子注入机（凯世通）", "掺杂工艺，验证中", "\u2605\u2605\u2605"],
        ["中科飞测","688361","检测设备", "良率控制关键设备", "\u2605\u2605"],
        ["精测电子","300567","半导体量测设备", "上海精测子公司", "\u2605\u2605"],
        ["华兴源创","688001","测试设备", "晶圆级测试", "\u2605\u2605"],
    ]
    pdf.add_table(eq_headers, eq_data,[24,18,42,52,24])

    pdf.body_text("关键判断：3D NAND刻蚀+CVD+CMP是需求最大的三大设备品类，"
                  "中微公司（刻蚀）和北方华创（综合平台）受益确定性最高。"
                  "华海清科和拓荆科技作为细分品类龙头，壁垒同样很高。")

    # 四、材料供应链
    pdf.section_title("材料供应链A股标的","四")
    mt_headers = ["A股标的", "代码", "核心产品", "在长江存储的验证状态", "受益弹性"]
    mt_data = [
        ["雅克科技","002409","前驱体/光刻胶", "High-k前驱体核心供应商", "\u2605\u2605\u2605\u2605\u2605"],
        ["沪硅产业","688126","300mm大硅片", "国产硅片核心供应商", "\u2605\u2605\u2605\u2605"],
        ["安集科技","688019","CMP抛光液/刻蚀液", "3D NAND抛光需求极大", "\u2605\u2605\u2605\u2605"],
        ["鼎龙股份","300054","CMP抛光垫", "已通过验证，批量供货", "\u2605\u2605\u2605\u2605"],
        ["华特气体","688268","电子特气（氟基/硅基）", "刻蚀/沉积工艺必需", "\u2605\u2605\u2605"],
        ["金宏气体","688106","电子特气", "大宗气体+电子特气", "\u2605\u2605\u2605"],
        ["彤程新材","603650","光刻胶", "ArF光刻胶验证中", "\u2605\u2605"],
        ["南大光电","300346","MO源/前驱体/光刻胶", "多品类推进", "\u2605\u2605"],
        ["立昂微","605358","硅片/外延片", "产品验证中", "\u2605\u2605"],
        ["凯美特气","002549","电子特气", "CO2/高纯气体", "\u2605"],
    ]
    pdf.add_table(mt_headers, mt_data,[24,18,38,52,24])

    pdf.body_text("关键判断：前驱体、硅片、CMP材料是为三大材料消耗量最大品类。"
                  "雅克科技（前驱体）和安集科技（CMP液）在3D NAND中单晶圆消耗量远超逻辑芯片，弹性最突出。"
                  "硅片方面，沪硅产业是国产大硅片龙头，长江存储扩产直接拉动。")

    # 五、封测与配套
    pdf.section_title("封测与配套服务","五")
    svc_headers = ["A股标的","代码","服务内容","受益弹性"]
    svc_data = [
        ["长电科技","600584","存储芯片封测", "\u2605\u2605\u2605"],
        ["通富微电","002156","存储芯片封测", "\u2605\u2605\u2605"],
        ["深科技","000021","沛顿存储封测", "\u2605\u2605"],
        ["太极实业","600667","洁净室工程（十一科技）", "\u2605\u2605"],
        ["中国海诚","002116","工程服务", "\u2605"],
        ["华大九天","301269","EDA软件", "\u2605\u2605"],
    ]
    pdf.add_table(svc_headers, svc_data,[24,18,82,40])

    # 六、产业链总览
    pdf.section_title("产业链总览与受益层次","六")
    pdf.sub_title("三层受益逻辑")
    pdf.body_text("第一层：直接股权受益（弹性最大，不确定性最高）")
    pdf.body_text("  通过大基金等通道传导，中芯国际/兆易创新等产业链龙头最先受益于IPO估值重估")
    pdf.body_text("第二层：设备材料订单受益（确定性最高，弹性中等）")
    pdf.body_text("  北方华创/中微公司/雅克科技/安集科技等，长江存储扩产直接拉动订单增长")
    pdf.body_text("  这是本轮IPO题材中基本面支撑最硬的层次")
    pdf.body_text("第三层：比价效应受益（弹性小，但安全）")
    pdf.body_text("  其他存储产业链标的（深科技/长电科技等），受板块情绪催化上涨")

    pdf.sub_title("标的梯队划分（综合确定性和弹性）")
    tier_headers = ["梯队","标的","逻辑","建议关注"]
    tier_data = [
        ["S级（核心）","北方华创/中微公司","设备国产化最大受益，确定性最强","\u2b50\u2b50\u2b50\u2b50\u2b50"],
        ["A级（高弹性）","雅克科技/安集科技/拓荆科技/华海清科","材料+CVD+CMP，高价值耗材","\u2b50\u2b50\u2b50\u2b50"],
        ["B级（中等）","盛美上海/沪硅产业/鼎龙股份/芯源微","细分赛道龙头，验证通过","\u2b50\u2b50\u2b50"],
        ["C级（偏概念）","万业企业/兆易创新/深科技/太极实业","股权关联或间接受益","\u2b50\u2b50"],
    ]
    pdf.add_table(tier_headers, tier_data,[22,60,62,34])

    # 七、风险提示
    pdf.section_title("风险提示","七")
    pdf.body_text("1. IPO时间不确定性：从提交到过会到发行，周期可能长达6-12个月，题材催化节奏难以把握")
    pdf.body_text("2. 股权关系不透明：长江存储未上市，股权结构信息有限，A股中的'股权概念股'可能存在夸大成份")
    pdf.body_text("3. NAND价格周期：存储芯片强周期行业，价格下行周期中公司盈利能力受损，可能影响IPO估值")
    pdf.body_text("4. 设备国产化进度：部分关键设备（光刻机等）仍受制于海外供应，扩产进度存在不确定性")
    pdf.body_text("5. 板块前期涨幅已较大：设备材料板块2025-2026年已有较大涨幅，需注意追高风险")

    # 核心结论
    pdf.section_title("核心结论","八")
    pdf.key_text("长江存储IPO是2026年A股半导体领域最重要的标志性事件之一。\n\n"
                 "短期看题材催化：IPO申报→受理→问询→过会→注册→发行，每个节点都会"
                 "对设备材料板块形成情绪提振。\n\n"
                 "中期看业绩兑现：设备材料公司的订单增长不是概念，而是长江存储真实扩产的"
                 "结果。北方华创、中微公司的业绩弹性最确定。\n\n"
                 "长期看产业格局：长江存储上市后将成为科创板市值最大的半导体公司之一，"
                 "带动整个存储产业链的估值重估。\n\n"
                 "操作建议：\n"
                 "  1) 稳健配置：北方华创、中微公司（设备双龙头，确定性最强）\n"
                 "  2) 弹性配置：雅克科技、鼎龙股份（材料耗材，3D NAND消耗量大）\n"
                 "  3) 事件驱动：关注IPO各里程碑节点前后板块催化\n"
                 "  4) 注意风险：不在大涨后追高，利用回调分批建仓")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "长江存储IPO_股权供应链深度分析_20260519.pdf")
    pdf.output(path)
    print(f"PDF saved: {path}")
    return path

if __name__ == "__main__":
    generate()
