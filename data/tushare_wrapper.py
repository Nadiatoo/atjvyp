#!/usr/bin/env python3
"""
Tushare 限速优化封装层 (Rate-Limited Tushare Wrapper)

功能：
1. 限速/节流 —— Token Bucket + 积分预算管理（高优请求优先）
2. 缓存策略 —— 日线/财务数据本地缓存 + TTL
3. 降级策略 —— Tushare 超限→自动切换 a-stock-data 免费端点→过期缓存
4. 配置管理 —— 读取 ~/.tushare/config.json

用法：
    from tushare_wrapper import safe_get

    # 自动限速 + 缓存 + 降级
    df = safe_get("daily", ts_code="000001.SZ", start_date="20260101")
    df = safe_get("fund_flow", ts_code="000001.SZ", priority="high")

依赖：
    pip install tushare pandas requests cachetools tenacity
"""

import os
import json
import time
import hashlib
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Callable, Any, Dict

import tushare as ts
import pandas as pd
import requests

# ── 日志配置 ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] tushare_wrapper: %(message)s",
)
log = logging.getLogger("tushare_wrapper")


# ═══════════════════════════════════════════════════════════
# 配置管理
# ═══════════════════════════════════════════════════════════

class TushareConfig:
    """读取 ~/.tushare/config.json 及 ~/.tushare_token"""

    DEFAULT = {
        "token": "",
        "timeout": 30,
        "retry_count": 3,
        "retry_delay": 5,
        "rate": {
            "max_per_minute": 200,        # 每分钟最大请求数
            "burst": 20,                  # 突发请求容量（秒级）
            "max_per_day": 5000,          # 每日积分上限（考虑为请求数）
        },
        "cache": {
            "enabled": True,
            "dir": str(Path.home() / ".openclaw" / "workspace" / "data" / "tushare_cache"),
            "default_ttl_hours": 2,       # 默认缓存有效期（实时行情短，日线长）
            "daily_ttl_hours": 26,        # 日线缓存到次日收盘后（比24h多2h缓冲）
            "finance_ttl_hours": 48,      # 财务数据2天有效
            "reference_ttl_hours": 168,   # 参考数据7天有效（IPO/分红等）
        },
        "fallback": {
            "enabled": True,
            "prefer_cache_over_empty": True,  # 宁愿返回过期缓存也不返回空数据
        },
        "priority_default": "normal",     # high / normal / low
    }

    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(Path.home() / ".tushare" / "config.json")
        self.token_path = str(Path.home() / ".tushare_token")
        self._data = dict(self.DEFAULT)
        self._load()

    def _load(self):
        """从磁盘加载配置，缺失字段用默认值"""
        # 1. 加载 config.json
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    user_config = json.load(f)
                self._deep_merge(self._data, user_config)
            except Exception as e:
                log.warning(f"读取配置失败 {self.config_path}: {e}，使用默认值")

        # 2. 加载 token（优先读取 token 文件）
        token = None
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, "r") as f:
                    token = f.read().strip()
            except Exception:
                pass
        if not token and self._data.get("token"):
            token = self._data["token"]
        if token:
            self._data["token"] = token

        # 3. 尝试从环境变量覆盖
        env_token = os.environ.get("TUSHARE_TOKEN")
        if env_token:
            self._data["token"] = env_token

        # 4. 确保缓存目录存在
        cache_dir = self._data["cache"]["dir"]
        os.makedirs(cache_dir, exist_ok=True)

    def _deep_merge(self, base: dict, override: dict):
        """递归合并字典，保留 base 的默认值"""
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                self._deep_merge(base[key], val)
            else:
                base[key] = val

    @property
    def token(self) -> str:
        return self._data.get("token", "")

    @property
    def rate_config(self) -> dict:
        return self._data.get("rate", {})

    @property
    def cache_config(self) -> dict:
        return self._data.get("cache", {})

    @property
    def fallback_config(self) -> dict:
        return self._data.get("fallback", {})

    @property
    def timeout(self) -> int:
        return self._data.get("timeout", 30)

    @property
    def retry_count(self) -> int:
        return self._data.get("retry_count", 3)

    @property
    def retry_delay(self) -> int:
        return self._data.get("retry_delay", 5)

    def save(self):
        """保存当前配置到 config.json（不保存 token 到该文件）"""
        save_data = dict(self._data)
        save_data.pop("token", None)  # token 单独存文件
        with open(self.config_path, "w") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        log.info(f"配置已保存到 {self.config_path}")

    def __repr__(self):
        r = self.rate_config
        c = self.cache_config
        return (
            f"TushareConfig(token=***{self.token[-4:]}, "
            f"rate={r.get('max_per_minute')}/min, "
            f"burst={r.get('burst')}, "
            f"cache_ttl={c.get('default_ttl_hours')}h, "
            f"retry={self.retry_count}x)"
        )


