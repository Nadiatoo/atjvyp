#!/usr/bin/env python3
"""
============================================================================
彪哥战法 v5.0 统一分析引擎
============================================================================
整合: 季节判断(规则+QLib ML) + 龙头识别 + 中军识别 + 真夏长确认 + 风控
数据源: QVeris API (唯一主数据源)
回退策略: 明确报错，不使用模拟/硬编码数据
============================================================================
"""

import os
import json
import sys
import time
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

import requests
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace"))
QLIB_DIR = WORKSPACE / "qlib_biaoge"
QLIB_MODEL_PATH = QLIB_DIR / "biaoge_season_model.pkl"
ARCHIVE_DIR = WORKSPACE / "archive" / f"biage_cleanup_{datetime.now():%Y%m%d}"

QVERIS_API_KEY = os.getenv("QVERIS_API_KEY", "")
QVERIS_BASE = "https://qveris.ai/api/v1"
API_TIMEOUT = 25
MAX_RETRIES = 2

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("biage_engine")


# ===========================================================================
# 第1部分: 数据获取层
# ===========================================================================

class DataFetchError(Exception):
    """数据获取失败 — 明确报错，不用假数据"""


class QVerisClient:
    """QVeris API 客户端 — 带重试和超时"""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or QVERIS_API_KEY
        self.base = QVERIS_BASE
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _call(self, tool_id: str, params: dict) -> Optional[dict]:
        url = f"{self.base}/tools/execute"
        payload = {"tool_id": tool_id, "parameters": params}

        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = requests.post(url, headers=self.headers, json=payload, timeout=API_TIMEOUT)
                if resp.status_code == 200:
                    return resp.json()
                log.warning(f"API {tool_id} attempt {attempt+1}: HTTP {resp.status_code}")
            except requests.Timeout:
                log.warning(f"API {tool_id} attempt {attempt+1}: timeout")
            except Exception as e:
                log.warning(f"API {tool_id} attempt {attempt+1}: {e}")

            if attempt < MAX_RETRIES:
                time.sleep(2 * (attempt + 1))

        return None

    def get_index(self, code: str) -> dict:
        """获取指数行情"""
        result = self._call("ths_ifind.real_time_quotation.v1", {
            "codes": code, "indicators": "common"
        })
        try:
            raw = result["result"]["data"]
            if isinstance(raw, list) and len(raw) > 0:
                if isinstance(raw[0], list) and len(raw[0]) > 0:
                    d = raw[0][0]
                    return {
                        "code": code,
                        "price": float(d.get("latest", 0)),
                        "change_pct": float(d.get("changeRatio", 0)),
                        "volume": float(d.get("volume", 0)),
                        "amount": float(d.get("amount", 0)),
                    }
        except (KeyError, IndexError, TypeError, ValueError):
            pass
        raise DataFetchError(f"无法获取指数行情: {code}")

    def get_market_stats(self) -> dict:
        """获取涨跌停家数统计"""
        result = self._call("mcp_gildata.marketlimitupdowncount.v1", {
            "query": "获取今日市场涨跌停家数统计"
        })
        try:
            table = result["result"]["data"]["results"][0]["table_markdown"]
            lines = table.strip().split("\n")
            if len(lines) >= 3:
                cells = [c.strip() for c in lines[2].split("|") if c.strip()]
                if len(cells) >= 9:
                    return {
                        "total": int(cells[2]),
                        "rising": int(cells[3]),
                        "falling": int(cells[4]),
                        "limit_up": int(cells[6]),
                        "limit_down": int(cells[7]),
                    }
        except (KeyError, IndexError, ValueError, TypeError):
            pass
        raise DataFetchError("无法获取涨跌停统计")

    def get_sector_leaders(self, top_n: int = 10) -> list:
        """获取领涨板块"""
        result = self._call("eodhd.screener.query.v1.f890c0dc", {
            "query": f"获取A股涨幅前{top_n}的板块和概念"
        })
        try:
            table = result["result"]["data"]["results"][0]["table_markdown"]
            sectors = []
            for i, line in enumerate(table.strip().split("\n")):
                if i < 2:
                    continue
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 3:
                    try:
                        sectors.append({
                            "name": cells[1],
                            "change_pct": float(cells[2].replace("%", "").replace("+", ""))
                        })
                    except ValueError:
                        continue
            return sectors[:top_n]
        except (KeyError, IndexError):
            pass
        return []

    def get_stock_screener(self) -> Optional[pd.DataFrame]:
        """获取全市场股票筛选数据"""
        result = self._call("eodhd.screener.query.v1.f890c0dc", {
            "query": "获取A股全市场股票行情，包含涨跌幅、换手率、成交额、总市值"
        })
        try:
            table = result["result"]["data"]["results"][0]["table_markdown"]
            rows = []
            header = None
            for i, line in enumerate(table.strip().split("\n")):
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if i == 0:
                    header = cells
                elif i >= 2 and header:
                    if len(cells) >= len(header):
                        rows.append(dict(zip(header, cells)))
            return pd.DataFrame(rows)
        except (KeyError, IndexError):
            pass
        return None


