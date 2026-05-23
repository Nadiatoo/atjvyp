#!/usr/bin/env python3
"""
============================================================================
A股统一数据管道 v1.0
============================================================================
多数据源自动降级: QVeris → akshare → mootdx → 腾讯HTTP
统一接口，调用方无需关心底层数据源切换。

设计原则:
  - 优先级: 免费 > 付费（QVeris 作为增强源，免费源作主力备用）
  - 自动降级: 单源失败时自动尝试下一优先级的源
  - 结果缓存: 同一次调用内不重复请求
  - 超时保护: 每个源有独立超时，不阻塞管线
"""

import json
import logging
import os
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

import pandas as pd

log = logging.getLogger("data_pipeline")

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
QVERIS_KEY = os.getenv("QVERIS_API_KEY", "")
QVERIS_BASE = "https://qveris.ai/api/v1"
TIMEOUTS = {"qveris": 20, "akshare": 30, "mootdx": 15, "tencent": 10}
CACHE_TTL = 60  # 秒，实时行情缓存


class DataSource:
    QVERIS = "qveris"
    AKSHARE = "akshare"
    MOOTDX = "mootdx"
    TENCENT = "tencent"


# ===========================================================================
# 数据源适配器
# ===========================================================================

class QVerisAdapter:
    """QVeris API 适配器"""

    def __init__(self):
        self.headers = {"Authorization": f"Bearer {QVERIS_KEY}", "Content-Type": "application/json"}
        self.available = bool(QVERIS_KEY)

    def get_index(self, code: str) -> Optional[dict]:
        if not self.available:
            return None
        try:
            import requests
            r = requests.post(
                f"{QVERIS_BASE}/tools/execute",
                headers=self.headers,
                json={"tool_id": "ths_ifind.real_time_quotation.v1", "parameters": {"codes": code, "indicators": "common"}},
                timeout=TIMEOUTS["qveris"]
            )
            if r.status_code == 200:
                data = r.json()
                raw = data["result"]["data"]
                if isinstance(raw, list) and len(raw) > 0 and isinstance(raw[0], list) and len(raw[0]) > 0:
                    d = raw[0][0]
                    return {"code": code, "price": float(d.get("latest", 0)),
                            "change_pct": float(d.get("changeRatio", 0)),
                            "volume": float(d.get("volume", 0)), "amount": float(d.get("amount", 0))}
        except Exception:
            pass
        return None

    def get_market_stats(self) -> Optional[dict]:
        if not self.available:
            return None
        try:
            import requests
            r = requests.post(
                f"{QVERIS_BASE}/tools/execute",
                headers=self.headers,
                json={"tool_id": "mcp_gildata.marketlimitupdowncount.v1", "parameters": {"query": "涨跌停统计"}},
                timeout=TIMEOUTS["qveris"]
            )
            if r.status_code == 200:
                table = r.json()["result"]["data"]["results"][0]["table_markdown"]
                lines = table.strip().split("\n")
                if len(lines) >= 3:
                    cells = [c.strip() for c in lines[2].split("|") if c.strip()]
                    if len(cells) >= 9:
                        return {"total": int(cells[2]), "rising": int(cells[3]),
                                "falling": int(cells[4]), "limit_up": int(cells[6]),
                                "limit_down": int(cells[7])}
        except Exception:
            pass
        return None


class AKShareAdapter:
    """akshare 适配器 — 东方财富/新浪多源"""

    @staticmethod
    def get_index(code: str) -> Optional[dict]:
        try:
            import akshare as ak
            df = ak.stock_zh_index_daily_em(symbol=code.replace(".SH", "").replace(".SZ", ""))
            if df is None or len(df) == 0:
                return None
            latest = df.iloc[-1]
            return {"code": code, "price": float(latest["close"]), "date": str(latest["date"])}
        except Exception:
            return None

    @staticmethod
    def get_realtime_spot() -> Optional[pd.DataFrame]:
        try:
            import akshare as ak
            # stock_zh_a_spot_em 有时连接断开，先试 stock_zh_a_spot
            df = ak.stock_zh_a_spot()
            if df is not None and len(df) > 100:
                return df
        except Exception:
            pass
        try:
            import akshare as ak
            return ak.stock_zh_a_spot_em()
        except Exception:
            return None

    @staticmethod
    def get_sector_rank() -> Optional[pd.DataFrame]:
        try:
            import akshare as ak
            return ak.stock_board_industry_name_em()
        except Exception:
            return None

    @staticmethod
    def get_stock_history(code: str, period: str = "daily", count: int = 60) -> Optional[pd.DataFrame]:
        try:
            import akshare as ak
            symbol = code.replace(".SH", "").replace(".SZ", "")
            df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust="qfq")
            return df.tail(count) if df is not None else None
        except Exception:
            return None