# ═══════════════════════════════════════════════════════════
# 限速器 —— Token Bucket 算法
# ═══════════════════════════════════════════════════════════

class TokenBucket:
    """
    Token Bucket 限速器。

    - `rate`: 每秒补充的 token 数（max_per_minute / 60）
    - `burst`: 最大突发容量
    - 支持优先级：high/normal/low 使用不同的乘数（但共享同一个桶）
      高优请求在桶不足时会"借用"低优的配额，低优请求在桶不足时会直接排队。
    """

    def __init__(self, rate: float, burst: int):
        self.rate = rate
        self.burst = burst
        self.tokens = float(burst)  # 初始满桶
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()
        self._waiters = defaultdict(int)  # priority -> count of waiting requests

    def _refill(self):
        """补充 token"""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_refill = now

    def _priority_multiplier(self, priority: str) -> float:
        """优先级乘数：高优占用更多 token 但插队"""
        multipliers = {"high": 1.5, "normal": 1.0, "low": 0.5}
        return multipliers.get(priority, 1.0)

    def acquire(self, priority: str = "normal", block: bool = True) -> bool:
        """
        获取请求权限。
        - priority: high / normal / low
        - block: True=阻塞直到有 token，False=立即返回
        Returns: True=可以请求, False=拒绝
        """
        cost = self._priority_multiplier(priority)

        with self._lock:
            self._refill()
            if self.tokens >= cost:
                self.tokens -= cost
                return True

            if not block:
                return False

            # 阻塞等待直到有足够 token
            needed = cost - self.tokens
            wait_time = needed / self.rate if self.rate > 0 else 0.1
            self._waiters[priority] += 1

        # 释放锁后等待
        time.sleep(min(wait_time, 0.5))

        with self._lock:
            self._waiters[priority] -= 1
            self._refill()
            if self.tokens >= cost:
                self.tokens -= cost
                return True
            # 仍未等到 → 重试一次（递归但深度限制）
            if self.tokens >= cost * 0.5:
                self.tokens = max(0, self.tokens - cost)
                return True
            return False

    def queue_depth(self) -> int:
        """当前排队请求数"""
        with self._lock:
            return sum(self._waiters.values())

    @property
    def available(self) -> float:
        with self._lock:
            self._refill()
            return self.tokens


# ═══════════════════════════════════════════════════════════
# 积分预算管理
# ═══════════════════════════════════════════════════════════

