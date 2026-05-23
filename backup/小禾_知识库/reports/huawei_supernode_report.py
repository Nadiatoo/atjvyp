#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""华为超节点产业链深度分析 | 小禾出品"""

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
        self.cell(0,8,"华为超节点产业链深度分析 | 小禾 2026.05.19",align="L")
        self.ln(2); self.set_draw_color(200,200,200); self.line(10,self.get_y(),200,self.get_y()); self.ln(4)

    def footer(self):
        self.set_y(-15); self.set_font("Ali","",8); self.set_text_color(150,150,150)
        self.cell(0,10,f"- {self.page_no()} -",align="C")

    def section(self,t,num=""):
        self.ln(6); self.set_fill_color(200,60,20); self.set_text_color(255,255,255)
        self.set_font("Ali","",12)
        self.cell(0,10,f"  {num+' ' if num else ''}{t}",fill=True,ln=True); self.ln(4)

    def sub(self,t):
        self.set_font("Ali","",10); self.set_text_color(200,60,20)
        self.cell(0,8,f"\u25ce {t}",ln=True); self.ln(2)

    def body(self,t):
        self.set_font("Ali","",9); self.set_text_color(50,50,50)
        self.multi_cell(0,5.5,t); self.ln(2)

    def key(self,t):
        self.set_fill_color(255,245,235); self.set_font("Ali","",9)
        self.set_text_color(180,50,10); self.set_x(15)
        self.multi_cell(180,6,t,fill=True,border=0); self.ln(3)

    def table(self,hdr,data,cw=None):
        if cw is None: cw=[190/len(hdr)]*len(hdr)
        self.set_fill_color(200,60,20); self.set_text_color(255,255,255); self.set_font("Ali","",8)
        for i,h in enumerate(hdr): self.cell(cw[i],7,h,border=0,fill=True,align="C")
        self.ln(); self.set_font("Ali","",8)
        for ri,row in enumerate(data):
            if self.get_y()>265:
                self.add_page()
                self.set_fill_color(200,60,20); self.set_text_color(255,255,255); self.set_font("Ali","",8)
                for i,h in enumerate(hdr): self.cell(cw[i],7,h,border=0,fill=True,align="C")
                self.ln()
            self.set_fill_color(255,245,240) if ri%2==0 else self.set_fill_color(255,255,255)
            self.set_text_color(50,50,50)
            for i,v in enumerate(row): self.cell(cw[i],6.5,str(v),border=0,fill=True,align="C")
            self.ln()
        self.ln(4)

