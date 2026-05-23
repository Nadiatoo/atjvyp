#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""长江存储IPO × 野村全球存储框架 | 整合深度分析"""

from fpdf import FPDF
import os

FONT_PATH = "/Users/tuqibiao/Library/Fonts/阿里巴巴普惠体 M.ttf"
OUTPUT_DIR = "/Users/tuqibiao/.hermes/knowledge_base/reports/"

class PDF(FPDF):
    def __init__(self):
        super().__init__("P","mm","A4")
        self.add_font("Ali","",FONT_PATH,uni=True)
        self.set_auto_page_break(auto=True,margin=25)

    def header(self):
        if self.page_no()==1: return
        self.set_font("Ali","",8); self.set_text_color(120,120,120)
        self.cell(0,8,"长江存储IPO × 野村全球存储框架 | 整合分析 | 小禾 2026.05.19",align="L")
        self.ln(2); self.set_draw_color(200,200,200); self.line(10,self.get_y(),200,self.get_y()); self.ln(4)

    def footer(self):
        self.set_y(-15); self.set_font("Ali","",8); self.set_text_color(150,150,150)
        self.cell(0,10,f"- {self.page_no()} -",align="C")

    def section(self,t,num=""):
        self.ln(6); self.set_fill_color(25,50,120); self.set_text_color(255,255,255)
        self.set_font("Ali","",12)
        self.cell(0,10,f"  {num+' ' if num else ''}{t}",fill=True,ln=True); self.ln(4)

    def sub(self,t):
        self.set_font("Ali","",10); self.set_text_color(25,50,120)
        self.cell(0,8,f"\u25ce {t}",ln=True); self.ln(2)

    def body(self,t):
        self.set_font("Ali","",9); self.set_text_color(50,50,50)
        self.multi_cell(0,5.5,t); self.ln(2)

    def key(self,t):
        self.set_fill_color(235,245,255); self.set_font("Ali","",9)
        self.set_text_color(20,60,140); self.set_x(15)
        self.multi_cell(180,6,t,fill=True,border=0); self.ln(3)

    def table(self,hdr,data,cw=None):
        if cw is None: cw=[190/len(hdr)]*len(hdr)
        self.set_fill_color(25,50,120); self.set_text_color(255,255,255); self.set_font("Ali","",8)
        for i,h in enumerate(hdr): self.cell(cw[i],7,h,border=0,fill=True,align="C")
        self.ln(); self.set_font("Ali","",8)
        for ri,row in enumerate(data):
            if self.get_y()>265:
                self.add_page()
                self.set_fill_color(25,50,120); self.set_text_color(255,255,255); self.set_font("Ali","",8)
                for i,h in enumerate(hdr): self.cell(cw[i],7,h,border=0,fill=True,align="C")
                self.ln()
            self.set_fill_color(245,247,252) if ri%2==0 else self.set_fill_color(255,255,255)
            self.set_text_color(50,50,50)
            for i,v in enumerate(row): self.cell(cw[i],6.5,str(v),border=0,fill=True,align="C")
            self.ln()
        self.ln(4)