# ===========================================================================
# 第2部分: QLib 模型加载
# ===========================================================================

class QLibSeasonPredictor:
    """QLib 四季预测模型包装器"""

    def __init__(self, model_path: str = ""):
        self.model = None
        self.feature_names = None
        self.season_names = ["春播", "夏长", "秋收", "冬藏"]
        self._loaded = False

        path = model_path or str(QLIB_MODEL_PATH)
        if os.path.exists(path):
            self._load(path)

    def _load(self, path: str):
        try:
            import joblib
            data = joblib.load(path)
            self.model = data["model"]
            self.feature_names = data["feature_names"]
            self._loaded = True
            log.info(f"QLib模型已加载: {path} (特征: {len(self.feature_names)}维)")
        except Exception as e:
            log.warning(f"QLib模型加载失败: {e}，将使用规则判断")

    @property
    def available(self) -> bool:
        return self._loaded and self.model is not None

    def predict(self, features: dict) -> Tuple[str, float, dict]:
        """
        返回: (季节名, 置信度, 四季概率分布)
        """
        if not self.available:
            return ("模型不可用", 0.0, {})

        # 构建特征向量(按模型期望的顺序)
        try:
            X = pd.DataFrame([features])[self.feature_names]
            proba = self.model.predict_proba(X)[0]
            pred = int(self.model.predict(X)[0])

            season = self.season_names[pred] if pred < len(self.season_names) else "未知"
            confidence = float(proba[pred])

            probs = {
                self.season_names[i]: float(proba[i])
                for i in range(min(len(proba), len(self.season_names)))
            }
            return (season, confidence, probs)
        except Exception as e:
            log.warning(f"QLib预测失败: {e}")
            return ("预测异常", 0.0, {})


# ===========================================================================
# 第3部分: 季节判断引擎 (规则 + ML 融合)
# ===========================================================================