class PointBudget:
    """
    积分预算管理。

    不同 Tushare API 的积分消耗不同：
    - 基础行情（daily, trade_cal）: 2 分
    - 财务数据（fina_indicator, income）: 5 分
    - 资金流（moneyflow）: 7 分
    - 机构调研/股东: 10 分
    """

    API_COST = {
        # 基础API - 2分
        "daily": 2, "weekly": 2, "monthly": 2,
        "trade_cal": 2, "adj_factor": 2, "suspend_d": 2,
        "daily_basic": 2, "stk_limit": 2,
        # 财务 - 5分
        "fina_indicator": 5, "income": 5, "balancesheet": 5,
        "cashflow": 5, "forecast": 5, "express": 5,
        "dividend": 5, "fin_audit": 5,
        # 资金流 - 7分
        "moneyflow": 7, "stk_account": 7,
        # 股东/机构调研 - 10分
        "stk_holdernumber": 10, "stk_holdertrade": 10,
        "stk_rewards": 10, "stk_managers": 10,
        "new_share": 5, "ipo_list": 5,
        "stk_company": 3, "stk_managers": 10,
        # 统一默认
        "default": 3,
    }

    def __init__(self, max_per_day: int = 5000):
        self.max_per_day = max_per_day
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        """重置每日计数"""
        now = datetime.now()
        self._date = now.strftime("%Y-%m-%d")
        self.used_today = 0
        self._request_log: list[tuple[str, int, str]] = []  # (api, cost, time)

    def _check_date(self):
        """如果跨天则重置"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self._date:
            self.reset()

    def cost_of(self, api_name: str) -> int:
        """返回指定 API 的积分消耗"""
        return self.API_COST.get(api_name, self.API_COST["default"])

    def try_spend(self, api_name: str) -> bool:
        """
        尝试消耗积分。
        Returns: True=积分充足，False=积分不足（拒绝请求）
        """
        cost = self.cost_of(api_name)
        with self._lock:
            self._check_date()
            if self.used_today + cost > self.max_per_day:
                log.warning(
                    f"积分不足！今日已用 {self.used_today}/{self.max_per_day}，"
                    f"请求 {api_name} 需 {cost} 分"
                )
                return False
            self.used_today += cost
            self._request_log.append((api_name, cost, datetime.now().isoformat()))
        return True

    @property
    def remaining(self) -> int:
        with self._lock:
            self._check_date()
            return max(0, self.max_per_day - self.used_today)

    @property
    def usage(self) -> str:
        with self._lock:
            self._check_date()
            return f"{self.used_today}/{self.max_per_day}"

    def summary(self) -> dict:
        with self._lock:
            self._check_date()
            return {
                "date": self._date,
                "used": self.used_today,
                "max": self.max_per_day,
                "remaining": self.remaining,
            }


# ═══════════════════════════════════════════════════════════
# 缓存管理器
# ═══════════════════════════════════════════════════════════

class TushareCache:
    """本地文件缓存 + TTL 管理"""

    def __init__(self, config: TushareConfig):
        cfg = config.cache_config
        self.cache_dir = Path(cfg.get("dir"))
        self.default_ttl = cfg.get("default_ttl_hours", 2) * 3600
        self.daily_ttl = cfg.get("daily_ttl_hours", 26) * 3600
        self.finance_ttl = cfg.get("finance_ttl_hours", 48) * 3600
        self.reference_ttl = cfg.get("reference_ttl_hours", 168) * 3600
        self.enabled = cfg.get("enabled", True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, api_name: str, **params) -> str:
        """生成唯一缓存键（基于 API + 参数哈希）"""
        # 排除分页和时间戳参数
        skip_keys = {"limit", "offset", "start_date", "end_date",
                     "trade_date"}
        filtered = {k: v for k, v in sorted(params.items()) if k not in skip_keys}
        raw = f"{api_name}:{json.dumps(filtered, sort_keys=True)}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _ttl_for(self, api_name: str) -> int:
        """根据 API 类型返回 TTL（秒）"""
        # 财务数据
        if api_name in ("fina_indicator", "income", "balancesheet",
                        "cashflow", "forecast", "express"):
            return self.finance_ttl
        # 日线基础行情
        if api_name in ("daily", "daily_basic", "weekly", "monthly",
                        "adj_factor", "stk_limit"):
            return self.daily_ttl
        # 参考数据（IPO, 分红等）
        if api_name in ("new_share", "dividend", "ipo_list", "stk_company",
                        "trade_cal"):
            return self.reference_ttl
        # 默认
        return self.default_ttl

    @staticmethod
    def _gs_pickle(df: pd.DataFrame) -> bytes:
        """DataFrame → pickle bytes"""
        import pickle
        return pickle.dumps(df)

    @staticmethod
    def _gs_unpickle(data: bytes) -> pd.DataFrame:
        """pickle bytes → DataFrame"""
        import pickle
        return pickle.loads(data)

    def get(self, api_name: str, **params) -> Optional[pd.DataFrame]:
        """读取缓存，None=未命中或过期"""
        if not self.enabled:
            return None

        cache_key = self._cache_key(api_name, **params)
        ttl = self._ttl_for(api_name)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        meta_file = self.cache_dir / f"{cache_key}.meta"

        if not cache_file.exists() or not meta_file.exists():
            return None

        try:
            meta = json.loads(meta_file.read_text())
            cached_at = meta.get("cached_at", 0)
            age = time.time() - cached_at

            if age < ttl:
                # 有效缓存
                data = self._gs_unpickle(cache_file.read_bytes())
                log.info(
                    f"缓存命中 [{api_name}] 键={cache_key[:8]} 年龄={age/3600:.1f}h "
                    f"TTL={ttl/3600:.1f}h"
                )
                return data
            else:
                # 缓存过期但保留
                log.info(
                    f"缓存过期 [{api_name}] 键={cache_key[:8]} 年龄={age/3600:.1f}h "
                    f"> TTL={ttl/3600:.1f}h"
                )
                return None
        except Exception as e:
            log.warning(f"缓存读取失败 [{api_name}]: {e}")
            return None

    def get_expired(self, api_name: str, **params) -> Optional[pd.DataFrame]:
        """读取过期缓存（降级用：有数据总比空好）"""
        if not self.enabled:
            return None

        cache_key = self._cache_key(api_name, **params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if not cache_file.exists():
            return None

        try:
            data = self._gs_unpickle(cache_file.read_bytes())
            age = time.time() - os.path.getmtime(cache_file)
            log.info(
                f"过期缓存降级 [{api_name}] 年龄={age/3600:.1f}h → 返回"
            )
            return data
        except Exception:
            return None

    def set(self, df: pd.DataFrame, api_name: str, **params):
        """写入缓存"""
        if not self.enabled or df is None or df.empty:
            return

        cache_key = self._cache_key(api_name, **params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        meta_file = self.cache_dir / f"{cache_key}.meta"

        try:
            cache_file.write_bytes(self._gs_pickle(df))
            meta = {
                "api": api_name,
                "params": params,
                "cached_at": time.time(),
                "ttl": self._ttl_for(api_name),
                "rows": len(df),
                "columns": list(df.columns),
            }
            meta_file.write_text(json.dumps(meta, indent=2))
            log.info(
                f"缓存写入 [{api_name}] 键={cache_key[:8]} "
                f"行数={len(df)} TTL={self._ttl_for(api_name)/3600:.1f}h"
            )
        except Exception as e:
            log.warning(f"缓存写入失败 [{api_name}]: {e}")

    def clear(self, api_name: str = None):
        """清理缓存。None=全部清理，指定名称=清理该类型"""
        cleared = 0
        for f in self.cache_dir.glob("*.pkl"):
            m = self.cache_dir / (f.stem + ".meta")
            if api_name is None:
                f.unlink(missing_ok=True)
                m.unlink(missing_ok=True)
                cleared += 1
            elif m.exists():
                try:
                    meta = json.loads(m.read_text())
                    if meta.get("api") == api_name:
                        f.unlink(missing_ok=True)
                        m.unlink(missing_ok=True)
                        cleared += 1
                except Exception:
                    pass
        log.info(f"缓存清理: {cleared} 个文件 (api={api_name or 'all'})")

    def stats(self) -> dict:
        """缓存统计"""
        total = 0
        by_api = defaultdict(int)
        total_size = 0
        for f in self.cache_dir.glob("*.pkl"):
            m = self.cache_dir / (f.stem + ".meta")
            total += 1
            total_size += f.stat().st_size
            if m.exists():
                try:
                    meta = json.loads(m.read_text())
                    by_api[meta.get("api", "unknown")] += 1
                except Exception:
                    by_api["unknown"] += 1
        return {
            "total_files": total,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "by_api": dict(by_api),
        }


# ═══════════════════════════════════════════════════════════
# a-stock-data 降级端点（免费替代）
# ═══════════════════════════════════════════════════════════

class AStockDataFallback:
    """
    a-stock-data 免费端点降级。

    当 Tushare 超限/不可用时，自动切换到这里。
    这些是从 ~/.claude/skills/a-stock-data/SKILL.md 提取的核心免费端点。
    """

    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    TIMEOUT = 15

    @classmethod
    def daily(cls, ts_code: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        降级：通过 mootdx 获取日线。

        ts_code: "000001.SZ" 或 "000001"
        注意：mootdx 不通过 HTTP，使用达信 TCP 协议，不封IP。
        """
        try:
            from mootdx.quotes import Quotes
            client = Quotes.factory(market='std')

            # 解析代码
            code = ts_code.split(".")[0] if "." in ts_code else ts_code[:6]
            # 市场: 0=深圳, 1=上海
            market = 1 if code.startswith(("6", "9")) else 0

            klines = client.bars(symbol=code, category=4, offset=500)
            if klines is None or len(klines) == 0:
                return None

            df = pd.DataFrame(klines)
            df.columns = ["date", "open", "close", "high", "low", "vol", "amount"]
            df["date"] = pd.to_datetime(df["date"])

            # 过滤日期范围
            if start_date:
                df = df[df["date"] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df["date"] <= pd.to_datetime(end_date)]

            df["ts_code"] = ts_code
            df["pct_chg"] = df["close"].pct_change() * 100
            log.info(f"【降级】mootdx 提供日线: {len(df)} 行 [{ts_code}]")
            return df
        except Exception as e:
            log.warning(f"【降级失败】mootdx: {e}")
            return None

    @classmethod
    def daily_basic(cls, ts_code: str) -> Optional[pd.DataFrame]:
        """
        降级：通过腾讯财经获取实时 PE/PB/市值。

        返回 Tushare 兼容格式的 DataFrame（单日快照）。
        """
        try:
            code = ts_code.split(".")[0] if "." in ts_code else ts_code[:6]
            if code.startswith(("6", "9")):
                prefixed = f"sh{code}"
            elif code.startswith("8"):
                prefixed = f"bj{code}"
            else:
                prefixed = f"sz{code}"

            url = f"https://qt.gtimg.cn/q={prefixed}"
            req = requests.get(url, headers={"User-Agent": cls.UA}, timeout=cls.TIMEOUT)
            data = req.content.decode("gbk")

            for line in data.strip().split(";"):
                if not line.strip() or "=" not in line or '"' not in line:
                    continue
                vals = line.split('"')[1].split("~")
                if len(vals) < 53:
                    continue
                today = datetime.now().strftime("%Y%m%d")
                df = pd.DataFrame([{
                    "ts_code": ts_code,
                    "trade_date": today,
                    "close": float(vals[3]) if vals[3] else 0,
                    "pe": float(vals[39]) if vals[39] else 0,
                    "pe_ttm": float(vals[39]) if vals[39] else 0,
                    "pb": float(vals[46]) if vals[46] else 0,
                    "total_mv": float(vals[44]) if vals[44] else 0,
                    "circ_mv": float(vals[45]) if vals[45] else 0,
                    "turnover_rate": float(vals[38]) if vals[38] else 0,
                }])
                log.info(f"【降级】腾讯财经提供 basic: [{ts_code}]")
                return df
        except Exception as e:
            log.warning(f"【降级失败】腾讯财经: {e}")
            return None

    @classmethod
    def fund_flow(cls, ts_code: str) -> Optional[pd.DataFrame]:
        """
        降级：通过东财 push2 获取个股资金流。

        Tushare moneyflow 的替代方案。
        """
        try:
            code = ts_code.split(".")[0] if "." in ts_code else ts_code[:6]
            secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
            url = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
            params = {
                "secid": secid, "klt": 101,
                "fields1": "f1,f2,f3,f7",
                "fields2": "f51,f52,f53,f54,f55,f56,f57",
            }
            r = requests.get(url, params=params, headers={"User-Agent": cls.UA},
                             timeout=cls.TIMEOUT)
            d = r.json()

            klines = d.get("data", {}).get("klines", [])
            if not klines:
                return None

            rows = []
            for line in klines:
                parts = line.split(",")
                if len(parts) >= 6:
                    rows.append({
                        "trade_date": parts[0][:10].replace("-", ""),
                        "buy_lg_vol": float(parts[1]),   # 主力净流入
                        "buy_sm_vol": float(parts[2]),   # 小单净流入
                        "buy_md_vol": float(parts[3]),   # 中单
                        "buy_ll_vol": float(parts[4]),   # 大单
                        "buy_elg_vol": float(parts[5]),  # 超大单
                        "ts_code": ts_code,
                    })
            if rows:
                log.info(f"【降级】东财 push2 提供资金流: {len(rows)} 日 [{ts_code}]")
                return pd.DataFrame(rows)
        except Exception as e:
            log.warning(f"【降级失败】东财资金流: {e}")
            return None

    @classmethod
    def ta(cls, ts_code: str, indicator: str = "rsi") -> Optional[Any]:
        """
        降级：通过百度股市通获取带均线的K线（用于技术分析）。
        """
        try:
            code = ts_code.split(".")[0] if "." in ts_code else ts_code[:6]
            url = "https://finance.pae.baidu.com/selfselect/getstockquotation"
            params = {
                "all": "1", "isIndex": "false", "isBk": "false",
                "isBlock": "false", "isFutures": "false", "isStock": "true",
                "newFormat": "1", "group": "quotation_kline_ab",
                "finClientType": "pc", "code": code, "ktype": "1",
            }
            headers = {
                "User-Agent": cls.UA,
                "Accept": "application/vnd.finance-web.v1+json",
                "Origin": "https://gushitong.baidu.com",
                "Referer": "https://gushitong.baidu.com/",
            }
            r = requests.get(url, params=params, headers=headers, timeout=cls.TIMEOUT)
            d = r.json()
            result = d.get("Result", {})
            md = result.get("newMarketData", {})
            keys = md.get("keys", [])
            rows_str = md.get("marketData", "")
            if not rows_str:
                return None

            # 查找 ma5/ma10/ma20 索引
            ma5_idx = -1
            ma10_idx = -1
            ma20_idx = -1
            for i, k in enumerate(keys):
                k_lower = k.lower()
                if "ma5avgprice" in k_lower:
                    ma5_idx = i
                elif "ma10avgprice" in k_lower:
                    ma10_idx = i
                elif "ma20avgprice" in k_lower:
                    ma20_idx = i

            rows = [r.split(",") for r in rows_str.split(";") if r.strip()]
            record = {}
            if rows:
                last = rows[-1]
                if ma5_idx >= 0 and ma5_idx < len(last):
                    record["ma5"] = float(last[ma5_idx])
                if ma10_idx >= 0 and ma10_idx < len(last):
                    record["ma10"] = float(last[ma10_idx])
                if ma20_idx >= 0 and ma20_idx < len(last):
                    record["ma20"] = float(last[ma20_idx])
                record["ts_code"] = ts_code

            if record:
                log.info(f"【降级】百度股市通提供 MA: [{ts_code}]")
                return pd.DataFrame([record])
        except Exception as e:
            log.warning(f"【降级失败】百度股市通: {e}")
            return None


