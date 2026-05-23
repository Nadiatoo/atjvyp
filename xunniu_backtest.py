#!/usr/bin/env python3
"""
寻牛战法 5年回测引擎
====================
基于趋势+极端值双因子做季节判定，模拟春播建仓→夏长持有→秋收减仓→冬藏空仓
"""

import csv, math, json
from collections import defaultdict, OrderedDict

# ============================================================
# Config
# ============================================================
DATA_FILE = "/tmp/sh000001_kline_tx.csv"
START_DATE = "2021-01-01"
INITIAL = 1_000_000

# Season detection params
TREND_MA = 60       # long-term trend MA
PANIC_DD = 0.07     # 20-day drawdown threshold for panic (7%)
EXHAUST_RISE = 0.06 # 20-day rise for exhaustion signal
MIN_SEASON = 20     # minimum days in a season

# ============================================================
# Helpers
# ============================================================
def load_data(path):
    with open(path) as f:
        data = []
        for row in csv.DictReader(f):
            d = {'date': row['date'], 'open': float(row['open']),
                 'close': float(row['close']), 'high': float(row['high']),
                 'low': float(row['low']), 'volume': float(row['volume'])}
            data.append(d)
    return [d for d in data if d['date'] >= START_DATE]

def ma(arr, n):
    return sum(arr)/n

def max_dd(curve):
    peak, dd = curve[0], 0
    for v in curve: peak = max(peak, v); dd = max(dd, (peak-v)/peak)
    return dd

def sharpe(rets, rf=0.03):
    if len(rets) < 2: return 0
    m = sum(rets)/len(rets)
    s = math.sqrt(sum((r-m)**2 for r in rets)/(len(rets)-1))
    return (m*252 - rf)/(s*math.sqrt(252)) if s > 0 else 0

# ============================================================
# Season detection: trend + extreme 2-factor
# ============================================================
def get_seasons(data):
    """
    Logic:
    - Compute MA60 slope to determine primary trend
    - Detect panic points (20D dd > 7%) → spring candidates
    - Detect exhaustion (20D rise > 6% + vol divergence) → autumn candidates
    - Fill in summer/winter based on trend between extremes
    - Enforce minimum season duration
    """
    closes = [d['close'] for d in data]
    volumes = [d['volume'] for d in data]
    n = len(data)

    # Compute MA60
    ma60 = [0]*n
    for i in range(n):
        if i >= 59:
            ma60[i] = ma(closes[i-59:i+1], 60)

    # Compute MA60 slope (10-day MA of the MA60 change)
    ma60_slope = [0]*n
    for i in range(60, n):
        if ma60[i-10] > 0:
            ma60_slope[i] = (ma60[i] - ma60[i-10]) / ma60[i-10]

    # 20-day returns and drawdowns
    ret20 = [0]*n; dd20 = [0]*n
    for i in range(20, n):
        ret20[i] = (closes[i] - closes[i-20]) / closes[i-20]
        dd20[i] = (max(closes[i-20:i+1]) - closes[i]) / max(closes[i-20:i+1])

    # Volume ratio (5d MA / 20d MA)
    vr = [1]*n
    for i in range(20, n):
        v5 = ma(volumes[i-4:i+1], 5)
        v20 = ma(volumes[i-19:i+1], 20)
        vr[i] = v5/v20 if v20 > 0 else 1

    # Step 1: Identify panic bottoms (extreme drawdown followed by stabilization)
    panic_flags = [False]*n
    for i in range(30, n):
        # Panic: sharp drawdown (20D dd > 7%) AND
        #   price within 3% of 20D low (stabilizing near the bottom)
        # OR recovering from a deeper dd with increasing volume
        recent_low = min(closes[i-20:i+1])
        near_low = (closes[i] - recent_low) / recent_low < 0.03

        if dd20[i] > PANIC_DD and near_low:
            # Panic just passed or is passing
            panic_flags[i] = True

    # Step 2: Identify exhaustion tops
    exhaust_flags = [False]*n
    for i in range(30, n):
        # Exhaustion: big 20D rise AND falling volume (distribution)
        if ret20[i] > EXHAUST_RISE and vr[i] < 0.85:
            exhaust_flags[i] = True
        # OR: long uptrend with diminishing momentum
        if (i >= 60 and ma60_slope[i] < 0.001 and ma60_slope[i-5] > 0.003
            and ret20[i] > 0.03):
            exhaust_flags[i] = True

    # Step 3: Assign seasons based on trend + extreme events
    seasons = ['春播']*n  # default

    for i in range(60, n):
        trend_up = ma60_slope[i] > 0.001
        trend_down = ma60_slope[i] < -0.001
        trend_flat = not trend_up and not trend_down
        in_panic = panic_flags[i]
        in_exhaust = exhaust_flags[i]

        # Check proximity to previous panic/exhaust
        near_panic = any(panic_flags[max(0,i-15):i+1])
        near_exhaust = any(exhaust_flags[max(0,i-15):i+1])

        # === Season logic ===
        if trend_down and dd20[i] > 0.04:
            seasons[i] = '冬藏'
        elif near_panic and trend_up:
            # Just came out of panic, trend turning up → 春播
            seasons[i] = '春播'
        elif near_panic and not trend_down:
            seasons[i] = '春播'
        elif trend_up and not near_exhaust and ret20[i] > 0.01:
            seasons[i] = '夏长'
        elif trend_up and near_exhaust:
            # In uptrend but exhaustion nearby → 秋收
            seasons[i] = '秋收'
        elif trend_flat and near_exhaust:
            seasons[i] = '秋收'
        elif trend_down and not near_panic:
            seasons[i] = '冬藏'
        elif trend_flat and near_panic:
            seasons[i] = '春播'
        elif trend_up:
            seasons[i] = '夏长'
        else:
            seasons[i] = '冬藏'

    # Step 4: Smooth - enforce minimum season duration
    smoothed = list(seasons)
    i = 60
    while i < n - 1:
        s = smoothed[i]
        # Find run of same season
        j = i
        while j < n and smoothed[j] == s:
            j += 1
        run_len = j - i

        if run_len < MIN_SEASON // 2:
            # Very short run: merge with neighbors
            prev_s = smoothed[i-1] if i > 0 else s
            next_s = smoothed[j] if j < n else s
            replacement = prev_s if s != prev_s else next_s
            for k in range(i, j):
                smoothed[k] = replacement

        i = j

    return smoothed, panic_flags, exhaust_flags

