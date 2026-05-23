#!/usr/bin/env python3
"""
真如铁「事不过三」选股回测系统
核心：三次探底同一支撑不破，第三次缩量收阳 = 买入信号
完全独立，不与其他战法融合
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

# 策略参数
SUPPORT_ZONE = 0.03    # 支撑位 ±3%
MIN_TOUCHES = 3         # 最少 3 次探底
MIN_TOUCH_GAP = 10      # 两次探底最少间隔 10 个交易日
MAX_TOUCH_GAP = 90      # 两次探底最多 90 个交易日
VOL_EXPAND = 1.2        # 第三次探底 > 前两次均量 120%（放量突破确认）
LOCAL_LOW_WINDOW = 15   # 局部低点窗口
MAX_DECLINE_PCT = -0.30 # 200日跌幅>30%视为单边下跌，过滤
LOOKBACK = 300          # 回溯天数
STOP_LOSS = -0.05       # 止损 -5%
TAKE_PROFIT = 0.25      # 止盈 +25%
HOLD_DAYS = 20          # 持仓天数
ENTRY_REQUIRE_BOTH = True  # 买入需同时满足放量+阳线

# Tushare
_PRO_API = None
_TOKEN = None


def _get_token():
    global _TOKEN
    if _TOKEN:
        return _TOKEN
    try:
        cfg = json.load(open(HOME / ".mcp.json"))
        for s in cfg.get("mcpServers", {}).values():
            url = s.get("url", "")
            if "tushare" in url:
                _TOKEN = url.split("token=")[-1].split("&")[0]
                return _TOKEN
    except Exception:
        pass
    _TOKEN = os.environ.get("TUSHARE_TOKEN", "")
    return _TOKEN


def _init_ts():
    global _PRO_API
    if _PRO_API is not None:
        return _PRO_API
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


def fetch_daily(ts_code: str, start: str = "20190101", end: str = "20260520") -> pd.DataFrame | None:
    api = _init_ts()
    try:
        df = api.daily(ts_code=ts_code, start_date=start, end_date=end)
        time.sleep(0.15)
        if df is None or df.empty:
            return None
        df = df.sort_values("trade_date").reset_index(drop=True)
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        for col in ["open", "high", "low", "close", "vol"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception:
        return None


# ── 形态识别 ────────────────────────────────────────────────────────────


def find_local_lows(df: pd.DataFrame, window: int = LOCAL_LOW_WINDOW) -> pd.Series:
    lows = df["low"].values
    n = len(lows)
    is_local_low = np.zeros(n, dtype=bool)
    for i in range(window, n - window):
        if lows[i] <= lows[i - window:i].min() and lows[i] <= lows[i + 1:i + window + 1].min():
            is_local_low[i] = True
    return pd.Series(is_local_low, index=df.index)


def detect_triple_bottoms(df: pd.DataFrame) -> list[dict]:
    """检测事不过三形态：同一支撑位被试探 3 次"""
    n = len(df)
    if n < 100:
        return []

    df = df.copy()
    df["ma60"] = df["close"].rolling(60).mean()
    df["vol_ma20"] = df["vol"].rolling(20).mean()

    # MACD
    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()
    df["dif"] = ema12 - ema26
    df["dea"] = df["dif"].ewm(span=9).mean()
    df["macd_bar"] = 2 * (df["dif"] - df["dea"])

    # KDJ (简化)
    low9 = df["low"].rolling(9).min()
    high9 = df["high"].rolling(9).max()
    rsv = (df["close"] - low9) / (high9 - low9).replace(0, np.nan) * 100
    df["k"] = rsv.ewm(com=2).mean()

    local_lows = find_local_lows(df)
    recent = df.iloc[-LOOKBACK:] if len(df) > LOOKBACK else df
    recent_lows = local_lows.iloc[-len(recent):]

    low_indices = recent_lows[recent_lows].index
    if len(low_indices) < 3:
        return []

    low_prices = recent.loc[low_indices, "low"].values
    low_dates = [recent.loc[idx, "trade_date"] for idx in low_indices]

    # 聚类：找 3 个低点在同一支撑区
    patterns = []
    for i in range(len(low_prices) - 2):
        base = low_prices[i]
        group = [i]
        for j in range(i + 1, len(low_prices)):
            if abs(low_prices[j] - base) / base <= SUPPORT_ZONE:
                group.append(j)
            if len(group) >= MIN_TOUCHES:
                break
        if len(group) >= MIN_TOUCHES:
            idxs = [low_indices[g] for g in group[:MIN_TOUCHES]]
            support_price = np.mean([low_prices[g] for g in group[:MIN_TOUCHES]])

            # 检查：第三次探底缩量 + 收阳
            third_idx = idxs[2]
            third_row = df.loc[third_idx]
            vol_third = third_row["vol"]
            avg_vol_first_two = np.mean([df.loc[idxs[0], "vol"], df.loc[idxs[1], "vol"]])
            is_bullish = third_row["close"] > third_row["open"]
            vol_ok = vol_third > avg_vol_first_two * VOL_EXPAND  # 放量突破确认反转

            # 辅助确认：MACD 改善、KDJ 低位
            macd_improve = df.loc[third_idx, "macd_bar"] > df.loc[idxs[1], "macd_bar"] if idxs[1] in df.index else False
            kdj_low = df.loc[third_idx, "k"] < 30

            # 低点是否在同一水平线
            prices_at_touches = [df.loc[idx, "low"] for idx in idxs]
            price_range = (max(prices_at_touches) - min(prices_at_touches)) / support_price

            # 两次探底间距
            gap1 = (df.loc[idxs[1], "trade_date"] - df.loc[idxs[0], "trade_date"]).days
            gap2 = (df.loc[idxs[2], "trade_date"] - df.loc[idxs[1], "trade_date"]).days

            if gap1 < MIN_TOUCH_GAP or gap2 < MIN_TOUCH_GAP:
                continue
            if gap1 > MAX_TOUCH_GAP or gap2 > MAX_TOUCH_GAP:
                continue
            if price_range > SUPPORT_ZONE * 2:
                continue

            # 趋势过滤：近200日不能是单边暴跌
            lookback_200 = max(0, third_idx - 200)
            price_200d_ago = df.iloc[lookback_200]["close"]
            decline_pct = (third_row["close"] - price_200d_ago) / price_200d_ago
            if decline_pct < MAX_DECLINE_PCT:
                continue

            patterns.append({
                "support_price": round(support_price, 2),
                "touch_dates": [df.loc[idx, "trade_date"].strftime("%Y-%m-%d") for idx in idxs],
                "third_idx": int(third_idx),
                "third_date": third_row["trade_date"].strftime("%Y-%m-%d"),
                "third_vol_shrink": bool(vol_ok),
                "third_bullish": bool(is_bullish),
                "macd_improve": bool(macd_improve),
                "kdj_low": bool(kdj_low),
                "price_range_pct": round(price_range * 100, 1),
                "entry_ready": bool(ENTRY_REQUIRE_BOTH and vol_ok and is_bullish),  # 缩量+阳线
            })

    return patterns


# ── 回测 ──────────────────────────────────────────────────────────────────


def classify_period(df: pd.DataFrame, idx: int) -> str:
    if idx < 60:
        return "unknown"
    ma20 = df["close"].iloc[idx - 20:idx + 1].mean()
    ma60 = df["close"].iloc[max(0, idx - 60):idx + 1].mean()
    price = df.iloc[idx]["close"]
    if price > ma20 > ma60:
        return "上升"
    elif price < ma20 < ma60:
        return "下跌"
    return "震荡"


def backtest_signal(df: pd.DataFrame, pattern: dict) -> dict | None:
    """对单个信号回测"""
    entry_idx = pattern["third_idx"]
    entry_price = float(df.iloc[entry_idx]["close"])
    support = pattern["support_price"]
    stop_price = support * (1 + STOP_LOSS)
    target_price = support * (1 + TAKE_PROFIT)
    period = classify_period(df, entry_idx)

    end_idx = min(entry_idx + HOLD_DAYS, len(df) - 1)
    hold_slice = df.iloc[entry_idx:end_idx + 1]

    max_price = hold_slice["high"].max()
    min_price = hold_slice["low"].min()
    exit_price = float(df.iloc[end_idx]["close"])

    # 止损/止盈触发
    stopped_out = min_price <= stop_price
    hit_target = max_price >= target_price

    if stopped_out:
        pnl_pct = round((stop_price - entry_price) / entry_price * 100, 2)
    elif hit_target:
        pnl_pct = round((target_price - entry_price) / entry_price * 100, 2)
    else:
        pnl_pct = round((exit_price - entry_price) / entry_price * 100, 2)

    return {
        "entry_date": df.iloc[entry_idx]["trade_date"].strftime("%Y-%m-%d"),
        "entry_price": round(entry_price, 2),
        "support": round(support, 2),
        "stop": round(stop_price, 2),
        "target": round(target_price, 2),
        "exit_price": round(exit_price, 2),
        "pnl_pct": pnl_pct,
        "max_high_pct": round((max_price - entry_price) / entry_price * 100, 2),
        "win": pnl_pct > 0,
        "period": period,
        "stopped_out": stopped_out,
        "hit_target": hit_target,
    }


def process_stock(ts_code: str) -> dict | None:
    df = fetch_daily(ts_code)
    if df is None or len(df) < 100:
        return None

    patterns = detect_triple_bottoms(df)
    if not patterns:
        return None

    results = []
    for p in patterns:
        bt = backtest_signal(df, p)
        if bt:
            bt["entry_ready"] = p["entry_ready"]
            bt["third_vol_shrink"] = p["third_vol_shrink"]
            bt["third_bullish"] = p["third_bullish"]
            results.append(bt)

    if not results:
        return None

    entry_ready = [r for r in results if r["entry_ready"]]
    wins = [r for r in entry_ready if r["win"]] if entry_ready else []
    all_wins = [r for r in results if r["win"]]

    return {
        "ts_code": ts_code,
        "signals": len(results),
        "ready_signals": len(entry_ready),
        "trades": len(entry_ready),
        "wins": len(wins),
        "win_rate": round(len(wins) / len(entry_ready) * 100, 1) if entry_ready else 0,
        "avg_pnl": round(np.mean([r["pnl_pct"] for r in entry_ready]), 2) if entry_ready else 0,
        "all_avg_pnl": round(np.mean([r["pnl_pct"] for r in results]), 2) if results else 0,
        "details": results[:5],
    }


# ── 主流程 ──────────────────────────────────────────────────────────────


def main():
    print("=" * 60)
    print("真如铁「事不过三」选股回测系统")
    print(f"参数: 支撑区±{SUPPORT_ZONE*100}%, 止损{STOP_LOSS*100}%, 止盈{TAKE_PROFIT*100}%")
    print("=" * 60)

    print("\n加载全A股...")
    stock_pool = load_stock_pool()
    random.seed(42)
    sample = random.sample(stock_pool, min(500, len(stock_pool)))
    print(f"股票池: {len(sample)} 只 (随机500只)")

    print("\n扫描事不过三形态...")
    all_results = []
    for i, code in enumerate(sample):
        if i % 100 == 0:
            print(f"  [{i}/{len(sample)}] 已发现 {len(all_results)} 只有效信号...")
        try:
            r = process_stock(code)
            if r:
                all_results.append(r)
        except Exception:
            pass

    print(f"\n结果: {len(all_results)} 只股票出现事不过三形态")
    total_signals = sum(r["signals"] for r in all_results)
    total_ready = sum(r["ready_signals"] for r in all_results)
    print(f"总信号: {total_signals}, 符合买入条件: {total_ready}")

    if all_results:
        all_wr = [r["win_rate"] for r in all_results if r["ready_signals"] >= 2]
        all_pnl = [r["avg_pnl"] for r in all_results if r["ready_signals"] >= 2]
        print(f"均胜率: {np.mean(all_wr):.1f}% (样本{len(all_wr)}只)")
        print(f"均收益: {np.mean(all_pnl):.2f}%")

        # 按周期统计
        period_stats = defaultdict(list)
        for r in all_results:
            for d in r["details"]:
                period_stats[d["period"]].append(d["pnl_pct"])
        print("\n各周期表现:")
        for p in ["上升", "震荡", "下跌"]:
            pnls = period_stats.get(p, [])
            if pnls:
                wr = sum(1 for x in pnls if x > 0) / len(pnls) * 100
                print(f"  {p}: {len(pnls)}笔 胜率{wr:.1f}% 均收益{np.mean(pnls):.2f}%")

        # TOP 10
        ranked = sorted([r for r in all_results if r["ready_signals"] >= 2],
                       key=lambda r: r["win_rate"], reverse=True)
        print("\nTOP 10 (按胜率):")
        for r in ranked[:10]:
            print(f"  {r['ts_code']}: {r['trades']}笔 胜率{r['win_rate']}% 均收益{r['avg_pnl']}%")

        # 保存
        report = {
            "strategy": "真如铁事不过三",
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "sample_size": len(sample),
            "stocks_with_signals": len(all_results),
            "total_signals": total_signals,
            "buyable_signals": total_ready,
            "avg_win_rate": round(np.mean(all_wr), 1) if all_wr else 0,
            "avg_return": round(np.mean(all_pnl), 2) if all_pnl else 0,
            "by_period": {p: {
                "count": len(period_stats.get(p, [])),
                "win_rate": round(sum(1 for x in period_stats.get(p, []) if x > 0) / len(period_stats.get(p, [])) * 100, 1) if period_stats.get(p, []) else 0,
                "avg_return": round(np.mean(period_stats.get(p, [])), 2) if period_stats.get(p, []) else 0,
            } for p in ["上升", "震荡", "下跌"]},
        }
        path = OUTPUT_DIR / "zhenrutie_report.json"
        with open(path, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n报告: {path}")


if __name__ == "__main__":
    main()