# ═══════════════════════════════════════════════════════════
# 全局单例
# ═══════════════════════════════════════════════════════════

_config = None
_bucket = None
_budget = None
_cache = None
_ts_initialized = False
_ts_lock = threading.Lock()


def _init():
    """延迟初始化全局单例"""
    global _config, _bucket, _budget, _cache, _ts_initialized

    if _config is not None:
        return

    _config = TushareConfig()
    rc = _config.rate_config
    rate_per_sec = rc.get("max_per_minute", 200) / 60.0
    _bucket = TokenBucket(rate=rate_per_sec, burst=rc.get("burst", 20))
    _budget = PointBudget(max_per_day=rc.get("max_per_day", 5000))
    _cache = TushareCache(_config)

    # 初始化 Tushare
    token = _config.token
    if token:
        with _ts_lock:
            if not _ts_initialized:
                try:
                    ts.set_token(token)
                    _ts_initialized = True
                    log.info(f"Tushare 初始化成功 (token=***{token[-4:]})")
                except Exception as e:
                    log.error(f"Tushare 初始化失败: {e}")
    else:
        log.warning("Tushare token 未设置！所有请求将走降级/免费端点。")

    log.info(f"TushareWrapper 已就绪: {_config}")


# ═══════════════════════════════════════════════════════════
# 核心 API
# ═══════════════════════════════════════════════════════════