# ============================================================
# Trading simulation
# ============================================================
def simulate(data, seasons):
    pos = 0; shares = 0; cash = INITIAL
    trades = []; eq = []; rets = []

    for i, d in enumerate(data):
        season = seasons[i]; price = d['close']
        changed = (i > 0 and seasons[i] != seasons[i-1])

        if changed:
            if season == '春播' and pos < 0.6:
                tgt = 0.7; bv = INITIAL*(tgt-pos)
                shares += bv/price; cash -= bv; pos = tgt
                trades.append({'date': d['date'], 'action': '🌱春播', 'price': price, 'pos': pos})
            elif season == '夏长' and 0 < pos < 0.85:
                av = INITIAL*0.15
                shares += av/price; cash -= av; pos += 0.15
                trades.append({'date': d['date'], 'action': '☀️夏长', 'price': price, 'pos': pos})
            elif season == '秋收' and pos > 0.05:
                sp = min(0.5, pos); sv = INITIAL*sp
                ss = sv/price; shares = max(0,shares-ss); cash += sv; pos -= sp
                trades.append({'date': d['date'], 'action': '🍂秋收', 'price': price, 'pos': pos})
            elif season == '冬藏' and pos > 0:
                cash += shares*price; shares = 0
                trades.append({'date': d['date'], 'action': '❄️冬藏', 'price': price, 'pos': 0})
                pos = 0

        tv = cash + shares*price; eq.append(tv)
        if i > 0: rets.append((eq[-1]-eq[-2])/eq[-2])

    return trades, eq, rets

# ============================================================
# Main
# ============================================================
data = load_data(DATA_FILE)
print(f"数据: {len(data)} 天, {data[0]['date']} → {data[-1]['date']}")

seasons, panics, exhausts = get_seasons(data)
trades, eq, rets = simulate(data, seasons)

# Benchmark
bh = [INITIAL/data[0]['close']*d['close'] for d in data]
bh_rets = [(bh[i]-bh[i-1])/bh[i-1] for i in range(1,len(bh))]

# Metrics
yrs = len(data)/252
sret = (eq[-1]-INITIAL)/INITIAL; bret = (bh[-1]-INITIAL)/INITIAL
scagr = (eq[-1]/INITIAL)**(1/yrs)-1 if eq[-1] > 0 else -1
bcagr = (bh[-1]/INITIAL)**(1/yrs)-1
ss = sharpe(rets); bs = sharpe(bh_rets)
dd_s = max_dd(eq); dd_b = max_dd(bh)

# Win rate
wins, rts, ep = 0, 0, 0
for t in trades:
    if t['action'] == '🌱春播': ep = t['price']
    elif t['action'] == '☀️夏长' and ep: ep = (ep + t['price'])/2
    elif t['action'] in ('🍂秋收', '❄️冬藏') and ep:
        if t['price'] > ep: wins += 1
        rts += 1; ep = 0
wr = wins/rts if rts > 0 else 0

# Season stats
sc = defaultdict(int); [sc.update({s: sc[s]+1}) for s in seasons]