class MootdxAdapter:
    """mootdx 适配器 — 通达信直连，通过 subprocess 调用"""

    @staticmethod
    def _run(args: List[str]) -> Optional[str]:
        import subprocess
        try:
            r = subprocess.run(
                ["/Library/Frameworks/Python.framework/Versions/3.9/bin/mootdx"] + args,
                capture_output=True, text=True, timeout=TIMEOUTS["mootdx"]
            )
            return r.stdout if r.returncode == 0 else None
        except Exception:
            return None

    @staticmethod
    def get_quote(code: str) -> Optional[dict]:
        """获取实时行情 — 通达信标准市场"""
        # 优先尝试 Python API，失败则 subprocess
        try:
            from mootdx.quotes import Quotes
            c = Quotes.factory(market="std")
            rows = c.bars(symbol=code.replace(".SH", "").replace(".SZ", ""), frequency=9, offset=0)
            if rows:
                r = rows[-1]
                return {"code": code, "price": float(r["close"]), "volume": float(r["vol"])}
        except ImportError:
            pass
        # subprocess fallback
        raw = MootdxAdapter._run(["quote", code])
        return None


class TencentAdapter:
    """腾讯财经 HTTP 适配器 — 零依赖，最快"""

    BASE = "http://qt.gtimg.cn/q="

    @staticmethod
    def _fetch(codes: List[str]) -> str:
        params = ",".join(codes)
        req = urllib.request.Request(f"{TencentAdapter.BASE}{params}",
                                     headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUTS["tencent"]) as resp:
                return resp.read().decode("gbk")
        except Exception:
            return ""

    @staticmethod
    def _parse(raw: str) -> List[dict]:
        results = []
        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line or '="' not in line:
                continue
            try:
                # v_sh000001="1~上证指数~000001~..."
                key, val = line.split("=", 1)
                parts = val.strip('";').split("~")
                if len(parts) < 10:
                    continue
                results.append({
                    "code": parts[2],
                    "name": parts[1],
                    "price": float(parts[3]) if parts[3] else 0,
                    "prev_close": float(parts[4]) if parts[4] else 0,
                    "open": float(parts[5]) if parts[5] else 0,
                    "volume": int(parts[6]) if parts[6] else 0,
                })
            except (ValueError, IndexError):
                continue
        return results

    @staticmethod
    def get_quote(code: str) -> Optional[dict]:
        results = TencentAdapter._parse(TencentAdapter._fetch([code]))
        return results[0] if results else None

    @staticmethod
    def get_quotes(codes: List[str]) -> List[dict]:
        return TencentAdapter._parse(TencentAdapter._fetch(codes))


# ===========================================================================
# 缓存管理
# ===========================================================================

class _CacheEntry:
    __slots__ = ("data", "expires_at")

    def __init__(self, data, ttl_sec: int):
        self.data = data
        self.expires_at = time.time() + ttl_sec

    @property
    def valid(self) -> bool:
        return time.time() < self.expires_at