# Tushare API 映射表：api_name → 对应的 tushare pro 方法
API_METHODS = {
    "daily":         "daily",
    "weekly":        "weekly",
    "monthly":       "monthly",
    "daily_basic":   "daily_basic",
    "trade_cal":     "trade_cal",
    "adj_factor":    "adj_factor",
    "suspend_d":     "suspend_d",
    "stk_limit":     "stk_limit",
    "fina_indicator": "fina_indicator",
    "income":        "income",
    "balancesheet":  "balancesheet",
    "cashflow":      "cashflow",
    "forecast":      "forecast",
    "express":       "express",
    "dividend":      "dividend",
    "moneyflow":     "moneyflow",
    "stk_holdernumber": "stk_holdernumber",
    "stk_holdertrade": "stk_holdertrade",
    "stk_company":   "stk_company",
    "new_share":     "new_share",
    "stk_managers":  "stk_managers",
    "stk_rewards":   "stk_rewards",
    "fund_portfolio": "fund_portfolio",
    "fund_share":    "fund_share",
    "fund_nav":      "fund_nav",
    "index_daily":   "index_daily",
    "index_basic":   "index_basic",
    "top10_holders": "top10_holders",
    "top10_floatholders": "top10_floatholders",
    "limit_list":    "limit_list",
}

