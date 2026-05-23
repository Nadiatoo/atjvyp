#!/usr/bin/env python3
"""
优化版盘前推送脚本
- 合并消息减少 API 调用
- Token 使用监控
- 精简输出
"""

import sys
sys.path.insert(0, '/Users/tuqibiao/.openclaw/workspace/qlib_biaoge')

from feishu_optimizer import send_optimized, show_token_usage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_prewatch_summary():
    """生成盘前摘要（精简版）"""
    
    summary = """📊 【彪哥战法】盘前策略 ({date})

🎯 当前季节: {season}
💰 建议仓位: {position}

📈 市场要点:
{market_points}

🔥 关注板块:
{sectors}

⚠️ 风险提示:
{risks}

💡 操作建议:
{action}

---
详细分析图片已保存到桌面
"""
    
    # 填充内容（实际运行时从模型获取）
    content = summary.format(
        date="2026-03-02 周一",
        season="冬藏→春播过渡期",
        position="20-30%",
        market_points="""• 美伊冲突: 基准情形低开高走 (概率60%)
• 两会窗口: 政策维稳预期
• 量能: 关注开盘30分钟成交额""",
        sectors="""1. 军工 (无人机+智能化)
2. 黄金 (避险+冲击前高)
3. 油运 (霍尔木兹风险)
4. 化工 (涨价+供给约束)
5. 有色 (稀土/战略小金属)""",
        risks="""• 伊朗报复手段升级
• 美军调动增加
• 霍尔木兹海峡通航
• 北向资金流向""",
        action="""基准剧本: 低开高走 → 加仓至40-50%
悲观剧本: 低开低走 → 保持20%或减仓
乐观剧本: 直接高开 → 不追高等回踩"""
    )
    
    return content


def send_prewatch_optimized():
    """优化版盘前推送（只调用一次 API）"""
    
    logger.info("=" * 60)
    logger.info("开始优化版盘前推送")
    logger.info("=" * 60)
    
    # 显示当前 Token 使用情况
    show_token_usage()
    
    # 生成摘要
    summary = generate_prewatch_summary()
    
    # 添加到缓冲区（不立即发送）
    send_optimized(text=summary)
    
    # 提示图片位置（不发送，节省 API）
    send_optimized(text="\n📎 详细图表: 桌面/彪哥战法_明日策略_0302.png")
    
    # 一次性发送（只调用一次 API）
    logger.info("发送消息...")
    success = send_optimized(flush=True, target="ou_cde15d08540b24715fa99809729cf1be")
    
    if success:
        logger.info("✅ 盘前推送成功（API 调用: 1次）")
    else:
        logger.error("❌ 发送失败")
    
    # 显示发送后状态
    status = send_optimized.__self__ if hasattr(send_optimized, '__self__') else None
    if status:
        logger.info(f"今日剩余 API 调用: {status.get('remaining_calls', 'N/A')}")
    
    return success


if __name__ == "__main__":
    send_prewatch_optimized()