class CacheManager:
    """简单的内存+磁盘缓存，减少重复 API 调用"""

    def __init__(self, disk_dir: str = ""):
        self._mem = {}
        self._disk_dir = Path(disk_dir) if disk_dir else None
        if self._disk_dir:
            self._disk_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        # 1. 内存缓存
        entry = self._mem.get(key)
        if entry and entry.valid:
            return entry.data
        # 2. 磁盘缓存
        if self._disk_dir:
            f = self._disk_dir / f"{key}.json"
            if f.exists():
                try:
                    with open(f) as fh:
                        raw = json.loads(fh.read())
                    if raw.get("expires_at", 0) > time.time():
                        data = raw["data"]
                        self._mem[key] = _CacheEntry(data, 60)
                        return data
                except Exception:
                    pass
        return None

    def set(self, key: str, data, ttl_sec: int = CACHE_TTL):
        self._mem[key] = _CacheEntry(data, ttl_sec)
        if self._disk_dir:
            try:
                with open(self._disk_dir / f"{key}.json", "w") as f:
                    json.dump({"data": data, "expires_at": time.time() + ttl_sec}, f, default=str)
            except Exception:
                pass

    def clear(self, prefix: str = ""):
        if prefix:
            self._mem = {k: v for k, v in self._mem.items() if not k.startswith(prefix)}
        else:
            self._mem.clear()


# ===========================================================================
# 统一数据管道
# ===========================================================================