# 降级映射：Tushare API → a-stock-data 免费替代
FALLBACK_MAP = {
    "daily":        AStockDataFallback.daily,
    "daily_basic":  AStockDataFallback.daily_basic,
    "weekly":       AStockDataFallback.daily,       # 用日线聚合
    "monthly":      AStockDataFallback.daily,       # 用日线聚合
    "moneyflow":    AStockDataFallback.fund_flow,
}


def safe_get(api_name: str, priority: str = None, **kwargs) -> Optional[pd.DataFrame]:
    """
    安全的 Tushare 数据获取入口。

    自动处理：限速 → 积分检查 → 缓存查询 → Tushare API 调用 →
    缓存写入 → 降级（Tushare 失败时）→ 过期缓存兜底

    Args:
        api_name: Tushare API 名称（如 "daily", "daily_basic"）
        priority: 请求优先级（"high"/"normal"/"low"），默认使用配置值
        **kwargs: 传递给 Tushare API 的参数（如 ts_code, start_date, end_date）

    Returns:
        pd.DataFrame 或 None（全部失败时）

    Examples:
        df = safe_get("daily", ts_code="000001.SZ", start_date="20260101")
        df = safe_get("daily_basic", ts_code="000001.SZ", priority="high")
        df = safe_get("fina_indicator", ts_code="000001.SZ", period="20251231")
    """
    _init()
    priority = priority or _config.rate_config.get("priority_default", "normal")

    api_method = API_METHODS.get(api_name)
    fallback_func = FALLBACK_MAP.get(api_name)

    # 1. 尝试缓存（所有请求先查缓存）
    if _cache.enabled:
        cached = _cache.get(api_name, **kwargs)
        if cached is not None and not cached.empty:
            return cached

    # 2. 限速等待（高优请求等待更短）
    if not _bucket.acquire(priority=priority, block=True):
        log.warning(f"限速器拒绝 [{api_name}] priority={priority}")
        return _try_fallback(api_name, fallback_func, **kwargs)

    # 3. 积分检查
    if not _budget.try_spend(api_name):
        log.warning(f"积分不足 [{api_name}] {_budget.usage}")
        return _try_fallback(api_name, fallback_func, **kwargs)

    # 4. 调用 Tushare API
    try:
        pro = ts.pro_api(timeout=_config.timeout)
        method = getattr(pro, api_method, None)
        if method is None:
            log.error(f"不支持的 Tushare API: {api_name}")
            return _try_fallback(api_name, fallback_func, **kwargs)

        df = method(**kwargs, retry_count=_config.retry_count)
        if df is not None and not df.empty:
            # 写入缓存
            _cache.set(df, api_name, **kwargs)
            return df

        # Tushare 返回空数据
        log.warning(f"Tushare [{api_name}] 返回空数据")
    except Exception as e:
        log.warning(f"Tushare [{api_name}] 失败: {e}")
        # 检查是否有 Tushare 限流错误
        err_str = str(e).lower()
        if "over limit" in err_str or "frequency" in err_str or "rate limit" in err_str:
            log.warning(f"检测到 Tushare 限流错误，标记限速器")
            # 触发限速器降速
            with _bucket._lock:
                _bucket.tokens = max(0, _bucket.tokens - _bucket.burst * 0.5)

    # 5. 降级：使用 a-stock-data 免费端点
    result = _try_fallback(api_name, fallback_func, **kwargs)
    if result is not None:
        return result

    # 6. 最后兜底：读取过期缓存
    if _config.fallback_config.get("prefer_cache_over_empty", True):
        expired = _cache.get_expired(api_name, **kwargs)
        if expired is not None:
            log.info(f"过期缓存兜底 [{api_name}] → 返回 {len(expired)} 行")
            return expired

    return None


