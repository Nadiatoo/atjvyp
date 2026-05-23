#!/usr/bin/env python3
"""
综合收盘报告系统 v2.1 — 数据管道版
合并彪哥战法盘后分析与市场收盘总结
所有数据来自 DataPipeline，不再使用模拟数据。
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add workspace to path for imports
WORKSPACE = Path("/Users/tuqibiao/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE))

from data_pipeline import DataPipeline


class DataQualityTracker:
    """跟踪数据获取质量，有降级时在报告中显式标注"""

    def __init__(self):
        self.issues = []
        self.degraded = False

    def add_issue(self, item: str):
        self.issues.append(item)
        self.degraded = True

    def warning_banner(self) -> str:
        if not self.degraded:
            return ""
        lines = ["⚠️  数据异常，以下为替代数据"]
        for i in self.issues:
            lines.append(f"  · {i}")
        return "\n".join(lines)


class CombinedMarketCloseReportV2:
    """综合收盘报告系统 v2.1"""

    def __init__(self):
        self.pipe = DataPipeline()
        self.today = datetime.now()
        self.date_str = self.today.strftime("%Y-%m-%d")
        self.quality = DataQualityTracker()

    # ------------------------------------------------------------------
    # 数据采集
    # ------------------------------------------------------------------

    def _get_index(self, code: str, name: str) -> dict:
        """获取单个指数，记录数据源"""
        r = self.pipe.get_index(code)
        if r is None:
            self.quality.add_issue(f"{name}({code}): 所有数据源均失败，使用最后已知值")
            return {"code": code, "name": name, "price": 0, "prev_close": 0,
                    "change_pct": 0, "open": 0, "source": "none"}
        src = r.get("source", "unknown")
        if src == "akshare":
            self.quality.add_issue(f"{name}: 腾讯HTTP/QVeris 失败，降级到 akshare 日线数据")
        return r

    def get_market_summary(self):
        """获取市场收盘数据 — 全部来自 DataPipeline"""
        print("📊 获取市场收盘数据...")

        # 三大指数
        sh = self._get_index("000001.SH", "上证指数")
        sz = self._get_index("399001.SZ", "深证成指")
        cy = self._get_index("399006.SZ", "创业板指")

        # 涨跌停统计
        stats = self.pipe.get_market_stats()
        if stats is None:
            stats = {"total": 0, "rising": 0, "falling": 0, "limit_up": 0, "limit_down": 0}
            self.quality.add_issue("涨跌停统计: 所有数据源均失败")

        # 板块排行
        sectors = self.pipe.get_sector_rank()
        sector_list = []
        if sectors is not None and len(sectors) > 0:
            try:
                top = sectors.head(8) if "涨跌幅" in sectors.columns else sectors.head(8)
                for _, row in top.iterrows():
                    sector_list.append({
                        "name": str(row.get("板块名称", row.get("name", ""))),
                        "change_pct": float(row.get("涨跌幅", row.get("change_pct", 0)))
                    })
            except Exception as e:
                self.quality.add_issue(f"板块数据解析异常: {e}")
        else:
            self.quality.add_issue("板块排行: 数据获取失败")

        # 成交量 — 从全市场数据汇总
        spot_df = self.pipe.get_realtime_spot()
        turnover = 0
        northbound = 0
        if spot_df is not None and len(spot_df) > 100:
            try:
                if "成交额" in spot_df.columns:
                    turnover = spot_df["成交额"].sum() / 1e8  # 转为亿
            except Exception:
                pass
        else:
            self.quality.add_issue("全市场行情: 数据获取失败，成交额缺失")

        # 涨跌家数
        rising = stats.get("rising", 0)
        falling = stats.get("falling", 0)
        total = rising + falling
        rising_ratio = round(rising / total * 100, 1) if total > 0 else 0

        market_data = {
            "indices": {
                "上证指数": {"close": sh["price"], "change_pct": sh.get("change_pct", 0)},
                "深证成指": {"close": sz["price"], "change_pct": sz.get("change_pct", 0)},
                "创业板指": {"close": cy["price"], "change_pct": cy.get("change_pct", 0)},
            },
            "stats": {
                "rising_stocks": rising,
                "falling_stocks": falling,
                "rising_ratio": rising_ratio,
                "limit_up": stats.get("limit_up", 0),
                "limit_down": stats.get("limit_down", 0),
                "turnover": f"{turnover/10000:.1f}万亿" if turnover > 10000 else f"{turnover:.0f}亿",
                "northbound": northbound,
            },
            "sectors": sector_list,
            "spot_df": spot_df,  # 传给 biage 分析用
        }

        print(f"✅ 市场数据获取完成 (数据质量: {'⚠️ 有降级' if self.quality.degraded else '✅ 正常'})")
        return market_data

    # ------------------------------------------------------------------
    # 彪哥战法分析
    # ------------------------------------------------------------------

    def run_biage_analysis(self, market_data):
        """运行彪哥战法分析 — 使用 SeasonEngine + StockIdentifier"""
        print("🔍 执行彪哥战法A股分析...")

        stats = market_data["stats"]
        sh_change = market_data["indices"]["上证指数"]["change_pct"]
        spot_df = market_data.get("spot_df")

        # Season judgment — rule-based (no QVeris dependency)
        season, score, position = self._judge_season(stats, sh_change)

        # 龙头/中军识别
        dragons, zhongjuns = self._identify_stocks(spot_df)

        suggestions = self._generate_suggestions(season, score)

        print(f"✅ 彪哥战法分析完成 → {season} ({score}/100)")
        return {
            "season": season,
            "score": score,
            "position_suggestion": position,
            "dragon_candidates": dragons,
            "army_candidates": zhongjuns,
            "suggestions": suggestions,
        }

    def _judge_season(self, stats: dict, sh_change: float) -> tuple:
        """
        季节判断 — 规则引擎
        基于涨跌停数 + 上涨比例 + 上证涨跌幅
        """
        limit_down = stats.get("limit_down", 0)
        limit_up = stats.get("limit_up", 0)
        rising_ratio = stats.get("rising_ratio", 50)

        # Rule-based engine (same logic as biage_engine.SeasonEngine._rule_judge)
        if limit_down >= 50:
            regime = "冬藏"
        elif limit_down >= 25:
            if rising_ratio < 40:
                regime = "冬藏"
            else:
                regime = "秋收"
        elif limit_up >= 80:
            regime = "夏长"
        elif limit_up >= 50:
            if sh_change > 0.5 and rising_ratio > 55:
                regime = "夏长"
            else:
                regime = "春播"
        elif sh_change > 1.0 and rising_ratio > 65:
            regime = "夏长"
        elif sh_change > 0:
            if rising_ratio > 55:
                regime = "春播"
            else:
                regime = "秋收"
        elif sh_change > -1.0:
            regime = "秋收"
        else:
            regime = "冬藏"

        # Score
        score = 50
        if limit_up > 80:
            score += 20
        elif limit_up > 50:
            score += 10
        if limit_down > 50:
            score -= 20
        elif limit_down > 25:
            score -= 10
        if sh_change > 1.0:
            score += 10
        elif sh_change < -1.0:
            score -= 10
        if rising_ratio > 65:
            score += 10
        elif rising_ratio < 35:
            score -= 10

        score = max(0, min(100, score))

        # Position suggestion
        if regime == "夏长":
            position = "60-80%"
        elif regime == "春播":
            position = "40-60%"
        elif regime == "秋收":
            position = "20-40%"
        else:
            position = "0-20%"

        return regime, score, position

    def _identify_stocks(self, spot_df) -> tuple:
        """识别龙头 + 中军候选"""
        dragons = []
        zhongjuns = []

        if spot_df is None or len(spot_df) == 0:
            self.quality.add_issue("全市场行情缺失，龙头/中军识别不可用")
            return dragons, zhongjuns

        try:
            import pandas as pd

            # Map column names
            col_map = {
                "代码": "code", "名称": "name",
                "最新价": "price", "涨跌幅": "change_pct",
                "成交量": "volume", "成交额": "amount",
                "换手率": "turnover", "流通市值": "market_cap",
            }
            # Also try English columns
            for cn, en in list(col_map.items()):
                if cn in spot_df.columns:
                    spot_df = spot_df.rename(columns={cn: en})

            # Check what we have
            needed = ["code", "name", "change_pct"]
            missing = [c for c in needed if c not in spot_df.columns]
            if missing:
                self.quality.add_issue(f"行情数据缺少关键字段: {missing}")
                return dragons, zhongjuns

            df = spot_df.dropna(subset=["change_pct"]).copy()

            # Filter out ST stocks
            if "name" in df.columns:
                df = df[~df["name"].str.contains("ST|退市", na=False)]

            # --- 龙头识别: 涨幅前20，按换手+封板筛选 ---
            df_leader = df.nlargest(100, "change_pct")
            if "turnover" in df_leader.columns:
                df_leader = df_leader[df_leader["turnover"] > 3]
            if "amount" in df_leader.columns:
                df_leader = df_leader[df_leader["amount"] > 5e8]  # 成交额 > 5亿
            if "market_cap" in df_leader.columns:
                df_leader = df_leader[df_leader["market_cap"] > 1e9]  # 市值 > 10亿

            # Score: 涨幅(40%) + 换手(25%) + 成交额(20%) + 市值(15%)
            for _, row in df_leader.head(20).iterrows():
                s = row.get("change_pct", 0) * 0.4
                if "turnover" in df_leader.columns:
                    s += min(row.get("turnover", 0), 30) / 30 * 25 * 0.25
                if "amount" in df_leader.columns:
                    s += min(row.get("amount", 0) / 5e9, 1) * 20
                dragons.append((s, row.get("name", ""), row.get("code", ""),
                                row.get("change_pct", 0)))

            dragons.sort(key=lambda x: x[0], reverse=True)

            # --- 中军识别: 大市值 + 稳定涨幅 ---
            if "market_cap" in df.columns and "amount" in df.columns:
                df_core = df[(df["market_cap"] > 5e10) & (df["amount"] > 2e8)]  # >500亿市值, >2亿成交
                df_core = df_core[df_core["change_pct"].between(-3, 8)]
                for _, row in df_core.nlargest(15, "market_cap").iterrows():
                    s = min(row.get("market_cap", 0) / 5e11, 1) * 35
                    s += min(row.get("amount", 0) / 1e10, 1) * 30
                    s += max(0, min(row.get("change_pct", 0), 5)) / 5 * 20
                    if "turnover" in df.columns:
                        s += min(row.get("turnover", 0), 15) / 15 * 15
                    zhongjuns.append((s, row.get("name", ""), row.get("code", ""),
                                      row.get("change_pct", 0)))

                zhongjuns.sort(key=lambda x: x[0], reverse=True)

        except Exception as e:
            self.quality.add_issue(f"龙头中军识别异常: {e}")

        return dragons[:5], zhongjuns[:5]

    def _generate_suggestions(self, season, score):
        if season == "夏长":
            return [
                "市场处于夏长期，可积极操作",
                "关注龙头股的连板机会，中军股趋势跟踪",
                "注意获利了结时点，防范过热回调",
            ]
        elif season == "春播":
            return [
                "市场处于春播期，可试探性建仓",
                "分批布局优质成长股，关注超跌反弹",
                "控制仓位，严格止损",
            ]
        elif season == "秋收":
            return [
                "市场处于秋收期，逐步减仓锁定利润",
                "关注防御性板块，降低仓位暴露",
                "防范回调风险，不追高",
            ]
        else:
            return [
                "市场处于冬藏期，防守为主",
                "轻仓或空仓等待，保持流动性",
                "关注企稳信号，等待反转确认",
            ]

    # ------------------------------------------------------------------
    # 报告生成
    # ------------------------------------------------------------------

    def generate_professional_report(self, biage_data, market_data):
        """生成专业收盘报告"""
        print("📝 生成专业收盘报告...")
        current_time = datetime.now().strftime("%H:%M")

        warnings = self.quality.warning_banner()

        # 指数表现
        indices_lines = []
        for name, data in market_data["indices"].items():
            pct = data["change_pct"]
            # change_pct is already in percent (e.g. 0.85 means 0.85%)
            indices_lines.append(f"  {name}: {data['close']:.2f} ({pct:+.2f}%)")

        # 板块表现（取前4）
        sectors = market_data.get("sectors", [])
        sorted_sectors = sorted(sectors, key=lambda s: s["change_pct"], reverse=True)
        sectors_lines = []
        for i, s in enumerate(sorted_sectors[:4]):
            sectors_lines.append(f"  {i+1}. {s['name']}: {s['change_pct']:+.2f}%")

        # 龙头
        dragon_lines = []
        for _, name, code, pct in biage_data["dragon_candidates"][:5]:
            dragon_lines.append(f"  · {name}({code})  {pct:+.2f}%")

        # 中军
        army_lines = []
        for _, name, code, pct in biage_data["army_candidates"][:5]:
            army_lines.append(f"  · {name}({code})  {pct:+.2f}%")

        stats = market_data["stats"]

        report = f"""🏁 【收盘综合报告】{self.date_str} {current_time}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{warnings + chr(10) if warnings else ''}
