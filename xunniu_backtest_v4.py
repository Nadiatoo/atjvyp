#!/usr/bin/env python3
"""
寻牛战法回测 V4 — 小禾的4个改进规则
====================================
改进1: 动态ATR恐慌阈值 (替代固定7%)
改进2: 量价配合高潮确认 (放量突破不卖)
改进3: 冰点类型分支 (冲击型 vs 内生型)
改进4: 牛市追回条件 (减仓后20日再涨>3%回补)

对比: V3(简单规则) vs V4(改进规则)
"""

import csv, math, json
from collections import defaultdict, OrderedDict

DATA_FILE = "/tmp/sh000001_kline_tx.csv"
INITIAL = 1_000_000

# ============================================================
def load(path):
    with open(path) as f:
        data = []
        for r in csv.DictReader(f):
            data.append({'date': r['date'], 'open': float(r['open']),
                         'close': float(r['close']), 'high': float(r['high']),
                         'low': float(r['low']), 'volume': float(r['volume'])})
    return [d for d in data if d['date'] >= '2021-01-01']

def max_dd(curve):
    pk, dd = curve[0], 0
    for v in curve: pk = max(pk, v); dd = max(dd, (pk-v)/pk)
    return dd

def sharpe(rets, rf=0.03):
    if len(rets) < 2: return 0
    m = sum(rets)/len(rets); s = math.sqrt(sum((r-m)**2 for r in rets)/(len(rets)-1))
    return (m*252-rf)/(s*math.sqrt(252)) if s > 0 else 0

def atr(data, i, n=14):
    """Average True Range over n days"""
    if i < n: return None
    trs = []
    for j in range(i-n+1, i+1):
        h, l = data[j]['high'], data[j]['low']
        pc = data[j-1]['close'] if j > 0 else data[j]['open']
        trs.append(max(h-l, abs(h-pc), abs(l-pc)))
    return sum(trs)/n

# ============================================================
# V3 基准 (原简单规则)
# ============================================================
def run_v3(data):
    closes = [d['close'] for d in data]
    pos, shares, cash = 0, 0, INITIAL
    trades, eq, rets = [], [], []
    cooldown = 0

    for i, d in enumerate(data):
        price = d['close']
        if i < 30: eq.append(INITIAL); continue

        dd20 = (max(closes[i-20:i+1]) - price) / max(closes[i-20:i+1])
        rise15 = (price - closes[i-15]) / closes[i-15] if i >= 15 else 0
        ret60 = (price - closes[i-60]) / closes[i-60] if i >= 60 else 0

        # Panic buy (20D dd > 7%)
        if dd20 > 0.07 and pos < 0.6 and cooldown > 40:
            tgt = 0.7; bv = INITIAL*(tgt-pos)
            shares += bv/price; cash -= bv; pos = tgt; cooldown = 0
            trades.append({'date': d['date'], 'action': '🌱V3恐慌买入', 'price': price, 'pos': pos})

        # Exhaustion sell (15D rise > 8%)
        if rise15 > 0.08 and pos > 0.1:
            sp = 0.3; sv = INITIAL*sp
            ss = sv/price; shares = max(0,shares-ss); cash += sv; pos -= sp; cooldown = 0
            trades.append({'date': d['date'], 'action': '🍂V3高潮减仓', 'price': price, 'pos': pos})

        # Deep correction exit (60D decline > 12%)
        if ret60 < -0.12 and pos > 0:
            cash += shares*price; shares = 0
            trades.append({'date': d['date'], 'action': '❄️V3深跌清仓', 'price': price, 'pos': 0})
            pos = 0; cooldown = 0

        # Add on dip
        if pos > 0 and ret60 > 0.02 and dd20 > 0.04 and pos < 0.85 and cooldown > 60:
            av = INITIAL*0.15; shares += av/price; cash -= av; pos += 0.15; cooldown = 0
            trades.append({'date': d['date'], 'action': '➕V3回调加仓', 'price': price, 'pos': pos})

        cooldown += 1
        tv = cash + shares*price; eq.append(tv)
        if len(eq) > 30: rets.append((eq[-1]-eq[-2])/eq[-2])

    return eq[:30] + eq[30:], trades, rets

# ============================================================
# V4 改进版
# ============================================================