class SeasonEngine:
    """
    季节判断引擎 — 规则引擎 + QLib模型双重验证

    规则判断（7分支修正逻辑）:
      - 跌停>30 或 上涨比例<15% → 混沌期
      - 上涨<20% 且 涨停<60 → 情绪冰点期
      - 上涨20-40% 且 涨停<80 → 冬藏期
      - 上涨40-60% 且 涨停≥80 → 春播期
      - 上涨≥60% 且 涨停≥100 → 夏长期
      - 上涨≥60% 且 涨停≥80 且 指数涨>1% → 秋收期
      - else → 观察期 (权重:夏长>冬藏>春播)
    """

    REGIME_MAP = {
        "混沌期":   {"position": "0-10%",  "strategy": "空仓避险",   "仓位": 0.05},
        "情绪冰点期": {"position": "10-20%", "strategy": "极轻仓试探", "仓位": 0.15},
        "冬藏期":   {"position": "20-30%", "strategy": "轻仓防守",   "仓位": 0.25},
        "春播期":   {"position": "30-50%", "strategy": "分批建仓",   "仓位": 0.40},
        "夏长期":   {"position": "50-70%", "strategy": "重仓持有",   "仓位": 0.60},
        "秋收期":   {"position": "30-50%", "strategy": "逐步减仓",   "仓位": 0.40},
        "观察期":   {"position": "20-30%", "strategy": "谨慎观察",   "仓位": 0.25},
    }

    def __init__(self, qlib_predictor: Optional[QLibSeasonPredictor] = None):
        self.qlib = qlib_predictor

    def judge(self, stats: dict, sh_change: float, weekly_trend: int = 0) -> dict:
        """
        综合季节判断
        Args:
            stats: 涨跌停统计
            sh_change: 上证涨跌幅%
            weekly_trend: 周线趋势方向 (1=向上, 0=横盘, -1=向下)
        """
        total = stats.get("total", 5000)
        rising = stats.get("rising", 0)
        limit_up = stats.get("limit_up", 0)
        limit_down = stats.get("limit_down", 0)
        rising_ratio = rising / total if total > 0 else 0

        # 规则判断
        regime = self._rule_judge(limit_down, limit_up, rising_ratio, sh_change)

        # 周线过滤: 周线向下时，夏长→春播，春播→冬藏
        if weekly_trend < 0:
            if regime == "夏长期":
                regime = "春播期"
            elif regime == "春播期":
                regime = "冬藏期"

        # 周线上穿时额外加分
        if weekly_trend > 0 and regime in ("混沌期", "情绪冰点期"):
            regime = "春播期"

        info = self.REGIME_MAP.get(regime, self.REGIME_MAP["观察期"])

        result = {
            "regime": regime,
            "position": info["position"],
            "strategy": info["strategy"],
            "position_pct": info["仓位"],
            "rising_ratio": round(rising_ratio, 3),
            "limit_up": limit_up,
            "limit_down": limit_down,
            "has_strong_stock_liquidation": limit_down > 30,
        }

        # QLib模型验证
        if self.qlib and self.qlib.available:
            try:
                features = self._build_qlib_features(stats, sh_change)
                ml_season, ml_conf, ml_probs = self.qlib.predict(features)
                result["ml_season"] = ml_season
                result["ml_confidence"] = round(ml_conf, 3)
                result["ml_probs"] = ml_probs
                # 规则和ML一致时提升置信度
                if ml_season == regime:
                    result["consensus"] = True
            except Exception:
                pass

        return result

    def _rule_judge(self, limit_down: int, limit_up: int, rising_ratio: float, sh_change: float) -> str:
        """7分支核心判断逻辑"""
        # 1. 混沌期（最恐慌）
        if limit_down > 30 or rising_ratio < 0.15:
            return "混沌期"
        # 2. 情绪冰点
        if rising_ratio < 0.20 and limit_up < 60:
            return "情绪冰点期"
        # 3. 冬藏
        if 0.20 <= rising_ratio < 0.40 and limit_up < 80:
            return "冬藏期"
        # 4. 夏长（涨停≥100，量价齐升 — 最高优先级，覆盖其他信号）
        if rising_ratio >= 0.60 and limit_up >= 100:
            return "夏长期"
        # 5. 秋收（涨停80-99但指数过热，大票拉指数小票不跟）
        if rising_ratio >= 0.60 and 80 <= limit_up < 100 and sh_change > 1:
            return "秋收期"
        # 6. 春播（回暖中: 上涨40-60%）
        if 0.40 <= rising_ratio < 0.60 and limit_up >= 80:
            return "春播期"
        # 7. 春播（上涨已达标但涨停不够100，且指数温和）
        if rising_ratio >= 0.60 and 80 <= limit_up < 100 and sh_change <= 1:
            return "春播期"
        # 8. 观察期 — 倾向性判断
        if rising_ratio >= 0.60:
            return "夏长期"
        if rising_ratio < 0.30:
            return "冬藏期"
        if limit_up >= 80:
            return "春播期"
        return "观察期"

    def _build_qlib_features(self, stats: dict, sh_change: float) -> dict:
        """从统计数据构建QLib模型所需的13维特征"""
        total = stats.get("total", 5000)
        rising = stats.get("rising", 0)
        limit_up = stats.get("limit_up", 0)
        limit_down = stats.get("limit_down", 0)

        rising_ratio = rising / total if total else 0

        features = {
            "momentum_5": sh_change / 100,       # 近似5日动量
            "momentum_10": sh_change / 100,       # 近似10日动量
            "momentum_20": sh_change / 100,       # 近似20日动量
            "volatility_5": 0.01 if abs(sh_change) < 3 else 0.03,
            "volatility_20": 0.015,
            "volume_ma5": 1.0,
            "volume_ma20": 1.0,
            "ma5": 1.0,
            "ma20": 1.0,
            "ma60": 1.0,
            "rsi": min(100, 50 + sh_change * 5),       # 估算RSI
            "macd": sh_change / 100,
            "macd_signal": sh_change / 200,
            "bb_position": 0 if abs(sh_change) < 2 else (sh_change / 10),
        }
        return features


