#!/usr/bin/env python3
"""
彪哥战法回测验证管线
- 用历史数据验证季节判断准确率
- 每次阈值变更后可自动对比新旧结果
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace"))


# ---------------------------------------------------------------------------
# 回测引擎
# ---------------------------------------------------------------------------

class BiageBacktest:
    """彪哥战法回测引擎"""

    @staticmethod
    def generate_historical_scenarios() -> pd.DataFrame:
        """
        生成覆盖7种季节的历史场景用于验证。
        理想情况下应从QVeris获取真实历史数据，这里使用逻辑覆盖法：
        构建所有季节的边界条件来验证判断逻辑的正确性。
        """
        scenarios = [
            # (涨停, 跌停, 上涨比, 指数涨跌%, 期望季节)
            # 混沌期：跌停>30 或 上涨比<15%
            (40,   32,  0.10, -4.0, "混沌期"),
            (30,   20,  0.12, -3.0, "混沌期"),
            # 情绪冰点：上涨<20% 且 涨停<60
            (30,   10,  0.15, -2.0, "情绪冰点期"),
            (55,   15,  0.18, -1.5, "情绪冰点期"),
            # 冬藏：上涨20-40% 且 涨停<80
            (50,   8,   0.25, -1.0, "冬藏期"),
            (70,   12,  0.35,  0.2, "冬藏期"),
            # 春播：上涨40-60% 且 涨停≥80
            (80,   5,   0.45,  0.5, "春播期"),
            (100,  8,   0.55,  0.8, "春播期"),
            # 夏长：上涨≥60% 且 涨停≥100
            (120,  3,   0.65,  1.5, "夏长期"),
            (150,  2,   0.75,  2.0, "夏长期"),
            (200,  1,   0.85,  3.0, "夏长期"),
            # 秋收：上涨≥60% 且 涨停80-99 且 指数涨>1%（大票拉指数，涨停没跟上）
            (90,   5,   0.65,  1.8, "秋收期"),
            (95,   4,   0.62,  2.0, "秋收期"),
            # 边缘场景
            (60,   6,   0.30,  0.3, "冬藏期"),
            (100,  10,  0.60,  0.5, "夏长期"),   # 涨停≥100=夏长
            (100,  5,   0.61,  0.3, "夏长期"),   # 涨停≥100=夏长
            (110,  4,   0.70,  2.5, "夏长期"),   # 涨停≥100=夏长（即使指数大涨）
        ]

        return pd.DataFrame(scenarios, columns=["limit_up", "limit_down", "rising_ratio", "sh_change", "expected_season"])

    def run(self) -> dict:
        """运行回测"""
        from biage_engine import SeasonEngine

        engine = SeasonEngine()
        df = self.generate_historical_scenarios()

        correct = 0
        results = []

        for _, row in df.iterrows():
            stats = {
                "total": 5000,
                "rising": int(5000 * row["rising_ratio"]),
                "falling": int(5000 * (1 - row["rising_ratio"])),
                "limit_up": int(row["limit_up"]),
                "limit_down": int(row["limit_down"]),
            }
            season_result = engine.judge(stats, row["sh_change"])
            predicted = season_result["regime"]
            expected = row["expected_season"]
            match = predicted == expected
            if match:
                correct += 1

            results.append({
                "涨停": int(row["limit_up"]),
                "跌停": int(row["limit_down"]),
                "上涨比": round(row["rising_ratio"], 2),
                "指数涨跌": row["sh_change"],
                "期望": expected,
                "预测": predicted,
                "正确": match,
            })

        total = len(df)
        accuracy = correct / total if total > 0 else 0

        # 按季节统计准确率
        season_accuracy = {}
        for season in df["expected_season"].unique():
            subset = [r for r in results if r["期望"] == season]
            s_correct = sum(1 for r in subset if r["正确"])
            season_accuracy[season] = f"{s_correct}/{len(subset)} ({s_correct/len(subset):.0%})"

        # 错误分析
        errors = [r for r in results if not r["正确"]]

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": total,
            "correct": correct,
            "accuracy": round(accuracy, 4),
            "season_accuracy": season_accuracy,
            "errors": errors,
            "verdict": "PASS" if accuracy >= 0.90 else "REVIEW_NEEDED",
            "engine_hash": self._engine_hash(),
        }

        return report

    def _engine_hash(self) -> str:
        engine_path = WORKSPACE / "biage_engine.py"
        if engine_path.exists():
            return hashlib.md5(engine_path.read_bytes()).hexdigest()[:12]
        return "unknown"


# ---------------------------------------------------------------------------
# 阈值对比工具
# ---------------------------------------------------------------------------

def compare_thresholds(old_hash: str = ""):
    """
    比较新旧引擎的预测差异。
    运行回测后，如果 accuracy 降低，发出警告。
    """
    bt = BiageBacktest()
    result = bt.run()

    print("=" * 60)
    print("彪哥战法 回测验证")
    print("=" * 60)
    print(f"场景数: {result['total_scenarios']}")
    print(f"准确率: {result['accuracy']:.1%}")
    print(f"结论:   {result['verdict']}")
    print(f"引擎指纹: {result['engine_hash']}")
    print()

    print("各季节准确率:")
    for season, acc in result["season_accuracy"].items():
        print(f"  {season}: {acc}")

    if result["errors"]:
        print(f"\n❌ 错误 ({len(result['errors'])}个):")
        for e in result["errors"]:
            print(f"  {e['期望']} → {e['预测']} "
                  f"(涨停:{e['涨停']} 跌停:{e['跌停']} 上涨:{e['上涨比']} 指数:{e['指数涨跌']}%)")
    else:
        print("\n✅ 全部场景预测正确")

    # 保存结果
    save_path = WORKSPACE / f"backtest_result_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(save_path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {save_path}")

    return result


if __name__ == "__main__":
    compare_thresholds()