def estimate_limit_stats(data, i):
    """
    用价格波动近似推断跌停家数。
    实际系统会用 real 涨跌停数据，这里用极端波动率作为代理：
    - 单日跌幅>5%的个股比例作为跌停代理
    - 对指数而言，用当日波动率+跌幅结合来推断

    简化方案：当日跌幅>2%且振幅>3% → 判断为冲击型
    正常：当日跌幅<1% → 内生型
    """
    d = data[i]
    change_pct = (d['close'] - d['open']) / d['open']
    amplitude = (d['high'] - d['low']) / d['open']

    # Proxy: big down day with high volatility = shock-type ice point
    if change_pct < -0.02 and amplitude > 0.03:
        return 'shock', 60  # 估计60+跌停
    elif change_pct < -0.01:
        return 'endogenous', 15  # 估计<20跌停
    else:
        return 'normal', 5

def run_v4(data):
    """V4 with all 4 improvements"""
    closes = [d['close'] for d in data]
    volumes = [d['volume'] for d in data]
    pos, shares, cash = 0, 0, INITIAL
    trades, eq, rets = [], [], []
    cooldown = 0
    last_sell_price = 0  # for re-entry tracking
    days_since_sell = 0

    for i, d in enumerate(data):
        price = d['close']; vol = d['volume']
        if i < 60: eq.append(INITIAL); continue

        # --- Metrics ---
        dd20 = (max(closes[i-20:i+1]) - price) / max(closes[i-20:i+1])
        rise15 = (price - closes[i-15]) / closes[i-15] if i >= 15 else 0
        ret60 = (price - closes[i-60]) / closes[i-60]

        # 改进1: Dynamic ATR threshold
        atr60 = atr(data, i, 60) or (price * 0.01)
        atr_pct = atr60 / price  # ATR as % of price
        panic_threshold = max(atr_pct * 3.5, 0.05)  # 3.5x ATR, floor 5%

        # 改进2: Volume confirmation for exhaustion
        v5 = sum(volumes[i-4:i+1])/5
        v20 = sum(volumes[i-19:i+1])/20
        vratio = v5/v20 if v20 > 0 else 1.0

        # 改进3: Ice point type detection
        ice_type, est_limits = estimate_limit_stats(data, i)

        # --- 改进3: Panic buy with ice point branching ---
        panic_triggered = dd20 > panic_threshold

        if ice_type == 'shock' and dd20 > panic_threshold * 0.6 and pos < 0.6 and cooldown > 20:
            # 冲击型冰点：放宽阈值，缩短观察期
            if pos < 0.6 and cooldown > 20:
                tgt = 0.7; bv = INITIAL*(tgt-pos)
                shares += bv/price; cash -= bv; pos = tgt; cooldown = 0
                trades.append({'date': d['date'], 'action': '🌱V4冲击买入', 'price': price, 'pos': pos,
                              'reason': f'冲击型冰点,ATR阈值={panic_threshold*100:.1f}%'})
        elif panic_triggered and pos < 0.6 and cooldown > 30:
            # 内生型冰点：标准规则
            tgt = 0.7; bv = INITIAL*(tgt-pos)
            shares += bv/price; cash -= bv; pos = tgt; cooldown = 0
            trades.append({'date': d['date'], 'action': '🌱V4内生买入', 'price': price, 'pos': pos,
                          'reason': f'内生冰点,ATR阈值={panic_threshold*100:.1f}%'})

        # --- 改进2: Volume-confirmed exhaustion sell ---
        if rise15 > 0.08 and pos > 0.1:
            v3 = sum(volumes[i-2:i+1])/3  # last 3 days avg
            breakout = v3 > v20 * 1.2  # 近3日放量>20% → 真突破
            if not breakout:
                # 缩量滞涨 → 真高潮，卖出
                sp = 0.3; sv = INITIAL*sp
                ss = sv/price; shares = max(0,shares-ss); cash += sv; pos -= sp
                last_sell_price = price; days_since_sell = 0; cooldown = 0
                trades.append({'date': d['date'], 'action': '🍂V4高潮减仓', 'price': price, 'pos': pos,
                              'reason': f'vratio={vratio:.2f},非突破'})
            else:
                trades.append({'date': d['date'], 'action': '🚀V4放量突破(不卖)', 'price': price, 'pos': pos,
                              'reason': f'vratio={vratio:.2f},真突破'})

        # --- 改进4: Re-entry after sell ---
        if last_sell_price > 0:
            days_since_sell += 1
            if days_since_sell <= 25 and pos < 0.7:
                rise_since_sell = (price - last_sell_price) / last_sell_price
                if rise_since_sell > 0.02 and cooldown > 3:
                    # 牛市延续，回补仓位
                    tgt = 0.85; bv = INITIAL*(tgt-pos)
                    shares += bv/price; cash -= bv; pos = tgt; cooldown = 0
                    last_sell_price = 0; days_since_sell = 0
                    trades.append({'date': d['date'], 'action': '🔄V4牛市追回', 'price': price, 'pos': pos,
                                  'reason': f'卖后{days_since_sell}日涨{rise_since_sell*100:.1f}%'})

        # Deep correction exit (with 10-day guard after buy: allow position to develop)
        if ret60 < -0.12 and pos > 0 and cooldown > 10:
            cash += shares*price; shares = 0
            last_sell_price = 0
            trades.append({'date': d['date'], 'action': '❄️V4深跌清仓', 'price': price, 'pos': 0})
            pos = 0; cooldown = 0

        # Add on dip (unchanged logic, adapted)
        if pos > 0 and ret60 > 0.02 and dd20 > 0.04 and pos < 0.85 and cooldown > 60:
            av = INITIAL*0.15; shares += av/price; cash -= av; pos += 0.15; cooldown = 0
            trades.append({'date': d['date'], 'action': '➕V4回调加仓', 'price': price, 'pos': pos})

        if last_sell_price == 0:
            cooldown += 1
        tv = cash + shares*price; eq.append(tv)
        if len(eq) > 60: rets.append((eq[-1]-eq[-2])/eq[-2])

    return eq[:60] + eq[60:], trades, rets