# Yearly
yearly = OrderedDict()
for i, d in enumerate(data):
    y = d['date'][:4]
    if y not in yearly: yearly[y] = {'s_start': eq[i], 'b_start': bh[i], 'sig': 0, 'ss': defaultdict(int)}
    yearly[y]['s_end'] = eq[i]; yearly[y]['b_end'] = bh[i]; yearly[y]['ss'][seasons[i]] += 1
for t in trades: yearly[t['date'][:4]]['sig'] += 1

# Key bottoms verification
key_dates = ['2022-04-26', '2022-10-31', '2024-02-05', '2024-09-24']
date_idx = {d['date']: i for i, d in enumerate(data)}

# ============================================================
# Report
# ============================================================
print(f"""
╔══════════════════════════════════════════════════════════════╗
║       寻牛战法 5年回测 — 趋势+极端值双因子                   ║
║   上证指数 {data[0]['date']} → {data[-1]['date']} ({len(data)}天)        ║
╚══════════════════════════════════════════════════════════════╝

━━━ 一、核心业绩 ━━━
{'  策略累计:':<16} {sret:>+8.2f}%     买入持有: {bret:>+8.2f}%
{'  超额收益:':<16} {(sret-bret):>+8.2f}%
{'  策略年化:':<16} {scagr:>+8.2f}%     持有年化: {bcagr:>+8.2f}%
{'  Sharpe:':<16} {ss:>8.2f}           持有Sharpe: {bs:>8.2f}
{'  最大回撤:':<16} {dd_s*100:>8.2f}%         持有回撤: {dd_b*100:>8.2f}%
{'  胜率:':<16} {wr*100:>8.1f}% ({wins}/{rts})        交易次数: {len(trades):>5}
{'  Calmar:':<16} {scagr/dd_s:>8.2f}

━━━ 二、四季分布 ━━━""")
for s in ['春播','夏长','秋收','冬藏']:
    print(f"  {s}: {sc[s]}天 ({sc[s]/len(seasons)*100:.1f}%)")

print(f"\n━━━ 三、逐年表现 ━━━")
print(f"  {'年份':<6} {'策略':>9} {'持有':>9} {'超额':>9} {'信号':>5}  {'季节特征'}")
print(f"  {'-'*65}")
for y, v in yearly.items():
    sr = (v['s_end']-v['s_start'])/v['s_start']; br = (v['b_end']-v['b_start'])/v['b_start']
    top = sorted(v['ss'].items(), key=lambda x:-x[1]); ds = '/'.join([f"{s[0]}{c}" for s,c in top[:2]])
    print(f"  {y:<6} {sr*100:>+8.2f}% {br*100:>+8.2f}% {(sr-br)*100:>+8.2f}% {v['sig']:>5}  {ds}")

print(f"\n━━━ 四、交易信号 ({len(trades)}次) ━━━")
for t in trades:
    print(f"  {t['date']} {t['action']} @{t['price']:.2f} 仓位{t['pos']*100:.0f}%")

print(f"\n━━━ 五、关键底部验证 ━━━")
for dt in key_dates:
    if dt in date_idx:
        i = date_idx[dt]; s = seasons[i]; p = data[i]['close']
        icon = '✅' if s in ('春播','夏长') else '❌'
        print(f"  {icon} {dt} @{p:.0f}: {s} — {'春播信号正确' if s == '春播' else '冬藏/秋收=错过底部'}")

# Issues
print(f"\n━━━ 六、待改进 ━━━")
issues = []
if sret < bret: issues.append(f"策略累计跑输买入持有 {(bret-sret)*100:.1f}%：夏长期仓位上限85%限制了牛市收益")
if dd_s > dd_b: issues.append("回撤大于买入持有：冬藏信号滞后，未能提前规避")
if len(trades) > 25: issues.append(f"交易{len(trades)}次偏多：季节切换仍有振荡，需更大平滑窗口")
if sc.get('秋收',0) == 0: issues.append("秋收检测缺失：20日涨超6%+量缩的信号在牛市中从未触发")
if sc.get('秋收',0) < 5: issues.append(f"秋收仅{sc.get('秋收',0)}天：上升趋势中难以识别衰竭信号")
if sc.get('夏长',0) < sc.get('春播',0) * 0.5: issues.append("夏长占比显著低于春播：趋势确认滞后，在春播停留过长")
for i, issue in enumerate(issues, 1): print(f"  {i}. {issue}")

print(f"""
━━━ 七、与已有定量验证的对应 ━━━
  恐慌后买入60日胜率91% → 原验证中的「恐慌」定义是20日跌超7%
  本次回测冬藏期捕捉了恐慌，但春播触发滞后（等趋势确认才进场）
  → 结论：规则框架有效，但纯价格驱动的自动化季节判定精度不够
  → 改进方向：需要引入更多维度的数据（涨跌停、连板高度、北向资金等）
""")