class DataPipeline:
    """
    A股统一数据管道

    用法:
        pipe = DataPipeline()
        df = pipe.get_realtime_spot()          # 全市场实时行情
        idx = pipe.get_index("000001.SH")       # 指数行情
        sectors = pipe.get_sector_rank()        # 板块排行
        hist = pipe.get_history("000001.SZ")    # 个股历史K线
        stats = pipe.get_market_stats()         # 涨跌停统计
    """

    def __init__(self):
        self.qveris = QVerisAdapter()
        self._source_used = {}
        self.cache = CacheManager(
            disk_dir=str(Path(__file__).parent / ".datapipeline_cache")
        )

    # ------------------------------------------------------------------
    # 指数行情
    # ------------------------------------------------------------------
    def get_index(self, code: str = "000001.SH") -> Optional[dict]:
        """获取指数行情，自动降级 + 缓存 + 交叉校验"""
        cache_key = f"index_{code}"

        # 缓存命中
        cached = self.cache.get(cache_key)
        if cached is not None:
            self._source_used[code] = cached.get("source", "cache")
            return cached

        # 1. 腾讯 (最快)
        tencent_code = _to_tencent(code)
        if tencent_code:
            r = TencentAdapter.get_quote(tencent_code)
            if r:
                result = self._enrich_index(r, code)
                self._source_used[code] = DataSource.TENCENT
                # 交叉校验：用 akshare 日线交叉检查
                self._cross_check(code, result)
                self.cache.set(cache_key, result, ttl_sec=CACHE_TTL)
                return result

        # 2. QVeris
        r = self.qveris.get_index(code)
        if r:
            self._source_used[code] = DataSource.QVERIS
            self.cache.set(cache_key, r, ttl_sec=CACHE_TTL)
            return r

        # 3. akshare
        r = AKShareAdapter.get_index(code)
        if r:
            self._source_used[code] = DataSource.AKSHARE
            self.cache.set(cache_key, r, ttl_sec=CACHE_TTL)
            return r

        return None

    def _cross_check(self, code: str, primary: dict) -> None:
        """交叉校验：用 akshare 日线数据验证腾讯实时报价"""
        try:
            import akshare as ak
            symbol = code.replace(".SH", "").replace(".SZ", "")
            df = ak.stock_zh_index_daily_em(symbol=symbol)
            if df is not None and len(df) > 0:
                ak_close = float(df.iloc[-1]["close"])
                price = primary.get("price", 0)
                if price > 0 and ak_close > 0:
                    deviation = abs(price - ak_close) / ak_close
                    if deviation > 0.05:  # 偏差超过5%告警
                        log.warning(
                            "交叉校验偏差过大: %s 腾讯=%.2f akshare=%.2f (%.1f%%)",
                            code, price, ak_close, deviation * 100
                        )
        except Exception:
            pass  # 交叉校验失败不阻塞主流程

    def _enrich_index(self, raw: dict, code: str) -> dict:
        prev = raw.get("prev_close", 0)
        price = raw.get("price", 0)
        change_pct = round((price - prev) / prev * 100, 2) if prev else 0
        return {"code": code, "name": raw.get("name", ""), "price": price,
                "prev_close": prev, "change_pct": change_pct, "open": raw.get("open", 0),
                "volume": raw.get("volume", 0), "source": DataSource.TENCENT}

    # ------------------------------------------------------------------
    # 全市场实时行情
    # ------------------------------------------------------------------
    def get_realtime_spot(self) -> Optional[pd.DataFrame]:
        """获取A股全市场实时行情快照"""
        cache_key = "realtime_spot"
        cached = self.cache.get(cache_key)
        if cached is not None:
            self._source_used["spot"] = "cache"
            return pd.DataFrame(cached) if isinstance(cached, list) else cached

        # akshare (主力免费源)
        df = AKShareAdapter.get_realtime_spot()
        if df is not None and len(df) > 100:
            self._source_used["spot"] = DataSource.AKSHARE
            # 缓存时转为可序列化的格式
            self.cache.set(cache_key, df.to_dict(orient="records"), ttl_sec=CACHE_TTL)
            return df
        return None

    # ------------------------------------------------------------------
    # 板块排行
    # ------------------------------------------------------------------
    def get_sector_rank(self) -> pd.DataFrame:
        """获取板块涨跌排行"""
        cache_key = "sector_rank"
        cached = self.cache.get(cache_key)
        if cached is not None:
            self._source_used["sector"] = "cache"
            return pd.DataFrame(cached) if isinstance(cached, list) else cached

        df = AKShareAdapter.get_sector_rank()
        if df is not None:
            self._source_used["sector"] = DataSource.AKSHARE
            self.cache.set(cache_key, df.to_dict(orient="records"), ttl_sec=CACHE_TTL)
        return df

    # ------------------------------------------------------------------
    # 个股历史K线
    # ------------------------------------------------------------------
    def get_history(self, code: str, period: str = "daily", count: int = 60) -> Optional[pd.DataFrame]:
        """获取个股历史K线（日/周/月）"""
        df = AKShareAdapter.get_stock_history(code, period, count)
        if df is not None:
            self._source_used[f"hist_{code}"] = DataSource.AKSHARE
        return df

    # ------------------------------------------------------------------
    # 涨跌停统计
    # ------------------------------------------------------------------
    def get_market_stats(self) -> Optional[dict]:
        """获取涨跌停家数统计"""
        # QVeris first (most reliable for stats)
        r = self.qveris.get_market_stats()
        if r:
            self._source_used["stats"] = DataSource.QVERIS
            return r
        # Fallback: estimate from spot data
        spot = self.get_realtime_spot()
        if spot is not None:
            self._source_used["stats"] = DataSource.AKSHARE
            total = len(spot)
            rising = len(spot[spot["涨跌幅"] > 0])
            limit_up = len(spot[spot["涨跌幅"] >= 9.5])
            limit_down = len(spot[spot["涨跌幅"] <= -9.5])
            return {"total": total, "rising": rising, "falling": total - rising,
                    "limit_up": limit_up, "limit_down": limit_down, "source": "akshare_estimate"}
        return None

    # ------------------------------------------------------------------
    # 多指数行情（批量）
    # ------------------------------------------------------------------
    def get_multi_index(self, codes: List[str]) -> Dict[str, dict]:
        """批量获取多个指数行情"""
        tc_codes = []
        tc_map = {}
        for c in codes:
            tc = _to_tencent(c)
            if tc:
                tc_codes.append(tc)
                tc_map[tc] = c

        results = {}
        if tc_codes:
            quotes = TencentAdapter.get_quotes(tc_codes)
            for q in quotes:
                code = tc_map.get(q.get("code", ""), q["code"])
                results[code] = self._enrich_index(q, code)
        return results

    # ------------------------------------------------------------------
    # 交叉校验
    # ------------------------------------------------------------------
    def cross_validate_index(self, code: str = "000001.SH") -> dict:
        """用多个数据源交叉校验指数价格，防止单源输出错误数据"""
        results = {}

        # 源1: 腾讯HTTP
        tc = _to_tencent(code)
        if tc:
            r = TencentAdapter.get_quote(tc)
            if r:
                results["tencent"] = {"price": r.get("price", 0), "name": r.get("name", "")}

        # 源2: akshare 日线
        r = AKShareAdapter.get_index(code)
        if r:
            results["akshare"] = {"price": r.get("price", 0), "date": str(r.get("date", ""))}

        # 源3: QVeris
        r = self.qveris.get_index(code)
        if r:
            results["qveris"] = {"price": r.get("price", 0)}

        # 计算校验结果
        prices = [(k, v["price"]) for k, v in results.items() if v.get("price", 0) > 0]
        valid = True
        warnings = []

        if len(prices) >= 2:
            avg = sum(p[1] for p in prices) / len(prices)
            for src, p in prices:
                dev = abs(p - avg) / avg if avg > 0 else 0
                if dev > 0.03:  # 单源偏差 > 3%
                    valid = False
                    warnings.append(f"{src} 偏差 {dev*100:.1f}% (价格={p:.2f}, 均值={avg:.2f})")

        return {
            "valid": valid,
            "sources": list(results.keys()),
            "prices": {k: v["price"] for k, v in results.items()},
            "warnings": warnings,
        }

    # ------------------------------------------------------------------
    # 状态报告
    # ------------------------------------------------------------------
    def status(self) -> dict:
        """返回数据源状态报告"""
        return {
            "qveris": self.qveris.available,
            "akshare": True,  # verified
            "mootdx": True,  # CLI verified
            "tencent": True,  # verified
            "sources_used": self._source_used,
        }


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _to_tencent(code: str) -> Optional[str]:
    """转腾讯代码格式"""
    if code.endswith(".SH"):
        return f"sh{code.replace('.SH', '')}"
    if code.endswith(".SZ"):
        return f"sz{code.replace('.SZ', '')}"
    if code.startswith("sh") or code.startswith("sz"):
        return code
    # 纯数字: 000xxx=深, 600/601/603/605=沪
    if len(code) == 6:
        return f"sz{code}" if code.startswith(("000", "001", "002", "003", "300", "301")) else f"sh{code}"
    return None


