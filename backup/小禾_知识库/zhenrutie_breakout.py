#!/usr/bin/env python3
"""
真如铁「事不过三」突破形态选股
只做压力突破：三次冲击同一压力位，第三次放量站上 = 买入
"""
import json, os, sys, time, warnings, random
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HOME = Path.home()
OUTPUT_DIR = HOME / ".hermes" / "knowledge_base" / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 参数（基于示例图验证）
RESISTANCE_ZONE = 0.03   # 压力位 ±3%
MIN_TESTS = 3            # 最少 3 次冲击
MIN_TEST_GAP = 10        # 两次冲击最少间隔 10 天
MAX_TEST_GAP = 120       # 两次冲击最多间隔 120 天
VOL_EXPAND = 1.5         # 第三次冲击量 > 前两次均量 150%
LOCAL_HIGH_WINDOW = 15   # 局部高点窗口
LOOKBACK = 400           # 回溯天数
STOP_LOSS = -0.05        # 止损 -5%
TAKE_PROFIT = 0.30       # 止盈 +30%
HOLD_DAYS = 20           # 持仓天数
MAX_DECLINE = -0.35      # 200日跌幅>35%过滤

_PRO_API = None
_TOKEN = None


def _get_token():
    global _TOKEN
    if _TOKEN: return _TOKEN
    try:
        cfg = json.load(open(HOME / ".mcp.json"))
        for s in cfg.get("mcpServers", {}).values():
            url = s.get("url", "")
            if "tushare" in url:
                _TOKEN = url.split("token=")[-1].split("&")[0]
                return _TOKEN
    except: pass
    _TOKEN = os.environ.get("TUSHARE_TOKEN", "")
    return _TOKEN


def _init_ts():
    global _PRO_API
    if _PRO_API is not None: return _PRO_API
    import tushare as ts
    ts.set_token(_get_token())
    _PRO_API = ts.pro_api()
    return _PRO_API


def load_stock_pool() -> list[str]:
    api = _init_ts()
    df = api.stock_basic(exchange='', list_status='L', fields='ts_code,name,list_date')
    df = df[~df['name'].str.contains('ST|退|N', na=False)]
    df = df[df['list_date'] < '20230101']
    return df['ts_code'].tolist()


def fetch_daily(ts_code: str, start="20190101", end="20260520") -> pd.DataFrame | None:
    api = _init_ts()
    try:
        df = api.daily(ts_code=ts_code, start_date=start, end_date=end)
        time.sleep(0.15)
        if df is None or df.empty: return None
        df = df.sort_values("trade_date").reset_index(drop=True)
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        for col in ["open","high","low","close","vol"]:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except: return None


# ── 形态识别：压力突破 ───────────────────────────────────────────────


def find_local_highs(df: pd.DataFrame, window=LOCAL_HIGH_WINDOW) -> pd.Series:
    """只在股价站上120日均线期间找局部高点"""
    highs = df["high"].values
    n = len(highs)
    is_high = np.zeros(n, dtype=bool)
    df["ma120"] = df["close"].rolling(120).mean()
    for i in range(window, n - window):
        if highs[i] >= highs[i-window:i].max() and highs[i] >= highs[i+1:i+window+1].max():
            # 过滤：高点当日必须在120日线上方
            if pd.notna(df.iloc[i]["ma120"]) and df.iloc[i]["close"] > df.iloc[i]["ma120"]:
                is_high[i] = True
    return pd.Series(is_high, index=df.index)


def cluster_price_levels(prices: np.ndarray, dates: list, band=0.05) -> list[dict]:
    if len(prices) == 0: return []
    idx = np.argsort(prices)
    prices, dates = prices[idx], [dates[i] for i in idx]
    clusters = []
    cur = {"center": prices[0], "prices": [prices[0]], "dates": [dates[0]]}
    for j, p in enumerate(prices[1:], 1):
        if p <= cur["center"] * (1 + band):
            cur["prices"].append(p); cur["dates"].append(dates[j])
            cur["center"] = np.mean(cur["prices"])
        else:
            if len(cur["prices"]) >= 2: clusters.append(cur)
            cur = {"center": p, "prices": [p], "dates": [dates[j]]}
    if len(cur["prices"]) >= 2: clusters.append(cur)
    return clusters