# ============================================================
# Run & Compare
# ============================================================
data = load(DATA_FILE)
print(f"数据: {len(data)} 天, {data[0]['date']} → {data[-1]['date']}")

eq_v3, tr_v3, re_v3 = run_v3(data)
eq_v4, tr_v4, re_v4 = run_v4(data)

# Benchmark
bh = [INITIAL/data[0]['close']*d['close'] for d in data]
bh_rets = [(bh[i]-bh[i-1])/bh[i-1] for i in range(1,len(bh))]

def metrics(eq, rets):
    yrs = len(data)/252
    sret = (eq[-1]-INITIAL)/INITIAL
    bret = (bh[-1]-INITIAL)/INITIAL
    cagr = (eq[-1]/INITIAL)**(1/yrs)-1 if eq[-1]>0 else -1
    return {
        '累计': f"{sret*100:+.2f}%",
        '超额': f"{(sret-bret)*100:+.2f}%",
        '年化': f"{cagr*100:+.2f}%",
        'Sharpe': sharpe(rets),
        '回撤': f"{max_dd(eq)*100:.2f}%",
        '回撤改善': f"{(max_dd(bh)-max_dd(eq))/max_dd(bh)*100:.1f}%"
    }

# Win rate
def calc_wr(trades):
    wins, rts, ep = 0, 0, 0
    for t in trades:
        if '买入' in t['action'] or '追回' in t['action'] or '加仓' in t['action']:
            ep = t['price'] if not ep else (ep+t['price'])/2
        elif ('减仓' in t['action'] or '清仓' in t['action']) and ep:
            if t['price'] > ep: wins += 1
            rts += 1; ep = 0
    return wins, rts

w3, r3 = calc_wr(tr_v3); w4, r4 = calc_wr(tr_v4)

# Year breakdown
def yearly_breakdown(data, eq):
    yearly = OrderedDict()
    for i, d in enumerate(data):
        y = d['date'][:4]
        if y not in yearly: yearly[y] = {'start': eq[i]}
        yearly[y]['end'] = eq[i]
    for y in yearly:
        s = yearly[y]['start']; e = yearly[y]['end']
        yearly[y] = (e-s)/s*100 if s > 0 else 0
    # Benchmark yearly
    by = OrderedDict()
    for i, d in enumerate(data):
        y = d['date'][:4]
        if y not in by: by[y] = {'start': bh[i]}
        by[y]['end'] = bh[i]
    for y in by: by[y] = (by[y]['end']-by[y]['start'])/by[y]['start']*100
    return yearly, by

