#!/usr/bin/env python3
"""
盘前/盘后分析脚本 — 多数据源三路冗余
数据源优先级: 腾讯HTTP → akshare → mootdx
无模拟数据，所有数据获取失败必须明确报错

用法:
  python3 analyze.py premarket    # 盘前分析
  python3 analyze.py postmarket   # 盘后分析
  python3 analyze.py market       # 实时行情快照
"""

import json
import sys
import time
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
ssl._create_default_https_context = ssl._create_unverified_context

# ── 数据源适配器 ──────────────────────────────────────────

class TencentSource:
    """腾讯财经 HTTP 接口（主力）"""
    name = "腾讯"

    def get_indices(self) -> dict:
        codes = {"sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指"}
        result = {}
        for code, label in codes.items():
            try:
                url = f"http://qt.gtimg.cn/q={code}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read().decode("gbk", errors="ignore")
                    # 格式: 1~名称~代码~现价~昨收~开盘~成交量~...~时间~涨跌额~涨跌幅~...
                    parts = content.split('"')[1].split("~") if '"' in content else []
                    if len(parts) >= 6:
                        price = float(parts[3])
                        prev_close = float(parts[4])
                        change = round(price - prev_close, 2)
                        change_pct = round(change / prev_close * 100, 2) if prev_close else 0
                        result[label] = {
                            "price": price,
                            "change": change,
                            "change_pct": change_pct,
                            "volume": parts[6] if len(parts) > 6 else "",
                        }
            except Exception as e:
                result[label] = {"error": str(e)}
        return result

    def get_stock(self, code: str) -> dict | None:
        """code 格式: sh000001 或 sz399001"""
        try:
            url = f"http://qt.gtimg.cn/q={code}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("gbk", errors="ignore")
                parts = content.split('"')[1].split("~") if '"' in content else []
                if len(parts) >= 6:
                    price = float(parts[3])
                    prev_close = float(parts[4])
                    change = round(price - prev_close, 2)
                    change_pct = round(change / prev_close * 100, 2) if prev_close else 0
                    return {"name": parts[1], "price": price, "change": change, "change_pct": change_pct}
        except Exception as e:
            return {"error": str(e)}
        return None


class AkShareSource:
    """AKShare Python 库（备用）"""
    name = "AkShare"

    def get_indices(self) -> dict:
        try:
            import akshare as ak
            df = ak.stock_zh_index_spot_em()
            result = {}
            targets = {"上证指数": "000001", "深证成指": "399001", "创业板指": "399006"}
            for _, row in df.iterrows():
                name = row.get("名称", "")
                if name in targets:
                    result[name] = {
                        "price": float(row.get("最新价", 0)),
                        "change": float(row.get("涨跌额", 0)),
                        "change_pct": float(row.get("涨跌幅", 0)),
                        "volume": str(row.get("成交量", "")),
                    }
            return result
        except Exception as e:
            return {"error": f"AkShare异常: {e}"}

    def get_limit_up_stats(self) -> dict:
        try:
            import akshare as ak
            today = datetime.now(TZ).strftime("%Y%m%d")
            df = ak.stock_zt_pool_em(date=today)
            return {"涨停家数": len(df), "data": df.head(20).to_dict(orient="records") if len(df) > 0 else []}
        except Exception as e:
            return {"error": f"涨停数据获取失败: {e}"}


class MootdxSource:
    """通达信 pytdx 接口（兜底）"""
    name = "mootdx"

    def get_indices(self) -> dict:
        try:
            from mootdx.quotes import Quotes
            client = Quotes.factory(market='std')
            result = {}
            for code, label in [("000001", "上证指数"), ("399001", "深证成指"), ("399006", "创业板指")]:
                try:
                    data = client.index(symbol=code, market=1 if code.startswith("6") else 0)
                    if data is not None and not (hasattr(data, 'empty') and data.empty):
                        row = data.iloc[-1] if hasattr(data, 'iloc') else data
                        result[label] = {
                            "price": float(row.get("price", row.get("close", 0))),
                            "change_pct": float(row.get("pct_chg", row.get("change_pct", 0))),
                        }
                except:
                    result[label] = {"error": "mootdx 获取失败"}
            return result
        except ImportError:
            return {"error": "mootdx 未安装 (pip3 install mootdx)"}
        except Exception as e:
            return {"error": f"mootdx异常: {e}"}