def gen():
    pdf=PDF()
    pdf.set_margins(10,10,10)

    # 封面
    pdf.add_page()
    pdf.set_fill_color(200,60,20); pdf.rect(0,0,210,120,"F")
    pdf.set_y(22); pdf.set_font("Ali","",26); pdf.set_text_color(255,255,255)
    pdf.cell(0,15,"华为超节点产业链",align="C",ln=True); pdf.ln(3)
    pdf.set_font("Ali","",14)
    pdf.cell(0,10,"深度分析与A股供应链全景",align="C",ln=True); pdf.ln(15)
    pdf.set_font("Ali","",11); pdf.set_text_color(240,210,200)
    for l in ["报告日期：2026年5月19日","分析师：小禾（Hermes Systems）",
              "数据来源：Tushare Pro/研讯社/公开信息整理","关联研报：华丰科技深度研报（同日发布）"]:
        pdf.cell(0,8,f"      {l}",align="C",ln=True)
    pdf.set_y(148); pdf.set_font("Ali","",8); pdf.set_text_color(120,120,120)
    pdf.multi_cell(0,5,"免责声明：本报告基于公开数据整理分析，仅供参考，不构成投资建议。",align="C")

    # 一、超节点是什么
    pdf.add_page()
    pdf.section("超节点技术全景","一")
    pdf.key("华为超节点（CloudMatrix）是整机柜级一体化紧耦合算力系统。"
             "核心设计：将数十至数千颗AI芯片通过自研MatrixLink总线全对等互联，"
             "形成一台逻辑统一的超级AI服务器。突破单芯片算力瓶颈，系统级算力每代5-6倍跃迁。")

    pdf.sub("Atlas 950 vs 英伟达NVL144 关键对比")
    pdf.table(["指标","华为Atlas 950","英伟达NVL144","倍数"],
        [["卡规模","8,192颗","144颗","56.8x"],
         ["总算力","6.7倍NVL144","基准","6.7x"],
         ["内存容量","1,152TB","76.8TB","15x"],
         ["互联带宽","16.3PB/s","260GB/s","62x"],
         ["量产时间","2026Q4","2026H2（计划）","—"]],[34,52,52,26])

    pdf.body("国产超节点的核心价值：用系统级优势弥补单芯片差距。"
             "昇腾910C单卡算力约为H100的60-80%，但通过超节点架构，系统层面实现了对英伟达的超越。"
             "DeepSeek V4已首发适配950超节点，单请求时延低至20ms，国产大模型+国产超节点生态正式闭环。")

    pdf.sub("2026年放量节奏")
    pdf.table(["时间","事件","关键标志"],
        [["Q2(4-6月)","384超节点小批量发货","头部OEM首批交付，互联网大厂测试"],
         ["Q3(7-9月)","Atlas 950量产","950PR芯片批量出货，规模放量"],
         ["Q4(10-12月)","950 SuperPoD上市","8192卡全光互联，单季超千台"],
         ["2027-2028","渗透率提升","超节点占AI服务器比例15%→60%"]],[20,42,108])

    # 二、整机层
    pdf.section("核心整机合作伙伴","二")
    oem_headers=["公司","代码","角色","最新价","核心看点"]
    oem_data=[
        ["华鲲振宇(高新发展)","000628","超节点整机核心集成商","—","华为昇腾最大合作伙伴之一"],
        ["四川长虹(华鲲振宇)","600839","通过华鲲振宇间接持股","—","国资背景，华为核心生态伙伴"],
        ["拓维信息","002261","兆瀚系列AI服务器","34.68","华为昇腾首批合作伙伴"],
        ["紫光股份(新华三)","000938","UniPoD S80000超节点","32.49","自研+华为双线受益"],
        ["神州数码","000034","鲲鹏/昇腾合作伙伴","—","华为企业业务总经销商"],
        ["软通动力","301236","华为核心ISV/同方服务器","—","华为生态核心软件服务商"],
    ]
    pdf.table(oem_headers,oem_data,[32,16,30,16,68])

    pdf.sub("核心拆解：华鲲振宇")
    pdf.body("华鲲振宇是华为昇腾服务器最核心的合作伙伴，由高新发展(000628)和四川长虹(600839)共同持股。"
             "在高新发展2024年收购华鲲振宇失败后，华鲲振宇目前由四川长虹通过旗下公司间接控制。"
             "华鲲振宇是华为Atlas服务器整机的主要出货通道，直接受益于超节点放量。")

    pdf.sub("核心拆解：新华三(紫光股份)")
    pdf.body("紫光股份(000938)旗下的新华三集团在2026年5月8日正式发布UniPoD S80000超节点系列，"
             "这是新华三面向AI时代打造的高性能算力平台。"
             "紫光股份同时受益于华为超节点生态（作为合作伙伴）和新华三自研超节点，双线驱动。"
             "2026年5月华鑫证券给予「买入」评级，核心逻辑是AI解决方案领导者深度受益于算力红利。")

    # 三、零部件供应链
    pdf.add_page()
    pdf.section("核心零部件供应链","三")

    pdf.sub("3.1 高速连接器（最大弹性环节）")
    pdf.key("华丰科技(688629)是华为超节点高速连接器的核心供应商。"
             "超节点内部384-8192颗芯片通过MatrixLink全互联，高速背板连接器和线模组的单台价值量"
             "是传统AI服务器的5-10倍。华丰科技的224Gbps互联方案已通过华为认证。"
             "详见同日发布的华丰科技深度研报。")

    conn_headers=["公司","代码","产品","最新价","1年涨跌"]
    conn_data=[
        ["华丰科技","688629","高速背板连接器/线模组","147.24","+209%"],
        ["鼎通科技","688668","I/O连接器/壳体","—","—"],
        ["中航光电","002179","高端连接器","—","—"],
    ]
    pdf.table(conn_headers,conn_data,[26,18,48,20,40])

    pdf.sub("3.2 散热/液冷系统")
    cool_headers=["公司","代码","产品","最新价","逻辑"]
    cool_data=[
        ["飞荣达","300602","电磁屏蔽+液冷方案","39.47","华为超节点散热核心供应商"],
        ["强瑞技术","301128","液冷解决方案","137.55","华为液冷测试设备供应商"],
        ["英维克","002837","液冷温控","—","数据中心液冷龙头"],
        ["高澜股份","300499","液冷板/冷板","—","华为超节点液冷"],
        ["中石科技","300684","导热/散热材料","—","华为散热材料供应商"],
    ]
    pdf.table(cool_headers,cool_data,[22,16,40,18,70])

    pdf.sub("3.3 PCB/背板")
    pcb_headers=["公司","代码","产品","最新价","逻辑"]
    pcb_data=[
        ["深南电路","002916","高速背板/封装基板","332.30","华为超节点背板核心供应商"],
        ["沪电股份","002463","高速PCB","—","华为AI服务器PCB"],
        ["兴森科技","002436","PCB/IC载板","—","华为PCB供应商"],
        ["鹏鼎控股","002938","FPC/HDI","—","全球PCB龙头"],
    ]
    pdf.table(pcb_headers,pcb_data,[22,16,38,20,70])

    pdf.sub("3.4 电源/供电")
    pwr_headers=["公司","代码","产品","最新价","逻辑"]
    pwr_data=[
        ["泰嘉股份","002843","服务器电源","27.31","华为服务器电源核心供应商"],
        ["欧陆通","300870","服务器电源","—","高功率服务器电源"],
        ["中国长城","000066","自主可控电源","—","国产服务器电源"],
    ]
    pdf.table(pwr_headers,pwr_data,[22,16,38,20,70])

    # 四、产业链对比
    pdf.add_page()
    pdf.section("产业链总览与受益层次","四")

    pdf.sub("价值量分布估算")
    val_headers=["环节","占超节点价值量","技术壁垒","国产替代进度"]
    val_data=[
        ["AI芯片(昇腾910C/950PR)","~50%","极高","华为自研"],
        ["整机集成","~15%","中","华鲲振宇/新华三/拓维"],
        ["高速连接器","~10%","高","华丰科技突破"],
        ["散热/液冷系统","~8%","中高","飞荣达/英维克领先"],
        ["PCB/背板","~5%","中","深南电路全球领先"],
        ["电源系统","~5%","中","泰嘉/欧陆通"],
        ["其他（结构件/线缆/软件）","~7%","中低","国产化充分"],
    ]
    pdf.table(val_headers,val_data,[32,30,24,54])

    pdf.sub("核心标的行情总览")
    mkt_headers=["标的","代码","最新价","1年高/低","涨跌幅","PE","市值"]
    mkt_data=[
        ["华丰科技","688629","147.24","148.5/123.6","+11.7%","157.2x","460亿"],
        ["紫光股份","000938","32.49","34.5/30.4","+2.1%","—","930亿"],
        ["拓维信息","002261","34.68","38.4/33.2","+2.2%","—","390亿"],
        ["飞荣达","300602","39.47","39.7/36.0","+1.8%","—","200亿"],
        ["强瑞技术","301128","137.55","215.5/128.7","+1.5%","—","100亿"],
        ["深南电路","002916","332.30","350.7/313.6","-1.1%","—","1,700亿"],
        ["泰嘉股份","002843","27.31","29.9/24.9","+5.9%","—","60亿"],
        ["工业富联","601138","68.56","74.0/61.7","-0.6%","—","1,360亿"],
    ]
    pdf.table(mkt_headers,mkt_data,[24,16,20,32,18,18,28])

    # 五、投资策略
    pdf.section("投资策略与催化节点","五")

    pdf.sub("事件催化日历")
    cal_headers=["时间","事件","影响标的"]
    cal_data=[
        ["2026年5月","无锡4台384超节点部署","华丰科技/华鲲振宇"],
        ["2026年6月","百度昆仑芯P800超节点上市","百度系/液冷供应商"],
        ["2026年7-8月","Atlas 950量产","华丰/飞荣达/泰嘉/深南"],
        ["2026年9月","华为全联接大会","全产业链催化"],
        ["2026年Q4","950 SuperPoD正式上市","最强催化，千台级放量"],
        ["2027年","渗透率15%→35%","持续订单驱动"],
    ]
    pdf.table(cal_headers,cal_data,[24,50,80])

    pdf.sub("配置建议")
    pdf.key("三层配置框架：\n\n"
             "【核心配置 50%】华丰科技(688629)+紫光股份(000938)\n"
             "华丰是超节点物理层最大弹性环节（连接器价值量+10倍），"
             "紫光是新华三自研+华为双保险。\n\n"
             "【弹性配置 30%】飞荣达(300602)+泰嘉股份(002843)\n"
             "散热和电源是超节点密度提升后的刚需环节。超节点功耗是传统8卡服务器的3-5倍，"
             "散热和电源的价值量同步翻倍。\n\n"
             "【事件配置 20%】关注华鲲振宇股权关系变化+新华三更多超节点客户公告\n"
             "华鲲振宇的控制权归属和高新发展的后续资本运作是关键变量。")

    pdf.sub("核心风险")
    pdf.body("1. 超节点放量节奏不及预期（产能爬坡、良率问题）")
    pdf.body("2. 昇腾950PR芯片供应制约（先进制程产能受限）")
    pdf.body("3. 英伟达H100/B200降价竞争（国产替代替代速度）")
    pdf.body("4. 连接器/散热/PCB等环节已有较大涨幅（华丰科技今日+11.7%）")
    pdf.body("5. 部分标的估值较高（华丰PE 157x），需关注业绩兑现能力")

    os.makedirs(OUTPUT_DIR,exist_ok=True)
    path=os.path.join(OUTPUT_DIR,"华为超节点产业链深度分析_20260519.pdf")
    pdf.output(path)
    print(f"PDF saved: {path}")
    return path

if __name__=="__main__":
    gen()