📈 **一、市场表现概览**

**主要指数**
{chr(10).join(indices_lines)}

**市场统计**
  涨 {stats['rising_stocks']} / 跌 {stats['falling_stocks']}
  上涨比例: {stats['rising_ratio']}%
  涨停: {stats['limit_up']} / 跌停: {stats['limit_down']}
  成交金额: {stats['turnover']}

**板块表现**
{chr(10).join(sectors_lines) if sectors_lines else '  数据获取失败'}

🎯 **二、彪哥战法分析**

**季节判断**: {biage_data['season']}（评分: {biage_data['score']}/100）
**仓位建议**: {biage_data['position_suggestion']}

**龙头候选**
{chr(10).join(dragon_lines) if dragon_lines else '  数据不足，无法识别'}

**中军候选**
{chr(10).join(army_lines) if army_lines else '  数据不足，无法识别'}

🔍 **三、综合分析与建议**

**彪哥战法建议**
{chr(10).join('  · ' + s for s in biage_data['suggestions'])}

💡 **四、操作策略**

  1. 仓位管理: {biage_data['position_suggestion']}，{biage_data['season']}期操作
  2. 板块配置: 关注{', '.join(s['name'] for s in sorted_sectors[:3]) if sorted_sectors else '待定'}等板块
  3. 风险控制: 严格止损，不追高不杀跌
  4. 明日关注: 龙头持续性 + 成交量变化