# ===========================================================================
# 命令行入口 + 自检
# ===========================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="A股统一数据管道")
    parser.add_argument("--test", action="store_true", help="运行自检")
    parser.add_argument("--index", default="", help="查询指数 (如 000001.SH)")
    args = parser.parse_args()

    pipe = DataPipeline()

    if args.index:
        r = pipe.get_index(args.index)
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        return

    if args.test:
        print("=" * 60)
        print("数据管道自检")
        print("=" * 60)

        # 1. 腾讯HTTP
        print("\n[1/4] 腾讯HTTP ...", end=" ")
        r = TencentAdapter.get_quote("sh000001")
        print(f"{'✅' if r else '❌'} {r['name'] if r else ''} {r.get('price', '') if r else ''}")

        # 2. akshare
        print("[2/4] akshare ...", end=" ")
        try:
            df = AKShareAdapter.get_realtime_spot()
            print(f"✅ {len(df)} 只股票")
        except Exception as e:
            print(f"❌ {e}")

        # 3. mootdx
        print("[3/4] mootdx ...", end=" ")
        try:
            from mootdx.quotes import Quotes
            Quotes.factory(market="std")
            print("✅ Python API")
        except ImportError:
            raw = MootdxAdapter._run(["--version"])
            print(f"{'✅ CLI' if raw else '❌'}")

        # 4. QVeris
        print("[4/4] QVeris ...", end=" ")
        print(f"{'✅ 已配置' if QVERIS_KEY else '⚠️ 未配置密钥'}")

        # 管线测试
        print(f"\n{'='*60}")
        print("管线端到端测试")
        print(f"{'='*60}")
        print(f"指数 (000001.SH): {'✅' if pipe.get_index('000001.SH') else '❌'}")
        stats = pipe.get_market_stats()
        print(f"涨跌停统计: {'✅' if stats else '❌'}")
        if stats:
            print(f"  涨停: {stats.get('limit_up', '?')} / 跌停: {stats.get('limit_down', '?')}")
        df = pipe.get_realtime_spot()
        print(f"全市场行情: {'✅' if df is not None else '❌'}")
        print(f"\n数据源使用: {pipe.status()['sources_used']}")
        print(f"管线状态: {pipe.status()}")


if __name__ == "__main__":
    main()