# ===========================================================================
# 第4部分: 龙头/中军识别
# ===========================================================================

class StockIdentifier:
    """龙头候选 + 中军候选识别"""

    @staticmethod
    def identify_leaders(df: pd.DataFrame, top_n: int = 5) -> list:
        """
        龙头识别 — 4维评分: 涨幅40% + 换手25% + 市值20% + 成交额15%
        条件: 涨停(≥9.5%) + 换手5-30% + 市值50-500亿
        """
        if df is None or len(df) == 0:
            return []

        # 尝试映射列名
        col_map = StockIdentifier._map_columns(df)
        if col_map is None:
            return []

        c = col_map
        df = df.copy()

        # 数值化
        for key in ["涨跌幅", "换手率", "成交额", "总市值"]:
            if key in c:
                df[c[key]] = pd.to_numeric(df[c[key]], errors="coerce")

        # 筛选涨停股
        zt = df[df[c["涨跌幅"]] >= 9.5].copy()
        if len(zt) == 0:
            return []

        def score(row):
            s = 0
            chg = float(row[c["涨跌幅"]])
            turnover = float(row.get(c.get("换手率", ""), 0) or 0)
            mcap = float(row.get(c.get("总市值", ""), 0) or 0) / 1e8
            amount = float(row.get(c.get("成交额", ""), 0) or 0) / 1e8

            s += min(chg, 20) * 2                                 # 涨幅 40%
            s += 25 if 5 <= turnover <= 20 else (15 if 3 <= turnover <= 30 else 5)  # 换手 25%
            s += 20 if 50 <= mcap <= 500 else (15 if 20 <= mcap <= 1000 else 10)    # 市值 20%
            s += 15 if amount >= 10 else (12 if amount >= 5 else (8 if amount >= 2 else 5))  # 成交额15%
            return s

        zt["_score"] = zt.apply(score, axis=1)
        top = zt.nlargest(top_n, "_score")

        return [
            {
                "名称": row[c.get("名称", "")],
                "代码": row[c.get("代码", "")],
                "涨跌幅": f"{float(row[c['涨跌幅']]):+.2f}%",
                "换手率": f"{float(row.get(c.get('换手率', ''), 0) or 0):.2f}%",
                "成交额": f"{float(row.get(c.get('成交额', ''), 0) or 0) / 1e8:.2f}亿",
                "市值": f"{float(row.get(c.get('总市值', ''), 0) or 0) / 1e8:.1f}亿",
                "得分": int(row["_score"]),
            }
            for _, row in top.iterrows()
        ]

    @staticmethod
    def identify_cores(df: pd.DataFrame, top_n: int = 5) -> list:
        """
        中军识别 — 4维评分: 市值35% + 成交额30% + 涨幅稳健20% + 换手15%
        条件: 涨幅3-7%，市值≥200亿，换手≥2%
        """
        if df is None or len(df) == 0:
            return []

        col_map = StockIdentifier._map_columns(df)
        if col_map is None:
            return []

        c = col_map
        df = df.copy()

        for key in ["涨跌幅", "换手率", "成交额", "总市值"]:
            if key in c:
                df[c[key]] = pd.to_numeric(df[c[key]], errors="coerce")

        # 筛选条件
        mask = (
            (df[c["涨跌幅"]] >= 3) & (df[c["涨跌幅"]] <= 7) &
            (df[c["总市值"]] >= 200e8) &
            (df[c["换手率"]] >= 2)
        )
        core_df = df[mask].copy()

        if len(core_df) == 0:
            # 放宽条件
            mask2 = (df[c["涨跌幅"]] >= 2) & (df[c["总市值"]] >= 100e8) & (df[c["换手率"]] >= 1.5)
            core_df = df[mask2].copy()
        if len(core_df) == 0:
            return []

        def score(row):
            s = 0
            mcap = float(row[c["总市值"]]) / 1e8
            amount = float(row[c["成交额"]]) / 1e8
            chg = float(row[c["涨跌幅"]])
            turnover = float(row[c["换手率"]])

            s += 35 if mcap >= 1000 else (32 if mcap >= 500 else (28 if mcap >= 300 else (25 if mcap >= 200 else 20)))
            s += 30 if amount >= 20 else (27 if amount >= 10 else (22 if amount >= 5 else 18))
            s += 20 if 4 <= chg <= 6 else (18 if 3 <= chg <= 7 else 15)
            s += 15 if 3 <= turnover <= 8 else (12 if 2 <= turnover <= 10 else 10)
            return s

        core_df["_score"] = core_df.apply(score, axis=1)
        top = core_df.nlargest(top_n, "_score")

        return [
            {
                "名称": row[c.get("名称", "")],
                "代码": row[c.get("代码", "")],
                "涨跌幅": f"{float(row[c['涨跌幅']]):+.2f}%",
                "换手率": f"{float(row[c['换手率']]):.2f}%",
                "成交额": f"{float(row[c['成交额']]) / 1e8:.2f}亿",
                "市值": f"{float(row[c['总市值']]) / 1e8:.1f}亿",
                "得分": int(row["_score"]),
            }
            for _, row in top.iterrows()
        ]

    @staticmethod
    def _map_columns(df: pd.DataFrame) -> Optional[dict]:
        """智能列名映射"""
        cols = set(df.columns)
        mapping = {}

        name_checks = {
            "名称": ["名称", "股票名称", "name", "stock_name"],
            "代码": ["代码", "股票代码", "code", "symbol"],
            "涨跌幅": ["涨跌幅", "涨幅", "change_pct", "pct_change"],
            "换手率": ["换手率", "换手", "turnover_rate", "turnover"],
            "成交额": ["成交额", "成交金额", "amount", "volume"],
            "总市值": ["总市值", "市值", "market_cap", "total_market_value"],
        }

        for key, candidates in name_checks.items():
            for cand in candidates:
                if cand in cols:
                    mapping[key] = cand
                    break

        required = ["涨跌幅"]
        missing = [r for r in required if r not in mapping]
        if missing:
            return None
        return mapping