# ── 数据管道 ──────────────────────────────────────────────

def fetch_with_fallback(method_name: str, *args):
    """三路冗余: 腾讯 → AkShare → mootdx"""
    sources = [TencentSource(), AkShareSource(), MootdxSource()]
    errors = []

    for src in sources:
        try:
            method = getattr(src, method_name, None)
            if method is None:
                continue
            result = method(*args)
            if result and not (isinstance(result, dict) and "error" in result and len(result) == 1):
                return result, src.name
            if isinstance(result, dict) and "error" in result:
                errors.append(f"{src.name}: {list(result.values())[0]}")
        except Exception as e:
            errors.append(f"{src.name}: {e}")

    return {"error": "所有数据源均失败", "details": errors}, "NONE"


# ── 分析输出 ──────────────────────────────────────────────

def print_premarket():
    """盘前分析"""
    print("=" * 50)
    print(f"📊 盘前分析 — {datetime.now(TZ).strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    # 1. 全球指数
    print("\n🌍 全球主要指数:")
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&secids=100.NDX,100.DJI,100.SPX,100.HSI&fields=f14,f2,f3"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            for item in data.get("data", {}).get("diff", []):
                print(f"  {item['f14']}: {item['f2']:.2f} ({item['f3']:+.2f}%)")
    except Exception as e:
        print(f"  ⚠️ 全球指数获取失败: {e}")

    # 2. A股指数 (三路冗余)
    print("\n📈 A股主要指数:")
    indices, source = fetch_with_fallback("get_indices")
    if "error" in indices:
        print(f"  ❌ {indices['error']}")
    else:
        print(f"  数据源: {source}")
        for name, info in indices.items():
            if "error" in info:
                print(f"  {name}: ⚠️ {info['error']}")
            else:
                print(f"  {name}: {info['price']:.2f} ({info['change_pct']:+.2f}%)")

    # 3. 涨停数据
    print("\n🎯 涨停统计:")
    akshare = AkShareSource()
    zt = akshare.get_limit_up_stats()
    if "error" in zt:
        print(f"  ⚠️ {zt['error']}")
    else:
        print(f"  今日涨停: {zt['涨停家数']} 家")
        if zt.get("data"):
            for s in zt["data"][:10]:
                print(f"    {s.get('名称', '?')} ({s.get('涨幅', '?')}%)")


def print_postmarket():
    """盘后分析"""
    print("=" * 50)
    print(f"📊 盘后分析 — {datetime.now(TZ).strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    print("\n📈 A股收盘数据:")
    indices, source = fetch_with_fallback("get_indices")
    if "error" in indices:
        print(f"  ❌ {indices['error']}")
        return
    print(f"  数据源: {source}")
    for name, info in indices.items():
        if "error" not in info:
            print(f"  {name}: {info['price']:.2f} ({info['change_pct']:+.2f}%)")

    # 涨停/跌停统计
    try:
        import akshare as ak
        today = datetime.now(TZ).strftime("%Y%m%d")
        zt = ak.stock_zt_pool_em(date=today)
        dt = ak.stock_zt_pool_dtgc_em(date=today)
        print(f"\n  涨停: {len(zt)} 家 | 跌停: {len(dt)} 家")
    except Exception as e:
        print(f"  ⚠️ 涨跌停统计失败: {e}")


def print_market():
    """实时行情快照"""
    print(f"📈 实时行情 — {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    indices, source = fetch_with_fallback("get_indices")
    print(f"数据源: {source}")
    if "error" not in indices:
        for name, info in indices.items():
            if "error" not in info:
                print(f"  {name}: {info['price']:.2f} ({info['change_pct']:+.2f}%)")


# ── 入口 ──────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法: python3 analyze.py [premarket|postmarket|market]")
        print("  premarket   — 盘前分析 (全球指数 + A股实时 + 涨停)")
        print("  postmarket  — 盘后分析 (A股收盘 + 涨跌停统计)")
        print("  market      — 实时行情快照")
        sys.exit(1)

    mode = sys.argv[1]

    try:
        if mode == "premarket":
            print_premarket()
        elif mode == "postmarket":
            print_postmarket()
        elif mode == "market":
            print_market()
        else:
            print(f"未知模式: {mode}")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 分析异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