def detect_resistance_breakouts(df: pd.DataFrame) -> list[dict]:
    """检测事不过三突破形态：三次冲击同一压力位，第三次放量站上"""
    n = len(df)
    if n < 120: return []

    # 技术指标
    df = df.copy()
    df["vol_ma20"] = df["vol"].rolling(20).mean()
    df["ma120"] = df["close"].rolling(120).mean()

    local_highs = find_local_highs(df)
    recent = df.iloc[-LOOKBACK:] if n > LOOKBACK else df
    recent_highs = local_highs.iloc[-len(recent):]

    hi_idx = recent_highs[recent_highs].index
    if len(hi_idx) < 3: return []

    hi_prices = recent.loc[hi_idx, "high"].values
    hi_dates = [recent.loc[i, "trade_date"] for i in hi_idx]

    clusters = cluster_price_levels(hi_prices, hi_dates, band=0.05)
    patterns = []

    for cl in clusters:
        if len(cl["prices"]) < 2: continue
        resistance = cl["center"]
        ref_date = min(cl["dates"])

        # 找三次冲击：价格从下方接近压力位 ±3%
        touches = []
        in_zone = False
        exited_above = False
        for i in range(df[df["trade_date"] >= ref_date].index[0], n):
            row = df.iloc[i]
            p = float(row["high"])
            upper = resistance * (1 + RESISTANCE_ZONE)
            lower = resistance * (1 - RESISTANCE_ZONE)

            if lower <= p <= upper:
                if not in_zone:
                    touches.append({"idx": i, "date": row["trade_date"], "price": round(p, 2)})
                    in_zone = True
            elif p > upper:
                in_zone = False
                exited_above = True
            else:
                in_zone = False

        if len(touches) < MIN_TESTS: continue

        # 取前 3 次
        t = touches[:MIN_TESTS]
        dates = [x["date"] for x in t]
        gap1 = (dates[1] - dates[0]).days
        gap2 = (dates[2] - dates[1]).days
        if gap1 < MIN_TEST_GAP or gap2 < MIN_TEST_GAP: continue
        if gap1 > MAX_TEST_GAP or gap2 > MAX_TEST_GAP: continue

        # 趋势确认：三次冲击期间股价均在120日线上方
        if not all(df.iloc[x["idx"]]["close"] > df.iloc[x["idx"]]["ma120"]
                   for x in t if pd.notna(df.iloc[x["idx"]]["ma120"])):
            continue

        # 第三次冲击确认
        third_idx = t[2]["idx"]
        third_row = df.iloc[third_idx]
        avg_vol_12 = np.mean([df.iloc[t[0]["idx"]]["vol"], df.iloc[t[1]["idx"]]["vol"]])
        vol_ok = float(third_row["vol"]) > avg_vol_12 * VOL_EXPAND
        is_bullish = third_row["close"] > third_row["open"]
        broke_through = third_row["close"] > resistance  # 收盘站上压力位

        # 趋势过滤
        lookback_200 = max(0, third_idx - 200)
        price_200d = df.iloc[lookback_200]["close"]
        decline = (third_row["close"] - price_200d) / price_200d
        if decline < MAX_DECLINE: continue

        # 周期判断
        ma20 = df["close"].iloc[max(0,third_idx-20):third_idx+1].mean()
        ma60 = df["close"].iloc[max(0,third_idx-60):third_idx+1].mean()
        if third_row["close"] > ma20 > ma60: period = "上升"
        elif third_row["close"] < ma20 < ma60: period = "下跌"
        else: period = "震荡"

        patterns.append({
            "resistance": round(resistance, 2),
            "touch_dates": [x["date"].strftime("%Y-%m-%d") for x in t],
            "third_date": dates[2].strftime("%Y-%m-%d"),
            "third_idx": third_idx,
            "vol_expand": bool(vol_ok),
            "bullish": bool(is_bullish),
            "broke_through": bool(broke_through),
            "entry_ready": bool(vol_ok and is_bullish and broke_through),
            "period": period,
        })

    return patterns