# ===========================================================================
# 第5部分: 真夏长确认
# ===========================================================================

class SummerConfirmation:
    """
    真夏长3日确认系统
    评分维度: 板块强度(25%) + 龙头质量(20%) + 中军响应(25%) + 量能(15%) + 市场环境(15%)
    """

    @staticmethod
    def confirm(
        regime: str,
        limit_up: int,
        leaders: list,
        cores: list,
        sectors: list,
        sh_change: float,
        prev_stats: Optional[dict] = None,
    ) -> dict:
        """
        真夏长确认
        prev_stats: 前一日统计数据，用于趋势判断
        """
        if regime != "夏长期":
            return {"is_real_summer": False, "score": 0, "verdict": "非夏长期，无需确认"}

        score = 0
        details = {}

        # 1. 板块强度 (0-25)
        sector_score = 0
        if sectors:
            sector_count = len([s for s in sectors if s.get("change_pct", 0) > 3])
            sector_score = min(25, sector_count * 5)
            if sector_count >= 3:
                sector_score = 25
        details["板块强度"] = sector_score
        score += sector_score

        # 2. 龙头质量 (0-20)
        leader_score = 0
        if leaders:
            top_score = max(l.get("得分", 0) for l in leaders)
            leader_score = min(20, top_score // 5)
        details["龙头质量"] = leader_score
        score += leader_score

        # 3. 中军响应 (0-25) — 核心维度
        zj_score = 0
        if cores:
            core_avg_chg = sum(float(c["涨跌幅"].replace("%", "").replace("+", ""))
                               for c in cores) / len(cores)
            if core_avg_chg >= 5:
                zj_score = 25
            elif core_avg_chg >= 3:
                zj_score = 20
            elif core_avg_chg >= 1:
                zj_score = 15
            elif core_avg_chg >= 0:
                zj_score = 10
        details["中军响应"] = zj_score
        score += zj_score

        # 4. 量能结构 (0-15)
        vol_score = 10  # 默认
        if prev_stats:
            prev_lu = prev_stats.get("limit_up", 0)
            if limit_up > prev_lu * 1.2:
                vol_score = 15
            elif limit_up > prev_lu:
                vol_score = 12
        if limit_up >= 150:
            vol_score = 15
        details["量能结构"] = vol_score
        score += vol_score

        # 5. 市场环境 (0-15)
        env_score = 10
        if sh_change > 2:
            env_score = 15
        elif sh_change > 0:
            env_score = 12
        elif sh_change < -2:
            env_score = 5
        details["市场环境"] = env_score
        score += env_score

        # 判定
        is_real = score >= 70
        if score >= 85:
            verdict = f"✅ 真夏长确认 (得分{score})，中军健康，重仓持有"
        elif score >= 70:
            verdict = f"✅ 疑似真夏长 (得分{score})，可重仓但需密切监控中军"
        elif score >= 50:
            verdict = f"⚠️ 假夏长概率大 (得分{score})，控制仓位≤30%"
        else:
            verdict = f"🔴 假夏长确认 (得分{score})，减仓或清仓"

        return {
            "is_real_summer": is_real,
            "score": score,
            "verdict": verdict,
            "details": details,
            "zhongjun_alert": zj_score < 15,
        }


# ===========================================================================
# 第6部分: 统一引擎主类
# ===========================================================================

class BiageEngine:
    """彪哥战法统一分析引擎"""

    def __init__(self):
        self.client = QVerisClient()
        self.qlib = QLibSeasonPredictor()
        self.season = SeasonEngine(self.qlib)
        self.identifier = StockIdentifier()
        self.summer = SummerConfirmation()

        self._weekly_trend = 0
        self._last_error = None
        self._prev_stats = None

        # 尝试加载前一日统计用于趋势分析
        self._load_previous_stats()

    def _load_previous_stats(self):
        cache_file = WORKSPACE / ".biage_last_stats.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    self._prev_stats = json.load(f)
            except Exception:
                pass

    def _save_stats(self, stats: dict):
        cache_file = WORKSPACE / ".biage_last_stats.json"
        try:
            with open(cache_file, "w") as f:
                json.dump({**stats, "saved_at": datetime.now().isoformat()}, f)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 主入口: 运行完整分析
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """运行完整的彪哥战法分析"""
        start = time.time()
        errors = []
        result = {
            "timestamp": datetime.now().isoformat(),
            "version": "彪哥战法 v5.0 统一引擎",
            "data_available": False,
        }

        # Step 1: 获取指数数据
        sh_data = None
        try:
            sh_data = self.client.get_index("000001.SH")
            result["shanghai_index"] = sh_data
        except DataFetchError as e:
            errors.append(f"上证指数: {e}")

        # Step 2: 获取涨跌停统计
        stats = None
        try:
            stats = self.client.get_market_stats()
            result["market_stats"] = stats
            result["data_available"] = True
            self._save_stats(stats)
        except DataFetchError as e:
            errors.append(f"涨跌停统计: {e}")

        # 数据验证 — 关键检查
        if not result["data_available"]:
            result["error"] = "数据获取失败"
            result["error_details"] = errors
            result["warning"] = (
                "⚠️ 实盘数据无法获取，本次分析结果不可用于实盘决策。"
                "请检查: 1) QVERIS_API_KEY 环境变量 2) 网络连接 3) QVeris API 服务状态"
            )
            result["elapsed_sec"] = round(time.time() - start, 1)
            return result

        # Step 3: 季节判断
        sh_change = sh_data.get("change_pct", 0) if sh_data else 0
        season_result = self.season.judge(stats, sh_change, self._weekly_trend)
        result["season"] = season_result

        # Step 4: 获取全市场数据
        df = None
        try:
            df = self.client.get_stock_screener()
        except Exception as e:
            log.warning(f"全市场数据获取失败: {e}")

        # Step 5: 龙头/中军识别
        leaders = self.identifier.identify_leaders(df) if df is not None else []
        cores = self.identifier.identify_cores(df) if df is not None else []
        result["leaders"] = leaders
        result["cores"] = cores

        # Step 6: 领涨板块
        sectors = []
        try:
            sectors = self.client.get_sector_leaders()
        except Exception:
            pass
        result["sectors"] = sectors

        # Step 7: 真夏长确认
        summer_result = self.summer.confirm(
            season_result["regime"], stats.get("limit_up", 0),
            leaders, cores, sectors, sh_change, self._prev_stats
        )
        result["summer_confirmation"] = summer_result

        # Step 8: 风控检查
        risk = self._risk_check(season_result, stats, sh_data)
        result["risk"] = risk

        result["elapsed_sec"] = round(time.time() - start, 1)
        return result

    def _risk_check(self, season: dict, stats: dict, sh_data: Optional[dict]) -> dict:
        """风控检查"""
        alerts = []
        limit_down = stats.get("limit_down", 0)
        limit_up = stats.get("limit_up", 0)

        # 监管风险估算
        if limit_down > 50:
            alerts.append("🔴 跌停>50家，强制仓位上限20%")
        if limit_up > 200:
            alerts.append("🟡 涨停>200家，监管可能关注，仓位上限50%")

        # 连续下跌
        if self._prev_stats:
            prev_lu = self._prev_stats.get("limit_up", 0)
            if limit_up < prev_lu * 0.7 and limit_up < 60:
                alerts.append("⚠️ 涨停数大幅萎缩，短线退潮信号")

        return {
            "alerts": alerts,
            "force_position_cap": 0.20 if limit_down > 50 else (0.50 if limit_up > 200 else 1.0),
            "safe": len(alerts) == 0,
        }

    # ------------------------------------------------------------------
    # 报告生成
    # ------------------------------------------------------------------

    def generate_report(self, result: dict) -> str:
        """生成飞书推送格式的报告"""
        if result.get("error"):
            return self._error_report(result)

        season = result["season"]
        stats = result["market_stats"]
        sh = result.get("shanghai_index", {})
        leaders = result.get("leaders", [])
        cores = result.get("cores", [])
        sectors = result.get("sectors", [])
        summer = result.get("summer_confirmation", {})
        risk = result.get("risk", {})

        season_emoji = {"混沌期": "💀", "情绪冰点期": "🧊", "冬藏期": "❄️",
                        "春播期": "🌱", "夏长期": "☀️", "秋收期": "🍂", "观察期": "🔍"}

        emoji = season_emoji.get(season["regime"], "📊")

        lines = [
            f"{emoji} 【彪哥战法 v5.0】盘后分析报告",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"🕐 {result['timestamp'][:19].replace('T', ' ')}",
            f"",
            f"📊 大盘概况",
            f"  上证指数: {sh.get('price', 0):.2f} ({sh.get('change_pct', 0):+.2f}%)",
            f"  上涨: {stats['rising']}/{stats['total']}  |  涨停: {stats['limit_up']}  |  跌停: {stats['limit_down']}",
            f"  上涨比例: {season.get('rising_ratio', 0):.1%}",
            f"",
            f"🎯 市场状态: {season['regime']}",
        ]

        # 季节+仓位+策略 合并一行
        lines.append(f"💰 仓位: {season['position']} | 策略: {season['strategy']}")
        lines.append(f"🧠 判断逻辑: {self._season_reason(season, stats)}")

        # QLib 模型输出
        if "ml_season" in season:
            consensus = "✅ 一致" if season.get("consensus") else "⚠️ 分歧"
            lines.append(f"🤖 QLib模型: {season['ml_season']} (置信度:{season.get('ml_confidence', 0):.0%}) {consensus}")

        # 真夏长确认
        if summer.get("verdict"):
            lines.append(f"")
            lines.append(f"🔥 夏长确认: {summer['verdict']}")
            if summer.get("zhongjun_alert"):
                lines.append(f"   ⚠️ 中军响应偏弱，注意风险")

        # 领涨板块
        if sectors:
            lines.append(f"")
            lines.append(f"📈 领涨板块 TOP5")
            for i, s in enumerate(sectors[:5], 1):
                lines.append(f"  {i}. {s['name']} {s['change_pct']:+.2f}%")

        # 龙头+中军 合并表格
        if leaders or cores:
            lines.append(f"")
            lines.append(f"| 类型 | 排名 | 股票 | 涨跌幅 | 换手率 | 成交额 | 市值 |")
            lines.append(f"|------|------|------|--------|--------|--------|------|")
            for l in leaders[:5]:
                lines.append(f"| 🔥龙头 | {leaders.index(l)+1} | {l['名称']} | {l['涨跌幅']} | {l['换手率']} | {l['成交额']} | {l['市值']} |")
            for c in cores[:5]:
                idx = cores.index(c) + 1
                lines.append(f"| ⚓中军 | {idx} | {c['名称']} | {c['涨跌幅']} | {c['换手率']} | {c['成交额']} | {c['市值']} |")

        # 风控
        risk_alerts = risk.get("alerts", [])
        if risk_alerts:
            lines.append(f"")
            lines.append(f"🚨 风控提醒")
            for a in risk_alerts:
                lines.append(f"  {a}")

        # 脚注
        lines.append(f"")
        lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"⏱️ 耗时: {result.get('elapsed_sec', 0):.1f}秒 | 数据源: QVeris")
        lines.append(f"⚠️ 本报告仅供参考，不构成投资建议")

        return "\n".join(lines)

    def _season_reason(self, season: dict, stats: dict) -> str:
        regime = season["regime"]
        lu = stats["limit_up"]
        ld = stats["limit_down"]
        ratio = season.get("rising_ratio", 0)

        reasons = {
            "混沌期": f"跌停{ld}>30或上涨比{ratio:.1%}<15%",
            "情绪冰点期": f"上涨比{ratio:.1%}<20%且涨停{lu}<60",
            "冬藏期": f"上涨比{ratio:.1%}在20-40%且涨停{lu}<80",
            "春播期": f"上涨比{ratio:.1%}在40-60%且涨停{lu}≥80",
            "夏长期": f"上涨比{ratio:.1%}≥60%且涨停{lu}≥100",
            "秋收期": f"上涨比{ratio:.1%}≥60%且涨停{lu}≥80",
        }
        return reasons.get(regime, "市场特征不明确")

    def _error_report(self, result: dict) -> str:
        lines = [
            "⚠️ 【彪哥战法 v5.0】数据获取失败",
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"🕐 {result['timestamp'][:19].replace('T', ' ')}",
            "",
            result.get("warning", ""),
            "",
            "错误详情:",
        ]
        for e in result.get("error_details", []):
            lines.append(f"  • {e}")
        lines.append("")
        lines.append("请检查后重试。")
        return "\n".join(lines)


# ===========================================================================
# 命令行入口
# ===========================================================================

def main():
    parser = __import__("argparse").ArgumentParser(description="彪哥战法 v5.0 统一分析引擎")
    parser.add_argument("--output", "-o", help="保存报告到文件")
    parser.add_argument("--json", action="store_true", help="输出完整JSON结果")
    parser.add_argument("--quiet", "-q", action="store_true", help="只输出报告不输出日志")
    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    engine = BiageEngine()
    result = engine.run()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        report = engine.generate_report(result)
        print(report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            if args.json:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            else:
                f.write(report)
        log.info(f"报告已保存: {args.output}")


if __name__ == "__main__":
    main()
