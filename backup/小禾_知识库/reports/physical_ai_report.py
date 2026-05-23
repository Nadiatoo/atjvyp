#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""物理AI(Physical AI)产业链深度研报 | 小禾出品"""

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
        self.cell(0,8,"物理AI产业链深度研报 | 小禾 2026.05.19",align="L")
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
    pdf.set_fill_color(40,20,100); pdf.rect(0,0,210,120,"F")
    pdf.set_y(22); pdf.set_font("Ali","",26); pdf.set_text_color(255,255,255)
    pdf.cell(0,15,"物理AI (Physical AI)",align="C",ln=True)
    pdf.ln(3); pdf.set_font("Ali","",16)
    pdf.cell(0,10,"产业链深度研报",align="C",ln=True); pdf.ln(15)
    pdf.set_font("Ali","",11); pdf.set_text_color(200,200,230)
    for l in ["报告日期：2026年5月19日","分析师：小禾（Hermes Systems）",
              "数据来源：金融梦想家/券商研报/公开信息整理"]:
        pdf.cell(0,8,f"      {l}",align="C",ln=True)
    pdf.set_y(148); pdf.set_font("Ali","",8); pdf.set_text_color(120,120,120)
    pdf.multi_cell(0,5,"免责声明：本报告基于公开数据整理分析，仅供参考，不构成投资建议。",align="C")

    # 一、概念溯源
    pdf.add_page()
    pdf.section("概念溯源：黄仁勋与Physical AI","一")
    pdf.key("物理AI（Physical AI）由英伟达CEO黄仁勋在2023年3月GTC大会上首次提出，"
             "定义AI发展的三阶段：感知AI（读懂图像/语言）→ 生成式AI（创造内容）→ 物理AI（在物理世界中行动）。"
             "黄仁勋原话：\u201cAI正在经历一场革命——从读懂语言到读懂物理世界。"
             "Physical AI是能够理解物理定律、在物理世界中导航和行动的AI系统。\u201d")

    pdf.sub("发展时间线")
    tl_headers=["时间","事件","阶段"]
    tl_data=[
        ["2023.03","黄仁勋GTC 2023首次提出Physical AI概念","概念提出"],
        ["2023.05","NVIDIA发布Isaac AMR + Isaac Sim机器人平台","概念提出"],
        ["2024.03","GTC 2024发布Project GR00T（人形机器人通用基础模型）","技术验证"],
        ["2024.06","特斯拉Optimus在工厂搬运任务测试","技术验证"],
        ["2024.10","We, Robot发布会：Optimus展示集体跳舞/倒酒","技术验证"],
        ["2025.03","GTC 2025发布Cosmos世界模型（解决sim-to-real迁移）","量产冲刺"],
        ["2025.10","优必选Walker S进入比亚迪工厂实训","量产冲刺"],
        ["2026.02","两会：Physical AI首次进入国家决策视野","量产元年"],
        ["2026.04","特斯拉官宣Optimus 2026年7-8月弗里蒙特投产，年产能目标100万台","量产元年"],
        ["2026.05","中国具身智能融资已超345亿元","量产元年"],
    ]
    pdf.table(tl_headers,tl_data,[22,100,30])

    pdf.body("关键判断：黄仁勋3年前的预判正被逐一验证。")
    pdf.body("2023: AI三阶段论 → 2024: GR00T成行业标准 → 2025: Cosmos解决仿真迁移 → 2026: Optimus量产")
    pdf.body("物理AI正从「黄仁勋的概念」变成「有收入/有订单/有产能」的真实产业。")

    # 二、技术架构
    pdf.section("技术架构与产业链全貌","二")
    pdf.sub("四层技术体系")
    arch_headers=["层级","功能","关键技术","代表厂商"]
    arch_data=[
        ["基础模型层（大脑）","感知-推理-决策一体化","多模态大模型/具身智能基础模型","NVIDIA GR00T/OpenAI/SkildAI"],
        ["仿真与数据层（训练场）","合成训练数据/虚拟测试","数字孪生/物理引擎/sim-to-real","NVIDIA Cosmos/索辰科技/达索"],
        ["硬件执行层（肌肉骨骼）","机械臂/移动底盘/灵巧手","电机/丝杠/减速器/传感器","绿的谐波/双环传动/汇川"],
        ["系统集成层（神经）","AI模型与硬件深度融合","异构通信/实时控制/中间件","特斯拉/优必选/宇树"],
    ]
    pdf.table(arch_headers,arch_data,[32,42,48,48])

    pdf.body("四层中价值量最高的两层：仿真数据层（壁垒最高，毛利率近99%）和硬件执行层（成本占比73%）。")

    # 三、产业链价值分布
    pdf.section("产业链价值量分布","三")
    pdf.key("人形机器人整机价值量分配：三大核心执行器（线性+旋转+灵巧手）合计占比73%。"
             "传感器+减速器+无框力矩电机合计占整机成本60%以上。")

    val_headers=["零部件","成本占比","技术壁垒","国产替代进度","A股核心标的"]
    val_data=[
        ["无框力矩电机","~20%","高","~30%","汇川技术/步科股份"],
        ["谐波减速器","~15%","极高","~20%（绿的谐波突破）","绿的谐波(688017)"],
        ["行星滚柱丝杠","~15%","极高","<10%","双环传动(002472)/恒立液压"],
        ["六维力矩传感器","~10%","高","<10%","柯力传感/昊志机电"],
        ["3D视觉传感器","~8%","高","~20%","奥比中光/凌云光"],
        ["轴承/其他精密件","~10%","中高","~30%","五洲新春/人本股份"],
        ["电池/电控","~8%","中","~50%","宁德时代/汇川技术"],
        ["结构件/外壳","~5%","低","~80%","银宝山新等"],
        ["AI芯片/模组","~5%","极高","~10%","地平线/黑芝麻"],
        ["软件/系统","~4%","高","~15%","中科创达/东土科技"],
    ]
    pdf.table(val_headers,val_data,[30,16,16,24,90])

    pdf.sub("受益逻辑拆解")
    pdf.body("国产替代空间最大的三个方向：")
    pdf.body("  1. 谐波减速器（绿的谐波已突破，国产化率从5%提升至~20%，但仍有巨大空间）")
    pdf.body("  2. 行星滚柱丝杠（壁垒最高、国产化率最低<10%，特斯拉机器人标配）")
    pdf.body("  3. 六维力矩传感器（力控核心，国产化率<10%，单价2-5万元/个）")

    # 四、市场规模
    pdf.section("市场规模预测","四")
    ms_headers=["市场","2026E","2030E","CAGR","来源"]
    ms_data=[
        ["中国具身智能","10,904亿","—","—","沙利文"],
        ["全球人形机器人","20亿美元","—","—","—"],
        ["中国关键零部件（丝杠/电机/减速器）","—","1,037亿","+94%","—"],
        ["灵巧手","48.2亿","630.6亿","+90%","—"],
        ["物理AI仿真数据平台","—","1,806亿","—","沙利文"],
    ]
    pdf.table(ms_headers,ms_data,[42,36,36,20,26])

    # 五、A股标的分析
    pdf.add_page()
    pdf.section("A股核心标的分析","五")

    pdf.sub("5.1 仿真数据平台（壁垒最高）")
    pdf.table(["标的","代码","核心产品","营收（最近完整年）","毛利率","券商评级"],
        [["索辰科技","688507","物理AI仿真平台\u201c开物\u201d","~2.1亿","98.58%","买入（8家）"]],[24,16,50,36,20,28])

    s1_notes = """索辰科技是A股最纯正的物理AI仿真标的。「开物」平台2025年已落地收入5816万元，工程仿真软件毛利率高达98.58%。
2026Q1营收3943万元（+1.66%），订单转化有望提速。券商研报：中银/国金/山西/信达/中航等8家全部「买入」。
核心看点：国内唯一在物理AI仿真平台具备商业化能力的公司。"""
    pdf.body(s1_notes)

    pdf.sub("5.2 执行器链（确定性最高）")
    pdf.table(["标的","代码","核心产品","总市值(亿)","券商评级","定位"],
        [["绿的谐波","688017","谐波减速器","~180","买入·增持","国内精密减速器龙头"],
         ["双环传动","002472","齿轮/减速器","~150","买入","精密传动系统龙头"],
         ["汇川技术","300124","伺服电机/控制器","~1,800","买入","工控+机器人双龙头"],
         ["步科股份","688160","低压伺服/人机交互","~50","买入","移动机器人电机核心"],
         ["鸣志电器","603728","步进电机/控制","~80","买入","高端电机供应商"]],[24,16,40,24,22,48])

    pdf.body("执行器链是物理AI产业链中确定性最高的一层。核心逻辑：")
    pdf.body("  a) 占人形机器人成本73%，是价值量最高的环节")
    pdf.body("  b) 绿的谐波、双环传动已在精密传动领域占据壁垒，产品验证周期长（2-3年）")
    pdf.body("  c) 特斯拉Optimus产能目标100万台/年，对执行器的需求是百亿级增量")
    pdf.body("  d) 国产替代空间大：谐波减速器国产化率仅20%，丝杠国产化率<10%")

    pdf.sub("5.3 传感器链（国产替代弹性最大）")
    pdf.table(["标的","代码","核心产品","备注"],
        [["柯力传感","603662","六维力矩传感器","力控核心，国产化率<10%"],
         ["奥比中光","688322","3D视觉传感器","已进入机器人供应链"],
         ["凌云光","688400","工业视觉","机器视觉龙头"]],[24,20,44,80])

    # 六、三条投资主线
    pdf.add_page()
    pdf.section("三条投资主线","六")
    pdf.key("从确定性到颠覆性：执行器链 > 仿真平台 > 整机集成")

    pdf.sub("主线一：执行器链（确定性最高）")
    pdf.body("逻辑：占人形机器人成本73%，国产替代空间巨大，直接受益于特斯拉/宇树/优必选量产放量。"
             "核心标的：绿的谐波（谐波减速器）、双环传动（丝杠/齿轮）、汇川技术（伺服电机）。"
             "优势：技术壁垒高，客户验证周期长（2-3年），不易被新进入者替代。"
             "估值参考：当前绿的谐波PE约80-100倍，对应2026-2027年业绩增速50%+，PEG在2倍左右。")

    pdf.sub("主线二：仿真数据平台（壁垒最高）")
    pdf.body("逻辑：物理AI研发成本80%+花在训练数据上。仿真平台能大幅降低训练成本，"
             "是产业链中毛利率最高（98%+）的环节。谁先跑通sim-to-real的商业闭环，谁就掌握了定价权。"
             "核心标的：索辰科技（A股唯一纯正标的）。"
             "风险：收入规模尚小（2025年~2.1亿），商业化路径较长。")

    pdf.sub("主线三：整机集成（弹性最大）")
    pdf.body("逻辑：一旦技术路线收敛、量产规模扩大，整机厂商将获得最大市场空间。"
             "目前技术路线尚未收敛（特斯拉vs优必选vs宇树vs Figure），且整机厂未在A股上市。"
             "操作策略：等赢家出现——要么等特斯拉Optimus供应链A股化，要么等宇树/优必选上市。")

    # 七、政策催化剂
    pdf.section("政策催化剂","七")
    pol_headers=["时间","政策/事件","级别","对A股影响"]
    pol_data=[
        ["2025.01","工信部人形机器人创新指导意见落实","国家级","确定产业方向"],
        ["2026.02","两会：物理AI首次进国家决策视野","最高级","政策预期升温"],
        ["2026.06","Optimus弗里蒙特正式投产","产业级","万亿市场打开"],
        ["2026全年","地方机器人产业政策密集出台","省市级","各地方配套落实"],
        ["2026H2","Optimus供应商定点公告","产业级","个股直接催化"],
    ]
    pdf.table(pol_headers,pol_data,[24,46,22,60])

    # 八、核心结论
    pdf.section("核心结论","八")
    pdf.key("物理AI从黄仁勋2023年提出到2026年Tesla Optimus量产，"
             "3年完成了从概念到产业的完整闭环。这不是下一个概念，而是下一个工业革命。\n\n"

             "核心判断：\n"
             "1. 2026年是物理AI量产元年，Optimus投产是最大的催化剂\n"
             "2. 执行器链（绿的谐波/双环传动）是确定性最高的配置方向\n"
             "3. 仿真平台（索辰科技）是壁垒最高的长期标的——毛利率98%，但尚需等商业化放量\n"
             "4. 特斯拉Optimus中国供应链占比已达70%，A股供应商受益确定性最强\n"
             "5. 三条主线不冲突——执行器链吃确定性，仿真平台吃壁垒，整机集成吃弹性\n\n"

             "配置建议：\n"
             "【底仓50%】汇川技术+绿的谐波——工控+减速器双核心，受益最全面\n"
             "【弹性仓30%】双环传动+柯力传感——丝杠+传感器，国产替代弹性最大\n"
             "【观察仓20%】索辰科技——等商业化放量信号再加重仓位\n\n"

             "核心风险：\n"
             "1. 特斯拉Optimus量产能否如期达产（产能爬坡风险）\n"
             "2. 技术路线尚未完全收敛（不同厂商使用不同执行器方案）\n"
             "3. 二级市场估值已包含较高预期（绿的谐波/双环PE均在80-100x）")

    os.makedirs(OUTPUT_DIR,exist_ok=True)
    path=os.path.join(OUTPUT_DIR,"物理AI_PhysicalAI_产业链深度研报_20260519.pdf")
    pdf.output(path)
    print(f"PDF saved: {path}")
    return path

if __name__=="__main__":
    gen()