# ── 回测 ───────────────────────────────────────────────────────────


def backtest_signal(df: pd.DataFrame, p: dict) -> dict | None:
    """只测选股成功率：买入后 N 天是否上涨"""
    entry_idx = p["third_idx"]
    entry_price = float(df.iloc[entry_idx]["close"])

    results = {}
    for hold_days in [5, 10, 20]:
        end_idx = min(entry_idx + hold_days, len(df) - 1)
        exit_price = float(df.iloc[end_idx]["close"])
        ret = round((exit_price - entry_price) / entry_price * 100, 2)
        max_price = df.iloc[entry_idx:end_idx + 1]["high"].max()
        max_ret = round((max_price - entry_price) / entry_price * 100, 2)
        results[f"ret_{hold_days}d"] = ret
        results[f"max_{hold_days}d"] = max_ret
        results[f"win_{hold_days}d"] = ret > 0

    return {"entry_date": df.iloc[entry_idx]["trade_date"].strftime("%Y-%m-%d"),
            "entry_price": round(entry_price, 2),
            "resistance": p["resistance"],
            "period": p["period"],
            "entry_ready": p["entry_ready"],
            **results}


def process_stock(ts_code: str) -> dict | None:
    df = fetch_daily(ts_code)
    if df is None or len(df) < 120: return None
    patterns = detect_resistance_breakouts(df)
    if not patterns: return None

    details = [backtest_signal(df, p) for p in patterns]
    details = [d for d in details if d is not None]
    if not details: return None

    ready = [d for d in details if d["entry_ready"]]
    if not ready: return None

    return {"ts_code": ts_code, "ready_signals": len(ready),
            "win_5d": round(sum(1 for d in ready if d["win_5d"]) / len(ready) * 100, 1),
            "win_10d": round(sum(1 for d in ready if d["win_10d"]) / len(ready) * 100, 1),
            "win_20d": round(sum(1 for d in ready if d["win_20d"]) / len(ready) * 100, 1),
            "avg_ret_5d": round(np.mean([d["ret_5d"] for d in ready]), 2),
            "avg_ret_10d": round(np.mean([d["ret_10d"] for d in ready]), 2),
            "avg_ret_20d": round(np.mean([d["ret_20d"] for d in ready]), 2),
            "details": details[:3]}


def main():
    print("=" * 60)
    print("事不过三·突破形态选股")
    print(f"参数: 压力区±{RESISTANCE_ZONE*100}% 放量>{VOL_EXPAND}x 间隔{MIN_TEST_GAP}~{MAX_TEST_GAP}d")
    print("=" * 60)

    stock_pool = load_stock_pool()
    random.seed(42)
    sample = random.sample(stock_pool, min(500, len(stock_pool)))
    print(f"股票池: {len(sample)} 只")

    all_results = []
    for i, code in enumerate(sample):
        if i % 100 == 0: print(f"  [{i}/{len(sample)}] {len(all_results)} 个信号...", flush=True)
        try:
            r = process_stock(code)
            if r and r["ready_signals"] > 0: all_results.append(r)
        except: pass

    print(f"\n信号: {len(all_results)} 只")
    if all_results:
        by_period = defaultdict(list)
        for r in all_results:
            for d in r["details"]:
                if d["entry_ready"]: by_period[d["period"]].append(d["pnl_pct"])
        for p in ["上升","震荡","下跌"]:
            pnls = by_period.get(p, [])
            if pnls: print(f"  {p}: {len(pnls)}笔 胜率{sum(1 for x in pnls if x>0)/len(pnls)*100:.1f}%")

        ranked = sorted(all_results, key=lambda r: -r["avg_pnl"])
        for r in ranked[:15]:
            print(f"  {r['ts_code']}: {r['ready_signals']}信号 胜率{r['win_rate']}% 收益{r['avg_pnl']}%")


if __name__ == "__main__":
    main()