📊 **五、数据源说明**
  数据管道: {' ⚠️ 有降级' if self.quality.degraded else ' ✅ 正常'}
  使用源: {json.dumps(self.pipe._source_used, ensure_ascii=False) if self.pipe._source_used else '无'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📱 报告类型: 收盘综合报告 v2.1（数据管道 + 彪哥战法）
"""

        return report

    # ------------------------------------------------------------------
    # 保存与显示
    # ------------------------------------------------------------------

    def save_report(self, report):
        report_dir = WORKSPACE / "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_file = report_dir / f"close_report_pro_{self.date_str}.txt"
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"✅ 报告已保存至: {report_file}")
            return str(report_file)
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
            return None

    def display_summary(self, report):
        print("\n" + "=" * 60)
        print("📋 收盘综合报告摘要")
        print("=" * 60)
        for line in report.split("\n")[:50]:
            print(line)
        print("=" * 60)

    def run(self):
        print("=" * 70)
        print(f"收盘综合报告系统 v2.1 - {self.date_str}")
        print(f"数据管道状态: {json.dumps(self.pipe.status(), ensure_ascii=False)}")
        print("=" * 70)

        # 1. 获取市场数据（来自 DataPipeline）
        market_data = self.get_market_summary()

        # 验证关键数据
        sh_idx = market_data["indices"].get("上证指数", {})
        if sh_idx.get("close", 0) == 0:
            print("❌ 致命错误: 上证指数数据不可用，所有数据源均失败")
            print("   请检查网络连接后重试")
            return False

        # 2. 彪哥战法分析
        biage_data = self.run_biage_analysis(market_data)

        # 3. 生成报告
        report = self.generate_professional_report(biage_data, market_data)

        # 4. 保存 + 显示
        report_file = self.save_report(report)
        if report_file:
            self.display_summary(report)
            print(f"\n📤 报告就绪: {report_file}")
            print(f"⏰ 下次报告: 明日17:00")
            return True
        else:
            print("\n❌ 报告生成失败")
            return False


if __name__ == "__main__":
    reporter = CombinedMarketCloseReportV2()
    success = reporter.run()
    sys.exit(0 if success else 1)