def gen():
    pdf=PDF()
    pdf.set_margins(10,10,10)

    # 封面
    pdf.add_page()
    pdf.set_fill_color(0,80,60); pdf.rect(0,0,210,120,"F")
    pdf.set_y(22); pdf.set_font("Ali","",26); pdf.set_text_color(255,255,255)
    pdf.cell(0,15,"长江存储IPO × 全球存储超级周期",align="C",ln=True)
    pdf.ln(3); pdf.set_font("Ali","",14)
    pdf.cell(0,10,"A股标的整合分析",align="C",ln=True); pdf.ln(12)
    pdf.set_font("Ali","",10); pdf.set_text_color(200,220,210)
    for l in ["报告日期：2026年5月19日","分析框架：野村证券全球存储研报(2026-05-15)+独立投研",
              "覆盖范围：股权链+设备链+材料链+封测配套","整理：小禾（Hermes Systems）"]:
        pdf.cell(0,8,f"      {l}",align="C",ln=True)
    pdf.set_y(148); pdf.set_font("Ali","",8); pdf.set_text_color(120,120,120)
    pdf.multi_cell(0,5,"免责声明：本报告基于公开数据整理分析，仅供参考，不构成投资建议。",align="C")

    # 一、野村全球框架：存储超级周期
    pdf.add_page()
    pdf.section("野村全球框架：存储超级周期","一")
    pdf.key("野村核心判断：存储行业从「周期性行业」变成「结构性增长行业」，全球存储收入5年从$1,810亿增长至$17,340亿（约10倍），市场仍用旧框架定价。三星目标价上调+74%，海力士+71%。")

    pdf.sub("需求端：乘数效应")
    pdf.table(["变量","驱动逻辑","增长弹性"],
        [["Token消耗","简单翻译40token→1h视频1亿token，差250万倍","指数级"],
         ["Agentic AI","自主Agent使单用户Token消耗再放大10-100倍","指数级"],
         ["企业AI+主权AI","全球企业AI部署+各国主权AI建设，不依赖消费端","结构性"],
         ["KV-cache","推理侧内存需求随上下文长度平方级增长","超线性"]],[34,106,28])

    pdf.sub("供给端：结构性约束")
    pdf.table(["公司","2024产能(千片/月)","2028F产能","年均增速"],
        [["三星","704","910","+7%"],["SK海力士","474","803","+14%"],
         ["美光","345","560","+13%"],["长鑫CXMT","200","500","+26%"],
         ["行业合计","1,723","2,981","+15%"]],[32,32,32,32])

    pdf.body("核心矛盾：DRAM产能CAGR仅15%，而AI驱动的存储需求可能增长数千倍。HBM从2024年181千片扩至2028年900千片，但HBM挤占commodity DRAM产能，供给越扩越紧。")

    pdf.sub("LTA框架：最重要的新变量")
    pdf.table(["维度","历史LTA","本轮LTA"],[["合同期","1年以内","3-5年"],["预付款","无","有"],
        ["Capex支持","无","CSP承担部分扩产投资"],["取消代价","低","高，难以退出"]],[30,70,68])
    pdf.body("野村判断：LTA不是存储厂「求来的」，而是客户「需要的」。需求端已经超过中长期供给能力，反而强化了存储厂的议价权。")

    # 二、长江存储IPO在超级周期中的定位
    pdf.add_page()
    pdf.section("长江存储IPO在超级周期中的定位","二")
    pdf.key("野村框架中唯一提到的中国存储公司是长鑫（CXMT，DRAM），未直接覆盖长江存储（NAND）。但NAND的AI弹性正在被市场重新认识——NAND offloading（容量比HBM高100倍）是解决推理侧内存瓶颈的关键方案。")

    pdf.sub("全球NAND市场格局")
    pdf.table(["排名","公司","市场份额","产品类型","中国替代进度"],
        [["1","三星","~34%","全线NAND/SDD","—"],["2","SK海力士(Solidigm)","~20%","全线NAND/SDD","—"],
         ["3","铠侠(Kioxia)","~15%","消费级/企业级","—"],["4","西部数据","~13%","消费级/企业级","—"],
         ["5","美光","~11%","全线NAND","—"],["6","长江存储YMTC","~7%","消费级/企业级SSD","国产唯一"]],[16,28,20,38,44])

    pdf.body("长江存储是全球NAND市场第6大厂商，也是唯一实现3D NAND规模量产的国产厂商。公司在232层3D NAND技术上已追平国际主流，300+层产品在研。IPO正值全球存储超级周期启动，估值窗口极佳。")

    pdf.sub("野村框架下YMTC的三重利好")
    ly_headers=["利好维度","具体逻辑","对A股影响"]
    ly_data=[
        ["行业估值重估","全球存储收入5年10倍，三星目标+118%，\n整体存储板块估值中枢上移","A股存储链标的获估值锚定提升"],
        ["NAND AI需求爆发","NAND offloading/HBF解决推理内存瓶颈，\nYMTC是国产NAND唯一标的","长存上市后产业链标的重估"],
        ["LTA合同制","3-5年长协+预付款，降低盈利波动，\n改善募资条件和发行估值","设备材料公司订单可见性提升"],
    ]
    pdf.table(ly_headers,ly_data,[30,90,48])

    # 三、A股标的整合
    pdf.add_page()
    pdf.section("A股标的整合分析","三")
    pdf.key("在野村「存储超级周期」框架下，A股受益标的需要重新分层。核心逻辑从「长江存储IPO事件驱动」升级为「全球存储结构性增长的长期配置」。")

    pdf.sub("S级：全球框架下的核心持仓")
    pdf.table(["标的","代码","野村框架下的逻辑","目标市值空间评估"],
        [["北方华创","002371","无论YMTC/CXMT/三星扩产，综合设备平台均受益。\n2028年全球DRAM产能+73%，设备需求同步增长","已是大市值龙头，看PE重估"],
         ["中微公司","688012","3D NAND高深宽比刻蚀与HBM先进封装刻蚀\n是AI存储时代最关键的两大设备工艺","国产刻蚀龙头，估值对标海外"],
         ["雅克科技","002409","前驱体+光刻胶，3D NAND单晶圆消耗量\n是逻辑芯片3-5倍，HBM带来增量","耗材属性，量价齐升弹性大"]],[26,22,94,36])

    pdf.sub("A级：细分赛道龙头")
    pdf.table(["标的","代码","逻辑","备注"],
        [["安集科技","688019","CMP液+刻蚀液，3D NAND多层结构抛光需求大","耗材，消耗量随层数提升"],
         ["鼎龙股份","300054","CMP抛光垫，国产替代刚突破","通过长存验证，放量期"],
         ["拓荆科技","688072","CVD薄膜沉积，ONON堆叠关键","3D NAND层数越多需求越大"],
         ["华海清科","688120","CMP设备，存储平坦化核心","与安集形成设备+材料组合"],
         ["沪硅产业","688126","大硅片，存储基本盘","长存扩产直接拉动硅片需求"]],[22,20,74,42])

    pdf.sub("B级：间接受益/偏概念")
    pdf.table(["标的","代码","逻辑"],
        [["盛美上海","688082","清洗设备，长存已有订单，受益扩产"],
         ["芯源微","688037","涂胶显影设备，可配套光刻机"],
         ["兆易创新","603986","NOR Flash龙头，产业链协同，有参股传闻"],
         ["深科技","000021","沛顿存储封测，与长存业务协同"],
         ["太极实业","600667","十一科技，长存洁净室工程"]],[22,20,108])

    # 四、投资策略
    pdf.add_page()
    pdf.section("投资策略与催化节点","四")

    pdf.sub("事件催化日历")
    pdf.table(["时间","事件","影响"],
        [["2026年6月","韩国MSCI升级","全球存储板块外资流入，A股映射"],
         ["2026年6-7月","长存IPO受理公告","最直接的板块催化，设备材料最先反应"],
         ["2026年8月","三星/海力士Q2财报","HBM盈利率兑现验证，全球框架的第一个验证点"],
         ["2026H2","长存IPO问询/过会","持续催化，关注反馈内容中产能/募投细节"],
         ["2026H2","LTA签约进展","野村框架的基础假设验证"]])

    pdf.sub("配置策略")
    pdf.key("三层仓位：\n\n"
            "【底仓·40%】北方华创+中微公司——确定性最强，全球存储扩产的刚性受益者，\n"
            "不受单一客户订单波动影响。适合持仓作为板块核心配置。\n\n"
            "【弹性仓·30%】雅克科技+安集科技+鼎龙股份——材料耗材，3D NAND单晶圆消耗量\n"
            "是逻辑芯片3-5倍，营收弹性大。且材料毛利率高（40-50%），利润弹性更大。\n\n"
            "【事件仓·30%】关注长存IPO各里程碑节点前2周布局设备材料ETF，节点后减仓。\n"
            "适合做波段增强收益。\n\n"
            "三个催化节点确定性最强：受理公告→过会→注册发行。\n"
            "每个节点前后1-2周是板块情绪最活跃的窗口。")

    pdf.sub("核心风险")
    pdf.body("1. 美国数据中心电力瓶颈（野村明确指出的最大下行风险）→ 系统性风险时板块无差别下跌")
    pdf.body("2. 长存IPO进度不及预期（审核问询周期可能拉长）→ 事件驱动时间窗口缩短")
    pdf.body("3. NAND价格波动（存储行业仍有周期性，价格下行会影响IPO估值）")
    pdf.body("4. 设备板块前期涨幅已大，注意追高风险")

    os.makedirs(OUTPUT_DIR,exist_ok=True)
    path=os.path.join(OUTPUT_DIR,"长江存储IPO_野村框架整合_20260519.pdf")
    pdf.output(path)
    print(f"PDF saved: {path}")
    return path

if __name__=="__main__":
    gen()