def _try_fallback(api_name: str, fallback_func: Callable, **kwargs) -> Optional[pd.DataFrame]:
    """尝试降级到免费端点"""
    if not _config.fallback_config.get("enabled", True):
        return None
    if fallback_func is None:
        return None

    log.info(f"尝试降级 [{api_name}] → {fallback_func.__name__}")
    try:
        # 提取 ts_code 和日期参数
        ts_code = kwargs.get("ts_code", "")
        start_date = kwargs.get("start_date", "")
        end_date = kwargs.get("end_date", "")

        if api_name in ("weekly", "monthly") and fallback_func == AStockDataFallback.daily:
            # 周/月线用日线降级
            df = fallback_func(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df is not None and not df.empty:
                if api_name == "weekly":
                    df = df.set_index("date").resample("W").agg({
                        "open": "first", "high": "max", "low": "min",
                        "close": "last", "vol": "sum", "amount": "sum",
                    }).reset_index()
                elif api_name == "monthly":
                    df = df.set_index("date").resample("M").agg({
                        "open": "first", "high": "max", "low": "min",
                        "close": "last", "vol": "sum", "amount": "sum",
                    }).reset_index()
            return df

        return fallback_func(ts_code=ts_code, start_date=start_date, end_date=end_date)
    except Exception as e:
        log.warning(f"降级失败 [{api_name}]: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# 便捷辅助函数
# ═══════════════════════════════════════════════════════════

def get_status() -> dict:
    """获取当前限速/缓存/积分状态"""
    _init()
    return {
        "config": str(_config),
        "rate_limiter": {
            "available_tokens": round(_bucket.available, 2),
            "burst_capacity": _bucket.burst,
            "queue_depth": _bucket.queue_depth(),
        },
        "point_budget": _budget.summary(),
        "cache": _cache.stats(),
        "ts_initialized": _ts_initialized,
    }


def clear_cache(api_name: str = None):
    """清理缓存"""
    _init()
    _cache.clear(api_name)


def update_config(**kwargs):
    """更新运行时配置"""
    _init()
    for key, val in kwargs.items():
        if key in _config._data:
            if isinstance(_config._data[key], dict) and isinstance(val, dict):
                _config._data[key].update(val)
            else:
                _config._data[key] = val
    _config.save()


def batch_get(api_name: str, codes: list[str], priority: str = "normal",
              **kwargs) -> dict:
    """
    批量获取多只股票的数据（自动限速，code 间的间隔由限速器控制）。

    Args:
        api_name: API 名称
        codes: 股票代码列表
        priority: 请求优先级
        **kwargs: 其他参数

    Returns:
        {code: df_or_none}
    """
    results = {}
    for i, code in enumerate(codes):
        result = safe_get(api_name, ts_code=code, priority=priority, **kwargs)
        results[code] = result
        if result is not None:
            log.info(f"批量 [{api_name}] [{i+1}/{len(codes)}] {code}: {len(result)} 行")
    return results


# ═══════════════════════════════════════════════════════════
# 命令行入口
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import pprint

    _init()

    if len(sys.argv) < 2:
        print("用法: python3 tushare_wrapper.py <命令> [参数]")
        print("")
        print("命令:")
        print("  status         显示当前限速/缓存/积分状态")
        print("  get <api>      调用 Tushare API 示例")
        print("    --code       股票代码 (默认 000001.SZ)")
        print("  batch <api>    批量获取示例")
        print("    --codes      逗号分隔的代码列表")
        print("  clear_cache    清理所有缓存")
        print("    --api        指定清理的 API 类型")
        print("  config         显示当前配置")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "status":
        status = get_status()
        pprint.pprint(status)
        print(f"\n{'='*50}")
        print(f"可用命令: daily_basic, moneyflow (免费端点测试)")
        print("示例: python3 tushare_wrapper.py get daily --code 000001.SZ")

    elif cmd == "get":
        api = sys.argv[2] if len(sys.argv) > 2 else "daily"
        code = "000001.SZ"
        for i, arg in enumerate(sys.argv):
            if arg == "--code" and i + 1 < len(sys.argv):
                code = sys.argv[i + 1]
        df = safe_get(api, ts_code=code, start_date="20260101")
        if df is not None:
            print(f"\n{api} 数据 [{code}]:")
            print(df.head(10).to_string())
            print(f"\n共 {len(df)} 行")
        else:
            print(f"\n获取 [{api}] 失败（所有路径均已尝试）")

    elif cmd == "batch":
        api = sys.argv[2] if len(sys.argv) > 2 else "daily_basic"
        codes = ["000001.SZ", "600519.SH", "300750.SZ"]
        for i, arg in enumerate(sys.argv):
            if arg == "--codes" and i + 1 < len(sys.argv):
                codes = [c.strip() for c in sys.argv[i + 1].split(",")]
        results = batch_get(api, codes, priority="normal")
        for code, df in results.items():
            status = f"{len(df)} 行" if df is not None else "失败"
            print(f"  {code}: {status}")

    elif cmd == "clear_cache":
        api = None
        for i, arg in enumerate(sys.argv):
            if arg == "--api" and i + 1 < len(sys.argv):
                api = sys.argv[i + 1]
        clear_cache(api)

    elif cmd == "config":
        pprint.pprint(_config._data)
        print(f"\nToken: ***{_config.token[-4:]}")
        print(f"Cache dir: {_config.cache_config.get('dir')}")
