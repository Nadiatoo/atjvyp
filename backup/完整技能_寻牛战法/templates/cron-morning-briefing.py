"""
盘前简报 · Cron 标准执行模板
==============================
寻牛战法框架下的盘前数据采集+框架分析+简报输出
依赖：zhuangjiren-seasonal-trading skill（必须已加载）
运行环境：Hermes cron（无 Chrome / 无 Eastmoney push2 / 无用户交互）

使用方式：由 cron job 直接调用小禾 agent，本文件为工作流参考
          不是被 Python 导入的模块，而是展示完整流程的参考模板
"""

# ============================================================
# 步骤一：隔夜外围市场（Sina API ✅ cron已验证）
# ============================================================

# 美股三大指数 + 核心个股
"""
curl -s 'https://hq.sinajs.cn/list=gb_$dji,gb_ixic,gb_inx,\
gb_nvda,gb_amd,gb_tsla,gb_aapl,gb_msft,gb_baba,gb_jd,\
gb_mu,gb_avgo,gb_qcom' \
  -H 'Referer: https://finance.sina.com.cn'
# 解析：名称,现价,涨跌幅(%),更新时间,涨跌额,前收盘...
"""

# 大宗商品期货
"""
curl -s 'https://hq.sinajs.cn/list=hf_CL,hf_GC,hf_SI' \
  -H 'Referer: https://finance.sina.com.cn'
# hf_CL=原油, hf_GC=黄金, hf_SI=白银
# 字段：名称,,当前价,买价,卖价,最高,最低,时间
"""

# ============================================================
# 步骤二：A股指数早盘（Sina API ✅ cron已验证）
# ============================================================

"""
curl -s 'https://hq.sinajs.cn/list=s_sh000001,s_sz399001,\
s_sz399006,s_sh000016,s_sh000688' \
  -H 'Referer: https://finance.sina.com.cn'
# 上证,深证,创业板,上证50,科创50
# 字段：名称,现价,涨跌额,涨跌幅%,成交量(手),成交额
"""

# ============================================================
# 步骤三：涨停池（AkShare ✅ cron已验证）
# ============================================================

import akshare as ak
import pandas as pd

def get_today_limitup(date_str="20260521"):
    """获取当日涨停池 + 行业分布 + 连板结构"""
    df = ak.stock_zt_pool_em(date=date_str)
    cols = list(df.columns)
    # 列索引映射（2026-05-20 验证）
    name_col   = cols[2]   # 名称
    close_col  = cols[4]   # 最新价
    ban_col    = cols[14]  # 连板数
    ind_col    = cols[15]  # 所属行业
    seal_col   = cols[9]   # 封板资金(元)
    
    print(f"涨停总数: {len(df)}")
    print(f"\n行业分布 TOP10:")
    print(df[ind_col].value_counts().head(10))
    print(f"\n连板分布:")
    print(df[ban_col].value_counts().sort_index())
    print(f"\n高连板(≥3板):")
    for _, r in df.iterrows():
        if r[ban_col] >= 3:
            print(f"  {r[name_col]}({r[ind_col]}): {r[ban_col]}板, "
                  f"封板{r[seal_col]/1e8:.2f}亿")
    
    # 检测板块效应：同一板块涨停数≥3为有板块效应
    sector_counts = df[ind_col].value_counts()
    strong_sectors = sector_counts[sector_counts >= 3]
    print(f"\n板块效应(≥3只):")
    if len(strong_sectors) > 0:
        for s, c in strong_sectors.items():
            names = df[df[ind_col] == s][name_col].tolist()
            has_mega = any(
                df[(df[ind_col] == s) & (df[seal_col] > 5e8)].shape[0] > 0
            )
            mega = " ★中军确认" if has_mega else ""
            print(f"  {s}: {c}只{mega}")
            print(f"    个股: {', '.join(names)}")
    else:
        print("  (无板块效应，散乱格局)")
    
    return df

def get_yesterday_limitup(date_str="20260520"):
    """获取前日涨停池，用于对比"""
    return get_today_limitup(date_str)

# ============================================================
# 步骤四：隔夜新闻（Sina新闻Feed ✅ cron验证可用，但数据新鲜度有限）
# ============================================================

import json, urllib.request

def fetch_sina_news(lid="2509", num=10):
    """lid: 2509=全球财经, 2510=国内经济, 2511=证券市场"""
    url = f"https://feed.mix.sina.com.cn/api/roll/get?"
    url += f"pageid=153&lid={lid}&k=&num={num}&page=1"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    items = data.get("result", {}).get("data", [])
    for i in items:
        print(i.get("ctime", "") + " | " + i.get("title", ""))
    return items

# ============================================================
# 步骤五：框架分析（在agent输出中完成，非脚本）
# ============================================================

"""
五层分析（在最终回复中呈现，不在脚本中）：
1️⃣ 大盘四季定位 → 趋势方向 + 量能 + 涨跌比
2️⃣ 板块四季定位 → 最强板块的阵型（先锋/中军/后排）
3️⃣ 风格四季定位 → 连板 vs 趋势（京东方/TCL涨停=趋势风格确认）
4️⃣ 前日对比 → 连板结构变化 + 行业分布变化 + 高标演进
5️⃣ 策略含义 → 仓位 + 方向 + 手法 + 风控 + 关键观察点

标准输出格式参见：references/cron-morning-briefing-format.md
"""

# ============================================================
# 步骤六：逐日跟踪（混沌→破局判断）
# ============================================================

"""
当混沌过渡期遇到板块爆发时，判断框架：
1. 该板块是否具有完整阵型（先锋+中军+后排）→ 是则可能破局
2. 中军是否为大市值机构票（如京东方1700亿+）→ 是则可信度高
3. 板块爆发是否伴随大盘共振 → 高开+板块带领=良好信号
4. 持续性验证：明天能否出2板晋级（最重要）
"""