y_v3, by_v3 = yearly_breakdown(data, eq_v3)
y_v4, by_v4 = yearly_breakdown(data, eq_v4)

# Critical dates
key_dates = ['2022-04-26','2022-10-31','2024-02-05','2024-09-24','2024-10-08']
di = {d['date']: i for i, d in enumerate(data)}
v3_hits = 0; v4_hits = 0
for dt in key_dates:
    if dt in di:
        # Check if positioned within 10 days after
        for t in tr_v3:
            if t['date'] <= dt and t['action'] in ('🌱V3恐慌买入','➕V3回调加仓') and (di[dt] - di.get(t['date'],0)) < 15 and t['pos'] > 0:
                v3_hits += 1; break
        for t in tr_v4:
            if t['date'] <= dt and any(a in t['action'] for a in ['V4冲击买入','V4内生买入','V4回调加仓','V4牛市追回']) and (di[dt] - di.get(t['date'],0)) < 15 and t['pos'] > 0:
                v4_hits += 1; break

# ============================================================
# Report
# ============================================================
m3 = metrics(eq_v3, re_v3); m4 = metrics(eq_v4, re_v4)

print(f"""
╔══════════════════════════════════════════════════════════════╗
║       寻牛战法 V3 vs V4 对比回测                           ║
║   上证指数 {data[0]['date']} → {data[-1]['date']} ({len(data)}天)        ║
╚══════════════════════════════════════════════════════════════╝

━━━ 核心业绩对比 ━━━
{'指标':<16} {'V3(原规则)':>14} {'V4(改进)':>14} {'改善':>10}
{'─'*16} {'─'*14} {'─'*14} {'─'*10}""")

for k in ['累计','超额','年化','回撤','回撤改善']:
    v3v = m3[k]; v4v = m4[k]
    if isinstance(v3v, str):
        v3n = float(v3v.replace('%','').replace('+',''))
        v4n = float(v4v.replace('%','').replace('+',''))
        impr = f"{v4n-v3n:+.1f}%"
        print(f"  {k:<16} {v3v:>14} {v4v:>14} {impr:>10}")

print(f"  {'Sharpe':<16} {m3['Sharpe']:>14.2f} {m4['Sharpe']:>14.2f}")
print(f"  {'胜率/交易':<16} {f'{w3}/{r3}/{len(tr_v3)}次':>14} {f'{w4}/{r4}/{len(tr_v4)}次':>14}")

print(f"\n━━━ 逐年对比 ━━━")
print(f"  {'年份':<6} {'持有':>8} {'V3':>8} {'V4':>8} {'V3超额':>8} {'V4超额':>8}")
for y in y_v3:
    v3 = y_v3.get(y,0); v4 = y_v4.get(y,0); bh_y = by_v4.get(y,0)
    print(f"  {y:<6} {bh_y:>+7.2f}% {v3:>+7.2f}% {v4:>+7.2f}% {(v3-bh_y):>+7.2f}% {(v4-bh_y):>+7.2f}%")

print(f"\n━━━ 关键底部命中 ━━━")
print(f"  V3: {v3_hits}/{len(key_dates)}   V4: {v4_hits}/{len(key_dates)}")
for dt in key_dates:
    if dt in di:
        print(f"  {dt}: V3={'✅' if v3_hits else '❌'} V4={'✅' if v4_hits else '❌'}")

print(f"\n━━━ V4 交易信号 ({len(tr_v4)}次) ━━━")
for t in tr_v4:
    reason = t.get('reason','')
    print(f"  {t['date']} {t['action']} @{t['price']:.2f} 仓位{t['pos']*100:.0f}% {f'({reason})' if reason else ''}")

print(f"\n━━━ V4 新增功能效果 ━━━")
# Count by type
types = defaultdict(int)
for t in tr_v4: types[t['action'].split('V4')[1].split(' ')[0]] += 1
print(f"  冲击买入: {types.get('冲击买入',0)}次")
print(f"  内生买入: {types.get('内生买入',0)}次")
print(f"  放量突破(不卖): {types.get('放量突破',0)}次")
print(f"  牛市追回: {types.get('牛市追回',0)}次")

# Save trades for analysis
with open('/tmp/v4_trades.json','w') as f:
    json.dump(tr_v4, f, ensure_ascii=False, default=str)
print(f"\n交易记录: /tmp/v4_trades.json")
